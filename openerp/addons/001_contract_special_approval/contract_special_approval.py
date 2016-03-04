#!usr/bin/env python
# -*- coding: utf-8 -*-
from osv import fields,osv
import datetime
import pymssql
import sys
from tools.translate import _
reload(sys)  

class contract_special_approval(osv.osv):
    _name='contract.special.approval'
    _description='contract_special_approval infomation'
    _columns={
             'name':fields.char(u'特批单号',size=20,readonly=True),
             'sale_order_new_id':fields.many2one('sale.order.new',u'合同号',domain=[('state','=','draft')]),  
             'approval_date':fields.date(u'预计回签日期'),
             'response_id': fields.many2one('res.users',u'申请人', readonly=True),
             'partner_id':fields.related('sale_order_new_id','partner_id',type='many2one',relation="res.partners",string='客户',readonly=True),
             'amount_total':fields.related('sale_order_new_id','amount_total',type='float',string='金额',readonly=True),
             'note':fields.text(u'申请原因'),
             'master_note':fields.text(u'主管意见'),
             'state':fields.selection([('draft',u'草稿'),('wait_confirm',u'待主管审批'),('done',u'完成'),('cancel',u'作废')],u'状态')
             
             }
    _defaults={
               'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'contract.special.approval'),
               'state':'draft',
               'response_id':lambda self,cr,uid,c:uid,
               }
    def button_refuse(self,cr,uid,ids,context=None):
        info=self.browse(cr,uid,ids[0])
        if info.state=='done':
             raise osv.except_osv(_('Error!'),_(u'此单已经完成,不能作废!'))
        self.write(cr,uid,ids[0],{
                                  'state':'cancel'
                                  })
        return True
       
    def done(self,cr,uid,ids,context=None):
        sale_order_new_obj=self.pool.get("sale.order.new")
        info=self.browse(cr,uid,ids[0])
        sale_order_new_id=info.sale_order_new_id.id
        
        sale_order_new_state=info.sale_order_new_id.state
                
        sale_order_new_obj.write(cr,uid,sale_order_new_id,{
                                                           'state':'special_approval'
                                                           })
        return True
contract_special_approval()