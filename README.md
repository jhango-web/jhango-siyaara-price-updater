# Jhango Siyaara - Shopify Price Updater

Automatic and manual price update system for Shopify jewelry products based on live gold and silver rates.

## ⚠️ IMPORTANT SECURITY NOTICE

**This is a PUBLIC repository** (to use free GitHub Actions).

🔒 **NEVER commit secrets, API keys, or tokens to this repository!**

- ✅ All credentials MUST be stored in GitHub Secrets
- ✅ Read [SECURITY.md](SECURITY.md) before making any commits
- ✅ Check your commits don't contain sensitive data
- ❌ Never commit `.env` files or configuration with real credentials

## 🎯 Features

- **Automatic Daily Updates**: Fetches live gold (24K) and silver (925) prices from GoldAPI.io and updates all product prices
- **Manual Updates**: Trigger price updates with custom gold/silver rates via GitHub Actions interface
- **Exact Price Calculation**: Replicates the exact pricing logic from your product listing system
- **Metafield Management**: Updates product metafields (`jhango.gold_rate` and `jhango.silver_rate`) and theme settings
- **Email Reports**: Detailed HTML email reports after every run with complete product-level changes (supports unlimited products!)
- **Safe & Validated**: Comprehensive error handling, validation, and dry-run mode for testing
- **Detailed Logging**: Complete audit trail with statistics and logs saved as artifacts

## 📋 Prerequisites

- Shopify store with Admin API access
- GoldAPI.io account (for automatic updates)
- GitHub repository to host this code
- Python 3.11+ (for local testing)

## 🚀 Setup Instructions

### 1. Fork/Clone This Repository

```bash
git clone https://github.com/YOUR_USERNAME/jhango-siyaara-github.git
cd jhango-siyaara-github
```

### 2. Configure GitHub Secrets

⚠️ **CRITICAL**: Since this is a public repository, ALL credentials MUST be stored as GitHub Secrets.

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add the following secrets (click "New repository secret" for each):

| Secret Name | Description | Example Format |
|-------------|-------------|----------------|
| `GOLDAPI_KEY` | Your GoldAPI.io API key | `goldapi-xxxxxx` |
| `SHOPIFY_SHOP_URL` | Your Shopify store URL | `yourstore.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Shopify Admin API access token | `shpat_xxxxxx` |
| `SHOPIFY_THEME_ID` | Your theme ID for settings | `143345254460` |
| `SENDER_EMAIL` | Email address to send reports from | `your-email@gmail.com` |
| `SENDER_PASSWORD` | App password for sender email | `xxxx xxxx xxxx xxxx` |
| `RECIPIENT_EMAIL` | Email address to receive reports | `recipient@example.com` |

**Note**: The "Example Format" column shows the format, not actual values. Use your real credentials when adding secrets.

**📧 Email Setup**: See [EMAIL_SETUP.md](EMAIL_SETUP.md) for detailed instructions on configuring email reporting.

### 3. Configure GitHub Variables (Optional)

Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** tab → **New repository variable**

| Variable Name | Description | Default |
|---------------|-------------|---------|
| `CURRENCY` | Currency code for price fetching | `INR` |

### 4. Enable GitHub Actions

Go to **Actions** tab → Enable workflows if prompted

## 🔄 How It Works

### Price Calculation Logic

The system calculates prices using the exact same formula as your product listing system:

1. **Metal Cost** = `weight × rate × purity_factor`
   - Gold purities: 24K (1.0), 22K (0.916), 18K (0.750), 14K (0.585), 10K (0.417)
   - Silver: 925 (0.925)

2. **Stone Cost** = Sum of `(carat × price_per_carat)` for each stone

3. **Subtotal** = `Metal Cost + Stone Cost + Making Charges + Laser Cost + Packaging Cost`
   - **Note**: Laser Cost and Packaging Cost are always set to ₹0 (as per requirements)

4. **Markup** = `Subtotal × (Markup % / 100)`

5. **Base Price** = `Subtotal + Markup`

6. **GST** = `Base Price × (GST % / 100)` (default 3%)

7. **Final Price** = `Base Price + GST` (rounded to nearest rupee)

### Rate Sources

- **Gold Rate**: From product metafield `jhango.gold_rate` (₹ per gram)
- **Silver Rate**: From product metafield `jhango.silver_rate` (₹ per gram)
- **Making Charges**: From theme settings
- **Markup %**: From theme settings
- **Laser Cost**: Always ₹0
- **Packaging Cost**: Always ₹0
- **GST %**: Fixed at 3%

## 📅 Automatic Updates

### Schedule

Automatic updates run **daily at 9:00 AM IST (3:30 AM UTC)**.

### Process Flow

1. **Fetch Rates**: Get live 24K gold and 925 silver prices from GoldAPI.io
2. **Validate**: Ensure rates are positive and non-zero (abort if invalid)
3. **Update Theme**: Update theme settings with new gold/silver rates
4. **Find Products**: Identify all products with `jhango.gold_rate` and `jhango.silver_rate` metafields
5. **Calculate Prices**: For each variant, calculate new price using:
   - Metal weight from variant metafield `custom.metal_weight`
   - Stone data from variant metafields
   - Gold/silver rates from product metafields
   - Making charges and markup % from theme settings
6. **Update Prices**: Update variant prices and product metafields
7. **Generate Report**: Save statistics and logs as artifacts

### Monitoring

- Check **Actions** tab for workflow runs
- Download artifacts for detailed logs and statistics
- Failed runs will show errors in the workflow log

### Manual Trigger

You can manually trigger the automatic workflow:

1. Go to **Actions** → **Automatic Price Update**
2. Click **Run workflow** → **Run workflow**

## 🎮 Manual Updates

### Via GitHub Actions

1. Go to **Actions** → **Manual Price Update**
2. Click **Run workflow**
3. Fill in the form:
   - **Gold rate per gram**: e.g., `7200`
   - **Silver rate per gram**: e.g., `95`
   - **Making charges**: (optional) Override theme setting
   - **Markup percentage**: (optional) Override theme setting
   - **Dry run**: Check to simulate without making changes
   - **Skip metafields**: Check to only update prices (not metafields)
4. Click **Run workflow**

### Via Command Line (Local)

```bash
cd scripts

