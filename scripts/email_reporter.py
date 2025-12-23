"""
Email Reporter Module

Sends detailed email reports after each price update run.
Includes complete logs of all products modified, errors, and statistics.
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailReporter:
    """Sends detailed email reports of price update runs."""

    def __init__(self, sender_email: str, sender_password: str, recipient_email: str,
                 smtp_server: str = 'smtp.gmail.com', smtp_port: int = 587):
        """
        Initialize email reporter.

        Args:
            sender_email: Email address to send from
            sender_password: App password for sender email
            recipient_email: Email address to send reports to
            smtp_server: SMTP server address (default: Gmail)
            smtp_port: SMTP server port (default: 587 for TLS)
        """
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

    def send_report(self, report_data: Dict[str, Any], is_success: bool = True) -> bool:
        """
        Send detailed email report.

        Args:
            report_data: Complete report data including all product changes and errors
            is_success: Whether the update was successful overall

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = self._generate_subject(report_data, is_success)
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email

            # Generate HTML and plain text content
            html_content = self._generate_html_report(report_data, is_success)
            text_content = self._generate_text_report(report_data, is_success)

            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            logger.info(f"Sending email report to {self.recipient_email}")

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logger.info("Email report sent successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            return False

    def _generate_subject(self, report_data: Dict[str, Any], is_success: bool) -> str:
        """Generate email subject line."""
        timestamp = report_data.get('timestamp', datetime.now().isoformat())
        stats = report_data.get('statistics', {})

        if not is_success:
            return f"❌ Price Update FAILED - {timestamp}"

        products = stats.get('products_processed', 0)
        variants = stats.get('variants_updated', 0)

        return f"✅ Price Update Complete - {products} products, {variants} variants updated - {timestamp}"

    def _generate_html_report(self, report_data: Dict[str, Any], is_success: bool) -> str:
        """Generate detailed HTML email report."""
        timestamp = report_data.get('timestamp', datetime.now().isoformat())
        gold_rate = report_data.get('gold_rate', 0)
        silver_rate = report_data.get('silver_rate', 0)
        currency = report_data.get('currency', 'INR')
        stats = report_data.get('statistics', {})
        products = report_data.get('products', [])
        errors = report_data.get('errors', [])

        status_color = '#28a745' if is_success else '#dc3545'
        status_icon = '✅' if is_success else '❌'
        status_text = 'SUCCESS' if is_success else 'FAILED'

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: {status_color}; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .header h1 {{ margin: 0; }}
                .section {{ background-color: #f8f9fa; padding: 15px; margin-bottom: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
                .section h2 {{ margin-top: 0; color: #007bff; }}
                .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
                .stat-box {{ background-color: white; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; }}
                .stat-label {{ font-size: 0.9em; color: #6c757d; }}
                .stat-value {{ font-size: 1.8em; font-weight: bold; color: #007bff; }}
                .product-table {{ width: 100%; border-collapse: collapse; background-color: white; }}
                .product-table th {{ background-color: #007bff; color: white; padding: 10px; text-align: left; }}
                .product-table td {{ padding: 10px; border-bottom: 1px solid #dee2e6; }}
                .product-table tr:hover {{ background-color: #f8f9fa; }}
                .variant-details {{ margin-left: 20px; font-size: 0.9em; color: #6c757d; }}
                .error-box {{ background-color: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .danger {{ color: #dc3545; }}
                .footer {{ text-align: center; color: #6c757d; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{status_icon} Price Update Report - {status_text}</h1>
                    <p style="margin: 5px 0 0 0;">Timestamp: {timestamp}</p>
                </div>

                <div class="section">
                    <h2>💰 Metal Rates</h2>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">24K Gold Rate</div>
                            <div class="stat-value">{currency} {gold_rate:.2f}/g</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">925 Silver Rate</div>
                            <div class="stat-value">{currency} {silver_rate:.2f}/g</div>
                        </div>
                    </div>
                </div>

                <div class="section">
                    <h2>📊 Summary Statistics</h2>
                    <div class="stats-grid">
                        <div class="stat-box">
                            <div class="stat-label">Products Processed</div>
                            <div class="stat-value">{stats.get('products_processed', 0)}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Variants Updated</div>
                            <div class="stat-value success">{stats.get('variants_updated', 0)}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Variants Skipped</div>
                            <div class="stat-value warning">{stats.get('variants_skipped', 0)}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Variants Failed</div>
                            <div class="stat-value danger">{stats.get('variants_failed', 0)}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Metafields Updated</div>
                            <div class="stat-value">{stats.get('metafields_updated', 0)}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">Total Errors</div>
                            <div class="stat-value danger">{len(errors)}</div>
                        </div>
                    </div>
                </div>
        """

        # Add errors section if there are any
        if errors:
            html += """
                <div class="section">
                    <h2>⚠️ Errors Encountered</h2>
            """
            for error in errors:
                html += f'<div class="error-box">{error}</div>'
            html += "</div>"

        # Add detailed product list
        if products:
            html += f"""
                <div class="section">
                    <h2>📦 Detailed Product Changes ({len(products)} products)</h2>
                    <table class="product-table">
                        <thead>
                            <tr>
                                <th>Product Handle</th>
                                <th>Product ID</th>
                                <th>Variants</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            for product in products:
                handle = product.get('handle', 'Unknown')
                product_id = product.get('product_id', 'N/A')
                variants = product.get('variants', [])
                status = product.get('status', 'unknown')

                status_class = 'success' if status == 'success' else 'danger'
                status_icon = '✓' if status == 'success' else '✗'

                html += f"""
                    <tr>
                        <td><strong>{handle}</strong></td>
                        <td>{product_id}</td>
                        <td>{len(variants)} variant(s)</td>
                        <td class="{status_class}">{status_icon} {status.upper()}</td>
                    </tr>
                """

                # Add variant details
                if variants:
                    html += '<tr><td colspan="4"><div class="variant-details">'
                    for variant in variants:
                        variant_id = variant.get('variant_id', 'N/A')
                        option1 = variant.get('option1', 'N/A')
                        old_price = variant.get('old_price', 0)
                        new_price = variant.get('new_price', 0)
                        variant_status = variant.get('status', 'unknown')

                        price_change = new_price - old_price
                        change_icon = '↑' if price_change > 0 else '↓' if price_change < 0 else '='

                        html += f"""
                            <div style="margin-bottom: 5px;">
                                <strong>Variant {variant_id}</strong> ({option1}):
                                ₹{old_price:.2f} → ₹{new_price:.2f} {change_icon}
                                ({variant_status})
                            </div>
                        """
                    html += '</div></td></tr>'

            html += """
                        </tbody>
                    </table>
                </div>
            """

        # Footer
        html += f"""
                <div class="footer">
                    <p>Generated by Jhango Siyaara Price Updater</p>
                    <p>Automated price updates for jewelry products</p>
                    <p><small>Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_text_report(self, report_data: Dict[str, Any], is_success: bool) -> str:
        """Generate plain text email report."""
        timestamp = report_data.get('timestamp', datetime.now().isoformat())
        gold_rate = report_data.get('gold_rate', 0)
        silver_rate = report_data.get('silver_rate', 0)
        currency = report_data.get('currency', 'INR')
        stats = report_data.get('statistics', {})
        products = report_data.get('products', [])
        errors = report_data.get('errors', [])

        status_icon = '[SUCCESS]' if is_success else '[FAILED]'

        text = f"""
{'='*80}
{status_icon} PRICE UPDATE REPORT
{'='*80}

Timestamp: {timestamp}

METAL RATES
{'='*80}
24K Gold Rate: {currency} {gold_rate:.2f}/g
925 Silver Rate: {currency} {silver_rate:.2f}/g

SUMMARY STATISTICS
{'='*80}
Products Processed:  {stats.get('products_processed', 0)}
Variants Updated:    {stats.get('variants_updated', 0)}
Variants Skipped:    {stats.get('variants_skipped', 0)}
Variants Failed:     {stats.get('variants_failed', 0)}
Metafields Updated:  {stats.get('metafields_updated', 0)}
Total Errors:        {len(errors)}
"""

        # Add errors
        if errors:
            text += f"\n\nERRORS ENCOUNTERED ({len(errors)})\n{'='*80}\n"
            for i, error in enumerate(errors, 1):
                text += f"{i}. {error}\n"

        # Add detailed product list
        if products:
            text += f"\n\nDETAILED PRODUCT CHANGES ({len(products)} products)\n{'='*80}\n"

            for product in products:
                handle = product.get('handle', 'Unknown')
                product_id = product.get('product_id', 'N/A')
                variants = product.get('variants', [])
                status = product.get('status', 'unknown')

                text += f"\nProduct: {handle} (ID: {product_id})\n"
                text += f"Status: {status.upper()}\n"
                text += f"Variants: {len(variants)}\n"

                if variants:
                    text += "-" * 40 + "\n"
                    for variant in variants:
                        variant_id = variant.get('variant_id', 'N/A')
                        option1 = variant.get('option1', 'N/A')
                        old_price = variant.get('old_price', 0)
                        new_price = variant.get('new_price', 0)
                        variant_status = variant.get('status', 'unknown')

                        price_change = new_price - old_price
                        change_text = f"+{price_change:.2f}" if price_change > 0 else f"{price_change:.2f}"

                        text += f"  Variant {variant_id} ({option1}):\n"
                        text += f"    Old Price: ₹{old_price:.2f}\n"
                        text += f"    New Price: ₹{new_price:.2f}\n"
                        text += f"    Change: ₹{change_text}\n"
                        text += f"    Status: {variant_status}\n"

        text += f"\n{'='*80}\n"
        text += f"Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += f"{'='*80}\n"

        return text
