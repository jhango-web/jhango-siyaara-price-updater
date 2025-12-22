"""
Price Updater Script

Updates product prices based on gold/silver rates from metafields.
Can be run manually with input parameters or automatically via GitHub Actions.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, List, Optional, Any
from datetime import datetime

from price_calculator import PriceCalculator
from shopify_client import ShopifyClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'price_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class PriceUpdater:
    """Handles updating product prices based on metal rates."""

    def __init__(self, shopify_client: ShopifyClient, price_calculator: PriceCalculator):
        """
        Initialize price updater.

        Args:
            shopify_client: Shopify API client
            price_calculator: Price calculator instance
        """
        self.client = shopify_client
        self.calculator = price_calculator
        self.stats = {
            'products_processed': 0,
            'variants_updated': 0,
            'variants_skipped': 0,
            'variants_failed': 0,
            'metafields_updated': 0,
            'metafields_failed': 0,
            'errors': []
        }

    def update_prices(self, gold_rate: float, silver_rate: float,
                     update_metafields: bool = True, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update prices for all products with gold_rate and silver_rate metafields.

        Args:
            gold_rate: New gold rate per gram (in rupees)
            silver_rate: New silver rate per gram (in rupees)
            update_metafields: Whether to update the metafields with new rates
            dry_run: If True, don't actually update prices (for testing)

        Returns:
            Dictionary with update statistics
        """
        logger.info("="*80)
        logger.info("PRICE UPDATE STARTED")
        logger.info("="*80)
        logger.info(f"Gold Rate: ₹{gold_rate}/g")
        logger.info(f"Silver Rate: ₹{silver_rate}/g")
        logger.info(f"Making Charges: ₹{self.calculator.making_charges}")
        logger.info(f"Markup Percentage: {self.calculator.markup_percentage}%")
        logger.info(f"Dry Run: {dry_run}")
        logger.info("="*80)

        # Validate rates
        if gold_rate <= 0 or silver_rate <= 0:
            error_msg = f"Invalid rates: gold={gold_rate}, silver={silver_rate}. Both must be > 0"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return self.stats

        # Fetch products with metafields
        products = self.client.get_products_with_metafields()

        if not products:
            logger.warning("No products found with required metafields")
            return self.stats

        logger.info(f"Processing {len(products)} products")

        for product in products:
            try:
                self._process_product(product, gold_rate, silver_rate, update_metafields, dry_run)
            except Exception as e:
                error_msg = f"Error processing product {product['id']}: {e}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)

        logger.info("\n" + "="*80)
        logger.info("PRICE UPDATE COMPLETED")
        logger.info("="*80)
        logger.info(f"Products Processed: {self.stats['products_processed']}")
        logger.info(f"Variants Updated: {self.stats['variants_updated']}")
        logger.info(f"Variants Skipped: {self.stats['variants_skipped']}")
        logger.info(f"Variants Failed: {self.stats['variants_failed']}")
        logger.info(f"Metafields Updated: {self.stats['metafields_updated']}")
        logger.info(f"Metafields Failed: {self.stats['metafields_failed']}")
        logger.info(f"Errors: {len(self.stats['errors'])}")
        logger.info("="*80)

        return self.stats

    def _process_product(self, product: Dict[str, Any], gold_rate: float, silver_rate: float,
                        update_metafields: bool, dry_run: bool):
        """Process a single product and update its variant prices."""
        product_id = product['id']
        product_handle = product['handle']

        logger.info(f"\nProcessing product: {product_handle} (ID: {product_id})")

        # Update product metafields if requested
        if update_metafields:
            logger.info(f"  Updating metafields with new rates")

            if not dry_run:
                # Update gold_rate metafield
                success_gold = self.client.update_product_metafield(
                    product_id, 'jhango', 'gold_rate',
                    str(gold_rate), 'number_decimal'
                )

                # Update silver_rate metafield
                success_silver = self.client.update_product_metafield(
                    product_id, 'jhango', 'silver_rate',
                    str(silver_rate), 'number_decimal'
                )

                if success_gold and success_silver:
                    self.stats['metafields_updated'] += 2
                    logger.info(f"  ✓ Updated metafields")
                else:
                    self.stats['metafields_failed'] += (0 if success_gold else 1) + (0 if success_silver else 1)
                    logger.warning(f"  ✗ Failed to update some metafields")
            else:
                logger.info(f"  [DRY RUN] Would update metafields")

        # Process variants
        variants = product.get('variants', [])
        logger.info(f"  Processing {len(variants)} variants")

        for variant in variants:
            self._process_variant(product, variant, gold_rate, silver_rate, dry_run)

        self.stats['products_processed'] += 1

    def _process_variant(self, product: Dict[str, Any], variant: Dict[str, Any],
                        gold_rate: float, silver_rate: float, dry_run: bool):
        """Process a single variant and update its price."""
        variant_id = variant['id']
        option1 = variant.get('option1', '')

        # Fetch variant metafields
        variant_metafields = self.client.get_variant_metafields(variant_id)

        # Extract required metafield values
        metal_weight = self._get_metafield_value(variant_metafields, 'custom', 'metal_weight', 0.0, float)
        stone_types_str = self._get_metafield_value(variant_metafields, 'custom', 'stone_types', '[]', str)
        stone_carats_str = self._get_metafield_value(variant_metafields, 'custom', 'stone_carats', '[]', str)
        stone_prices_str = self._get_metafield_value(variant_metafields, 'custom', 'stone_prices_per_carat', '[]', str)

        # Parse lists
        try:
            stone_types = json.loads(stone_types_str) if stone_types_str else []
            stone_carats = json.loads(stone_carats_str) if stone_carats_str else []
            stone_prices = json.loads(stone_prices_str) if stone_prices_str else []
        except json.JSONDecodeError as e:
            logger.warning(f"    Variant {variant_id}: Failed to parse stone data: {e}")
            stone_types = []
            stone_carats = []
            stone_prices = []

        # Skip if no metal weight (can't calculate price)
        if metal_weight <= 0:
            logger.debug(f"    Variant {variant_id}: Skipped (no metal weight)")
            self.stats['variants_skipped'] += 1
            return

        # Calculate new price
        price_result = self.calculator.calculate_price(
            metal_weight=metal_weight,
            stone_types=stone_types,
            stone_carats=stone_carats,
            stone_prices_per_carat=stone_prices,
            option1_value=option1,
            gold_rate=gold_rate,
            silver_rate=silver_rate
        )

        if not price_result:
            logger.warning(f"    Variant {variant_id}: Could not calculate price (invalid option: {option1})")
            self.stats['variants_skipped'] += 1
            return

        new_price = price_result['total_price']
        old_price = float(variant.get('price', 0))

        # Log price breakdown
        logger.info(f"    Variant {variant_id} ({option1})")
        logger.info(f"      Metal: ₹{price_result['metal_cost']} "
                   f"(Weight: {metal_weight}g × Rate: ₹{price_result['breakdown']['metal']['base_rate']}/g × "
                   f"Purity: {price_result['breakdown']['metal']['purity_factor']})")
        logger.info(f"      Stones: ₹{price_result['stone_cost']}")
        logger.info(f"      Making: ₹{price_result['making_charges']}")
        logger.info(f"      Markup: ₹{price_result['markup_cost']} ({self.calculator.markup_percentage}%)")
        logger.info(f"      GST: ₹{price_result['gst_cost']} ({self.calculator.gst_percentage}%)")
        logger.info(f"      Old Price: ₹{old_price} → New Price: ₹{new_price}")

        # Update price if changed
        if abs(new_price - old_price) >= 0.01:  # Only update if difference is significant
            if not dry_run:
                success = self.client.update_variant_price(variant_id, new_price)
                if success:
                    self.stats['variants_updated'] += 1
                    logger.info(f"      ✓ Price updated")
                else:
                    self.stats['variants_failed'] += 1
                    logger.warning(f"      ✗ Failed to update price")
            else:
                logger.info(f"      [DRY RUN] Would update price")
                self.stats['variants_updated'] += 1
        else:
            logger.info(f"      No price change needed")
            self.stats['variants_skipped'] += 1

    @staticmethod
    def _get_metafield_value(metafields: List[Dict], namespace: str, key: str,
                            default: Any, value_type: type) -> Any:
        """Extract metafield value by namespace and key."""
        for mf in metafields:
            if mf['namespace'] == namespace and mf['key'] == key:
                try:
                    return value_type(mf['value'])
                except (ValueError, TypeError):
                    return default
        return default