# Install dependencies
pip install -r requirements.txt

# Run with custom rates
python price_updater.py \
  --shop-url "mystore.myshopify.com" \
  --access-token "shpat_xxxxx" \
  --theme-id "143345254460" \
  --gold-rate 7200 \
  --silver-rate 95 \
  --making-charges 500 \
  --markup-percentage 10

# Dry run (simulate without updating)
python price_updater.py \
  --shop-url "mystore.myshopify.com" \
  --access-token "shpat_xxxxx" \
  --theme-id "143345254460" \
  --gold-rate 7200 \
  --silver-rate 95 \
  --dry-run
```

## 🧪 Testing

### Test Price Calculator

```bash
cd tests
python test_price_calculator.py
```

This runs comprehensive tests on the price calculation logic to ensure accuracy.

### Test Connections

```bash
cd scripts

# Test GoldAPI connection
python -c "
from goldapi_client import GoldAPIClient
client = GoldAPIClient('YOUR_API_KEY', 'INR')
print('Testing connection...')
if client.test_connection():
    print('✓ Connection successful')
    prices = client.get_metal_prices()
    if prices:
        print(f'Gold: ₹{prices[\"gold_rate\"]:.2f}/g')
        print(f'Silver: ₹{prices[\"silver_rate\"]:.2f}/g')
else:
    print('✗ Connection failed')
