from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class BmgAppointment(models.Model):
    _name= 'bmg.appointment'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = "Appointment"
    _order = 'id desc'

    appointment_sequence = fields.Char(string='Appointment Sequence')
    appointment_name = fields.Char(string='Appointment Name')
    date_appointment = fields.Date(string='Date Appointment')
    time_appointment = fields.Float(string='Time Appointment')
    duration_appoinment =fields.Integer(string='Duration Appoinment')
    private_appointment = fields.Boolean(string='Private Appointment')
    appointment_type = fields.Selection([('person','Person'),('umkm','UMKM'),('small company','Small Company'),('big company','Big Company'),('other','Other')],string='Appointment Type')
    company_name = fields.Char(string='Company Name')
    company_contacts = fields.Many2one('res.partner',string='Company Contacts')
    company_phone = fields.Char(string='Company Phone')
    company_email =  fields.Char(string='Company Email')
    person_name = fields.Char(string='Person Name')
    person_contacts = fields.Many2one('res.partner',string='Person Contacts')
    person_phone = fields.Char(string='Person Phone')
    person_email = fields.Char(string='Person Email')
    employee_in_charge = fields.Many2one('hr.employee',string='Employee in Charge to Consult')
    state = fields.Selection([('new','New'),('ongoing','Ongoing'),('done','Done'),('cancel','Cancel')],default='new',string='Status')
    client_ids = fields.One2many('res.partner','client_id')
    descriptions = fields.Text('Description')

    @api.constrains('date_appointment')
    def check_date_appointment(self):
        date_appointment = datetime.strftime()
        days_name = date.today().strftime("%A")
        print('days_name constrain..',days_name)
        if days_name in ('Saturday','Sunday'):
            raise UserError(_('Cannot fill weekend')) 
        

    @api.model
    def create(self, vals):
        if vals.get('appointment_sequence', 'New') == 'New':
            vals['appointment_sequence'] = self.env['ir.sequence'].next_by_code('bmg.appointment.seq') or '/'
        return super(BmgAppointment, self).create(vals)

class ResParnter(models.Model):
    _inherit = 'res.partner'

    client_id = fields.Many2one('bmg.appointment',"Appointment")