"""
Shopify API Client

Handles all interactions with Shopify API including:
- Fetching products with specific metafields
- Updating product metafields
- Updating variant prices
- Fetching theme settings
"""

import requests
import json
import time
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ShopifyClient:
    """Client for Shopify API operations."""

    def __init__(self, shop_url: str, access_token: str):
        """
        Initialize Shopify client.

        Args:
            shop_url: Shopify store URL (e.g., 'mystore.myshopify.com')
            access_token: Shopify Admin API access token
        """
        self.shop_url = shop_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.base_url = f"https://{self.shop_url}/admin/api/2024-01"
        self.graphql_url = f"https://{self.shop_url}/admin/api/2024-01/graphql.json"
        self.headers = {
            'X-Shopify-Access-Token': self.access_token,
            'Content-Type': 'application/json'
        }

    def get_theme_settings(self, theme_id: str) -> Dict[str, Any]:
        """
        Fetch theme settings from Shopify.

        Args:
            theme_id: Theme ID to fetch settings from

        Returns:
            Dict with making_charges, markup_percentage, etc.
        """
        logger.info(f"Fetching theme settings for theme ID: {theme_id}")

        try:
            url = f"{self.base_url}/themes/{theme_id}/assets.json"
            params = {'asset[key]': 'config/settings_data.json'}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            asset_data = response.json()
            settings_json = asset_data['asset']['value']
            settings_data = json.loads(settings_json)

            current_settings = settings_data.get('current', {})

            theme_settings = {
                'making_charges': float(current_settings.get('making_charges', 0)),
                'markup_percentage': float(current_settings.get('markup_percentage', 0)),
                'gst_percentage': float(current_settings.get('gst_percentage', 3))
            }

            logger.info(f"Successfully fetched theme settings")
            logger.info(f"  Making Charges: ₹{theme_settings['making_charges']}")
            logger.info(f"  Markup Percentage: {theme_settings['markup_percentage']}%")
            logger.info(f"  GST Percentage: {theme_settings['gst_percentage']}%")

            return theme_settings

        except Exception as e:
            logger.error(f"Failed to fetch theme settings: {e}")
            logger.warning("Using default theme settings")
            return {
                'making_charges': 0,
                'markup_percentage': 0,
                'gst_percentage': 3
            }

    def update_theme_settings(self, theme_id: str, gold_rate: float, silver_rate: float) -> bool:
        """
        Update gold and silver rates in theme settings.

        Args:
            theme_id: Theme ID to update
            gold_rate: New gold rate per gram
            silver_rate: New silver rate per gram

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Updating theme settings with gold_rate: ₹{gold_rate}/g, silver_rate: ₹{silver_rate}/g")

        try:
            # First, get current settings
            url = f"{self.base_url}/themes/{theme_id}/assets.json"
            params = {'asset[key]': 'config/settings_data.json'}

            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            asset_data = response.json()
            settings_json = asset_data['asset']['value']
            settings_data = json.loads(settings_json)

            # Update the rates
            if 'current' not in settings_data:
                settings_data['current'] = {}

            settings_data['current']['gold_rate'] = gold_rate
            settings_data['current']['silver_rate'] = silver_rate

            # Save updated settings
            updated_json = json.dumps(settings_data)

            put_data = {
                'asset': {
                    'key': 'config/settings_data.json',
                    'value': updated_json
                }
            }

            response = requests.put(url, json=put_data, headers=self.headers, timeout=30)
            response.raise_for_status()

            logger.info(f"Successfully updated theme settings")
            return True

        except Exception as e:
            logger.error(f"Failed to update theme settings: {e}")
            return False

    def get_products_with_metafields(self, limit: int = 250) -> List[Dict[str, Any]]:
        """
        Fetch all products that have jhango.gold_rate and jhango.silver_rate metafields.

        Args:
            limit: Number of products to fetch per page

        Returns:
            List of product dictionaries with variants and metafields
        """
        logger.info("Fetching products with jhango.gold_rate and jhango.silver_rate metafields")

        all_products = []
        page_info = None
        page = 1

        while True:
            try:
                # Build URL with pagination
                url = f"{self.base_url}/products.json"
                params = {'limit': limit}

                if page_info:
                    params['page_info'] = page_info

                response = requests.get(url, headers=self.headers, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                products = data.get('products', [])

                if not products:
                    break

                logger.info(f"Fetched page {page} with {len(products)} products")

                # Filter products that have the required metafields
                for product in products:
                    # Fetch product metafields
                    metafields = self.get_product_metafields(product['id'])

                    # Check if product has both gold_rate and silver_rate metafields
                    has_gold_rate = any(
                        mf['namespace'] == 'jhango' and mf['key'] == 'gold_rate'
                        for mf in metafields
                    )
                    has_silver_rate = any(
                        mf['namespace'] == 'jhango' and mf['key'] == 'silver_rate'
                        for mf in metafields
                    )

                    if has_gold_rate and has_silver_rate:
                        product['metafields'] = metafields
                        all_products.append(product)

                # Check for next page
                link_header = response.headers.get('Link', '')
                if 'rel="next"' in link_header:
                    # Extract page_info from Link header
                    for link in link_header.split(','):
                        if 'rel="next"' in link:
                            page_info = link.split('page_info=')[1].split('>')[0]
                            break
                    page += 1
                    time.sleep(0.5)  # Rate limiting
                else:
                    break

            except Exception as e:
                logger.error(f"Error fetching products page {page}: {e}")
                break

        logger.info(f"Found {len(all_products)} products with gold_rate and silver_rate metafields")
        return all_products

    def get_product_metafields(self, product_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all metafields for a product.

        Args:
            product_id: Product ID

        Returns:
            List of metafield dictionaries
        """
        try:
            url = f"{self.base_url}/products/{product_id}/metafields.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get('metafields', [])

        except Exception as e:
            logger.error(f"Error fetching metafields for product {product_id}: {e}")
            return []

    def get_variant_metafields(self, variant_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all metafields for a variant.

        Args:
            variant_id: Variant ID

        Returns:
            List of metafield dictionaries
        """
        try:
            url = f"{self.base_url}/variants/{variant_id}/metafields.json"
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data.get('metafields', [])

        except Exception as e:
            logger.error(f"Error fetching metafields for variant {variant_id}: {e}")
            return []

    def update_product_metafield(self, product_id: int, namespace: str, key: str,
                                 value: str, value_type: str) -> bool:
        """
        Update or create a product metafield.

        Args:
            product_id: Product ID
            namespace: Metafield namespace
            key: Metafield key
            value: Metafield value (as string)
            value_type: Metafield type (e.g., 'number_decimal')

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, check if metafield exists
            metafields = self.get_product_metafields(product_id)
            existing_mf = None

            for mf in metafields:
                if mf['namespace'] == namespace and mf['key'] == key:
                    existing_mf = mf
                    break

            if existing_mf:
                # Update existing metafield
                url = f"{self.base_url}/products/{product_id}/metafields/{existing_mf['id']}.json"
                data = {
                    'metafield': {
                        'id': existing_mf['id'],
                        'value': value,
                        'type': value_type
                    }
                }
                response = requests.put(url, json=data, headers=self.headers, timeout=30)
            else:
                # Create new metafield
                url = f"{self.base_url}/products/{product_id}/metafields.json"
                data = {
                    'metafield': {
                        'namespace': namespace,
                        'key': key,
                        'value': value,
                        'type': value_type
                    }
                }
                response = requests.post(url, json=data, headers=self.headers, timeout=30)

            response.raise_for_status()
            return True

        except Exception as e:
            logger.error(f"Error updating metafield {namespace}.{key} for product {product_id}: {e}")
            return False

    def update_variant_price(self, variant_id: int, price: float) -> bool:
        """
        Update variant price.

        Args:
            variant_id: Variant ID
            price: New price

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/variants/{variant_id}.json"
            data = {
                'variant': {
                    'id': variant_id,
                    'price': str(price)
                }
            }

            response = requests.put(url, json=data, headers=self.headers, timeout=30)
            response.raise_for_status()

            return True

        except Exception as e:
            logger.error(f"Error updating price for variant {variant_id}: {e}")
            return False

    def get_variant_option1(self, product: Dict[str, Any], variant_id: int) -> Optional[str]:
        """
        Get option1 value for a variant.

        Args:
            product: Product dictionary
            variant_id: Variant ID

        Returns:
            Option1 value string or None
        """
        for variant in product.get('variants', []):
            if variant['id'] == variant_id:
                return variant.get('option1')
        return None
