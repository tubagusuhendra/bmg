from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class BmgRegistration(models.Model):
    _name = 'bmg.registration'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Registration"
    _order = 'id desc'


    name = fields.Char('Name')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    gender = fields.Selection([('women','Women'),('men','Men')],string='Gender')
    address = fields.Text(string='Address')
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')], index=True,copy=False,default='draft',string='Status', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('bmg.registration.seq') or '/'
        return super(BmgRegistration, self).create(vals)

    def action_confirm(self):
        self.state = 'confirm'
    
    def action_cancel(self):
        self.state = 'cancel'

    def set_to_draft(self):
        self.state = 'draft'