
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.tools.translate import _
import logging



_logger = logging.getLogger(__name__)

class invoice(osv.osv):
    _inherit = 'account.invoice'

    def _get_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id


    def invoice_pay_customer(self, cr, uid, ids, context=None):
        _logger.warning('invoice_pay_customer')
        inv = self.browse(cr, uid, ids[0], context=context)
        partner_id = inv.partner_id.id
        wizard = super(invoice, self).invoice_pay_customer(cr, uid, ids, context=context)
        _logger.info("invoice pay customer")
        _logger.info(wizard)
        if len(inv.sale_ids) == 1:
            if inv.sale_ids[0].iface_deposit:
                wizard['context']['default_journal_id'] = self._get_company(cr, uid, context=context).deposit_journal_id.id
                wizard['context']['default_cust_deposit_id'] = inv.sale_ids[0].cust_deposit_id.id
                wizard['context']['default_iface_deposit'] = True
        _logger.info(wizard)
        return wizard