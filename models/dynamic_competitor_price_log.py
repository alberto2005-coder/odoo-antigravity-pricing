from odoo import models, fields

class DynamicCompetitorPriceLog(models.Model):
    _name = 'dynamic.competitor.price.log'
    _description = 'Competitor Price History Log'
    _order = 'create_date desc'

    competitor_url_id = fields.Many2one('dynamic.competitor.url', string='Competitor URL', required=True, ondelete='cascade')
    price = fields.Float(string='Scraped Price', required=True)
    product_id = fields.Many2one(
        related='competitor_url_id.product_id',
        store=True,
        string='Product',
        readonly=True
    )
    platform = fields.Selection(
        related='competitor_url_id.platform',
        store=True,
        string='Platform',
        readonly=True
    )
