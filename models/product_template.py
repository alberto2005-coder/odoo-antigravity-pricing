from odoo import models, fields, api
from .scraper_utils import scrape_price
import time
import random
import concurrent.futures
import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dynamic_pricing_active = fields.Boolean(string='Enable Dynamic Pricing', default=False)
    min_margin = fields.Float(string='Minimum Margin (%)', help='Minimum profit margin allowed in percentage.')
    competitor_rule = fields.Selection([
        ('lowest_minus', 'Lowest competitor - X%'),
        ('lowest_minus_fixed', 'Lowest competitor - Fixed Amount'),
        ('average', 'Average competitor'),
        ('predictive', 'Predictive Trend Match'),
    ], string='Adjustment Rule', default='lowest_minus')
    rule_value = fields.Float(string='Rule Value (X)', help='Percentage or fixed amount for the rule.')
    competitor_alert_threshold = fields.Float(string='Alert Threshold (%)', default=15.0, help='Notify when competitor price changes by more than this percentage.')
    
    competitor_url_ids = fields.One2many('dynamic.competitor.url', 'product_id', string='Competitor URLs')
    dynamic_price_log_count = fields.Integer(compute='_compute_dynamic_price_log_count', string='Price Logs')

    # Sales Impact Analysis Computed Fields
    dynamic_pricing_sales_qty = fields.Float(compute='_compute_sales_impact', string='Units Sold (Active Period)')
    dynamic_pricing_sales_revenue = fields.Monetary(compute='_compute_sales_impact', string='Revenue (Active Period)', currency_field='currency_id')
    dynamic_pricing_sales_qty_before = fields.Float(compute='_compute_sales_impact', string='Units Sold (Previous Period)')
    dynamic_pricing_sales_rev_before = fields.Monetary(compute='_compute_sales_impact', string='Revenue (Previous Period)', currency_field='currency_id')
    sales_improvement_qty_pct = fields.Float(compute='_compute_sales_impact', string='Sales Qty Improvement (%)')
    sales_improvement_rev_pct = fields.Float(compute='_compute_sales_impact', string='Revenue Improvement (%)')

    def _compute_dynamic_price_log_count(self):
        for record in self:
            record.dynamic_price_log_count = self.env['dynamic.price.log'].search_count([('product_id', '=', record.id)])

    def action_view_dynamic_price_logs(self):
        self.ensure_one()
        return {
            'name': 'Dynamic Price Fluctuation',
            'type': 'ir.actions.act_window',
            'res_model': 'dynamic.price.log',
            'view_mode': 'graph,tree',
            'domain': [('product_id', '=', self.id)],
            'context': {'default_product_id': self.id},
        }

    def _compute_sales_impact(self):
        for product in self:
            # Find the oldest price log to know when dynamic pricing started
            first_log = self.env['dynamic.price.log'].search([
                ('product_id', '=', product.id)
            ], order='create_date asc', limit=1)
            
            if not first_log:
                product.dynamic_pricing_sales_qty = 0.0
                product.dynamic_pricing_sales_revenue = 0.0
                product.dynamic_pricing_sales_qty_before = 0.0
                product.dynamic_pricing_sales_rev_before = 0.0
                product.sales_improvement_qty_pct = 0.0
                product.sales_improvement_rev_pct = 0.0
                continue
                
            start_date = first_log.create_date
            now = fields.Datetime.now()
            duration = now - start_date
            
            # Use a duration of at least 1 day for comparison
            days = max(duration.days, 1)
            before_start_date = start_date - datetime.timedelta(days=days)
            
            # Confirmed sales during the active period
            lines_after = self.env['sale.order.line'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('order_id.state', 'in', ('sale', 'done')),
                ('order_id.date_order', '>=', start_date)
            ])
            qty_after = sum(lines_after.mapped('product_uom_qty'))
            rev_after = sum(lines_after.mapped('price_subtotal'))
            
            # Confirmed sales during the previous period of equal duration
            lines_before = self.env['sale.order.line'].search([
                ('product_id.product_tmpl_id', '=', product.id),
                ('order_id.state', 'in', ('sale', 'done')),
                ('order_id.date_order', '>=', before_start_date),
                ('order_id.date_order', '<', start_date)
            ])
            qty_before = sum(lines_before.mapped('product_uom_qty'))
            rev_before = sum(lines_before.mapped('price_subtotal'))
            
            # Calculate improvement percentage
            product.dynamic_pricing_sales_qty = qty_after
            product.dynamic_pricing_sales_revenue = rev_after
            product.dynamic_pricing_sales_qty_before = qty_before
            product.dynamic_pricing_sales_rev_before = rev_before
            product.sales_improvement_qty_pct = ((qty_after - qty_before) / qty_before * 100.0) if qty_before > 0 else 0.0
            product.sales_improvement_rev_pct = ((rev_after - rev_before) / rev_before * 100.0) if rev_before > 0 else 0.0

    def _predict_next_price(self, competitor_url):
        """
        Predicts the next price of a competitor using a linear regression trend
        based on the last 5 logs in dynamic.competitor.price.log.
        """
        logs = self.env['dynamic.competitor.price.log'].search([
            ('competitor_url_id', '=', competitor_url.id)
        ], order='create_date desc', limit=5)
        
        if len(logs) < 2:
            return competitor_url.last_scraped_price
            
        # Reverse to get oldest to newest
        prices = [log.price for log in reversed(logs)]
        n = len(prices)
        x = list(range(1, n + 1))
        y = prices
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(i*i for i in x)
        sum_xy = sum(i*j for i, j in zip(x, y))
        
        denominator = (n * sum_xx - sum_x * sum_x)
        if denominator == 0:
            return prices[-1]
            
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Predict the next point (n + 1)
        mean_x = sum_x / n
        mean_y = sum_y / n
        predicted_price = mean_y + slope * ((n + 1) - mean_x)
        
        # Safety fallback
        if predicted_price <= 0 or predicted_price < prices[-1] * 0.5:
            return prices[-1]
            
        return round(predicted_price, 2)

    @api.model
    def action_update_dynamic_prices(self):
        """
        Cron job method to update prices.
        """
        # Fetch optional proxy and API configs from system parameters
        config = self.env['ir.config_parameter'].sudo()
        proxy_url = config.get_param('dynamic_pricing.proxy_url', default=None)
        api_provider = config.get_param('dynamic_pricing.api_provider', default=None)
        api_key = config.get_param('dynamic_pricing.api_key', default=None)
        render_js = config.get_param('dynamic_pricing.render_js', default='False').lower() == 'true'
        debug_mock = config.get_param('dynamic_pricing.debug_mock_prices', default='False').lower() == 'true'
        
        products = self.search([('dynamic_pricing_active', '=', True)])
        
        # Scrape concurrently to save time
        for product in products:
            if not product.competitor_url_ids:
                continue

            prices = []
            # Extract competitor data in the main thread (thread safety for Odoo environment)
            competitor_data = [(comp.id, comp.url, comp.platform) for comp in product.competitor_url_ids]
            
            def scrape_and_update(data):
                comp_id, url, platform = data
                # Add random sleep between requests to avoid rate limits if not using API
                if not api_provider:
                    time.sleep(random.uniform(1.0, 3.5))
                
                price = scrape_price(
                    url, 
                    platform, 
                    proxy=proxy_url,
                    api_provider=api_provider,
                    api_key=api_key,
                    render_js=render_js,
                    debug_mock=debug_mock
                )
                return comp_id, price

            # Use ThreadPoolExecutor for multi-threading
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = list(executor.map(scrape_and_update, competitor_data))
                
            for comp_id, price in results:
                if price is not None:
                    comp = self.env['dynamic.competitor.url'].browse(comp_id)
                    old_scraped_price = comp.last_scraped_price
                    comp.write({
                        'last_scraped_price': price,
                        'last_scraped_date': fields.Datetime.now()
                    })
                    
                    # Log competitor price history
                    self.env['dynamic.competitor.price.log'].create({
                        'competitor_url_id': comp.id,
                        'price': price
                    })
                    
                    prices.append(price)
                    
                    # Detect price changes and trigger alert if superior to alert threshold
                    if old_scraped_price and old_scraped_price > 0.0:
                        pct_diff = (abs(price - old_scraped_price) / old_scraped_price) * 100.0
                        if pct_diff >= product.competitor_alert_threshold:
                            # Log warning in chatter
                            product.message_post(
                                body=f"⚠️ <b>Competitor Price Alert:</b> Competitor ({comp.platform}) price changed from {old_scraped_price:.2f} to {price:.2f} ({pct_diff:.1f}% change).",
                                subtype_xmlid="mail.mt_note"
                            )
                            # Create activity for admin
                            activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
                            if activity_type:
                                self.env['mail.activity'].create({
                                    'res_id': product.id,
                                    'res_model_id': self.env['ir.model']._get(product._name).id,
                                    'activity_type_id': activity_type.id,
                                    'summary': f"Price Alert: {product.name}",
                                    'note': f"Competitor price on {comp.platform} changed by {pct_diff:.1f}% from {old_scraped_price:.2f} to {price:.2f}.",
                                    'user_id': self.env.user.id or self.env.ref('base.user_admin').id or 2
                                })

            if not prices and product.competitor_rule != 'predictive':
                continue

            # Calculate proposed price
            proposed_price = product.list_price
            
            if product.competitor_rule == 'predictive':
                predicted_prices = []
                for comp in product.competitor_url_ids:
                    pred_price = product._predict_next_price(comp)
                    if pred_price:
                        predicted_prices.append(pred_price)
                if not predicted_prices:
                    continue
                lowest_predicted = min(predicted_prices)
                if product.rule_value:
                    proposed_price = lowest_predicted * (1 - (product.rule_value / 100.0))
                else:
                    proposed_price = lowest_predicted
            else:
                lowest_price = min(prices)
                average_price = sum(prices) / len(prices)

                if product.competitor_rule == 'lowest_minus':
                    proposed_price = lowest_price * (1 - (product.rule_value / 100.0))
                elif product.competitor_rule == 'lowest_minus_fixed':
                    proposed_price = lowest_price - product.rule_value
                elif product.competitor_rule == 'average':
                    proposed_price = average_price

            # Safety Validation: Never go below cost + minimum margin
            # Margin = (Price - Cost) / Cost  =>  Price = Cost * (1 + Margin)
            # Standard price in Odoo is 'standard_price'
            cost = product.standard_price
            min_price = cost * (1 + (product.min_margin / 100.0))

            if proposed_price < min_price:
                # Add to chatter
                product.message_post(body=f"Dynamic Pricing skipped: Proposed price {proposed_price:.2f} is below the minimum allowed price {min_price:.2f} (Cost + Min Margin).")
                continue
            
            if round(proposed_price, 2) != round(product.list_price, 2):
                old_price = product.list_price
                product.list_price = proposed_price
                
                # Log the change
                self.env['dynamic.price.log'].create({
                    'product_id': product.id,
                    'old_price': old_price,
                    'new_price': proposed_price,
                    'reason': f"Rule '{product.competitor_rule}' applied. Competitor prices: {prices if product.competitor_rule != 'predictive' else predicted_prices}"
                })
                
                # Also log in chatter
                product.message_post(body=f"Dynamic Pricing updated price from {old_price:.2f} to {proposed_price:.2f}.")
