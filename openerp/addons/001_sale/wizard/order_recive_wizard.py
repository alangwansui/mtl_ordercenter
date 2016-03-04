#! /usr/bin/python
# -*- coding:utf-8 -*-


from osv import  fields,osv
from tools.translate import _
import time
from datetime import datetime
class order_recive_wizard(osv.osv_memory):
    _name='order.recive.wizard'
    _columns={
        'name':fields.char(u'客户',readonly=False,size=16),
    }
    
   
    def creat_pcb_info(self,cr,uid,ids,context=None): 
        act_id=context.get('active_id')
        #obj=self.pool.get('crm.lead')
#        obj=self.pool.get(context.get('active_model'))
        obj=self.pool.get('order.recive')
        my=obj.browse(cr,uid,act_id)
        print my.sale_type,'type'
        print my.pcb_info_id,'pcb_info'
        
        if my.sale_type in ('new','revise') and not my.pcb_info_id:
            res_id=self.pool.get('pcb.info').create(cr,uid,{
                    'product_id':my.product_id.id,
                    'partner_id':my.partner_ids.id,
                    'responsible_id':uid,
            })
           
            
            return { 
                'name':_("Create new pcb info"),
                'view_type':'form',
                'view_mode':'form',
                'res_model':'pcb.info',
                'res_id':res_id,
                #'domain': [('partner_id','=',my.partner_id.id),('responsible_id','=',uid),('delivery_leadtime','=',delivery_leadtime)],
                #'context':context,
                'type':'ir.actions.act_window',
            }
            print res_id,'res_id'
        else:
            raise osv.except_osv(_('Error!'),_(u'订单类型必须是新单或者复投有更改，而且没有存在的用户单！'))
        
        
order_recive_wizard()

class lead_price_sheet(osv.osv_memory):
    _name='lead.price.sheet'
    _columns={
        'name':fields.char('name',readonly=False,size=16),
    }
    def transform_price_sheet(self,cr,uid,ids,context=None):
        act_id=context.get('active_id',False)
        #lead_obj=self.pool.get('crm.lead')
        lead_obj=self.pool.get(context.get('active_model'))
        lead=lead_obj.browse(cr,uid,act_id)
        if  lead.pcb_info_id :
            ps_id=self.pool.get('price.sheet').create(cr,uid,{
                'pcb_info_id':lead.pcb_info_id.id,
                'lead_id':act_id,
                'responsible_id':uid,
                'product_number':lead.product_number,
               
            })
          
            if ps_id:
                lead_obj.write(cr,uid,act_id,{'state':'done'})
                return{
                    'name':_('transform pcb info'),
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model':'price.sheet',
                    'type':'ir.actions.act_window',
                    'res_id':ps_id,
                    #'domain':[('res_id','=',ps_id)],  
                }
        else:
            raise osv.except_osv(_('Error!'),_('not pcb_info or state not done'))
lead_price_sheet()

