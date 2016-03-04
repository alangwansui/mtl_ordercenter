#! /usr/bin/python
# -*- coding:utf-8 -*-


import time
from osv import osv,fields
from tools.translate  import _
import netsvc
import datetime
import pymssql

server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'



class sale_order_new_line_wizard(osv.osv_memory):
    _name='sale.order.new.line.wizard'
    _type_list=[('new','新单'),('repeat','复投无更改'),('revise','复投有更改')]
    
    def  _func_type(self,cr,uid,context=None):

        act_id=context.get('active_id',False)
        so_line=self.pool.get('sale.order.new.line').browse(cr,uid,act_id)
        res_type=so_line.price_sheet_id.lead_id.sale_type
        
        if  res_type == 'new' and  so_line.wait_production_count < so_line.product_qty:
            res_type=sale_order_new_line_wizard._type_list[1][0]
        return res_type
    
    
    
    _columns={

        'delivery_date':fields.date(u'交货日期'),
        'count':fields.integer(u'投产数量'),
        'store_qty':fields.integer(u'库存unit数'),
        'type' :fields.selection(_type_list,u'投产类型', size=32, required=True,),
        'company_name':fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂')],string=u'投产工厂'),
        'memo':fields.text(u'投产备注'),
        }
    _defaults={
       'delivery_date': lambda self,cr,uid,context:self.pool.get('sale.order.new.line').browse(cr,uid,context.get('active_id')).delivery_date,
       'count': lambda self,cr,uid,context:self.pool.get('sale.order.new.line').browse(cr,uid,context.get('active_id')).wait_production_count,
       'type':lambda self,cr,uid,context:self._func_type(cr,uid,context),
       'company_name':'szmtl',
       'store_qty':0,
    }
   
    def create_mrp_production_info(self,cr,uid,ids,context=None): 
        
        act_id=context.get('active_id')
        mrp_obj=self.pool.get('mrp.production.new')
        line_obj=self.pool.get('sale.order.new.line')
        sale_order_obj=self.pool.get('sale.order.new')
        user_obj=self.pool.get('res.users')
        sheet_obj=self.pool.get('price.sheet')
        my=self.browse(cr,uid,ids[0])
        production_count=my.count
        de_date=my.delivery_date.split('-')
        y,m,d=tuple(map(int,de_date))     
        order_line=line_obj.browse(cr,uid,act_id)
        wait_production_count=order_line.wait_production_count
        obj=mrp_obj.search(cr,uid,[('sale_order_new_line_id','=',order_line.id),('state','!=','cancel')])
        sale_order_info=sale_order_obj.browse(cr,uid,order_line.sale_order_new_id.id)
        
        print sale_order_info.state,'sale_order_info.state'
        if sale_order_info.state not in['done','special_approval']:
            print sale_order_info.state,'sale_order_info.state'
            raise osv.except_osv(_('Error'),_(u'合同既没有回签,也没有特批,不能投产,请检查!'))
        

        if obj:
            mrp_info=mrp_obj.browse(cr,uid,obj[-1])
            if mrp_info.company_name!=my.company_name:
                raise osv.except_osv(_('Error'),_(u'同一个合同不能投产不同的工厂，请检查!'))
            if my.type=='new':
                raise osv.except_osv(_('Error'),_(u'此订单批次已经投过产,投产类型不允许选新单类型!')) 
            
            
 #       if  production_count == wait_production_count:
#            line_obj.write(cr,uid,act_id,{'state':'done'})
        
        if  production_count > wait_production_count:
            raise osv.except_osv(_('Error'),_(u'投产数量不能大于待投产数量!'))
       
        elif  production_count <=0:
            raise osv.except_osv(_('Error'),_(u'投产数量必须大于0!'))

        elif my.delivery_date > order_line.delivery_date:
            raise osv.except_osv(_('Error'),_('投产交货日期不能晚于合同交货日期'))

        else:
            if not order_line.product_id:
                sheet_obj.create_product_code(cr,uid,[order_line.price_sheet_id.id],line_id=act_id)
                
            info_id=mrp_obj.create(cr,uid,{ 
               'sale_order_new_line_id':order_line.id,
               'delivery_date' :my.delivery_date,
               'type'          :my.type,
               'delivery_count':production_count,
               'product_qty':production_count,
               'sale_order_new_ids':order_line.sale_order_new_id.name,
               'partner_id':order_line.sale_order_new_id.partner_id.name,
               'ref':order_line.sale_order_new_id.partner_id.partner_code,
               'layer_count':order_line.price_sheet_id.pcb_info_id.layer_count,
               'standard_days':order_line.price_sheet_id.standard_days,
               'product_id':order_line.product_id,
               'company_name':my.company_name,
               'store_qty':my.store_qty,
               'memo':my.memo,
               })  
  
            print info_id,'info_id'
            total=0
            for i in obj :
                line=mrp_obj.browse(cr,uid,i).delivery_count
                total=total+line
            total_count=total + my.count
            wait_total=wait_production_count - total_count + total
            print wait_total,'wait_total'
          #  if order_line.product_qty < total_count:
           #     raise osv.except_osv(_('Error'),_(u'投产数量不能大于待投产数量!'))
            line_obj.write(cr,uid,act_id,{'wait_production_count':wait_total})
            ####如果待投产数据为0则更新接单的状态为完成
            if wait_total==0:
                order_recive_id=order_line.price_sheet_id.lead_id.id
                self.pool.get('order.recive').write(cr,uid,order_recive_id,{'state':'done'})
                line_obj.write(cr,uid,act_id,{'state':'done'})
           #----------调用东烁投产的存储过程---------------
           # try:
           #     mrp_info=mrp_obj.browse(cr,uid,info_id)
           #     print '111111'
          #      user_info=user_obj.browse(cr,uid,uid)
          #      print '2222222'
          #      conn=pymssql.connect(server=server,user=user,password=password,database=database)  
         #       print '3333333'
          #      cur=conn.cursor()  
          #      sql_fetch_billsubcode=''' select billsubcode,id from TCContractS where batchcode='%s' ''' %(order_line.name)
         #       print sql_fetch_billsubcode,'sql_fetch_billsubcode'
         #       print '4444444'
          #      cur.execute(sql_fetch_billsubcode)  
          #      billsubcode=cur.fetchall()
         #       pinto_id=billsubcode[0][1]
         #       pinto_billsubcode=billsubcode[0][0]
         #       print '111111'
         #       sql='''  exec PPassOPhaseinRecord '0392','%s',%s,'%s','','','' ''' %(pinto_billsubcode,pinto_id,user_info.login)
         #       print sql
         #       cur.execute(sql) 
         #       print '222222'   
        #    except:
        #        raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        #    else:
         #       conn.commit()
         #       conn.close() 
        return True
        
sale_order_new_line_wizard()

