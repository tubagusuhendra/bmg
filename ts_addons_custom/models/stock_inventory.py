from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import string
import os
import itertools
import random
import string
import tempfile
import binascii
from email.utils import formataddr
from odoo.tools import float_compare, float_is_zero
import uuid 
import xlrd
import logging
_logger = logging.getLogger(__name__)
import json

import io
try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')
try:
    import xlwt
except ImportError:
    _logger.debug('Cannot `import xlwt`.')
try:
    import cStringIO
except ImportError:
    _logger.debug('Cannot `import cStringIO`.')
try:
    import base64
except ImportError:
    _logger.debug('Cannot `import base64`.')

class StockInventory(models.Model):
    _name = 'stock.inventory'
    _inherit = ['stock.inventory','mail.thread']

    INVENTORY_STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirm', 'In Progress'),
        ('to approve', 'To Approve'),
        ('done', 'Validated'),
        ('cancel', 'Cancelled'),
    ]

    state = fields.Selection(string='Status', selection=INVENTORY_STATE_SELECTION,
        tracking=True,
        copy=False, index=True, readonly=True,
        default='draft')
    
    filter = fields.Selection([('product','Product Variant'),('import','Import CSV')],string="Filter",default='product')
    data_file = fields.Binary(string='Import Inventory Line',attachment=False)
    valid_file = fields.Boolean(string=u'File Valid', default=False,)
    notes = fields.Text('Notes')
    name = fields.Char('Inventory Reference', required=True, readonly=True,copy=False, states={'draft': [('readonly', False)]},default=lambda self: _('New'), help="Inventory Name.")

    def action_set_to_draft(self):
        self.state='draft'
        self.valid_file = False

    def action_cancel(self):
        for inv in self:
            if inv.state =='done':
                raise UserError(_('Cannot cancel,adjustment already done'))
            inv.line_ids.unlink()
            inv.write({'state': 'cancel'})

    @api.onchange('data_file')
    def onchange_valid_file(self):
        self.valid_file =False

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.inventory.seq') or '/'
        return super(StockInventory, self).create(vals)

    def request_approval(self):
        self.write({'state': 'to approve'})


    def validate_file(self):
        for record in self:
            keys = ['Product', 'Unit', 'Location', 'Qty Diff']
            try:
                csv_data = base64.b64decode(self.data_file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except:

                raise UserError(_("The uploaded file must be in .csv!"))
            list_data = []
            product_err =""
            product_uom_loc_err =""
            product_account_err =""
            product_cons_err =""
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue
                list_data.append(values)    
                code = values['Product']
                product_obj = self.env['product.product'].search([('default_code', '=', code)])
                location_obj = self.env['stock.location'].search([('complete_name', '=', values['Location'])])
                uom_obj = self.env['uom.uom'].search([('name', '=', values['Unit'])])
                if not location_obj:
                    message_error = """- [%s] is not found, might be inactive or not part of selected warehouse!""" % values['Location']
                    if message_error not in product_uom_loc_err:
                        product_uom_loc_err += """
    - [%s] is not found, might be inactive or not part of selected warehouse!""" % values['Location']
                if not uom_obj:
                    product_uom_loc_err += """
    - For [%s]'s UoM value in the file is incorrect or not found!""" % code
                if not product_obj:
                    product_err += """
    - [%s] Product Variant is not found, might be inactive or not yet registered!""" % code
                elif len(product_obj) > 1:
                    product_err += """
    - There is have multi reference product using [%s]!""" % code
                elif product_obj:
                    if self.env['stock.inventory.line'].search_count([('product_id', '=', product_obj.id), ('inventory_id.state', 'in', ['confirm', 'to approve'])]) > 0:
                        product_err += """
    - [%s] Product already registered on progressing inventory adjustment!""" % code
            if len(product_uom_loc_err) > 0:
                record.update({'data_file': False})
                raise UserError(_("""We have following error: %s""") % (product_uom_loc_err))
            if len(product_err) > 0:
                record.update({'data_file': False})
                raise UserError(_("""We have following Product Variant error: %s""") % (product_err))
            else:
                record.update({'valid_file': True})    

    def import_file(self):
        for record in self:
            record.validate_file()
            product_obj = self.env['product.product']
            keys = ['Product', 'Unit', 'Location', 'Qty Diff']
            try:
                csv_data = base64.b64decode(self.data_file)
                data_file = io.StringIO(csv_data.decode("utf-8"))
                data_file.seek(0)
                file_reader = []
                values = {}
                csv_reader = csv.reader(data_file, delimiter=',')
                file_reader.extend(csv_reader)
            except:

                raise UserError(_("The uploaded file must be in .csv!"))
            list_data = []
            location_ids = []
            product_ids = []
            for i in range(len(file_reader)):
                field = list(map(str, file_reader[i]))
                values = dict(zip(keys, field))
                if values:
                    if i == 0:
                        continue  
                    list_data.append(values)
                    location_ids.append(values['Location'])
                    product_ids.append(values['Product'])
            if list_data:
                record.with_context(bulk_check=True).update({
                    'state': 'confirm', 
                    'line_ids': self._prepare_stock_inventory_line(list_data)})
            record.update({'data_file': False})
        return {}

    def _prepare_stock_inventory_line(self,data):
        vals = []
        for rec in data:
            owner_id = []
            product = self.env['product.product'].search([('default_code', '=', rec['Product'])])
            uom = self.env['uom.uom'].search([('name', '=', rec['Unit'])])
            location = self.env['stock.location'].search([('complete_name', '=', rec['Location'])])
            res = {
                'company_id': self.env.company.id,
                'product_uom_id': uom.id,
                'location_id': location.id,
                'product_id': product.id,
                'product_qty': rec['Qty Diff'],
            }
            vals.append([0, 0, res])
        return vals