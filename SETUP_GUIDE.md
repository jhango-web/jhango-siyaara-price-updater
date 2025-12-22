# Setup Guide - Step by Step

This guide walks you through setting up the automatic price updater from scratch.

## ⚠️ IMPORTANT: Public Repository Security

**This repository will be PUBLIC** to use free GitHub Actions.

🔒 **Before you begin:**
- Read [SECURITY.md](SECURITY.md) first
- Never commit secrets to the repository
- All credentials go in GitHub Secrets only
- Double-check every commit for sensitive data

## Prerequisites Checklist

- [ ] Shopify store with products created using the product splitter
- [ ] Shopify Admin API access token with permissions:
  - `read_products`
  - `write_products`
  - `read_themes`
  - `write_themes`
- [ ] GoldAPI.io account (free tier available)
- [ ] GitHub account

## Step 1: Get Shopify Admin API Token

### 1.1 Create Custom App

1. Log in to your Shopify admin panel
2. Go to **Settings** → **Apps and sales channels**
3. Click **Develop apps**
4. Click **Create an app**
5. Name it: `Price Updater` (or any name)
6. Click **Create app**

### 1.2 Configure API Scopes

1. Click **Configure Admin API scopes**
2. Enable the following scopes:
   - `read_products`
   - `write_products`
   - `read_themes`
   - `write_themes`
3. Click **Save**

### 1.3 Get Access Token

1. Click **API credentials** tab
2. Click **Install app**
3. Click **Reveal token once**
4. **IMPORTANT**: Copy the token immediately and save it securely
   - Format: `shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - You won't be able to see it again!

### 1.4 Get Shop URL

Your shop URL is: `[your-store-name].myshopify.com`

Example: If your store is at `https://mystore.myshopify.com`, use `mystore.myshopify.com`

### 1.5 Get Theme ID

#### Option A: Via Admin URL
1. Go to **Online Store** → **Themes**
2. Click **Customize** on your active theme
3. Look at the URL in your browser:
   - Format: `https://[store].myshopify.com/admin/themes/[THEME_ID]/editor`
   - The number after `themes/` is your theme ID
   - Example: `143345254460`

#### Option B: Via API
```bash
curl -X GET \
  "https://[your-store].myshopify.com/admin/api/2024-01/themes.json" \
  -H "X-Shopify-Access-Token: [your-token]"
```

Look for the theme with `"role": "main"` and copy its `id`.

## Step 2: Get GoldAPI.io Key

### 2.1 Sign Up

