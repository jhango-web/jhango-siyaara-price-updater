# Email Reporting Setup Guide

## 📧 Overview

The price updater sends detailed email reports after every run, including:
- ✅ Complete list of ALL products modified (no limits - 10,000+ products supported)
- ✅ Detailed variant-level changes with old/new prices
- ✅ Error tracking with specific products affected
- ✅ Summary statistics
- ✅ Metal rates used
- ✅ Beautifully formatted HTML email with tables

## 🔧 Required GitHub Secrets

You need to add **3 new secrets** for email reporting:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `SENDER_EMAIL` | Email address to send from | `your-email@gmail.com` |
| `SENDER_PASSWORD` | App password for sender email | `xxxx xxxx xxxx xxxx` |
| `RECIPIENT_EMAIL` | Email address to receive reports | `recipient@example.com` |

### Optional Variables

| Variable Name | Description | Default |
|---------------|-------------|---------|
| `SMTP_SERVER` | SMTP server address | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP server port | `587` |

## 📝 Step-by-Step Setup

### For Gmail (Recommended)

#### 1. Enable 2-Factor Authentication

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click **Security** → **2-Step Verification**
3. Follow the steps to enable 2FA

#### 2. Create App Password

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click **Security** → **2-Step Verification**
3. Scroll to bottom → Click **App passwords**
4. Select app: **Mail**
5. Select device: **Other (Custom name)**
6. Enter name: `Jhango Price Updater`
7. Click **Generate**
8. **Copy the 16-character password** (format: `xxxx xxxx xxxx xxxx`)

#### 3. Add GitHub Secrets

1. Go to your repository: https://github.com/jhango-web/jhango-siyaara-price-updater
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

**SENDER_EMAIL:**
```
your-email@gmail.com
```

**SENDER_PASSWORD:**
```
xxxx xxxx xxxx xxxx
```
(The 16-character app password from step 2.8)

**RECIPIENT_EMAIL:**
```
recipient@example.com
```
(Can be the same as SENDER_EMAIL or different)

### For Other Email Providers

#### Microsoft Outlook/Office 365

