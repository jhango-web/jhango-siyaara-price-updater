"""
GoldAPI Client

Fetches live gold and silver prices from GoldAPI.io
"""

import requests
import json
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GoldAPIClient:
    """Client for GoldAPI.io."""

    def __init__(self, api_key: str, currency: str = 'INR'):
        """
        Initialize GoldAPI client.

        Args:
            api_key: GoldAPI.io API key
            currency: Currency code (default: INR for Indian Rupees)
        """
        self.api_key = api_key
        self.currency = currency
        self.base_url = 'https://www.goldapi.io/api'

    def get_metal_prices(self) -> Optional[Dict[str, float]]:
        """
        Fetch current gold and silver prices.

        Returns:
            Dict with 'gold_rate' and 'silver_rate' per gram in specified currency,
            or None if fetch fails or rates are zero/invalid
        """
        logger.info(f"Fetching metal prices from GoldAPI.io (Currency: {self.currency})")

        try:
            # Fetch gold price (24K)
            gold_rate = self._fetch_gold_24k_per_gram()

            if gold_rate is None or gold_rate <= 0:
                logger.error("Invalid gold rate received (zero or negative)")
                return None

            # Fetch silver price (925)
            silver_rate = self._fetch_silver_925_per_gram()

            if silver_rate is None or silver_rate <= 0:
                logger.error("Invalid silver rate received (zero or negative)")
                return None

            logger.info(f"Successfully fetched rates:")
            logger.info(f"  24K Gold: {self.currency} {gold_rate:.2f}/g")
            logger.info(f"  Silver 925: {self.currency} {silver_rate:.2f}/g")

            return {
                'gold_rate': gold_rate,
                'silver_rate': silver_rate
            }

        except Exception as e:
            logger.error(f"Error fetching metal prices: {e}")
            return None

    def _fetch_gold_24k_per_gram(self) -> Optional[float]:
        """
        Fetch 24K gold price per gram.

        Returns:
            Price per gram in specified currency, or None if fetch fails
        """
        try:
            # GoldAPI.io endpoint for current gold price
            url = f"{self.base_url}/XAU/{self.currency}"
            headers = {
                'x-access-token': self.api_key,
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"GoldAPI response for XAU: {json.dumps(data, indent=2)}")

            # GoldAPI returns price per troy ounce for gold
            # We need to extract the per-gram price for 24K gold
            # The response typically has 'price_gram_24k' field
            if 'price_gram_24k' in data:
                gold_rate = float(data['price_gram_24k'])
                logger.info(f"Extracted gold rate from price_gram_24k: {gold_rate}")
                return gold_rate
            elif 'price' in data:
                # If price_gram_24k not available, calculate from price per troy ounce
                # 1 troy ounce = 31.1035 grams
                price_per_oz = float(data['price'])
                gold_rate = price_per_oz / 31.1035
                logger.info(f"Calculated gold rate from price per oz: {price_per_oz} / 31.1035 = {gold_rate}")
                return gold_rate
            else:
                logger.error(f"Unexpected gold API response format - missing both 'price_gram_24k' and 'price' fields")
                logger.error(f"Response keys: {list(data.keys())}")
                logger.error(f"Full response: {json.dumps(data, indent=2)}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error fetching gold price: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing gold price response: {e}")
            return None

    def _fetch_silver_925_per_gram(self) -> Optional[float]:
        """
        Fetch Silver 925 (sterling silver) price per gram.

        Returns:
            Price per gram in specified currency, or None if fetch fails
        """
        try:
            # GoldAPI.io endpoint for current silver price
            url = f"{self.base_url}/XAG/{self.currency}"
            headers = {
                'x-access-token': self.api_key,
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"GoldAPI response for XAG: {json.dumps(data, indent=2)}")

            # GoldAPI returns price per troy ounce for silver
            # Silver 925 is 92.5% pure silver (sterling silver)
            # We need to calculate the per-gram price and adjust for purity

            if 'price_gram_24k' in data:
                # This field might exist for silver as well (representing pure silver per gram)
                pure_silver_per_gram = float(data['price_gram_24k'])
                logger.info(f"Extracted pure silver rate from price_gram_24k: {pure_silver_per_gram}")
            elif 'price' in data:
                # Calculate from price per troy ounce
                # 1 troy ounce = 31.1035 grams
                price_per_oz = float(data['price'])
                pure_silver_per_gram = price_per_oz / 31.1035
                logger.info(f"Calculated pure silver rate from price per oz: {price_per_oz} / 31.1035 = {pure_silver_per_gram}")
            else:
                logger.error(f"Unexpected silver API response format - missing both 'price_gram_24k' and 'price' fields")
                logger.error(f"Response keys: {list(data.keys())}")
                logger.error(f"Full response: {json.dumps(data, indent=2)}")
                return None

            # For 925 silver (sterling silver), multiply by 0.925 purity factor
            silver_925_per_gram = pure_silver_per_gram * 0.925
            logger.info(f"925 Silver rate: {pure_silver_per_gram} × 0.925 = {silver_925_per_gram}")

            return silver_925_per_gram

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error fetching silver price: {e}")
            return None
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error parsing silver price response: {e}")
            return None

    def test_connection(self) -> bool:
        """
        Test API connection and credentials.

        Returns:
            True if connection successful, False otherwise
        """
        logger.info("Testing GoldAPI connection")

        try:
            url = f"{self.base_url}/XAU/{self.currency}"
            headers = {
                'x-access-token': self.api_key,
                'Content-Type': 'application/json'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()

            if 'price' in data or 'price_gram_24k' in data:
                logger.info("✓ GoldAPI connection successful")
                return True
            else:
                logger.error("✗ GoldAPI connection failed: unexpected response format")
                return False

        except Exception as e:
            logger.error(f"✗ GoldAPI connection failed: {e}")
            return False
