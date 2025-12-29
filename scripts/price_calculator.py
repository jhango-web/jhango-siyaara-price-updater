"""
Price Calculator Module

Replicates the exact price calculation logic from shopify_product_splitter.py
Used for updating product prices based on gold/silver rates stored in metafields.
"""

import re
from typing import Dict, List, Any, Optional


class PriceCalculator:
    """Calculate product prices based on metafields and theme settings."""

    def __init__(self, making_charges_percentage: float, markup_percentage: float):
        """
        Initialize with theme settings.

        Args:
            making_charges_percentage: Making charges percentage from theme settings (applied to gold cost)
            markup_percentage: Markup percentage from theme settings

        Note: laser_cost and packaging_cost are always set to 0 as per requirements
        """
        self.making_charges_percentage = float(making_charges_percentage)
        self.markup_percentage = float(markup_percentage)
        self.laser_cost = 0.0  # Always 0 as per requirements
        self.packaging_cost = 0.0  # Always 0 as per requirements
        self.gst_percentage = 3.0  # Standard GST percentage

    @staticmethod
    def parse_metal_from_option(option_value: str) -> Dict[str, Any]:
        """
        Parse metal type and purity from option value.
        Examples: "10K Yellow Gold", "14K Rose Gold", "SILVER925"
        Returns: {'type': 'gold'|'silver', 'purity': '14kt', 'purity_factor': 0.585, 'display_name': '...'}
        """
        if not option_value:
            return {'type': None, 'purity': None, 'purity_factor': None, 'display_name': None}

        option_upper = option_value.upper().strip()

        # Check for Silver
        if 'SILVER' in option_upper:
            return {
                'type': 'silver',
                'purity': '925',
                'purity_factor': 0.925,
                'display_name': 'Silver 925'
            }

        # Check for Gold (10K, 14K, 18K, 22K, 24K)
        gold_match = re.search(r'(\d+)K\s*(Yellow|White|Rose)?\s*Gold', option_value, re.IGNORECASE)
        if gold_match:
            karat = gold_match.group(1)
            color = gold_match.group(2) or 'Yellow'

            purity_map = {
                '24': ('24kt', 1.000),
                '22': ('22kt', 0.916),
                '18': ('18kt', 0.750),
                '14': ('14kt', 0.585),
                '10': ('10kt', 0.417),
                '9': ('9kt', 0.375)
            }

            purity, factor = purity_map.get(karat, ('14kt', 0.585))

            return {
                'type': 'gold',
                'purity': purity,
                'purity_factor': factor,
                'display_name': f"{color} Gold {purity}"
            }

        return {'type': None, 'purity': None, 'purity_factor': None, 'display_name': None}

    def calculate_price(self,
                       metal_weight: float,
                       stone_types: List[str],
                       stone_carats: List[float],
                       stone_prices_per_carat: List[float],
                       option1_value: str,
                       gold_rate: float,
                       silver_rate: float) -> Optional[Dict[str, Any]]:
        """
        Calculate price based on metafields and rates.

        Args:
            metal_weight: Weight of metal in grams
            stone_types: List of stone type names
            stone_carats: List of stone weights in carats
            stone_prices_per_carat: List of stone prices per carat
            option1_value: Metal type option (e.g., "14K Yellow Gold")
            gold_rate: Gold rate per gram from metafield (in rupees)
            silver_rate: Silver rate per gram from metafield (in rupees)

        Returns: {
            'metal_cost': float,
            'stone_cost': float,
            'making_charges': float,
            'laser_cost': float,
            'packaging_cost': float,
            'markup_cost': float,
            'gst_cost': float,
            'total_price': float (includes GST),
            'breakdown': {...}
        }
        """
        # Parse metal info from option1
        metal_info = self.parse_metal_from_option(option1_value)

        if not metal_info['type']:
            return None

        # Calculate metal cost using rates from metafields
        base_rate = gold_rate if metal_info['type'] == 'gold' else silver_rate
        effective_rate = base_rate * metal_info['purity_factor']
        metal_cost = metal_weight * effective_rate

        # Calculate making charges as percentage of gold cost (only for gold)
        if metal_info['type'] == 'gold':
            gold_cost = metal_weight * metal_info['purity_factor'] * gold_rate
            making_charges = gold_cost * (self.making_charges_percentage / 100)
        else:
            # For silver, making charges is 0
            making_charges = 0

        # Calculate stone costs
        # Use stone_carats as the main driver since that's what we need for calculation
        # Even if stone_types is empty, calculate based on carats and prices
        total_stone_cost = 0
        stone_details = []

        # Determine how many stones to process based on carats (primary) and prices
        num_stones = max(len(stone_carats), len(stone_prices_per_carat))

        for i in range(num_stones):
            if i < len(stone_carats) and i < len(stone_prices_per_carat):
                carat = stone_carats[i]
                price = stone_prices_per_carat[i]

                # Only calculate if both carat and price are valid
                if carat and price:
                    cost = carat * price
                    total_stone_cost += cost

                    # Get stone type if available, otherwise use generic name
                    stone_type = stone_types[i] if i < len(stone_types) else f'stone_{i+1}'

                    stone_details.append({
                        'type': stone_type,
                        'carat': carat,
                        'price_per_carat': price,
                        'cost': cost
                    })

        # Use theme settings and hardcoded values
        laser_cost = self.laser_cost  # Always 0
        packaging_cost = self.packaging_cost  # Always 0
        markup_percentage = self.markup_percentage
        gst_percentage = self.gst_percentage

        # Calculate subtotal
        subtotal = metal_cost + total_stone_cost + making_charges + laser_cost + packaging_cost

        # Calculate markup
        markup_cost = subtotal * (markup_percentage / 100)

        # Calculate base price (after markup, before GST)
        base_price = subtotal + markup_cost

        # Calculate GST
        gst_cost = base_price * (gst_percentage / 100)

        # Calculate final price (including GST)
        final_price = round(base_price + gst_cost)

        # Round to nearest integer like the Liquid snippet (Math.round)
        return {
            'metal_cost': round(metal_cost),
            'stone_cost': round(total_stone_cost),
            'making_charges': round(making_charges),
            'laser_cost': round(laser_cost),
            'packaging_cost': round(packaging_cost),
            'markup_cost': round(markup_cost),
            'gst_cost': round(gst_cost),
            'total_price': final_price,
            'breakdown': {
                'metal': {
                    'type': metal_info['type'],
                    'display_name': metal_info['display_name'],
                    'weight': metal_weight,
                    'purity_factor': metal_info['purity_factor'],
                    'base_rate': base_rate,
                    'effective_rate': round(effective_rate),
                    'cost': round(metal_cost)
                },
                'stones': stone_details,
                'charges': {
                    'making': round(making_charges),
                    'laser': round(laser_cost),
                    'packaging': round(packaging_cost),
                    'markup_percentage': markup_percentage,
                    'markup_cost': round(markup_cost),
                    'gst_percentage': gst_percentage,
                    'gst_cost': round(gst_cost)
                }
            }
        }
