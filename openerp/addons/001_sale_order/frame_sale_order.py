#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import openerp.addons.decimal_precision as dp
from osv import fields,osv
import datetime
import pymssql
import sys
from tools.translate import _
reload(sys)  
sys.setdefaultencoding('utf8')



class frame_sale_order(osv.osv):
    _name="frame.sale.order"
    _description="frame sale order"
    _columns={
              'name':fields.char(u'编号',size=32,readonly=True),
              'partner_id':fields.many2one('res.partners',u'客户',required=True),
              'partner_code':fields.related('partner_id','partner_code',type='char',string='客户代号',relation="res.partners",readonly=True),
              'quality_agreement':fields.boolean(u'质量保证协议'),
              'environment_agreement':fields.boolean(u'环保协议'),
              'technology_agreement':fields.boolean(u'技术协议'),
              'confidentiality_agreement':fields.boolean(u'保密协议'),
              'integrity_agreement':fields.boolean(u'廉洁协议'),
              'pcn_agreement':fields.boolean(u'PCN更改协议'),
              'sale_order_agreement':fields.boolean(u'订单协议'),
              'cooperation_agreement':fields.boolean(u'框架合作协议'),
              'state':fields.selection([('draft',u'草稿'),('wait_director',u'待主管'),('wait_master',u'待总监'),('done',u'完成')],string=u'状态'),
              }
    
    _defaults={
               'state':'draft',
#               'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'frame.sale.order'),
               'name':lambda obj, cr, uid, context:'/',
               }
    
    _sql_constraints = [
        ('partner_id', 'unique (partner_id)', '客户不能重复，请检查!'),]
    
    
    def create(self,cr,uid,vals,context=None):
          
          if vals.get('name','/')=='/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'frame.sale.order') or '/'
          id=super(frame_sale_order,self).create(cr,uid,vals,context=context)
          return id 
      
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
                if not args:
                    args = []
                args = args[:]
                ids = []
                if name:
                    ids = self.search(cr, user, [('default_code', 'ilike', name)]+args, limit=limit, context=context)
                    if not ids:
                        ids = self.search(cr, user, [('partner_code', 'ilike', name)]+ args, limit=limit, context=context)
                    if not ids:
                        ids = self.search(cr, user, [('partner_ids', operator, name)]+ args, limit=limit, context=context)
                else:
                    ids = self.search(cr, user, args, limit=limit, context=context)
                return self.name_get(cr, user, ids, context=context)
frame_sale_order()