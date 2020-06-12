from openerp.osv import osv, fields

class jakc_cust_deposit_report(osv.osv_memory):
    _name = 'jakc.cust.deposit.report'
    _description = 'Customer Deposit'

    _columns = {
        'start_date': fields.date('Start Date'),
        'end_date': fields.date('End Date'),
        'partner_ids': fields.many2many('res.partner', 'jak_cust_deposit_report_partner_rel', 'partner_id', 'wizard_id', 'Customers'),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
         To get the date and print the report
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return : retrun report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['start_date','end_date','partner_ids'], context=context)
        res = res and res[0] or {}
        datas['form'] = res
        if res.get('id',False):
            datas['ids']=[res['id']]
        return self.pool['report'].get_action(cr, uid, [], 'jakc_cust_deposit.report_custdeposit', data=datas, context=context)
