import csv
import base64
import io
from odoo import models, fields, _, api
from odoo.exceptions import UserError

class ImportCompetitorUrlWizard(models.TransientModel):
    _name = 'import.competitor.url.wizard'
    _description = 'Import Competitor URLs from CSV'

    csv_file = fields.Binary(string='CSV File', required=True, help='Upload a CSV file containing competitor pricing URLs.')
    filename = fields.Char(string='Filename')
    
    def action_import(self):
        self.ensure_one()
        if not self.filename or not self.filename.endswith('.csv'):
            raise UserError(_("Please upload a valid CSV file."))
            
        data = base64.b64decode(self.csv_file)
        try:
            file_input = io.StringIO(data.decode('utf-8'))
        except UnicodeDecodeError:
            try:
                file_input = io.StringIO(data.decode('latin1'))
            except Exception:
                raise UserError(_("Could not decode the CSV file. Please make sure it is UTF-8 encoded."))
                
        reader = csv.DictReader(file_input)
        
        imported_count = 0
        skipped_count = 0
        errors = []
        
        for row in reader:
            sku = row.get('sku') or row.get('product_sku') or row.get('default_code')
            product_id_val = row.get('product_id')
            product_name = row.get('product_name') or row.get('name')
            platform = row.get('platform', 'custom').strip().lower()
            url = row.get('url')
            
            if not url:
                skipped_count += 1
                errors.append(f"Row {reader.line_num}: Missing URL.")
                continue
                
            # Find the product
            product = None
            if sku:
                product = self.env['product.template'].search([('default_code', '=', sku.strip())], limit=1)
            if not product and product_id_val:
                try:
                    product = self.env['product.template'].browse(int(product_id_val))
                    if not product.exists():
                        product = None
                except ValueError:
                    pass
            if not product and product_name:
                product = self.env['product.template'].search([('name', '=', product_name.strip())], limit=1)
                
            if not product:
                skipped_count += 1
                errors.append(f"Row {reader.line_num}: Product not found (SKU: {sku}, Name: {product_name}, ID: {product_id_val}).")
                continue
                
            # Validate platform selection
            if platform not in ['amazon', 'google', 'custom']:
                platform = 'custom'
                
            # Create or update competitor URL
            existing = self.env['dynamic.competitor.url'].search([
                ('product_id', '=', product.id),
                ('url', '=', url.strip())
            ], limit=1)
            
            if not existing:
                self.env['dynamic.competitor.url'].create({
                    'product_id': product.id,
                    'platform': platform,
                    'url': url.strip()
                })
                # Auto-activate dynamic pricing for the product
                if not product.dynamic_pricing_active:
                    product.dynamic_pricing_active = True
                imported_count += 1
            else:
                existing.write({'platform': platform})
                imported_count += 1
                
        message = _("Successfully imported/updated %s competitor URLs.") % imported_count
        if skipped_count > 0:
            message += _(" Skipped %s rows due to unresolved products or errors.") % skipped_count
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('CSV Import Results'),
                'message': message,
                'type': 'success' if skipped_count == 0 else 'warning',
                'sticky': False,
            }
        }
