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
             'sale_order_new_id':fields.many2one('sale.order.new',u'合同号',domain=[('state','=','wait_sign_back')]),  
             'approval_date':fields.date(u'预计回签日期'),
             'response_id': fields.many2one('res.users',u'申请人', readonly=True),
             'partner_id':fields.related('sale_order_new_id','partner_id',type='many2one',relation="res.partners",string='客户',readonly=True),
             'amount_total':fields.related('sale_order_new_id','amount_total',type='float',string='金额',readonly=True),
             'note':fields.text(u'申请原因'),
             'master_note':fields.text(u'主管意见'),
             'state':fields.selection([('draft',u'草稿'),('wait_confirm',u'待主管审批'),('done',u'完成'),('cancel',u'作废')],u'状态')
             
             }
    _defaults={
#               'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'contract.special.approval'),
               'name':lambda obj, cr, uid, context:'/',
               'state':'draft',
               'response_id':lambda self,cr,uid,c:uid,
               }
    
    def create(self,cr,uid,vals,context=None):
          
          if vals.get('name','/')=='/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'contract.special.approval') or '/'
          id=super(contract_special_approval,self).create(cr,uid,vals,context=context)
          return id 

    def button_refuse(self,cr,uid,ids,context=None):
        info=self.browse(cr,uid,ids[0])
        if info.state=='done':
             raise osv.except_osv(_('Error!'),_(u'此单已经完成,不能作废!'))
        self.write(cr,uid,ids[0],{
                                  'state':'cancel'
                                  })
        return True
    
    def unlink(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state!='draft':
               raise osv.except_osv(_('Error!'),_(u'不是草稿状态，不能删除，请检查！'))  
        return unlink(self,cr,uid,ids)

    def button_approve(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state=='draft':
            self.write(cr,uid,ids[0],{'state':'wait_confirm'})
        if my.state=='wait_confirm':
            if my.amount_total<3000:
                self.write(cr,uid,ids[0],{'state':'done'})
                self.done(cr,uid,ids,context=None)
            if my.amount_total<8000 and my.amount_total>=3000:
                self.write(cr,uid,ids[0],{'state':'wait_sale_manager'})
        if my.state=='wait_sale_manager':
            if my.amount_total<8000 and my.amount_total>=3000:
                 self.write(cr,uid,ids[0],{'state':'done'})
                 self.done(cr,uid,ids,context=None)
            if my.amount_total>=8000:
                self.write(cr,uid,ids[0],{'state':'wait_manager'})
        if my.state=='wait_manager':
             self.write(cr,uid,ids[0],{'state':'done'})
             self.done(cr,uid,ids,context=None)
        return True


    def done(self,cr,uid,ids,context=None):
        sale_order_new_obj=self.pool.get("sale.order.new")
        sale_order_new_line_obj=self.pool.get("sale.order.new.line")
        sheet_obj=self.pool.get('price.sheet') 
        info=self.browse(cr,uid,ids[0])
        sale_order_new_id=info.sale_order_new_id.id 
        
        sale_order_new_state=info.sale_order_new_id.state
        
        line_ids=sale_order_new_line_obj.search(cr,uid,[('sale_order_new_id','=',sale_order_new_id)]) 
         
                     
       # sale_order_new_line_obj.write(cr,uid,line_ids,{
        #                                                   'state':'wait_confirm'
        #                                                   })
        for line_id in line_ids:
            line_info=sale_order_new_line_obj.browse(cr,uid,line_id)
            sheet_obj.create_product_code(cr,uid,[line_info.price_sheet_id.id],line_id=None)
            sheet_info=sheet_obj.browse(cr,uid,line_info.price_sheet_id.id)
            sale_order_new_line_obj.write(cr,uid,line_id,{
                                                           'state':'wait_confirm',
                                                           'product_id':sheet_info.product_id,
                                                           })
        
        sale_order_new_obj.write(cr,uid,sale_order_new_id,{
                                                           'state':'special_approval'
                                                           })
        return True
contract_special_approval()