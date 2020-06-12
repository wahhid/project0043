# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_auto_posted = fields.Boolean('Auto Posted', default=False)
    
    customer_deposit_journal_id = fields.Many2one(
        string='Customer Deposit Journal',
        comodel_name='account.journal',
        config_parameter='0043_customer_deposit.customer_deposit_journal_id',
        oldname='customer_deposit_journal_id',
    )
    
    
    customer_deposit_account_id = fields.Many2one(
        string='Customer Deposit Account',
        comodel_name='account.account',
        config_parameter='0043_customer_deposit.customer_deposit_account_id',
        oldname='customer_deposit_account_id',
    )


    customer_overpay_journal_id = fields.Many2one(
        string='Customer Overpay Journal',
        comodel_name='account.journal',
        config_parameter='0043_customer_deposit.customer_overpay_journal_id',
        oldname='customer_overpay_journal_id',
    )
    
    
    customer_overpay_account_id = fields.Many2one(
        string='Customer Overpay Account',
        comodel_name='account.account',
        config_parameter='0043_customer_deposit.customer_overpay_account_id',
        oldname='customer_overpay_account_id',
    )
    
    

    # @api.model
    # def get_values(self):
    #     res = super(ResConfigSettings, self).get_values()

    #     Param = self.env['ir.config_parameter'].sudo()
    #     res['customer_deposit_journal_id'] = Param.get_param('0043_customer_deposit.customer_deposit_account_id')
    #     res['customer_deposit_account_id'] = Param.get_param('0043_customer_deposit.customer_deposit_account_id')
    #     res['customer_overpay_journal_id'] = Param.get_param('0043_customer_deposit.customer_overpay_journal_id') 
    #     res['customer_overpay_account_id'] = Param.get_param('0043_customer_deposit.customer_overpay_account_id')
        
    #     return res

    # @api.model
    # def set_values(self):
    #     super(ResConfigSettings, self).set_values()
    #     Param = self.env['ir.config_parameter'].sudo()
    #     Param.set_param('0043_customer_deposit.customer_deposit_journal_id', self.customer_deposit_journal_id)
    #     Param.set_param('0043_customer_deposit.customer_deposit_account_id', self.customer_deposit_account_id)
    #     Param.set_param('0043_customer_deposit.customer_overpay_journal_id', self.customer_overpay_journal_id)
    #     Param.set_param('0043_customer_deposit.customer_overpay_account_id', self.customer_overpay_account_id)


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()

        Param = self.env['ir.config_parameter'].sudo()
        res['is_auto_posted'] = Param.get_param('0043_customer_deposit.is_auto_posted')
        
        return res

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()

        Param = self.env['ir.config_parameter'].sudo()
        Param.set_param('0043_customer_deposit.is_auto_posted', self.is_auto_posted)