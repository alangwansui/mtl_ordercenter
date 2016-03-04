#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime
from tools.translate import _

class mrp_production_new(osv.osv):
    _name='mrp.production.new'
    _description='MRP Production New'
    _type_list=[('new',u'新单'),('repeat',u'复投无更改'),('revise',u'复投有更改'),('eng_panel',u'工程分卡')]
    _columns={
              
        'name':     fields.char(u'生产单号', size=64, readonly=True),
        'sale_order_line_new_id':fields.many2one('sale.order.new.line',u'订单批次号'),
        'order_create_date':fields.datetime(u'投产日期'),
        'delivery_date':fields.date(u'交货日期'),
        'delivery_count':fields.integer(u'交货数量'),
        'product_qty':fields.integer(u'投入数量'),
        'panel_count':fields.integer(u'PNL数量'),
        'pcs_count':fields.integer(u'pcs数量'),
        'customer_name':fields.char(u'客户零件号',size=64),
        'product_id':fields.char(u'档案号',size=32,readonly=True),
        'sale_order_new_ids':fields.char(u'合同号',size=32,readonly=True),
      
        'price_sheet_id':fields.related('sale_order_line_new_id','price_sheet_id',type='many2one',relation='price.sheet',string=u'报价单号',readonly=True,store=True),
        'pcb_info_id':fields.related('price_sheet_id','pcb_info_id',type='many2one',relation='pcb.info',string=u'用户单号',readonly=True,store=True),
        'layer_count':fields.integer(u'层数',readonly=True,),
        'so_user_id':fields.many2one('res.users',u'下单人',readonly=True),
        'standard_days':fields.integer(u'标准天数',readonly=True),
        'partner_id'   :fields.char( u'客户',size=64,readonly=True),
        'ref':fields.char(u'客户代号',size=32,readonly=True),
        'cam_id':fields.many2one('res.users',u'接单人',),
        'type' :fields.selection(_type_list,u'投产类型', size=32,),
        'urgent_type':fields.many2one('select.selection',u'加急类型',domain=[('type','=','urgent_type')]),#加急方式：
        'company_id':fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂')],string=u'投产工厂'),
        'state':fields.selection([('draft',u'待计划投产'),('eng_recive',u'待工程接单')],u'单据状态'),
        
        }
    
    _defaults={
        'state':'draft',
        'so_user_id':lambda self,cr,uid,c:uid,
        'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'mrp.production.new'),
        'order_create_date':fields.date.context_today,
        }
 
    


		
		
		
		
		
mrp_production_new()