- **SMTP_SERVER**: `smtp-mail.outlook.com` or `smtp.office365.com`
- **SMTP_PORT**: `587`
- **App Password**: [Create app password](https://support.microsoft.com/account-billing)

#### Yahoo Mail

- **SMTP_SERVER**: `smtp.mail.yahoo.com`
- **SMTP_PORT**: `587`
- **App Password**: [Generate app password](https://login.yahoo.com/account/security)

#### Custom SMTP Server

If using a custom email server:

1. Add GitHub **Variable** (not secret) for `SMTP_SERVER`:
   - Go to **Settings** → **Secrets and variables** → **Actions** → **Variables** tab
   - Add `SMTP_SERVER` with your server address

2. Add GitHub **Variable** for `SMTP_PORT` if not 587:
   - Add `SMTP_PORT` with your port number

## 📬 Email Report Format

### Subject Line

- **Success**: `✅ Price Update Complete - 150 products, 823 variants updated - 2024-12-22T09:00:00`
- **Failure**: `❌ Price Update FAILED - 2024-12-22T09:00:00`

### Email Content (HTML)

The email includes:

1. **Header** - Status (success/failure) with timestamp
2. **Metal Rates** - Gold and silver rates used
3. **Summary Statistics**:
   - Products processed
   - Variants updated/skipped/failed
   - Metafields updated
   - Total errors

4. **Errors Section** (if any):
   - List of all errors encountered
   - Specific products affected

5. **Detailed Product Changes**:
   - Complete table of ALL products (no limit!)
   - Each product shows:
     - Product handle and ID
     - Number of variants
     - Status (success/failed)
   - Expandable variant details showing:
     - Variant ID
     - Metal type (option1)
     - Old price → New price
     - Price change indicator (↑/↓/=)
     - Status per variant

### Email Content (Plain Text)

A plain text version is also included for email clients that don't support HTML.

## 🎨 Sample Email Report

```
================================================================================
✅ PRICE UPDATE REPORT - SUCCESS
================================================================================

Timestamp: 2024-12-22T09:00:00+05:30

METAL RATES
================================================================================
24K Gold Rate: INR 7,250.50/g
925 Silver Rate: INR 97.25/g

SUMMARY STATISTICS
================================================================================
Products Processed:  150
Variants Updated:    823
Variants Skipped:    45
Variants Failed:     0
Metafields Updated:  300
Total Errors:        0

DETAILED PRODUCT CHANGES (150 products)
================================================================================

Product: gold-ring-001 (ID: 12345678)
Status: SUCCESS
Variants: 5
----------------------------------------
  Variant 111 (14K Yellow Gold):
    Old Price: ₹29,100.00
    New Price: ₹30,308.00
    Change: +₹1,208.00
    Status: updated

  Variant 112 (18K Yellow Gold):
    Old Price: ₹35,200.00
    New Price: ₹36,450.00
    Change: +₹1,250.00
    Status: updated

... [continues for all variants in all products]
```

## 🧪 Testing Email Setup

### Test with Manual Workflow

1. Go to **Actions** → **Manual Price Update**
2. Click **Run workflow**
3. Fill in test rates (e.g., gold: 7200, silver: 95)
4. **Check** `dry_run` option
5. Click **Run workflow**
6. Check your email inbox for the test report

### Verify Email Delivery

Check:
- ✅ Email received in inbox (check spam folder if not)
- ✅ HTML formatting displays correctly
- ✅ All product details are present
- ✅ Statistics are accurate

## ⚠️ Troubleshooting

### "Failed to send email report"

**Possible causes:**

1. **Wrong app password**
   - Solution: Regenerate app password and update `SENDER_PASSWORD` secret

2. **2FA not enabled** (Gmail)
   - Solution: Enable 2-Factor Authentication first

3. **Wrong SMTP server/port**
   - Solution: Verify SMTP_SERVER and SMTP_PORT for your email provider

4. **Email blocked by provider**
   - Solution: Check email provider's security settings
   - Gmail: Check [Less secure app access](https://myaccount.google.com/security)

5. **Firewall blocking SMTP**
   - Solution: GitHub Actions shouldn't have this issue, but verify SMTP_PORT is 587 (not 465)

### Email not received

1. **Check spam/junk folder**
2. **Verify RECIPIENT_EMAIL is correct**
3. **Check workflow logs** for "Email report sent successfully"
4. **Check sender email's Sent folder**

### HTML not displaying

- Your email client may not support HTML
- Check the plain text version
- Try a different email client (Gmail web, Outlook, etc.)

## 📊 Email Report Limits

**No limits!** The email reporter handles:
- ✅ Unlimited products (tested with 10,000+)
- ✅ Unlimited variants
- ✅ Unlimited errors
- ✅ All data is included in every report

**Note**: Very large emails (>10MB) may be rejected by some email providers. For 10,000+ products, consider:
- Using a business email account with higher limits
- Reviewing the JSON artifact in GitHub Actions as backup

## 🔒 Security Notes

- ✅ Email passwords are stored as encrypted GitHub Secrets
- ✅ Passwords are never logged or exposed
- ✅ Emails are sent over TLS (encrypted)
- ✅ App passwords can be revoked anytime
- ⚠️ Don't share app passwords
- ⚠️ Don't use your main email password (use app password!)

## 📋 Summary Checklist

Before first run:

- [ ] 2FA enabled on sender email account
- [ ] App password generated
- [ ] `SENDER_EMAIL` secret added
- [ ] `SENDER_PASSWORD` secret added (app password, not account password!)
- [ ] `RECIPIENT_EMAIL` secret added
- [ ] Optional: `SMTP_SERVER` and `SMTP_PORT` variables configured if not Gmail
- [ ] Test email sent successfully (dry run)
- [ ] Email received and formatted correctly

---

**Last Updated**: 2024-12-22
**Version**: 1.0.0