1. Go to [https://www.goldapi.io](https://www.goldapi.io)
2. Click **Sign Up** or **Get API Key**
3. Complete registration

### 2.2 Get API Key

1. Log in to your GoldAPI dashboard
2. Copy your API key
   - Format: `goldapi-xxxxxxxxxxxxxxxx`

### 2.3 Test API Key (Optional)

```bash
curl -X GET \
  "https://www.goldapi.io/api/XAU/INR" \
  -H "x-access-token: [your-goldapi-key]"
```

Should return JSON with gold prices.

## Step 3: Prepare GitHub Repository

### 3.1 Create Repository

1. Go to [https://github.com/new](https://github.com/new)
2. Repository name: `jhango-siyaara-price-updater` (or any name)
3. Choose **Private** (recommended) or **Public**
4. Click **Create repository**

### 3.2 Upload Code

#### Option A: Git Command Line

```bash
cd JHANGO-SIYAARA-GITHUB

# Initialize git (if not already)
git init

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Add all files
git add .

# Commit
git commit -m "Initial commit - Shopify price updater"

# Push
git branch -M main
git push -u origin main
```

#### Option B: GitHub Desktop

1. Open GitHub Desktop
2. File → Add Local Repository
3. Select the `JHANGO-SIYAARA-GITHUB` folder
4. Publish repository

#### Option C: Upload Files

1. Go to your repository on GitHub
2. Click **Add file** → **Upload files**
3. Drag and drop all files from `JHANGO-SIYAARA-GITHUB` folder
4. Commit changes

## Step 4: Configure GitHub Secrets

### 4.1 Navigate to Secrets

1. Go to your repository on GitHub
2. Click **Settings** tab
3. In left sidebar: **Secrets and variables** → **Actions**

### 4.2 Add Secrets

Click **New repository secret** for each:

#### Secret 1: GOLDAPI_KEY
- Name: `GOLDAPI_KEY`
- Value: Your GoldAPI.io API key (e.g., `goldapi-abc123...`)
- Click **Add secret**

#### Secret 2: SHOPIFY_SHOP_URL
- Name: `SHOPIFY_SHOP_URL`
- Value: Your shop URL (e.g., `mystore.myshopify.com`)
  - **Do NOT include** `https://`
  - **Do NOT include** trailing `/`
- Click **Add secret**

#### Secret 3: SHOPIFY_ACCESS_TOKEN
- Name: `SHOPIFY_ACCESS_TOKEN`
- Value: Your Shopify Admin API token (e.g., `shpat_abc123...`)
- Click **Add secret**

#### Secret 4: SHOPIFY_THEME_ID
- Name: `SHOPIFY_THEME_ID`
- Value: Your theme ID (e.g., `143345254460`)
  - Just the number, no quotes
- Click **Add secret**

### 4.3 Verify Secrets

You should now see 4 secrets listed:
- ✓ GOLDAPI_KEY
- ✓ SHOPIFY_ACCESS_TOKEN
- ✓ SHOPIFY_SHOP_URL
- ✓ SHOPIFY_THEME_ID

## Step 5: Enable GitHub Actions

### 5.1 Enable Workflows

1. Go to **Actions** tab in your repository
2. If prompted, click **I understand my workflows, go ahead and enable them**

### 5.2 Verify Workflows

You should see two workflows:
- **Automatic Price Update** (scheduled daily)
- **Manual Price Update** (manual trigger)

## Step 6: Test Manual Update

### 6.1 Run Test with Dry Run

1. Go to **Actions** tab
2. Click **Manual Price Update** workflow
3. Click **Run workflow** button (top right)
4. Fill in the form:
   - **gold_rate**: `7200` (example rate)
   - **silver_rate**: `95` (example rate)
   - **making_charges**: Leave empty (uses theme settings)
   - **markup_percentage**: Leave empty (uses theme settings)
   - **dry_run**: ✓ **Check this box** (important for testing!)
   - **skip_metafields**: Leave unchecked
5. Click **Run workflow**

### 6.2 Monitor Test Run

1. Wait a few seconds, then refresh the page
2. Click on the workflow run (top of the list)
3. Click on the job name **Manual Update Product Prices**
4. Watch the logs in real-time

### 6.3 Check Results

1. Workflow should complete successfully (green checkmark)
2. Check the logs for:
   - "Dry Run: true"
   - Number of products processed
   - Price calculations shown
   - "Update completed successfully"
3. Download artifacts:
   - Click **Summary** (top)
   - Under **Artifacts**, download the logs and stats files
   - Review `price_update_stats_*.json` for details

### 6.4 Verify No Changes

Since dry run was enabled:
- ✓ No prices were actually changed in Shopify
- ✓ No metafields were updated
- ✓ Only calculations were performed and logged

## Step 7: Run Actual Update (Optional)

⚠️ **This will update real prices!**

### 7.1 Run Without Dry Run

1. Go to **Actions** → **Manual Price Update**
2. Click **Run workflow**
3. Fill in with **current actual rates**
4. **Uncheck** dry_run
5. Click **Run workflow**

### 7.2 Verify Updates

1. Check workflow completes successfully
2. Go to Shopify admin → Products
3. Verify some product prices have updated
4. Check product metafields updated with new rates

## Step 8: Verify Automatic Schedule

### 8.1 Check Schedule

The automatic workflow is scheduled to run **daily at 9:00 AM IST (3:30 AM UTC)**.

### 8.2 Test Automatic Workflow

You can manually trigger it to test:

1. Go to **Actions** → **Automatic Price Update**
2. Click **Run workflow** → **Run workflow**
3. Monitor the run
4. Check it completes successfully

### 8.3 Wait for Scheduled Run

The automatic workflow will run on schedule. Check next day at 9 AM IST.

## Step 9: Monitoring & Maintenance

### 9.1 Daily Monitoring

- Check **Actions** tab regularly
- Look for failed runs (red X)
- Download artifacts for detailed reports

### 9.2 Email Notifications

GitHub will email you if workflows fail (if notifications are enabled in your GitHub settings).

### 9.3 Review Statistics

Download and review the JSON statistics files:
- Number of products processed
- Number of variants updated
- Any errors encountered

## Troubleshooting

### Workflow fails with "Missing required environment variables"

**Fix**: Go back to Step 4 and verify all secrets are correctly set.

### Workflow fails with "Invalid credentials"

**Fix**:
- Check SHOPIFY_ACCESS_TOKEN is correct
- Verify the custom app is still installed in Shopify
- Check API scopes are correct

### "Failed to fetch theme settings"

**Fix**:
- Verify SHOPIFY_THEME_ID is correct (numbers only)
- Check theme exists and is active
- Verify API token has `read_themes` scope

### "No products found with required metafields"

**Fix**:
- Ensure products were created with the product splitter script
- Verify metafields exist: Go to Shopify admin → Products → Select a product → Check metafields
- Look for `jhango.gold_rate` and `jhango.silver_rate`

### GoldAPI errors

**Fix**:
- Check API key is correct
- Verify account is active
- Check if you've exceeded API quota (free tier has limits)
- Test API key using curl command from Step 2.3

### Workflow runs but no prices update

**Fix**:
- Check if dry_run was enabled (it should be disabled for actual updates)
- Review the logs for errors or "skipped" messages
- Verify products have metal_weight metafields on variants
- Check option1 values are valid (e.g., "14K Yellow Gold")

## Next Steps

Once everything is working:

1. ✓ Monitor the first few automatic runs
2. ✓ Adjust schedule if needed (edit `.github/workflows/auto-price-update.yml`)
3. ✓ Set up notifications/alerts for failures
4. ✓ Document any custom configurations
5. ✓ Share access with team members if needed

## Support

If you encounter issues not covered here:

1. Check the main [README.md](README.md) file
2. Review workflow logs carefully
3. Test individual components (API connections, theme settings, etc.)
4. Contact the development team

---

**Setup Version**: 1.0.0
**Last Updated**: 2024-12-21
