# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2024-12-21

### Initial Release

#### Features
- ✅ Automatic daily price updates from GoldAPI.io
- ✅ Manual price updates with custom rates
- ✅ Exact price calculation matching product splitter logic
- ✅ Product metafield updates (jhango.gold_rate, jhango.silver_rate)
- ✅ Theme settings updates with new rates
- ✅ Comprehensive error handling and validation
- ✅ Dry-run mode for testing
- ✅ Detailed logging and statistics
- ✅ GitHub Actions workflows for automation

#### Price Calculation
- Metal cost based on weight, rate, and purity factor
- Stone cost calculation from variant metafields
- Making charges from theme settings
- Markup percentage from theme settings
- Laser cost fixed at ₹0
- Packaging cost fixed at ₹0
- GST fixed at 3%
- Rates sourced from product metafields (jhango.gold_rate, jhango.silver_rate)

#### Supported Metals
- 24K Gold (100% pure)
- 22K Gold (91.6% pure)
- 18K Gold (75% pure)
- 14K Gold (58.5% pure)
- 10K Gold (41.7% pure)
- Silver 925 (92.5% pure)

#### Safety Features
- Rate validation (must be > 0)
- Abort on invalid API responses
- Product filtering (only updates products with required metafields)
- Variant skipping (skips variants without metal weight)
- Price change detection (only updates if price actually changes)
- Secure secret management via GitHub Secrets

#### Documentation
- README.md - Main documentation
- SETUP_GUIDE.md - Step-by-step setup instructions
- QUICK_REFERENCE.md - Quick reference for common tasks
- Test suite for price calculator

#### Workflows
- `auto-price-update.yml` - Daily automatic updates at 9:00 AM IST
- `manual-price-update.yml` - Manual updates with form inputs

#### Scripts
- `price_calculator.py` - Core price calculation logic
- `shopify_client.py` - Shopify API integration
- `goldapi_client.py` - GoldAPI.io integration
- `price_updater.py` - Manual update script
- `auto_price_updater.py` - Automatic update script with API fetching

#### Testing
- `test_price_calculator.py` - Unit tests for price calculations
- Validates all metal types and purity factors
- Tests price calculation with and without stones
- Validates edge cases (zero weight, invalid metals)

---

## Future Enhancements (Planned)

### Version 1.1.0
- [ ] Support for additional metal types
- [ ] Email notifications on update completion/failure
- [ ] Dashboard for viewing update history
- [ ] Batch processing optimization for large stores
- [ ] Price change limits/thresholds

### Version 1.2.0
- [ ] Support for multiple currency conversions
- [ ] Historical rate tracking and analytics
- [ ] Automatic rollback on detection of errors
- [ ] Slack/Discord webhook notifications
- [ ] Custom scheduling per product collection

### Version 2.0.0
- [ ] Web UI for monitoring and management
- [ ] GraphQL API support for better performance
- [ ] Multi-store support
- [ ] Advanced reporting and analytics
- [ ] A/B testing for pricing strategies

---

## Notes

- All prices are in Indian Rupees (INR) by default
- Gold rates are for 24K gold per gram
- Silver rates are for 925 sterling silver per gram
- Purity adjustments are applied automatically based on option1 value
- Theme settings are fetched automatically unless overridden
- All updates are logged with detailed statistics

---

**Format**: This changelog follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) format
**Versioning**: This project uses [Semantic Versioning](https://semver.org/)