"
```

## 📊 Understanding the Logs

### Log Levels

- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (e.g., skipped variants)
- **ERROR**: Critical failures

### Sample Log Output

```
2024-01-15 09:00:00 - INFO - Fetching live metal prices from GoldAPI
2024-01-15 09:00:02 - INFO - ✓ Valid metal prices fetched
2024-01-15 09:00:02 - INFO -   24K Gold: INR 7250.50/g
2024-01-15 09:00:02 - INFO -   Silver 925: INR 97.25/g
2024-01-15 09:00:03 - INFO - Processing product: gold-ring-001 (ID: 12345)
2024-01-15 09:00:03 - INFO -   Updating metafields with new rates
2024-01-15 09:00:04 - INFO -   ✓ Updated metafields
2024-01-15 09:00:04 - INFO -   Processing 5 variants
2024-01-15 09:00:05 - INFO -     Variant 67890 (14K Yellow Gold)
2024-01-15 09:00:05 - INFO -       Metal: ₹21250 (5g × ₹7250.50/g × 0.585)
2024-01-15 09:00:05 - INFO -       Stones: ₹5000
2024-01-15 09:00:05 - INFO -       Making: ₹500
2024-01-15 09:00:05 - INFO -       Markup: ₹2675 (10%)
2024-01-15 09:00:05 - INFO -       GST: ₹883 (3%)
2024-01-15 09:00:05 - INFO -       Old Price: ₹29100 → New Price: ₹30308
2024-01-15 09:00:06 - INFO -       ✓ Price updated
```

### Statistics Summary

```json
{
  "products_processed": 150,
  "variants_updated": 823,
  "variants_skipped": 45,
  "variants_failed": 2,
  "metafields_updated": 300,
  "metafields_failed": 0,
  "errors": []
}
```

## 🔒 Security

- **All secrets are stored in GitHub Secrets** (encrypted at rest)
- **Secrets are never logged** or exposed in workflow output
- **API tokens are passed via environment variables** only
- **No credentials in code** or version control

## ⚠️ Important Notes

### Rate Validation

The system will **abort** the update if:
- Gold rate ≤ 0
- Silver rate ≤ 0
- API returns invalid/zero rates

This prevents incorrect pricing.

### Product Selection

Only products with **both** metafields are updated:
- `jhango.gold_rate`
- `jhango.silver_rate`

Products without these metafields are ignored.

### Variant Skipping

Variants are skipped if:
- Metal weight is 0 or missing
- Option1 value cannot be parsed (invalid metal type)

### Price Changes

Prices are only updated if the new price differs from the old price by at least ₹0.01.

## 🛠️ Troubleshooting

### "Missing required environment variables"

**Solution**: Ensure all GitHub secrets are configured correctly:
- `GOLDAPI_KEY`
- `SHOPIFY_SHOP_URL`
- `SHOPIFY_ACCESS_TOKEN`
- `SHOPIFY_THEME_ID`

### "Invalid rates received: gold=0, silver=0"

**Solution**:
- Check GoldAPI.io account status and API key
- Verify API quota hasn't been exceeded
- Check if GoldAPI.io service is operational

### "Failed to fetch theme settings"

**Solution**:
- Verify `SHOPIFY_THEME_ID` is correct
- Check Shopify API access token has required permissions
- Ensure theme exists and is accessible

### "No products found with required metafields"

**Solution**:
- Ensure products have been created with the product splitter script
- Verify metafields `jhango.gold_rate` and `jhango.silver_rate` exist
- Check metafield namespace is exactly `jhango`

### Workflow fails immediately

**Solution**:
- Check workflow syntax in `.github/workflows/` files
- Review workflow run logs for specific errors
- Ensure Python version is compatible (3.11+)

## 📝 File Structure

```
JHANGO-SIYAARA-GITHUB/
├── .github/
│   └── workflows/
│       ├── auto-price-update.yml       # Automatic daily updates
│       └── manual-price-update.yml     # Manual trigger workflow
├── scripts/
│   ├── price_calculator.py             # Price calculation logic
│   ├── shopify_client.py               # Shopify API client
│   ├── goldapi_client.py               # GoldAPI.io client
│   ├── price_updater.py                # Manual update script
│   ├── auto_price_updater.py           # Automatic update script
│   └── requirements.txt                # Python dependencies
├── tests/
│   └── test_price_calculator.py        # Unit tests
├── .gitignore                          # Git ignore rules
└── README.md                           # This file
```

## 🤝 Contributing

This is a private/internal tool. For issues or improvements, contact the development team.

## 📄 License

Proprietary - Internal use only

## 🆘 Support

For support or questions:
1. Check the **Troubleshooting** section above
2. Review workflow logs in GitHub Actions
3. Contact the development team

---

**Last Updated**: 2024-12-21
**Version**: 1.0.0
