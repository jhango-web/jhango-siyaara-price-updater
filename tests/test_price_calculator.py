"""
Tests for Price Calculator

Run with: python -m pytest tests/test_price_calculator.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from price_calculator import PriceCalculator


def test_parse_gold_14k():
    """Test parsing 14K gold option."""
    result = PriceCalculator.parse_metal_from_option("14K Yellow Gold")
    assert result['type'] == 'gold'
    assert result['purity'] == '14kt'
    assert result['purity_factor'] == 0.585


def test_parse_gold_18k():
    """Test parsing 18K gold option."""
    result = PriceCalculator.parse_metal_from_option("18K Rose Gold")
    assert result['type'] == 'gold'
    assert result['purity'] == '18kt'
    assert result['purity_factor'] == 0.750


def test_parse_gold_22k():
    """Test parsing 22K gold option."""
    result = PriceCalculator.parse_metal_from_option("22K Gold")
    assert result['type'] == 'gold'
    assert result['purity'] == '22kt'
    assert result['purity_factor'] == 0.916


def test_parse_silver():
    """Test parsing silver option."""
    result = PriceCalculator.parse_metal_from_option("SILVER925")
    assert result['type'] == 'silver'
    assert result['purity'] == '925'
    assert result['purity_factor'] == 0.925


def test_parse_invalid():
    """Test parsing invalid option."""
    result = PriceCalculator.parse_metal_from_option("Invalid Metal")
    assert result['type'] is None


def test_calculate_price_gold_14k_no_stones():
    """Test price calculation for 14K gold without stones."""
    calc = PriceCalculator(making_charges=500, markup_percentage=10)

    result = calc.calculate_price(
        metal_weight=5.0,  # 5 grams
        stone_types=[],
        stone_carats=[],
        stone_prices_per_carat=[],
        option1_value="14K Yellow Gold",
        gold_rate=7000,  # ₹7000 per gram
        silver_rate=100   # Not used for gold
    )

    assert result is not None

    # Metal cost: 5g × 7000 × 0.585 = 20,475
    assert result['metal_cost'] == 20475

    # Stone cost: 0 (no stones)
    assert result['stone_cost'] == 0

    # Making charges: 500
    assert result['making_charges'] == 500

    # Laser: 0 (always 0)
    assert result['laser_cost'] == 0

    # Packaging: 0 (always 0)
    assert result['packaging_cost'] == 0

    # Subtotal: 20475 + 0 + 500 + 0 + 0 = 20,975
    # Markup: 20975 × 0.10 = 2,097.5 → 2097 (rounded down)
    assert result['markup_cost'] == 2097

    # Base price: 20975 + 2097 = 23,072
    # GST: 23072 × 0.03 = 692.16 → 692 (rounded down)
    assert result['gst_cost'] == 692

    # Total: round(23072 + 692.16) = 23765 (final price uses exact base + gst before rounding)
    assert result['total_price'] == 23765


def test_calculate_price_silver_with_stones():
    """Test price calculation for silver with stones."""
    calc = PriceCalculator(making_charges=300, markup_percentage=15)

    result = calc.calculate_price(
        metal_weight=10.0,  # 10 grams
        stone_types=["Diamond", "Ruby"],
        stone_carats=[0.5, 0.3],
        stone_prices_per_carat=[10000, 5000],
        option1_value="SILVER925",
        gold_rate=7000,  # Not used for silver
        silver_rate=100   # ₹100 per gram
    )

    assert result is not None

    # Metal cost: 10g × 100 × 0.925 = 925
    assert result['metal_cost'] == 925

    # Stone cost: (0.5 × 10000) + (0.3 × 5000) = 5000 + 1500 = 6500
    assert result['stone_cost'] == 6500

    # Making charges: 300
    assert result['making_charges'] == 300

    # Subtotal: 925 + 6500 + 300 = 7,725
    # Markup: 7725 × 0.15 = 1,158.75 → 1159 (rounded down)
    assert result['markup_cost'] == 1159

    # Base price: 7725 + 1159 = 8,884
    # GST: 8884 × 0.03 = 266.52 → 267 (rounded down)
    assert result['gst_cost'] == 267

    # Total: round(8884 + 266.52) = 9150
    assert result['total_price'] == 9150


def test_calculate_price_18k_gold():
    """Test price calculation for 18K gold."""
    calc = PriceCalculator(making_charges=800, markup_percentage=12)

    result = calc.calculate_price(
        metal_weight=3.5,  # 3.5 grams
        stone_types=["Diamond"],
        stone_carats=[0.25],
        stone_prices_per_carat=[15000],
        option1_value="18K White Gold",
        gold_rate=7200,
        silver_rate=100
    )

    assert result is not None

    # Metal cost: 3.5g × 7200 × 0.750 = 18,900
    assert result['metal_cost'] == 18900

    # Stone cost: 0.25 × 15000 = 3,750
    assert result['stone_cost'] == 3750

    # Making charges: 800
    assert result['making_charges'] == 800

    # Verify final price is positive and reasonable
    assert result['total_price'] > 0
    assert result['total_price'] > result['metal_cost']


def test_zero_metal_weight():
    """Test that zero metal weight doesn't cause errors."""
    calc = PriceCalculator(making_charges=500, markup_percentage=10)

    result = calc.calculate_price(
        metal_weight=0.0,
        stone_types=[],
        stone_carats=[],
        stone_prices_per_carat=[],
        option1_value="14K Yellow Gold",
        gold_rate=7000,
        silver_rate=100
    )

    assert result is not None
    assert result['metal_cost'] == 0


if __name__ == '__main__':
    print("Running price calculator tests...")
    print("\nTest 1: Parse 14K Gold")
    test_parse_gold_14k()
    print("PASSED")

    print("\nTest 2: Parse 18K Gold")
    test_parse_gold_18k()
    print("PASSED")

    print("\nTest 3: Parse 22K Gold")
    test_parse_gold_22k()
    print("PASSED")

    print("\nTest 4: Parse Silver")
    test_parse_silver()
    print("PASSED")

    print("\nTest 5: Parse Invalid")
    test_parse_invalid()
    print("PASSED")

    print("\nTest 6: Calculate Price - 14K Gold (No Stones)")
    test_calculate_price_gold_14k_no_stones()
    print("PASSED")

    print("\nTest 7: Calculate Price - Silver (With Stones)")
    test_calculate_price_silver_with_stones()
    print("PASSED")

    print("\nTest 8: Calculate Price - 18K Gold")
    test_calculate_price_18k_gold()
    print("PASSED")

    print("\nTest 9: Zero Metal Weight")
    test_zero_metal_weight()
    print("PASSED")

    print("\n" + "="*50)
    print("All tests passed!")
    print("="*50)
