#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
from osv import fields,osv
from tools.translate import _
from decimal_precision import decimal_precision as dp
import psycopg2
import pymssql
server='192.168.10.2'
user='sa'
password='719799'
database='20150204'


class sale_order_change(osv.osv):
    _name='sale.order.change'
    
    _state_list=[('draft',u'草稿'),('wait_plan_clerk',u'待计划文员'),('wait_eng',u'待工程'),('wait_plan',u'待计划'),('wait_tech',u'待工艺'),('wait_stock',u'待仓库'),('wait_purchase',u'待采购'),('wait_quality',u'待品质'),('wait_order_center',u'待订单中心'),('wait_order_manager',u'待订单主管'),('done',u'完成'),('cancel',u'取消')]
    _select_link=[('pcb.info',u'存档资料更改'),('sale.order.new',u'公司更改'),('mrp.production.new',u'在线更改'),('pcb.info',u'复投有更改'),('normal_change',u'批量更改')]
    
    def _func_state(self, cr, uid, ids, field_name, arg, context=None,):
        res={}
        for my in self.browse(cr,uid,ids):
            if field_name=='obj_state':
                res[my.id]=my.ref_obj.state
            elif field_name=='obj_name':
                res[my.id]=my.ref_obj.name
            elif field_name=='obj_type':
                res[my.id]=_(my.ref_obj._table_name)
            elif field_name=='org_price_unit':
                print my.ref_obj.name,'name'
                if my.ref_obj._table_name=='sale.order.line':
                    res[my.id]=my.ref_obj.price_unit
            elif field_name=='old_price_unit':
                if my.ref_obj._table_name=='sale.order.line':
                    if my.ref_obj.org_price_unit:
                        res[my.id]=my.ref_obj.org_price_unit
                    else:
                        res[my.id]=my.ref_obj.price_unit
        return res
    
    
    
    _columns={
        'name':                             fields.char(u'合同更改单',size=32,readonly=True,), # 更改单号
      
        'type':                             fields.selection([('order_change_before',u'存档资料更改'),('online_board_change',u'在线更改'),
                                                             ('repeat_change',u'复投更改'),
                                                             ('company_change',u'公司更改'),
                                                             ('order_production_change',u'批量更改')],u'更改类型',select=True,size=64,required=True),#ype  更改类型
                                   
        'stock_count':                      fields.integer(u'库存数'),#  库存数
        'context':                          fields.text(u'更改内容'),#    更改内容
        'so_change_lines_ids':               fields.one2many('so.change.records','sale_order_change_id',u'更改明细'),
        'change_forerer':                   fields.boolean(u'永久更改'),#  永久更改
        'chang_temp':                       fields.boolean(u'临时更改'),# 临时
        'stop_now':                         fields.boolean(u'立即暂停'), #临时stop_now  立即暂停
        'stop_workcenter':                  fields.boolean(u'暂停生产'), #临时stop_workcenter  暂停在工序前
        'renew_production':                 fields.boolean(u'恢复生产'), #临时renew_production  恢复生产
        'wait_create_dpt':                  fields.boolean(u'待申请部门'),#wait_create_dpt   待申请部门
        'wait_updata_dpt':                  fields.boolean(u'待更改部门 '),#wait_updata_dpt  待更改部门
        'response_id':                      fields.many2one('res.users',u'申请人', readonly=True),   #申请人  默认uid
      
 #       'create_datetime':                  fields.datetime(u'申请日期',readonly=True), #create_date 申请日期
        'create_date':                  fields.datetime(u'申请日期',readonly=True), #create_date 申请日期
        'change_order':                     fields.boolean(u'修改合同'), #change_order修改合同  
        'change_price':                     fields.boolean(u'修改单价'),  #change_price  改单价  
        'change_pcb_info_id':                  fields.boolean( u'修改用户单'), #change_pcb_info改用户单
        'change_impedance':                 fields.boolean(u'修改阻抗'),#change_impedance改阻抗
        'wait_plan':                        fields.boolean(u'计划部'),
        'wait_tech':                        fields.boolean(u'工艺部'),
        'wait_stock':                       fields.boolean(u'仓库部'),
        'wait_purchase':                    fields.boolean(u'采购部'),
        'wait_quality':                     fields.boolean(u'品质部'),
        'loss_amount':                      fields.float(u'预计损失金额'),
        'state':                            fields.selection(_state_list,u'单据状态',size=64,readonly=True),
        'ref_obj':fields.reference(u'更改类型', selection=_select_link, size=128,),
        'obj_state': fields.function(_func_state, method=True, type='char', string=u"状态",size=50,store=True),
        'product_id':fields.char(u'档案号',size=128),
        'pcb_info_id':fields.many2one('pcb.info',u'用户单号'),
        'sale_order_id':fields.many2one('sale.order.new',u'销售订单'),
        'partner_id':fields.many2one('res.partners',u'客户',domain=[('customer','=',True)]),
        'change_pcb_info':fields.boolean(u'是否锁定用户单'),
        'change_sale_order_new':fields.boolean(u'是否取消合同'),
        'change_company':fields.boolean('是否需要工厂评审'),
        'delivery_date':fields.date(u'交货日期'),
        'company':fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂')],string=u'投产工厂'),
        'mrp_production_id':fields.many2one('mrp.production.new',u'投产批次号',domain=[('state','!=','cancel')]),
        'plan_process':fields.text(u'现场在制品情况'),
        'eng_process':fields.text(u'工程更改方案'),
        'plan_clerk':fields.char(u'计划文员',size=32),
        'plan_time':fields.datetime(u'计划审核时间'),
        'order_manager':fields.char(u'订单主管',size=32),
        'finally_time':fields.datetime(u'最终审核时间'),
        'finally_note':fields.text(u'订单主管意见'),
    }
    _defaults={
        'state': lambda *a:'draft', 
        'response_id':lambda self,cr,uid,c:uid,
 #       'create_datetime': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
#        'name':lambda self,cr,uid,c: self.pool.get('ir.sequence').get(cr,uid,'sale.order.change'),
        'name':lambda obj, cr, uid, context:'/',
    }

    def create(self,cr,uid,vals,context=None):
          
          if vals.get('name','/')=='/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order.change') or '/'
         
          id=super(sale_order_change,self).create(cr,uid,vals,context=context)
          return id
      
    def change_state(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])

        record=my.ref_obj
        print record,'record'
        print record.state,'state'
        obj=self.pool.get(record._table_name)
        print obj,'obj'
        if my.obj_state!='wait_change' and not my.partner_id:
            obj.write(cr,uid,record.id,{'temp_state':record.state,'state':'wait_change'})
        return True
    def renew_state(self,cr,uid,ids,context=None):      
        my=self.browse(cr,uid,ids[0])
        

        record=my.ref_obj
        obj=self.pool.get(record._table_name)
        temp_state=record.temp_state
        if  my.obj_state=='wait_change':
            obj.write(cr,uid,record.id,{'state':temp_state}) 
        return True  
    
    def updata_price(self,cr,uid,ids,context=None):
        so_rec=self.browse(cr,uid,ids[0])
        line_obj=self.pool.get('sale.order.line')
        price_obj=self.pool.get('price.sheet')
        invoice_obj=self.pool.get('account.invoice.line')
        change_obj=self.pool.get('so.change.records')
        
        if so_rec.so_change_lines_ids:
            for line in so_rec.so_change_lines_ids:
                if line.ref_obj._table_name=='sale.order.line':
                    my=change_obj.browse(cr,uid,line.id)               
                    if my.new_price_unit and my.ref_obj.id:
                        ##
                        org_price_unit=line_obj.browse(cr,uid,my.ref_obj.id).price_unit
                        line_obj.write(cr,uid,my.ref_obj.id,{'price_unit':my.new_price_unit,'org_price_unit':org_price_unit,'updata_time':time.strftime('%Y-%m-%d %H:%M:%S')})
                        ##
                        price_rec=my.ref_obj.price_sheet_id
                        if price_rec:
                            price_obj.write(cr,uid,price_rec.id,{'new_price_unit':my.new_price_unit,'updata_time':time.strftime('%Y-%m-%d %H:%M:%S')})
                        ##:done
                        inv_ser=invoice_obj.search(cr,uid,[('state','!=','done'),('sale_line_id','=',my.ref_obj.id)])
                        for inv_id in inv_ser:
                            inv_rec=invoice_obj.browse(cr,uid,inv_id)
                            if inv_rec.price_unit < my.new_price_unit:
                                add_amount=(my.new_price_unit - inv_rec.price_unit) * inv_rec.quantity
                                invoice_obj.write(cr,uid,inv_id,{'price_add_amount':add_amount})
                            else:
                                red_amount=(inv_rec.price_unit - my.new_price_unit) * inv_rec.quantity
                                invoice_obj.write(cr,uid,inv_id,{'price_reduce_amount':red_amount})
                            invoice_obj.write(cr,uid,inv_id,{'price_unit':my.new_price_unit})
        return True
        
        
    def write_dpt(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        contractcode=my.sale_order_id.name
        so_change_lines_ids=my.so_change_lines_ids
        obj=self.pool.get('so.change.records')
        dpt=self.pool.get('res.department')
        pcb_info=self.pool.get('pcb.info')
        user_obj=self.pool.get('res.users')
        sale_order_new=self.pool.get('sale.order.new')
        mrp_obj=self.pool.get('mrp.production.new')
        user_info=user_obj.browse(cr,uid,uid)
        s=[u'计划部',u'工艺部',u'物控部',u'采购',u'品质部',u'工程部',u'订单中心']
        so={u'计划部':'wait_plan',
               u'工艺部':'wait_tech',
               u'物控部':'wait_stock',
               u'采购':'wait_purchase',
               u'品质部':'wait_quality',
               u'订单中心':'wait_order_center',
               }
        e=dpt.search(cr,uid,[('name','=',s[5])])[0]
        if my.state=='draft' and my.type!='company_change':
            self.write(cr,uid,ids[0],{'state':'wait_plan_clerk'})
            
       ###存档资料更改
        if my.state=='wait_plan_clerk' and my.type=='order_change_before' and not my.partner_id:
             self.write(cr,uid,ids[0],{'state':'wait_eng','plan_time':time.strftime('%Y-%m-%d %H:%M:%S'),'plan_clerk':user_info.name,})
             obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':e,'state':'draft'})
        ###复投有更改   
        if my.state=='wait_plan_clerk' and not my.partner_id and my.type=='repeat_change':
            self.write(cr,uid,ids[0],{'state':'wait_eng','plan_time':time.strftime('%Y-%m-%d %H:%M:%S'),'plan_clerk':user_info.name,})
            obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':e,'state':'draft'})
        ####公司更改
        if my.state=='draft' and my.type=='company_change':
            if  my.change_sale_order_new==True:
                self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
            elif my.change_company !=True:
                self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
            else:
                self.write(cr,uid,ids[0],{'state':'wait_eng'})
                obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':e,'state':'draft'})
                
                
        ##批量客户级更改，把这个客户的所有档案号最后一个版本的更改
        if my.state=='wait_plan_clerk' and my.partner_id and my.type=='order_production_change':
            self.write(cr,uid,ids[0],{'state':'wait_order_manager','plan_time':time.strftime('%Y-%m-%d %H:%M:%S'),'plan_clerk':user_info.name,})
            
            
        ####在线更改
        if my.type=='online_board_change' and my.state=='wait_plan_clerk':
           
            if my.renew_production==True and  my.stop_now==True or my.renew_production==True and my.stop_workcenter:
                 raise osv.except_osv(_('Error'),(u'不能同时恢复生产和暂停生产！！！！') )
            if my.renew_production==False and  my.stop_workcenter==False:
                raise osv.except_osv(_('Error'),(u'恢复生产和暂停生产必须选择一个！！！！') )
            else:
                self.write(cr,uid,ids[0],{'state':'wait_eng','plan_time':time.strftime('%Y-%m-%d %H:%M:%S'),'plan_clerk':user_info.name,})
                obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':e,'state':'draft'})
        ####工程选定需要评审的部门
        if my.state=='wait_eng':
            b=[]
            if my.wait_plan !=False:
                a=dpt.search(cr,uid,[('name','=',s[0])])[0]
                print a,'a'
                jh_id=obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                print jh_id,'jh_id'
                if jh_id:
                    b.append(jh_id)
            if my.wait_tech !=False:
                a=dpt.search(cr,uid,[('name','=',s[1])])[0]
                gy_id=obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                if gy_id:
                    b.append(gy_id)
            if my.wait_stock !=False:
                a=dpt.search(cr,uid,[('name','=',s[2])])[0]
                ck_id=obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                if ck_id:
                    b.append(ck_id)
            if my.wait_purchase !=False:
                a=dpt.search(cr,uid,[('name','=',s[3])])[0]
                cg_id=obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                if cg_id:
                    b.append(cg_id)
            if my.wait_quality  !=False:
                a=dpt.search(cr,uid,[('name','=',s[4])])[0]
                pz_id=obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                if pz_id:
                    b.append(pz_id)
            if  my.wait_plan ==False and my.wait_tech ==False and my.wait_stock ==False and my.wait_purchase ==False and my.wait_quality ==False:
                raise osv.except_osv(_('Warning !'), _(u'请选择相关部门审批！'))
            

            
            dpts=(obj.browse(cr,uid,b[0]).dpt_id).name
          
            self.write(cr,uid,ids[0],{'state':so[dpts]})
            line_ids=obj.search(cr,uid,[('sale_order_change_id','=',my.id),('dpt_id','=',e)])
            if line_ids:
                obj.write(cr,uid,line_ids[0],{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S'),'responsible_name':uid,})
            else:
                raise osv.except_osv(_('Warning !'), _(u'工程部不存在,请检查！'))
            
            
        #####各部门审批到下个部门最终审批到待订单中心
        if my.state not in ['draft','wait_plan_clerk','wait_eng','done','wait_order_manager','wait_order_center']:
            line_ids=obj.search(cr,uid,[('sale_order_change_id','=',my.id),('state','!=','done')])
            print line_ids,'ids'
          
            lines=obj.browse(cr,uid,line_ids[0])
            print lines.state,'lines'
            if lines.state !='done':
                if len(line_ids)>1:
                    dpt_one=obj.browse(cr,uid,line_ids[1]).dpt_id.name
                    print dpt_one,'id'
                    self.write(cr,uid,ids[0],{'state':so[dpt_one]})
                else:
                    if my.type !='online_board_change':
                        self.write(cr,uid,ids[0],{'state':'wait_order_center'})
                        a=dpt.search(cr,uid,[('name','=',s[6])])[0]
                        obj.create(cr,uid,{'sale_order_change_id':my.id,'dpt_id':a,'state':'draft'})
                    else:
                        self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
                obj.write(cr,uid,line_ids[0],{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S'),'responsible_name':uid,})
                
        ####存档资料更改
        if my.state=='wait_order_center' and my.type=='order_change_before':
            print my.pcb_info_id.id,'pcb_info_id.id'
            if my.change_pcb_info==True:
                pcb_info.write(cr,uid,my.pcb_info_id.id,{'state':'wait_change'})
            self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
            a=dpt.search(cr,uid,[('name','=',s[6])])[0]
            line_ids=obj.search(cr,uid,[('sale_order_change_id','=',my.id),('dpt_id','=',a)])
            if line_ids:
                obj.write(cr,uid,line_ids[0],{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S'),'responsible_name':uid,})
           
            
        if my.state=='wait_order_manager' and my.type=='order_change_before':
            self.write(cr,uid,ids[0],{'state':'done'})
            
        ###公司更改不需要工厂评审
        if my.state=='wait_order_center' and my.type=='company_change' and my.change_company ==True:
            self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
            a=dpt.search(cr,uid,[('name','=',s[6])])[0]
            line_ids=obj.search(cr,uid,[('sale_order_change_id','=',my.id),('dpt_id','=',a)])
            if line_ids:
                obj.write(cr,uid,line_ids[0],{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S'),'responsible_name':uid,})
                
        #公司更改时，只更改用户单时把用户单号改为待更改状态！
        if my.state=='wait_order_manager' and my.type=='company_change' and my.change_company !=True and my.change_sale_order_new !=True and  my.pcb_info_id:
            pcb_info.write(cr,uid,my.pcb_info_id.id,{'state':'wait_change'})
            self.write(cr,uid,ids[0],{'state':'done',})
        #公司更改时，只更改销售订单时把单号改为待更改状态！
        if my.state=='wait_order_manager' and my.type=='company_change' and my.change_company !=True and my.change_sale_order_new !=True and my.sale_order_id:
            sale_order_new.write(cr,uid,my.sale_order_id.id,{'state':'order_wait_change'})
            self.write(cr,uid,ids[0],{'state':'done',})
          #公司更改时，只更改销售订单时，而且取消合同打勾了把单号改为作废状态！    
        if my.state=='wait_order_manager' and my.type=='company_change' and my.change_sale_order_new ==True:
            sale_order_new.write(cr,uid,my.sale_order_id.id,{'state':'cancel'})
            self.write(cr,uid,ids[0],{'state':'done',})
            #####同步东烁数据
            try:
                conn=pymssql.connect(server=server,user=user,password=password,database=database)
                cur=conn.cursor()
                
                sql='''exec PP_cancel_contract_OE '%s','' ''' %(contractcode)
                sql=sql.decode('utf-8')
                print sql,'sql'
                cur.execute(sql) 
            except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
            else:
                conn.commit()
                conn.close() 
                print u'更新成功'
            
        if my.state=='wait_order_manager' and my.type=='company_change' and my.change_company ==True:
            pcb_info.write(cr,uid,my.pcb_info_id.id,{'state':'wait_change'})
            self.write(cr,uid,ids[0],{'state':'done',})
        #强制更新订单主管审批人和审批时间   
        if my.state=='wait_order_manager':
            self.write(cr,uid,ids[0],{'state':'done','finally_time':time.strftime('%Y-%m-%d %H:%M:%S'),'order_manager':user_info.name,})      
        ####复投有更改
        if my.state=='wait_order_center' and my.type=='repeat_change':
            self.write(cr,uid,ids[0],{'state':'wait_order_manager'})
            a=dpt.search(cr,uid,[('name','=',s[6])])[0]
            line_ids=obj.search(cr,uid,[('sale_order_change_id','=',my.id),('dpt_id','=',a)])
            if line_ids:
                obj.write(cr,uid,line_ids[0],{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S'),'responsible_name':uid,})
        
        if my.state=='wait_order_manager' and my.type=='repeat_change':
            if my.change_pcb_info !=True:
                self.write(cr,uid,ids[0],{'state':'done',})
            else:
                pcb_info.write(cr,uid,my.pcb_info_id.id,{'state':'wait_change'})
            self.write(cr,uid,ids[0],{'state':'done',})
        
        
        ####批量更改
        if my.state=='wait_order_manager' and my.type=='order_production_change':
            pcb_list=self.pool.get('pcb.list')
            pcb_info=self.pool.get('pcb.info')
            line=pcb_list.search(cr,uid,[('partner_id','=',my.partner_id.id)])
            print line,'line'
            for i in line:
                print i
                id=pcb_list.browse(cr,uid,i).pcb_info_id.id
                s=pcb_info.write(cr,uid,id,{'next_note':my.context,'state':'wait_change'})
            self.write(cr,uid,ids[0],{'state':'done',})
        
        #####在线更改
        if my.state=='wait_order_manager' and my.type=='online_board_change':
           
            if my.change_sale_order_new==True:
                    sale_order_new.write(cr,uid,my.sale_order_id.id,{'state':'cancel'})       
            else:
                if my.change_pcb_info==True:
                        pcb_info.write(cr,uid,my.pcb_info_id.id,{'state':'wait_change'})
                       
                if my.stop_workcenter==True:
                        mrp_obj.write(cr,uid,my.mrp_production_id.id,{'stop_state':True})
                if my.renew_production==True:
                        
                        mrp_obj.write(cr,uid,my.mrp_production_id.id,{'stop_state':False})
                
            self.write(cr,uid,ids[0],{'state':'done',})
            
            
        return True
    
    def set_draft(self,cr,uid,ids,vals,context=None):
        my=self.browse(cr,uid,ids[0])
        self.write(cr,uid,ids[0],{'state':'draft'})
    
    

 
        
sale_order_change()




class so_change_records(osv.osv):
    _name='so.change.records'
    _select_link=[('sale.order.new',u'合同更改'),('sale.order.line.news',u'合同明细更改'),('pcb.info',u'用户单更改'),('price.sheet',u'报价单更改')]
    def _func_state(self, cr, uid, ids, field_name, arg, context=None,):
        res={}
        for my in self.browse(cr,uid,ids):
            if field_name=='obj_state':
                res[my.id]=my.ref_obj.state
            elif field_name=='obj_name':
                res[my.id]=my.ref_obj.name
            elif field_name=='obj_type':
                res[my.id]=_(my.ref_obj._table_name)
            elif field_name=='org_price_unit':
                print my.ref_obj.name,'name'
                if my.ref_obj._table_name=='sale.order.line':
                    res[my.id]=my.ref_obj.price_unit
            elif field_name=='old_price_unit':
                if my.ref_obj._table_name=='sale.order.line':
                    if my.ref_obj.org_price_unit:
                        res[my.id]=my.ref_obj.org_price_unit
                    else:
                        res[my.id]=my.ref_obj.price_unit
        return res
      
    _columns={
       
        'sale_order_change_id':fields.many2one('sale.order.change',cascade=True),
        'dpt_id':fields.many2one('res.department',u'部门',required=True),
        'is_sure':fields.boolean(u'是否满足要求'),
        'responsible_name':fields.many2one('res.users',u'评审人'),
        'note':fields.text(u'评审意见'),
        'state':fields.selection([('draft',u'草稿'),('done',u'完成')],string=u'单据状态',readonly=True),
        'finish_date':fields.datetime(u'审批时间'),
        'change_loss':fields.char(u'更改造成的损失',size=200),
        'deal_board':fields.char(u'库存板处理',size=200),
        'tool_loss':fields.char(u'工具损失',size=200),
        'produt_loss':fields.char(u'产品损失',size=200),
        'rework_cost':fields.float(u'返工费用'),
        'consultation':fields.char(u'协商结果',size=200),
        'state':fields.selection([('draft',u'草稿'),('done',u'完成')],u'状态')
        
        }
    _defualts={
               
        'dpt_id': lambda self,cr,uid,context,: context.get('dpt_id'),
        'state': lambda *a: 'draft',
        'responsible_name':lambda self,cr,uid,c:uid,

               }
    

    def write_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done','finish_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        
        
        
        
        
        
    
so_change_records()


    
    
    
    
    









