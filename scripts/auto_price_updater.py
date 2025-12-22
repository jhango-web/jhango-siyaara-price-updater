"""
Automatic Price Updater

Fetches live gold/silver prices from GoldAPI and updates Shopify product prices.
Designed to be run via GitHub Actions on a schedule.
"""

import os
import sys
import json
import logging
from datetime import datetime

from goldapi_client import GoldAPIClient
from shopify_client import ShopifyClient
from price_calculator import PriceCalculator
from price_updater import PriceUpdater

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for automatic price updates via GitHub Actions."""
    logger.info("="*80)
    logger.info("AUTOMATIC PRICE UPDATE STARTED")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("="*80)

    # Read environment variables
    goldapi_key = os.environ.get('GOLDAPI_KEY')
    shopify_shop_url = os.environ.get('SHOPIFY_SHOP_URL')
    shopify_access_token = os.environ.get('SHOPIFY_ACCESS_TOKEN')
    shopify_theme_id = os.environ.get('SHOPIFY_THEME_ID')
    currency = os.environ.get('CURRENCY', 'INR')

    # Validate required environment variables
    missing_vars = []
    if not goldapi_key:
        missing_vars.append('GOLDAPI_KEY')
    if not shopify_shop_url:
        missing_vars.append('SHOPIFY_SHOP_URL')
    if not shopify_access_token:
        missing_vars.append('SHOPIFY_ACCESS_TOKEN')
    if not shopify_theme_id:
        missing_vars.append('SHOPIFY_THEME_ID')

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please ensure all required secrets are configured in GitHub repository settings")
        sys.exit(1)

    try:
        # Step 1: Fetch live metal prices from GoldAPI
        logger.info("\nStep 1: Fetching live metal prices from GoldAPI")
        logger.info("-" * 80)

        goldapi = GoldAPIClient(goldapi_key, currency)

        # Test connection first
        if not goldapi.test_connection():
            logger.error("Failed to connect to GoldAPI. Aborting update.")
            sys.exit(1)

        # Fetch prices
        prices = goldapi.get_metal_prices()

        if not prices:
            logger.error("Failed to fetch valid metal prices from GoldAPI. Aborting update.")
            sys.exit(1)

        gold_rate = prices['gold_rate']
        silver_rate = prices['silver_rate']

        # Validate rates (must be positive and non-zero)
        if gold_rate <= 0 or silver_rate <= 0:
            logger.error(f"Invalid rates received: gold={gold_rate}, silver={silver_rate}")
            logger.error("Both rates must be positive and non-zero. Aborting update.")
            sys.exit(1)

        logger.info(f"✓ Valid metal prices fetched")
        logger.info(f"  24K Gold: {currency} {gold_rate:.2f}/g")
        logger.info(f"  Silver 925: {currency} {silver_rate:.2f}/g")

        # Step 2: Initialize Shopify client and fetch theme settings
        logger.info("\nStep 2: Connecting to Shopify and fetching theme settings")
        logger.info("-" * 80)

        shopify = ShopifyClient(shopify_shop_url, shopify_access_token)
        theme_settings = shopify.get_theme_settings(shopify_theme_id)

        making_charges = theme_settings['making_charges']
        markup_percentage = theme_settings['markup_percentage']

        logger.info(f"✓ Theme settings fetched")

        # Step 3: Update theme settings with new rates
        logger.info("\nStep 3: Updating theme settings with new rates")
        logger.info("-" * 80)

        success = shopify.update_theme_settings(shopify_theme_id, gold_rate, silver_rate)

        if not success:
            logger.warning("Failed to update theme settings, but continuing with price updates")
        else:
            logger.info(f"✓ Theme settings updated")

        # Step 4: Initialize price calculator
        logger.info("\nStep 4: Initializing price calculator")
        logger.info("-" * 80)

        calculator = PriceCalculator(making_charges, markup_percentage)
        logger.info(f"✓ Price calculator initialized")

        # Step 5: Update product prices
        logger.info("\nStep 5: Updating product prices")
        logger.info("-" * 80)

        updater = PriceUpdater(shopify, calculator)

        stats = updater.update_prices(
            gold_rate=gold_rate,
            silver_rate=silver_rate,
            update_metafields=True,
            dry_run=False
        )

        # Step 6: Generate summary and exit
        logger.info("\n" + "="*80)
        logger.info("AUTOMATIC PRICE UPDATE COMPLETED")
        logger.info("="*80)
        logger.info(f"Products Processed: {stats['products_processed']}")
        logger.info(f"Variants Updated: {stats['variants_updated']}")
        logger.info(f"Variants Skipped: {stats['variants_skipped']}")
        logger.info(f"Variants Failed: {stats['variants_failed']}")
        logger.info(f"Metafields Updated: {stats['metafields_updated']}")
        logger.info(f"Metafields Failed: {stats['metafields_failed']}")
        logger.info(f"Errors: {len(stats['errors'])}")

        if stats['errors']:
            logger.error("\nErrors encountered:")
            for error in stats['errors']:
                logger.error(f"  - {error}")

        logger.info("="*80)

        # Save summary to file for GitHub Actions artifact
        summary = {
            'timestamp': datetime.now().isoformat(),
            'gold_rate': gold_rate,
            'silver_rate': silver_rate,
            'currency': currency,
            'statistics': stats
        }

        with open('price_update_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info("\nSummary saved to: price_update_summary.json")

        # Exit with appropriate code
        if stats['variants_failed'] > 0 or stats['errors']:
            logger.warning("Update completed with errors")
            sys.exit(1)
        else:
            logger.info("Update completed successfully")
            sys.exit(0)

    except Exception as e:
        logger.error(f"\n{'='*80}")
        logger.error(f"CRITICAL ERROR: {e}")
        logger.error(f"{'='*80}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
