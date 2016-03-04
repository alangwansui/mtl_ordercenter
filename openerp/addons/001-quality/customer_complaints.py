#!/usr/bin/python
# -*- coding: utf-8 -*-
from osv import fields, osv
import time
from tools.translate import _

class customer_complaints(osv.osv):
    _name='customer.complaints'
    _inherit='base.follow'
#    _state_list=[('draft',u'草稿'),('sale_manager',u'销售经理'), ('w_confirm',u'确认人'),('w_plan',u'待计划部'),('w_engineer',u'待工程部'),('w_quality',u'待品质部'),('w_order',u'待订单中心'),('w_sale',u'销售部'),('w_other',u'待其他'),('w_quality_manager','待品质部'),('sale_engineer',u'待销售工程师'),('w_gmanager',u'待总经办'),('done',u'完成')]
    _state_list=[('draft',u'草稿'),('sale_manager',u'销售经理'), ('w_confirm',u'确认人'),('w_quality_manager','待品质部'),('sale_engineer',u'待销售工程师'),('w_gmanager',u'待总经办'),('done',u'完成')]
    _columns={
        'name':                 fields.char(u'客诉单号',size=64,select=True,),#系统编号
        'date':                 fields.datetime(u'创建日期'),#单据日期
        'code':                 fields.char(u'编号',size=64,select=True),#编号
        'production_id':        fields.many2one('mrp.production.new','订单批次号',select=True,required=True),#投诉的订单批次号
        'partner_id':           fields.related('production_id','partner_id',type='char',relation='res.partners',string=u'客户',store=True,readonly=True,select=True),#客户代号
        'ref':                  fields.related('production_id','ref',type='char',relation='res.partners',string=u'客户代号',select=True,readonly=True,store=True),#客户代号
        'customer_name':        fields.related('production_id','customer_name',type='char',string=u'零件号',size=128,readonly=True,store=True),
        'product_id':           fields.related('production_id','product_id',type='char',string=u'档案号',size=128,readonly=True,store=True),
        'delivery_date':        fields.related('production_id','delivery_date',type='date',string=u'交货日期',readonly=True,store=True),
        'delivery_count':       fields.related('production_id','delivery_count',type='integer',string=u'交货数量',readonly=True,store=True),
        'ng_number':            fields.integer(u'不良数量'),
        'customer_number':      fields.integer(u'客户已贴片数量'),
        'customer_stock_number':fields.integer(u'客户库存数量'),
        'stock_quantity':       fields.integer(u'我司库存数量'),
        'online_quantity':      fields.integer(u'我司在线库存数量'),
        'return_goods':         fields.boolean(u'退货'),
        'replenish_goods':      fields.boolean(u'补货'),
        'repair_goods':         fields.boolean(u'修理'),
        'recive_goods':         fields.boolean(u'让步接收'),
        'other':                fields.boolean(u'其它'),
        'others':                fields.boolean(u'其它'),
        'one_day':                fields.boolean(u'一天'),
        'three_days':                fields.boolean(u'三天'),
        'really':                fields.boolean(u'属实非我司责任'),
        'really_one':                fields.boolean(u'属实我司责任'),
        'unreally':                fields.boolean(u'不属实'),
        'plan_dpt':                fields.boolean(u'生产计划部'),
        'eng_dpt':                fields.boolean(u'工程技术部'),
        'qulity_dpt':                fields.boolean(u'品质部'),
        'order_dpt':                fields.boolean(u'订单中心'),
        'sale_dpt':                fields.boolean(u'销售部'),
        'other_dpt':                fields.boolean(u'其它部门'),
        'customer_result':                fields.text(u'与客户联系结果'),
        'process_type':                fields.text(u'退货产品数量及处理方式'),   
        'stock_type':                fields.text(u'库存处理方式'),         
        'sale_manager':         fields.many2one('res.users',u'销售部经理'),
        'confirm_name':         fields.many2one('res.users',u'确认人'),
        'confirm_time':          fields.datetime(u'日期'),
        
        'dpt_id':               fields.many2one('res.department',u'申请部门'),#申请部门
        'user_id':              fields.many2one('res.users',u'申请人'),#申请人
        'request':              fields.char(u'要求措施',size=64),#要求措施
        'reply_time':           fields.integer(u'期限回复天数'),#限期回复天数
        'content':              fields.text(u'投诉内容'),#投诉内容
        'note':                 fields.text(u'验证'),#备注
        'finish_time':          fields.datetime(u'完成日期'),
        'require':                fields.boolean(u'需要'),
        'unrequire':                fields.boolean(u'不需要'),
        'project_note':         fields.text(u'客户满意情况'),
        'customer_complaints_lines':fields.one2many('customer.complaints.line','customer_complaints_id','客户投诉明细'),
        'state':                fields.selection(_state_list,'State', size=64, required=False, translate=True, readonly=True,select=True),
    }
    _defaults={
        'user_id': lambda self,cr,uid,ids: uid,
        'dpt_id':  lambda self,cr,uid,context:context.get('department_id'),
        'state':    lambda *a:'draft',
		'name':lambda s,cr,uid,c:s.pool.get('ir.sequence').get(cr,uid,'customer.complaints'),
		'date':lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),  
         }
    
    def update_name(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        
        self.write(cr,uid,ids,{'state':'w_confirm',
                              'confirm_name':uid,
                              'confirm_time':time.strftime('%Y-%m-%d %H:%M:%S'),
                                 })
        return True
    def update_line(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('customer.complaints.line')
        if my.customer_complaints_lines:
            obj.write(cr,uid,ids,{
                              'approve_name':uid,
                              'approve_time':time.strftime('%Y-%m-%d %H:%M:%S'),
                                 })
        return True
    
customer_complaints()








class customer_complaints_line(osv.osv):

    _name='customer.complaints.line'
    _description='Customer Complaints Line'

    _columns={
              
                'customer_complaints_id':fields.many2one('customer.complaints',u'客户投诉明细'),
                'dpt_name':fields.many2one('res.department',u'部门',readonly=True),
                'approve_time':             fields.datetime(u'确认日期',readonly=True), 
                'approve_name':             fields.many2one('res.users',u'确认人',readonly=True),
                'reason_report':            fields.text(u'原因分析'),
                'request_report':           fields.text(u'纠正措施'),
                'lead_report':              fields.text(u'预防措施'),
              
              }



customer_complaints_line()










        