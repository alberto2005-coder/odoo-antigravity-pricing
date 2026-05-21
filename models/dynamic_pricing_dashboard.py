from odoo import models, fields, api
import datetime

class DynamicPricingDashboard(models.TransientModel):
    _name = 'dynamic.pricing.dashboard'
    _description = 'Dynamic Pricing Dashboard'

    active_products_count = fields.Integer(string='Active Products', compute='_compute_stats')
    total_logs_count = fields.Integer(string='Total Price Adjustments', compute='_compute_stats')
    today_logs_count = fields.Integer(string='Adjustments Today', compute='_compute_stats')
    total_urls_count = fields.Integer(string='Tracked Competitors', compute='_compute_stats')
    avg_qty_improvement = fields.Float(string='Avg Sales Qty Improvement (%)', compute='_compute_stats')
    avg_rev_improvement = fields.Float(string='Avg Revenue Improvement (%)', compute='_compute_stats')
    active_alerts_count = fields.Integer(string='Alerts Today', compute='_compute_stats')

    def _compute_stats(self):
        for record in self:
            # Active products
            products = self.env['product.template'].search([('dynamic_pricing_active', '=', True)])
            record.active_products_count = len(products)

            # Total and today's logs
            record.total_logs_count = self.env['dynamic.price.log'].search_count([])
            
            today_start = datetime.datetime.combine(fields.Date.today(), datetime.time.min)
            record.today_logs_count = self.env['dynamic.price.log'].search_count([
                ('create_date', '>=', today_start)
            ])

            # Total competitor URLs
            record.total_urls_count = self.env['dynamic.competitor.url'].search_count([])

            # Avg improvements
            qty_pcts = [p.sales_improvement_qty_pct for p in products if p.sales_improvement_qty_pct]
            rev_pcts = [p.sales_improvement_rev_pct for p in products if p.sales_improvement_rev_pct]
            
            record.avg_qty_improvement = sum(qty_pcts) / len(qty_pcts) if qty_pcts else 0.0
            record.avg_rev_improvement = sum(rev_pcts) / len(rev_pcts) if rev_pcts else 0.0

            # Active alerts today
            record.active_alerts_count = self.env['mail.activity'].search_count([
                ('res_model', '=', 'product.template'),
                ('summary', 'like', 'Price Alert'),
                ('create_date', '>=', today_start)
            ])

    @api.model
    def action_open_dashboard(self):
        dashboard = self.create({})
        return {
            'name': 'Dynamic Pricing Dashboard',
            'type': 'ir.actions.act_window',
            'res_model': 'dynamic.pricing.dashboard',
            'view_mode': 'form',
            'res_id': dashboard.id,
            'target': 'current',
            'flags': {'mode': 'readonly'},
        }
