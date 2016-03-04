#! usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime

from osv import fields,osv
from tools.translate import _

class supplier_product(osv.osv):
    _name='supplier.product'
    _description='Supplier Product'
    _rec_name='product_id'
    _columns={
              
              'product_id':fields.many2one('product.new',u'我司物料名称'),
              'supplier_id':fields.many2one('vendor',u'供应商'),
              'supplier_name':fields.char(u'供应商物料名称',size=256),
              'responsible_name':fields.many2one('res.users',u'创建人'),
              }
    _defaults = {
                 
                 'responsible_name':lambda obj, cr, uid, context: uid,
                 
                 
                 }
supplier_product()
              
              
              
              
              
              