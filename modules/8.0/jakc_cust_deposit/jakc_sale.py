from openerp.osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def onchange_partner_id_2(self, cr, uid, ids, part, iface_deposit, cust_deposit_id,  context=None):
        cust_deposit_obj = self.pool.get('cust.deposit')
        cust_deposit_partner_obj = self.pool.get('cust.deposit.partner')

        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False, 'payment_term': False,
                              'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        deposit = self.pool.get('cust.deposit').browse(cr, uid, cust_deposit_id, context=context)

        if iface_deposit:
            pricelist = deposit.pricelist_id.id or False

        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'user_id': dedicated_salesman,
        }

        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False,
                                                      context=context)
        val.update(delivery_onchange['value'])

        if pricelist:
            val['pricelist_id'] = pricelist

        if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
            val['section_id'] = part.section_id.id

        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)

        if sale_note:
            val.update({'note': sale_note})

        cust_deposit_partner_ids = cust_deposit_partner_obj.search(cr, uid, [('partner_id','=',part.id)], context=context)
        if cust_deposit_partner_ids:
            return {'warning': {'title':'Information', 'message':'Deposit available for this customer!',},'value': val}
        else:
            return {'value': val}


    def onchange_cust_deposit_id(self, cr, uid, ids,  cust_deposit_id, context=None):
        res = {}
        pricelist_ids = []
        cust_deposit_obj = self.pool.get('cust.deposit')
        cust_deposit = cust_deposit_obj.browse(cr, uid, cust_deposit_id, context=context)
        #res['value'] = {'pricelist_id': cust_deposit.pricelist_id.id}
        return {'value': {'pricelist_id': cust_deposit.pricelist_id}}

    def onchange_iface_deposit(self, cr, uid, ids, iface_deposit, partner_id, context=None):
        res = {}
        cust_deposit_ids = []
        if iface_deposit:
            cust_deposit_partner_obj = self.pool.get('cust.deposit.partner')
            args = [('partner_id','=', partner_id)]
            cust_deposit_partner_ids = cust_deposit_partner_obj.search(cr, uid, args, context=context)
            cust_deposit_partners = cust_deposit_partner_obj.browse(cr, uid, cust_deposit_partner_ids, context=context)
            for cust_deposit_partner in cust_deposit_partners:
                if cust_deposit_partner.cust_deposit_id.state == 'open':
                    cust_deposit_ids.append(cust_deposit_partner.cust_deposit_id.id)
            res['domain'] = {'cust_deposit_id': [('id', 'in', cust_deposit_ids)]}
        else:
            res = self.onchange_partner_id_2(cr, uid, ids, partner_id, iface_deposit, False, context=context)
        return res
        
    _columns = {
        'iface_deposit': fields.boolean('Harga Deposit'),
        'cust_deposit_id': fields.many2one('cust.deposit','Nama Deposit'),
        'rest_amount': fields.related('cust_deposit_id','rest_amount', type="float", string="Sisa Saldo", readonly=True),
    }

sale_order()