def main():
    """Main entry point for manual execution."""
    parser = argparse.ArgumentParser(description='Update Shopify product prices based on metal rates')
    parser.add_argument('--shop-url', required=True, help='Shopify store URL (e.g., mystore.myshopify.com)')
    parser.add_argument('--access-token', required=True, help='Shopify Admin API access token')
    parser.add_argument('--theme-id', required=True, help='Theme ID for fetching settings')
    parser.add_argument('--gold-rate', type=float, required=True, help='Gold rate per gram (in rupees)')
    parser.add_argument('--silver-rate', type=float, required=True, help='Silver rate per gram (in rupees)')
    parser.add_argument('--making-charges', type=float, help='Override making charges (optional)')
    parser.add_argument('--markup-percentage', type=float, help='Override markup percentage (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Simulate updates without making changes')
    parser.add_argument('--skip-metafields', action='store_true', help='Skip updating metafields')

    args = parser.parse_args()

    # Initialize Shopify client
    client = ShopifyClient(args.shop_url, args.access_token)

    # Fetch theme settings or use overrides
    if args.making_charges is not None and args.markup_percentage is not None:
        making_charges = args.making_charges
        markup_percentage = args.markup_percentage
        logger.info("Using provided making charges and markup percentage")
    else:
        theme_settings = client.get_theme_settings(args.theme_id)
        making_charges = theme_settings['making_charges']
        markup_percentage = theme_settings['markup_percentage']

    # Initialize price calculator
    calculator = PriceCalculator(making_charges, markup_percentage)

    # Initialize price updater
    updater = PriceUpdater(client, calculator)

    # Update theme settings with new rates (unless skip-metafields is set)
    if not args.skip_metafields and not args.dry_run:
        logger.info("Updating theme settings with new rates")
        client.update_theme_settings(args.theme_id, args.gold_rate, args.silver_rate)

    # Update prices
    stats = updater.update_prices(
        gold_rate=args.gold_rate,
        silver_rate=args.silver_rate,
        update_metafields=not args.skip_metafields,
        dry_run=args.dry_run
    )

    # Save stats to JSON file
    stats_file = f'price_update_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info(f"\nStatistics saved to: {stats_file}")

    # Exit with error code if there were failures
    if stats['variants_failed'] > 0 or stats['metafields_failed'] > 0 or stats['errors']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
