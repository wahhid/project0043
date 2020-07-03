# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import date, datetime
from odoo.exceptions import Warning
from odoo import models, fields, exceptions, api, _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from xlrd import open_workbook
import xlrd
import os
import tempfile
import binascii
from xlwt import Workbook
import xlwt
import logging
_logger = logging.getLogger(__name__)
from io import StringIO
import io

try:
    import xmlrpclib
except ImportError:
    _logger.debug('Cannot `import xmlrpclib`.')

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
# for xls 
try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')

class gen_inv(models.TransientModel):
    _name = "gen.inv"

    file = fields.Binary('File')
    inv_name = fields.Char('Inventory Name')
    location_id = fields.Many2one('stock.location', "Location")
    import_option = fields.Selection([('csv', 'CSV File'),('xls', 'XLS File')],string='Select',default='csv')
    import_prod_option = fields.Selection([('barcode', 'Barcode'),('code', 'Code'),('name', 'Name')],string='Import Product By ',default='code')
    lot_option = fields.Boolean(string="Import Serial/Lot number with Expiry Date")
    location_id_option = fields.Boolean(string="Allow to Import Location on inventory line from file")
#    filename = fields.Char('Filename')

    @api.multi
    def import_csv(self):

        """Load Inventory data from the CSV file."""
        if self.import_option == 'csv': 
            """Load Inventory data from the CSV file."""
            if self.lot_option == True:
                if self.location_id_option == True:
                    keys=['code', 'quantity','UOM','lot','life_date','line_location_id'] 
                else:
                    keys=['code', 'quantity','UOM','lot','life_date']
            elif self.location_id_option == True:
                keys=['code', 'quantity','UOM','lot','line_location_id']
            else:
                keys=['code', 'quantity','UOM','lot'] 
            ctx = self._context
            stloc_obj = self.env['stock.location']
            inventory_obj = self.env['stock.inventory']
            product_obj = self.env['product.product']
            stock_lot_obj = self.env['stock.production.lot']
            csv_data = base64.b64decode(self.file)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=',')
            try:
                file_reader.extend(csv_reader)
            except Exception:
                raise exceptions.Warning(_("Invalid file!"))
            values = {}
            #actual_date = fields.Date.today()
            inventory_id = inventory_obj.create({'name':self.inv_name,'filter':'partial','location_id':self.location_id.id})
            for i in range(len(file_reader)):
                val = {}
                try:
                     field = list(map(str, file_reader[i]))
                except ValueError:
                     raise exceptions.Warning(_("Dont Use Charecter only use numbers"))
                
    #             field = reader_info[i]
                values = dict(zip(keys, field))
                if self.import_prod_option == 'barcode':
                    prod_lst = product_obj.search([('barcode',  '=',values['code'])]) 
                elif self.import_prod_option == 'code':
                    prod_lst = product_obj.search([('default_code', '=', values['code'])])
                else:
                    prod_lst = product_obj.search([('name', '=', values['code'])])         
                
                if self.lot_option == True:
                    if self.location_id_option == True:
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                            val['UOM'] = values['UOM']
                            val['lot'] = values['lot']
                            val['life_date'] = values['life_date']
                        if bool(val):
                            #product_uom_id=product_obj.browse(val['product']).uom_id
                            product_uom_obj = self.env['uom.uom']
                            product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                            if not product_uom_id:
                                raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                
                            stock_location_id = self.env['stock.location'].search([('name','=',values['line_location_id'])])
                            if not stock_location_id:
                                raise UserError(_('"%s" Location is not available.')%(values['line_location_id']))

                            lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                            for lot in lot_id:
                                lot_obj = stock_lot_obj.browse(lot_id)
                                
                            if not lot_id:
                                lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product'],
                                                        'life_date': val['life_date']})
                                lot_id = lot

                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : stock_location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                        else:
                            continue
                    else:
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                            val['UOM'] = values['UOM']
                            val['lot'] = values['lot']
                            val['life_date'] = values['life_date']
                        if bool(val):
                            #product_uom_id=product_obj.browse(val['product']).uom_id
                            product_uom_obj = self.env['uom.uom']
                            product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                            if not product_uom_id:
                                raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                
                            lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                            for lot in lot_id:
                                lot_obj = stock_lot_obj.browse(lot_id)
                                
                            if not lot_id:
                                lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product'],
                                                        'life_date': val['life_date']})
                                lot_id = lot

                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                        else:
                            continue
                else:
                    if self.location_id_option == True:
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                            val['UOM'] = values['UOM']
                            val['lot'] = values['lot']
                        if bool(val):
                            #product_uom_id=product_obj.browse(val['product']).uom_id
                            product_uom_obj = self.env['uom.uom']
                            product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                            if not product_uom_id:
                                raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                
                            stock_location_id = self.env['stock.location'].search([('name','=',values['line_location_id'])])
                            if not stock_location_id:
                                raise UserError(_('"%s" Location is not available.')%(values['line_location_id']))

                            lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                            for lot in lot_id:
                                lot_obj = stock_lot_obj.browse(lot_id)
                                
                            if not lot_id:
                                lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product']})
                                lot_id = lot

                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : stock_location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                        else:
                            continue 
                    else:   
                        if prod_lst:
                            val['product'] = prod_lst[0].id
                            val['quantity'] = values['quantity']
                            val['UOM'] = values['UOM']
                            val['lot'] = values['lot']
                        if bool(val):
                            #product_uom_id=product_obj.browse(val['product']).uom_id
                            product_uom_obj = self.env['uom.uom']
                            product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                            if not product_uom_id:
                                raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                
                            lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                            for lot in lot_id:
                                lot_obj = stock_lot_obj.browse(lot_id)
                                
                            if not lot_id:
                                lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product']})
                                lot_id = lot

                            res = inventory_id.write({
                        'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                        else:
                            continue 
            res = inventory_obj.with_context(ids=inventory_id).prepare_inventory()
            return res
        else:
            fp = tempfile.NamedTemporaryFile(delete= False,suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.file))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)
            inventory_id = self.env['stock.inventory'].create({'name':self.inv_name,'filter':'partial','location_id':self.location_id.id})
            product_obj = self.env['product.product']
            stock_lot_obj = self.env['stock.production.lot']
            for row_no in range(sheet.nrows):
                val = {}
                if row_no <= 0:
                    fields = list(map(lambda row:row.value.encode('utf-8'), sheet.row(row_no)))
                else:
                    line = list(map(lambda row:isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value), sheet.row(row_no)))
                    if self.lot_option == True:
                        if self.location_id_option == True:
                            if line:
                                values.update({'code':line[0],'quantity':line[1],'UOM':line[2],'lot':line[3],'life_date':line[4],'line_location_id':line[5]})
                                a1 = int(float(line[4]))
                                a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                                date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                                if self.import_prod_option == 'barcode':
                                    prod_lst = product_obj.search([('barcode',  '=',values['code'])])
                                elif self.import_prod_option == 'code':
                                    prod_lst = product_obj.search([('default_code', '=', values['code'])])
                                else:
                                    prod_lst = product_obj.search([('name', '=', values['code'])])            
                                if prod_lst:
                                    val['product'] = prod_lst[0].id
                                    val['quantity'] = values['quantity']
                                    val['UOM'] = values['UOM']
                                    val['lot'] = values['lot']
                                    val['life_date'] = date_string
                                if bool(val):
                                    #product_uom_id=product_obj.browse(val['product']).uom_id
                                    product_uom_obj = self.env['uom.uom']
                                    product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                                    if not product_uom_id:
                                        raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                        
                                    stock_location_id = self.env['stock.location'].search([('name','=',values['line_location_id'])])
                                    if not stock_location_id:
                                        raise UserError(_('"%s" Location is not available.')%(values['line_location_id']))

                                    lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                                    for lot in lot_id:
                                        lot_obj = stock_lot_obj.browse(lot_id)
                                
                                    if not lot_id:
                                        lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product'],
                                                              'life_date': date_string})
                                        lot_id = lot
                                        
                                    res = inventory_id.write({
                                'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : stock_location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                                else:
                                    continue
                        else:
                            if line:
                                values.update({'code':line[0],'quantity':line[1],'UOM':line[2],'lot':line[3],'life_date':line[4]})
                                a1 = int(float(line[4]))
                                a1_as_datetime = datetime(*xlrd.xldate_as_tuple(a1, workbook.datemode))
                                date_string = a1_as_datetime.date().strftime('%Y-%m-%d')
                                if self.import_prod_option == 'barcode':
                                    prod_lst = product_obj.search([('barcode',  '=',values['code'])])
                                elif self.import_prod_option == 'code':
                                    prod_lst = product_obj.search([('default_code', '=', values['code'])])
                                else:
                                    prod_lst = product_obj.search([('name', '=', values['code'])])            
                                if prod_lst:
                                    val['product'] = prod_lst[0].id
                                    val['quantity'] = values['quantity']
                                    val['UOM'] = values['UOM']
                                    val['lot'] = values['lot']
                                    val['life_date'] = date_string
                                if bool(val):
                                    #product_uom_id=product_obj.browse(val['product']).uom_id
                                    product_uom_obj = self.env['uom.uom']
                                    product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                                    if not product_uom_id:
                                        raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                        
                                    lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                                    for lot in lot_id:
                                        lot_obj = stock_lot_obj.browse(lot_id)
                                
                                    if not lot_id:
                                        lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product'],
                                                              'life_date': date_string})
                                        lot_id = lot
                                        
                                    res = inventory_id.write({
                                'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                                else:
                                    continue
                    else:
                        if self.location_id_option == True:
                            if line:
                                values.update({'code':line[0],'quantity':line[1],'UOM':line[2],'lot':line[3],'line_location_id':line[4]})
                                if self.import_prod_option == 'barcode':
                                    prod_lst = product_obj.search([('barcode',  '=',values['code'])])
                                elif self.import_prod_option == 'code':
                                    prod_lst = product_obj.search([('default_code', '=', values['code'])])
                                else:
                                    prod_lst = product_obj.search([('name', '=', values['code'])])            
                                if prod_lst:
                                    val['product'] = prod_lst[0].id
                                    val['quantity'] = values['quantity']
                                    val['UOM'] = values['UOM']
                                    val['lot'] = values['lot']
                                if bool(val):
                                    #product_uom_id=product_obj.browse(val['product']).uom_id
                                    product_uom_obj = self.env['uom.uom']
                                    product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                                    if not product_uom_id:
                                        raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                        
                                    stock_location_id = self.env['stock.location'].search([('name','=',values['line_location_id'])])
                                    if not stock_location_id:
                                        raise UserError(_('"%s" Location is not available.')%(values['line_location_id']))

                                    lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                                    for lot in lot_id:
                                        lot_obj = stock_lot_obj.browse(lot_id)
                                
                                    if not lot_id:
                                        lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product']})
                                        lot_id = lot
                                        
                                    res = inventory_id.write({
                                'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : stock_location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                                else:
                                    continue 
                        else:
                            if line:
                                values.update({'code':line[0],'quantity':line[1],'UOM':line[2],'lot':line[3]})
                                if self.import_prod_option == 'barcode':
                                    prod_lst = product_obj.search([('barcode',  '=',values['code'])])
                                elif self.import_prod_option == 'code':
                                    prod_lst = product_obj.search([('default_code', '=', values['code'])])
                                else:
                                    prod_lst = product_obj.search([('name', '=', values['code'])])            
                                if prod_lst:
                                    val['product'] = prod_lst[0].id
                                    val['quantity'] = values['quantity']
                                    val['UOM'] = values['UOM']
                                    val['lot'] = values['lot']
                                if bool(val):
                                    #product_uom_id=product_obj.browse(val['product']).uom_id
                                    product_uom_obj = self.env['uom.uom']
                                    product_uom_id = product_uom_obj.search([('name','=',val['UOM'])])
                                    if not product_uom_id:
                                        raise UserError(_('"%s" Product UOM category is not available.')%(val['UOM'] ))
                                        
                                    lot_id = stock_lot_obj.search([('product_id','=',val['product']),('name','=',val['lot'])])
                                    for lot in lot_id:
                                        lot_obj = stock_lot_obj.browse(lot_id)
                                
                                    if not lot_id:
                                        lot = stock_lot_obj.create({'name': val['lot'],
                                                      'product_id': val['product']})
                                        lot_id = lot
                                        
                                    res = inventory_id.write({
                                'line_ids': [(0, 0, {'product_id':val['product'] , 'location_id' : self.location_id.id, 'product_uom_id' : product_uom_id.id  ,'product_qty': val['quantity'],'prod_lot_id':lot_id.id})]})
                                else:
                                    continue                            
            res = self.env['stock.inventory'].with_context(ids=inventory_id).prepare_inventory()
            return res

class stock_inventory(models.Model):
    _inherit = "stock.inventory"


    @api.multi
    def action_start(self):
        if self._context.get('ids'):
            self = self._context.get('ids')
            for inventory in self:
                vals = {'state': 'confirm', 'date': fields.Datetime.now()}
                if (inventory.filter != 'partial') and not inventory.line_ids:
                    vals.update({'line_ids': [(0, 0, line_values) for line_values in inventory.line_ids]})
                    inventory.write(vals)
        else:
            super(stock_inventory, self).action_start()
        return True
    prepare_inventory = action_start

