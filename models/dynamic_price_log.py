from odoo import models, fields

class DynamicPriceLog(models.Model):
    _name = 'dynamic.price.log'
    _description = 'Dynamic Price History Log'
    _order = 'create_date desc'

    product_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade')
    old_price = fields.Float(string='Old Price', required=True)
    new_price = fields.Float(string='New Price', required=True)
    reason = fields.Text(string='Reason')
