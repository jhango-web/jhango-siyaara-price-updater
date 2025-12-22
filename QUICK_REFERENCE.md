# Quick Reference Guide

## 🚀 Quick Commands

### Run Manual Update (Local)

```bash
cd scripts
python price_updater.py \
  --shop-url "mystore.myshopify.com" \
  --access-token "shpat_xxxxx" \
  --theme-id "143345254460" \
  --gold-rate 7200 \
  --silver-rate 95
```

### Dry Run (Test Without Updating)

```bash
python price_updater.py \
  --shop-url "mystore.myshopify.com" \
  --access-token "shpat_xxxxx" \
  --theme-id "143345254460" \
  --gold-rate 7200 \
  --silver-rate 95 \
  --dry-run
```

### Run Tests

```bash
cd tests
python test_price_calculator.py
```

## 📋 GitHub Secrets Required

| Secret | Example | Description |
|--------|---------|-------------|
| `GOLDAPI_KEY` | `goldapi-abc123` | GoldAPI.io API key |
| `SHOPIFY_SHOP_URL` | `mystore.myshopify.com` | Shop URL (no https://) |
| `SHOPIFY_ACCESS_TOKEN` | `shpat_abc123` | Admin API token |
| `SHOPIFY_THEME_ID` | `143345254460` | Theme ID (numbers only) |

## ⏰ Automatic Schedule

- **Frequency**: Daily
- **Time**: 9:00 AM IST (3:30 AM UTC)
- **Workflow**: `.github/workflows/auto-price-update.yml`

To change schedule, edit the `cron` expression:
```yaml
schedule:
  - cron: '30 3 * * *'  # minute hour * * *
```

[Cron expression generator](https://crontab.guru/)

## 💰 Price Calculation Formula

```
Metal Cost = weight × rate × purity_factor
Stone Cost = Σ(carat × price_per_carat)
Subtotal = Metal Cost + Stone Cost + Making + Laser + Packaging
           (Laser and Packaging are always ₹0)
Markup = Subtotal × (Markup % / 100)
Base Price = Subtotal + Markup
GST = Base Price × (3 / 100)
Final Price = Base Price + GST (rounded)
```

## 🎯 Metal Purity Factors

| Metal | Purity Factor |
|-------|---------------|
| 24K Gold | 1.000 |
| 22K Gold | 0.916 |
| 18K Gold | 0.750 |
| 14K Gold | 0.585 |
| 10K Gold | 0.417 |
| Silver 925 | 0.925 |

## 📊 Understanding Statistics

```json
{
  "products_processed": 150,      // Total products updated
  "variants_updated": 823,        // Variants with price changes
  "variants_skipped": 45,         // Variants without metal weight
  "variants_failed": 2,           // Update failures
  "metafields_updated": 300,      // Metafields updated (2 per product)
  "metafields_failed": 0,         // Metafield update failures
  "errors": []                    // List of error messages
}
```

## 🔍 Common Error Messages

### "Missing required environment variables"
- **Cause**: GitHub secrets not configured
- **Fix**: Add all required secrets in repository settings

### "Invalid rates: gold=0, silver=0"
- **Cause**: GoldAPI returned zero/invalid rates
- **Fix**: Check GoldAPI account, API key, and service status

### "No products found with required metafields"
- **Cause**: Products don't have jhango.gold_rate/silver_rate metafields
- **Fix**: Ensure products were created with product splitter script

### "Could not parse metal info"
- **Cause**: Invalid option1 value (e.g., not "14K Gold" format)
- **Fix**: Check product option1 values follow expected format

## 🎮 Manual Workflow Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `gold_rate` | Number | Yes | Gold rate per gram (₹) |
| `silver_rate` | Number | Yes | Silver rate per gram (₹) |
| `making_charges` | Number | No | Override theme setting |
| `markup_percentage` | Number | No | Override theme setting |
| `dry_run` | Boolean | No | Test without updating |
| `skip_metafields` | Boolean | No | Only update prices |

## 📁 Important Files

| File | Purpose |
|------|---------|
| `scripts/price_calculator.py` | Price calculation logic |
| `scripts/shopify_client.py` | Shopify API interactions |
| `scripts/goldapi_client.py` | GoldAPI.io integration |
| `scripts/price_updater.py` | Manual update script |
| `scripts/auto_price_updater.py` | Automatic update script |
| `.github/workflows/auto-price-update.yml` | Automatic workflow |
| `.github/workflows/manual-price-update.yml` | Manual workflow |

## 🔐 Security Best Practices

- ✅ Always use GitHub Secrets for sensitive data
- ✅ Never commit `.env` files
- ✅ Use private repository for production
- ✅ Limit API token permissions to minimum required
- ✅ Regularly rotate API keys and tokens
- ✅ Monitor workflow runs for suspicious activity

## 📈 Monitoring Checklist

Daily:
- [ ] Check Actions tab for workflow status
- [ ] Review any failed runs
- [ ] Verify prices updated correctly in Shopify

Weekly:
- [ ] Download and review statistics artifacts
- [ ] Check for patterns in skipped/failed variants
- [ ] Verify gold/silver rates are reasonable

Monthly:
- [ ] Review API usage (GoldAPI quota)
- [ ] Check for any deprecated API endpoints
- [ ] Update dependencies if needed

## 🆘 Emergency Procedures

### Pause Automatic Updates

1. Go to `.github/workflows/auto-price-update.yml`
2. Add `#` before the `schedule:` section:
   ```yaml
   # schedule:
   #   - cron: '30 3 * * *'
   ```
3. Commit and push

### Rollback Prices

The system doesn't store old prices. To rollback:
1. Run manual update with previous gold/silver rates
2. Or restore from Shopify backup if available

### Disable Workflows Completely

1. Go to **Actions** tab
2. Click **...** (three dots) on workflow
3. Click **Disable workflow**

## 📞 Support Contacts

- **Repository Issues**: GitHub Issues tab
- **Shopify API**: [Shopify Developer Docs](https://shopify.dev/docs/api/admin-rest)
- **GoldAPI**: [GoldAPI.io Support](https://www.goldapi.io/support)

## 🔗 Useful Links

- [Shopify Admin API](https://shopify.dev/docs/api/admin-rest)
- [GoldAPI.io Docs](https://www.goldapi.io/docs)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Python Requests Docs](https://requests.readthedocs.io/)

---

**Last Updated**: 2024-12-21
