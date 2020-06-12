from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging


_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.payment_type == 'inbound' and self.journal_id.inbound_payment_method_ids or self.journal_id.outbound_payment_method_ids
            payment_methods_list = payment_methods.ids

            default_payment_method_id = self.env.context.get('default_payment_method_id')
            if default_payment_method_id:
                # Ensure the domain will accept the provided default value
                payment_methods_list.append(default_payment_method_id)
            else:
                self.payment_method_id = payment_methods and payment_methods[0] or False

            Params = self.env['ir.config_parameter'].sudo()
            customer_deposit_journal_id = Params.get_param('0043_customer_deposit.customer_deposit_journal_id') or False    
            if customer_deposit_journal_id:
                if int(customer_deposit_journal_id) == self.journal_id.id :
                    if self.is_deposit:
                        self.deposit_amount = self.partner_id.deposit_amount
                    else:
                        raise UserError("Cannot user deposit journal")

            Params = self.env['ir.config_parameter'].sudo()
            customer_overpay_journal_id = Params.get_param('0043_customer_deposit.customer_overpay_journal_id') or False    
            if customer_overpay_journal_id:
                if int(customer_overpay_journal_id) == self.journal_id.id:
                    self.is_overpay = True
                    self.overpay_amount = self.partner_id.overpay_amount
                    if self.amount > self.overpay_amount:
                        self.amount = self.overpay_amount
                else:
                    self.is_overpay = False
                    self.overpay_amount = 0.0

            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = self.payment_type in ('outbound', 'transfer') and 'outbound' or 'inbound'
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods_list)]}}
        return {}


    @api.onchange('payment_difference_handling')
    def _onchange_payment_difference_handling(self):
        if self.payment_difference_handling == 'overpay':
            Params = self.env['ir.config_parameter'].sudo()
            customer_overpay_account_id = Params.get_param('0043_customer_deposit.customer_overpay_account_id') or False
            self.writeoff_account_id = int(customer_overpay_account_id)
        else:
            self.writeoff_account_id = False

    def _create_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
            Return the journal entry.
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(amount, self.currency_id, self.company_id.currency_id)

        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)

        #Reconcile with the invoices
        if self.payment_difference_handling in ['reconcile','overpay'] and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            debit_wo, credit_wo, amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date)._compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo

        #Write counterpart lines
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            aml_obj.create(liquidity_aml_dict)

        #validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        #reconcile the invoice receivable/payable line(s) with the payment
        if self.invoice_ids:
            self.invoice_ids.register_payment(counterpart_aml)

        return move

    def _get_move_vals(self, journal=None):
        move_vals = super(AccountPayment, self)._get_move_vals()
        move_vals.update({'cust_deposit_id': self.customer_deposit_id.id})
        return move_vals

    

    # @api.onchange('journal_id')
    # def _onchange_journal(self):
    #     res = super(AccountPayment, self)._onchange_journal()
    #     if self.journal_id.is_deposit:
    #         values = {
    #             'is_deposit': True,
    #         }
    #         self.update(values)
    #     else:
    #         values = {
    #             'is_deposit': False,
    #         }
    #         self.update(values)
    #     return res

    is_deposit = fields.Boolean(
        string='Is Deposit',
        default = False,
    )
    
    deposit_amount = fields.Float("Deposit Balance", readonly=True)
    
    customer_deposit_id = fields.Many2one(
        string='Deposit #',
        comodel_name='customer.deposit',
    )
    
    payment_difference_handling = fields.Selection(selection_add=[('overpay','Overpay Account')])

    is_overpay = fields.Boolean('Is Overpay')

    overpay_amount = fields.Float("Overpay Balance", readonly=True)

 