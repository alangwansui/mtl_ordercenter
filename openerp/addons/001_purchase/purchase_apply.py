#! usr/bin/python
# -*- coding:utf-8 -*-

from datetime import datetime

from osv import fields,osv
from tools.translate import _

class purchase_apply(osv.osv):
    _name='purchase.apply'
    _description='Purchase Apply'

    _columns={
              'name':fields.char(u'申请单号',size=128),
              'product_id':fields.many2one('product.new',u'物料名称'),
              'responsible_name':fields.many2one('res.users',u'申请人',readonly=True),
              'type':fields.selection([('normal',u'普通类'),('unnormal',u'固定资产类')],string=u'请购类型',required=True),
              'dpt_name':fields.many2one('res.department',u'申请部门'),
              'apply_date':fields.datetime(u'申请日期'),
              'request_date':fields.date(u'需求日期'),
              'state':fields.selection([('draft',u'草稿'),('done',u'完成')],string=u'状态',readonly=True),
              'purchase_apply_line_ids':fields.one2many('purchase.apply.line','purchase_apply_ids',u'申请明细'),
              }
    _defaults = {
                 
                 'responsible_name':lambda obj, cr, uid, context: uid,
                 
                 
                 }
purchase_apply()
              
              
class purchase_apply_line(osv.osv):
    _name='purchase.apply.line'
    _description='Purchase apply line'
              
              
    _columns={
              'purchase_apply_ids':fields.many2one('purchase.apply','purchase_apply_ids'),
              'product_id':fields.many2one('product.new',u'物料名称'),
              'quantity':fields.float(u'数量'),
              'unit':fields.many2one('unit.info',u'单位'),
              'note':fields.char(u'备注',size=256),
              'stock_qty':fields.float(u'现有库存数',readonly=True),
              
              
              
              }
              
         
         
purchase_apply_line()    