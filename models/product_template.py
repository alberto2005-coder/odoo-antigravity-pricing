from odoo import models, fields, api
from .scraper_utils import scrape_price
import time
import random
import concurrent.futures

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    dynamic_pricing_active = fields.Boolean(string='Enable Dynamic Pricing', default=False)
    min_margin = fields.Float(string='Minimum Margin (%)', help='Minimum profit margin allowed in percentage.')
    competitor_rule = fields.Selection([
        ('lowest_minus', 'Lowest competitor - X%'),
        ('lowest_minus_fixed', 'Lowest competitor - Fixed Amount'),
        ('average', 'Average competitor'),
    ], string='Adjustment Rule', default='lowest_minus')
    rule_value = fields.Float(string='Rule Value (X)', help='Percentage or fixed amount for the rule.')
    
    competitor_url_ids = fields.One2many('dynamic.competitor.url', 'product_id', string='Competitor URLs')
    dynamic_price_log_count = fields.Integer(compute='_compute_dynamic_price_log_count', string='Price Logs')

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
        
        products = self.search([('dynamic_pricing_active', '=', True)])
        
        # Scrape concurrently to save time
        for product in products:
            if not product.competitor_url_ids:
                continue

            prices = []
            
            def scrape_and_update(comp):
                # Add random sleep between requests to avoid rate limits if not using API
                if not api_provider:
                    time.sleep(random.uniform(1.0, 3.5))
                
                return comp, scrape_price(
                    comp.url, 
                    comp.platform, 
                    proxy=proxy_url,
                    api_provider=api_provider,
                    api_key=api_key,
                    render_js=render_js
                )

            # Use ThreadPoolExecutor for multi-threading
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                results = executor.map(scrape_and_update, product.competitor_url_ids)
                
            for comp, price in results:
                if price:
                    comp.write({
                        'last_scraped_price': price,
                        'last_scraped_date': fields.Datetime.now()
                    })
                    prices.append(price)

            if not prices:
                continue

            # Calculate proposed price
            proposed_price = product.list_price
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
                    'reason': f"Rule '{product.competitor_rule}' applied. Competitor prices: {prices}"
                })
                
                # Also log in chatter
                product.message_post(body=f"Dynamic Pricing updated price from {old_price:.2f} to {proposed_price:.2f}.")
