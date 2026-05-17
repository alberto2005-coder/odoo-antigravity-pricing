from odoo import models, fields

class DynamicCompetitorUrl(models.Model):
    _name = 'dynamic.competitor.url'
    _description = 'Competitor URL for Dynamic Pricing'

    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    url = fields.Char(string='Competitor URL', required=True)
    platform = fields.Selection([
        ('amazon', 'Amazon'),
        ('google', 'Google Shopping'),
        ('custom', 'Custom')
    ], string='Platform', default='custom', required=True)
    last_scraped_price = fields.Float(string='Last Scraped Price', readonly=True)
    last_scraped_date = fields.Datetime(string='Last Scraped Date', readonly=True)
