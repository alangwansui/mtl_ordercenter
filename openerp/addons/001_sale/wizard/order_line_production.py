# !/usr/bin/python
# -*- coding:utf-8 -*-

import time
from osv import osv,fields
from tools.translate  import _
import netsvc
import datetime
class order_line_production(osv.osv_memory):
    _name='wizard.production.count'
    _type_list=[('new','new'),('repeat','repeat'),('revise','revise')]
    
    def  _func_type(self,cr,uid,context=None):

        act_id=context.get('active_id',False)
        so_line=self.pool.get('sale.order.line').browse(cr,uid,act_id)
        res_type=so_line.price_sheet_id.lead_id.sale_type
        
        if  res_type == 'new' and  so_line.wait_production_count < so_line.product_uom_qty:
            res_type=order_line_production._type_list[1][0]
        return res_type
    
    _columns={
       'delivery_date':       fields.date('Sales order datetime'),
       'production_count':     fields.integer('Production count',),
       'type' :fields.selection(_type_list,'type', size=32, required=True,),
       'company_id':fields.many2one('res.company','company_id'),
    }
    _defaults={
       'delivery_date': lambda self,cr,uid,context:self.pool.get('sale.order.line').browse(cr,uid,context.get('active_id')).delivery_date,
       'production_count': lambda self,cr,uid,context:self.pool.get('sale.order.line').browse(cr,uid,context.get('active_id')).wait_production_count,
       'type':lambda self,cr,uid,context:self._func_type(cr,uid,context),
    }
    def convent_production_count(self,cr,uid,ids,context):
       
        act_id=context.get('active_id')
        mrp_obj=self.pool.get('mrp.production')
        line_obj=self.pool.get('sale.order.line')
        bom_obj=self.pool.get('mrp.bom')
        rout_obj=self.pool.get('mrp.routing')
        sheet_obj=self.pool.get('price.sheet')
        wkf_ser=netsvc.LocalService('workflow')
        
        my=self.browse(cr,uid,ids[0])
        production_count=my.production_count
        
        de_date=my.delivery_date.split('-')
        y,m,d=tuple(map(int,de_date))     
    
        order_line=line_obj.browse(cr,uid,act_id)
        wait_production_count=order_line.wait_production_count
        
        mark_list=[(i.label+'\n') for i in order_line.price_sheet_id.pcb_info_id.mark_request]
        mark_info=''+'\n'
        for i in mark_list:
            mark_info+=i
            
        if  production_count > wait_production_count:
            raise osv.except_osv(_('Error'),_('production_count cannot > wait_production_count')) 
        elif order_line.state == 'draft':
            raise osv.except_osv(_('Error'),_('draft sale order line cant be production')) 
        elif my.delivery_date > order_line.order_id.requested_date:
            raise osv.except_osv(_('Error'),_('Sale order:requested_date must be > order product:delivery_date'))
        else:
            if not order_line.product_id:
                sheet_obj.create_product_code(cr,uid,[order_line.price_sheet_id.id],line_id=act_id)
            order_line=line_obj.browse(cr,uid,act_id)
          
            res_id=mrp_obj.create(cr,uid,{ 
               'origin'        :order_line.price_sheet_id.name,
               'delivery_date' :my.delivery_date,
               'pre_start_date':str(datetime.date(y,m,d) - datetime.timedelta(days=order_line.price_sheet_id.standard_days)),
               'product_uom'   :order_line.product_id.uom_id.id,
               'product_id'    :order_line.product_id.id,
               'type'          :my.type,
               'location_src_id'  :28,
               'location_dest_id' :28,
               'sale_order_line_id':order_line.id,
               'sale_lots'      :self.pool.get('ir.sequence').get(cr, uid, 'sale.lots'),
               'delivery_count' :production_count,
               'partner_id'     :order_line.order_id.partner_id.id,
               'market_eng_required':mark_info,
               'via_sold_type':order_line.price_sheet_id.pcb_info_id.solder_via.id,
               'company_id':my.company_id.id,
            })
            if res_id: 
                wkf_ser.trg_validate(uid,'mrp.production',res_id,'button_approver',cr)
                if my.type in ['revise','repeat']:
                    bom_id=bom_obj.search(cr,uid,[('product_id','=',order_line.product_id.id)])
                    rout_id=rout_obj.search(cr,uid,[('product_id','=',order_line.product_id.id)])
                    ##update: bom_id,routing_id
                    if bom_id and rout_id:
                        mrp_obj.write(cr,uid,res_id,{'bom_id':bom_id[0],'routing_id':rout_id[0]})
                        
                    #else:
                    #    raise osv.except_osv(_('product error:bom_id and routing_id'),_('please create:product bom and routing!'))
                line_obj.write(cr,uid,act_id,{'wait_production_count':wait_production_count - production_count,})
                ##create one record of the input output statistics
                pcb_info=order_line.price_sheet_id.pcb_info_id
                inout_obj=self.pool.get('statistics.input.output').create(cr,uid,{
                    'production_id' :res_id,
                    'partner_id'    :order_line.order_id.partner_id.id,
                    'layer'         :pcb_info.layer_count,
                    'pcs_size_l'    :pcb_info.pcs_length,#单元尺寸L
                    'pcs_size_w'    :pcb_info.pcs_width,#单元尺寸W
                    'delivery_qty'  :production_count,
                    'delivery_date' :my.delivery_date,
                })
                
            ## return new production interface
            return{
                'name' :_('Convent mrp production'),
                'res_model':'mrp.production',
                'view_mode':'form',
                'view_type':'form',
                'type':'ir.actions.act_window',
                'domain':[],
                'res_id'  :res_id,
            }

    #===========================================================================
    # def get_wait_production_count(self,cr,uid,ids,context):
    #    line_obj=self.pool.get('sale.order.line')
    #    act_id=context.get('active_id',False)
    #    number= line_obj.read(cr,uid,act_id,['wait_production_count'])['wait_production_count']  or  0
    #    self.write(cr, uid, ids[0], {'production_count':number})
    #===========================================================================

order_line_production()

