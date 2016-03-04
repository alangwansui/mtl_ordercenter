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

server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'
sign_addr={
       'sz':u'深圳',
       'bj':u'北京',
       'cs':u'长沙',
       'cd':u'成都',
       'fz':u'福州',
       'hz':u'杭州',
       'nj':u'南京',
       'sh':u'上海',
       'wh':u'武汉',
       'xa':u'西安',
       }



class sale_order_new(osv.osv):
    _name='sale.order.new'
    _description='sale information'
    _order='name desc'
    def _total(self,cr,uid,ids,field_name,args,context=None):
        res={}
        obj=self.browse(cr,uid,ids[0])
        id=obj.id
        my=self.pool.get('sale.order.new.line')
        line_ids=my.search(cr,uid,[('sale_order_new_id','=',id)])
        total=0
        if field_name=='amount_total':
            for line_id in line_ids:
                line=my.browse(cr,uid,line_id)
                total=total+line.line_amount_total
        if field_name=='amount_tax':
            for line_id in line_ids:
                line=my.browse(cr,uid,line_id)
                total=total+line.line_tax
        if field_name=='amount_untaxed':
            for line_id in line_ids:
                line=my.browse(cr,uid,line_id)
                total=total+line.line_untax_amount_total
        res[id]=total
        return res
        
    def insert_to_ds(self,cr,uid,id,vals,context=None):
       
       column=[]
       info=self.browse(cr,uid,id)
       addr=''
       if info.sign_addr:
           addr=sign_addr[info.sign_addr]
       else:
           addr=''
       contact=''
       if info.receiver:
          contact=info.receiver.contact
          
       pur_contact=''
       if info.pur_contact:
           pur_contact=info.pur_contact.contact
       column.append(info.create_date)
       column.append(addr)
       column.append(info.city)
       column.append(pur_contact)
       column.append(info.phone)
       column.append(info.delivery_way)
       column.append(info.currency)
       column.append(info.acceptance_period)
       column.append('')
       column.append(info.carriage)
       
       column.append(info.tax)
       column.append(info.settle)
       column.append('')
       column.append(info.payment)
       column.append('')
       column.append('')
       column.append(info.special_instruction)
       column.append('')
       column.append(info.sale_order)
       column.append(info.street2)
       
       column.append(info.receiver_unit)
       column.append(contact)
       column.append(info.receive_addr)
       column.append(info.user_id)
       column.append(info.sale_company)
       column.append(info.name)


       column.append(info.partner_code)
       column.append('')
       column.append('')
       column.append('create')
       column.append('')
       print column
#       if not info.name:
#               raise osv.except_osv(_('Error!'),_(u'合同编号不存在，请检查！'))
       row=[]
       for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
       row=tuple(row)
       print row
       try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            print '1111111111111111'
            sql=''' exec pp_TCContractM_OE '%s','%s','%s','%s','%s','%s','%s','%d','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s' ''' %row
                                           
                                        

            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
       except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
       else:
            conn.commit()
            conn.close() 
            print u'更新成功！'
       return id 
    
    def create(self,cr,uid,vals,context=None):
          print 'sale.order.new','create'
          if vals.get('name','/')=='/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order.new') or '/'
          id=super(sale_order_new,self).create(cr,uid,vals,context=context)
          return id and self.insert_to_ds(cr,uid,id,vals,context=context)
   
   
   
    def update_to_ds(self,cr,uid,ids,context=None):
       column=[]
       if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
       else:
            info=self.browse(cr,uid,ids)
       s_addr=''
       if info.sign_addr:
           s_addr=sign_addr[info.sign_addr]
       else:
           s_addr=''
       if info.receiver:
           receiver=info.receiver.contact
       else:
           receiver=''
           
       pur_contact=''
       if info.pur_contact:
           pur_contact=info.pur_contact.contact
           
       column.append(info.create_date)
       column.append(s_addr)
       column.append(info.city)
       column.append(pur_contact)
       column.append(info.phone)
       column.append(info.delivery_way)
       column.append(info.currency)
       column.append(info.acceptance_period)
       column.append('')
       column.append(info.carriage)
       
       column.append(info.tax)
       column.append(info.settle)
       column.append('')
       column.append(info.payment)
       column.append('')
       column.append('')
       column.append(info.special_instruction)
       column.append('')
       column.append(info.sale_order)
       column.append(info.street2)
       
       column.append(info.receiver_unit)
       column.append(receiver)
       column.append(info.receive_addr)
       column.append(info.user_id)
       column.append(info.sale_company)
       column.append(info.name)


       column.append(info.partner_code)
       column.append('')
       column.append('')
       column.append('write')
       column.append('')
       print column
#       if not info.name:
#               raise osv.except_osv(_('Error!'),_(u'合同编号不存在，请检查！'))
       row=[]
       for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
       row=tuple(row)
       print row
       try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            sql=''' exec pp_TCContractM_OE '%s','%s','%s','%s','%s','%s','%s','%d','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
       except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
       else:
            conn.commit()
            conn.close() 
            print u'更新成功！'
       return True
   
    def write(self,cr,uid,ids,vals,context=None):
        super(sale_order_new,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True 
      
    def delete_to_ds(self,cr,uid,ids,context=None):
       column=[]
       if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
       else:
            info=self.browse(cr,uid,ids)
       s_addr=''
       if info.sign_addr:
           s_addr=sign_addr[info.sign_addr]
       if info.receiver:
           receiver=info.receiver.contact
       else:
           receiver=''
       pur_contact=''
       if info.pur_contact:
           pur_contact=info.pur_contact.contact
       column.append(info.create_date)
       column.append(s_addr)
       column.append(info.city)
       column.append(pur_contact)
       column.append(info.phone)
       column.append(info.delivery_way)
       column.append(info.currency)
       column.append(info.acceptance_period)
       column.append('')
       column.append(info.carriage)
       
       column.append(info.tax)
       column.append(info.settle)
       column.append('')
       column.append(info.payment)
       column.append('')
       column.append('')
       column.append(info.special_instruction)
       column.append('')
       column.append(info.sale_order)
       column.append(info.street2)
       
       column.append(info.receiver_unit)
       column.append(receiver)
       column.append(info.receive_addr)
       column.append(info.user_id)
       column.append(info.sale_company)
       column.append(info.name)


       column.append(info.partner_code)
       column.append('')
       column.append('')
       column.append('unlink')
       column.append('')
       print column
 #      if not info.name:
#               raise osv.except_osv(_('Error!'),_(u'合同编号不存在，请检查！'))
       row=[]
       for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
       row=tuple(row)
       print row
       try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            sql=''' exec pp_TCContractM_OE '%s','%s','%s','%s','%s','%s','%s','%d','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
       except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
       else:
            conn.commit()
            conn.close() 
            print u'更新成功！'
       return True
    def unlink(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state!='draft':
               raise osv.except_osv(_('Error!'),_(u'不是草稿状态，不能删除，请检查！'))  
        else:
             print 'sale.order.new','unlink'
             self.delete_to_ds(cr,uid,ids,context=None)
             return super(sale_order_new,self).unlink(cr,uid,ids)
    
    def _delivery_way_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','delivery_way')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]     
    sign_addr_list=[('sz',u'深圳'),('bj',u'北京'),('cs',u'长沙'),('cd',u'成都'),('fz',u'福州'),('hz',u'杭州'),('nj',u'南京'),('sh',u'上海'),('wh',u'武汉'),('xa',u'西安')]
    _columns={
              'name':fields.char(u'合同编号',readonly=True),
              'create_date':fields.date(u'签订日期'),
              'invoiced':fields.boolean(u'支付',readonly=True),
              
              'sale_order':fields.char(u'客户订单号',size=64),
              'shipped':fields.boolean(u'交货',readonly=True),
              'partner_id':fields.many2one('res.partners',u'客户',required=True,readonly=True,),
              'partner_code':fields.related('partner_id','partner_code',relation='res.partners',string='客户代码',type='char',store=True,readonly=True),
              'sale_company':fields.related('partner_id','sale_company',relation='res.partners',string=u'销售公司',type='char',store=True,readonly=True),
              'street':fields.related('partner_id','street',string='注册地址',type='char',store=True,readonly=True),
              'street2':fields.related('partner_id','street2',string='送货地址',type='char',store=True,readonly=True),
              'currency':fields.related('partner_id','currency',type='char',string='币种',store=True),
              'tax':fields.related('partner_id','tax',type='char',string='发票类型',store=True),
              'phone':fields.related('partner_id','phone',type='char',string='客户电话',store=True,readonly=True),
              'sign_addr':fields.selection(sign_addr_list,u'签订地点'),
#              'pur_contact':fields.related('partner_id','pur_contact',type='char',relation='res.partners',string='客户联系人',store=True,readonly=True),
              'pur_contact':fields.many2one('res.partner.contact',u'客户联系人',required=True,domain="[('res_partner_contact_id','=',partner_id)]"),
              'fax':fields.related('partner_id','fax',type='char',string='传真',store=True,readonly=True),
              'receiver':fields.many2one('res.partner.contact',u'收货人',required=True,domain="[('res_partner_contact_id','=',partner_id)]"),
              'carriage':fields.related('partner_id','carriage',type='char',string='运费负担',store=True),
              'receiver_unit':fields.related('receiver','company_name',string="收货单位",type='char',relation="res.partner.contact",store=True),
              'receive_addr':fields.related('receiver','street3',string="收货地址",type='char',relation="res.partner.contact",store=True),
              'delivery_way':fields.selection(_delivery_way_get,u'交货方式'),
              'acceptance_period':fields.integer(u'验收期限'),
              'special_instruction':fields.text(u'特殊说明'),
             # 'customer_material_code':fields.char(u'客户物料编码',size=50),
             # 'customer_project_name':fields.char(u'客户工程名称',size=50),
             # 'bar_code':fields.char(u'条形码',size=50),
              'sale_order_new_line':fields.one2many('sale.order.new.line','sale_order_new_id',u'订单明细'),
              'city':fields.related('partner_id','city',string='所属地区',type='char',store=True,readonly=True),
              'user_id':fields.related('partner_id','user_id',type='char',relation='res.partners',string='业务员',store=True),
              'payment':fields.related('partner_id','payment',type='char',relation='res.partners',string='付款方式',store=True),
              'settle':fields.related('partner_id','settle',type='char',relation='res.partners',string='结算方式',store=True),
              'amount_untaxed':fields.function(_total,method=True,string='不含税金额',store=True),
              'amount_tax':fields.function(_total,method=True,string='税款',store=True),
              'amount_total':fields.function(_total,method=True,string='合计',store=True),
              'state':fields.selection([('draft',u'草稿'),('wait_confirm',u'待确认'),('wait_master',u'总经办'),('wait_sign_back',u'待回签'),('special_approval',u'特批'),('order_wait_change',u'待更改'),('done',u'已回签'),('cancel',u'作废')],string=u'单据状态'),
              'cancel_note':fields.char(u'作废备注',size=256),
              }
    _defaults={
               'state':'draft',
#               'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'sale.order.new'), 
               'name':lambda obj, cr, uid, context:'/',
               'acceptance_period':7,
               }
    
 #####默认带出联系人
    def onchange_partner_contact(self,cr,uid,ids,res_id,context=None):
        sel_obj=self.pool.get('res.partner.contact')
        if res_id:
            print sel_obj.search(cr,uid,[('res_partner_contact_id','=',res_id)],context=context),'sese'
            ids=sel_obj.search(cr,uid,[('res_partner_contact_id','=',res_id),('defualt_connact','=',True)],context=context)[0] or None
           
        return {'value':{'receiver':ids}}
        
        return res_id
    
    

    def button_refuse(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        contractcode=my.name
        obj=self.pool.get('sale.order.new.line')
        price_order=self.pool.get('price.sheet')
        pcb_info=self.pool.get('pcb.info')
        state=my.state 
        if state  in('special_approval','done'):
           raise osv.except_osv(_('Error!'),_(u'合同状态是完成或特批,不能直接作废,请检查!'))
        else:
            if my.sale_order_new_line:
                for r in my.sale_order_new_line:
                    print r.id,'idsids'
                    print r.price_sheet_id.id,'price_sheet_id'
                    obj.write(cr,uid,r.id,{'state':'cancel'})
                    price_order.write(cr,uid,r.price_sheet_id.id,{'state':'cancel'})
                    pcb_info.write(cr,uid,r.price_sheet_id.pcb_info_id.id,{'state':'wait_change'})
            self.write(cr,uid,ids,{'state':'cancel'},context=context)
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
        return  True
    
    def update_state(self,cr,uid,ids,context=None):
        obj=self.pool.get('sale.order.new.line')
        my=self.browse(cr,uid,ids[0])
        line_ids=obj.search(cr,uid,[('sale_order_new_id','=',ids[0])])
        for line_id in line_ids:
            line_info=obj.browse(cr,uid,line_id)
            if not line_info.delivery_date:
                raise osv.except_osv(_('Error!'),_(u'有合同交期未填,请检查！'))
        if my.amount_total<50000:
            print u'此金额大于50000，需要总经理确认！'
            return True

    def done(self,cr,uid,ids,context=None):  
        
        line_obj=self.pool.get("sale.order.new.line")   
        line_ids=line_obj.search(cr,uid,[('sale_order_new_id','=',ids[0])])
        sheet_obj=self.pool.get('price.sheet') 
        for i in line_ids:
                sale_line=line_obj.browse(cr,uid,i)
                sheet_price_id=sale_line.price_sheet_id
                lead_id=sheet_price_id.lead_id.id
                self.pool.get('order.recive').write(cr,uid,lead_id,{'state':'wait_production'})
       # line_obj.write(cr,uid,line_ids,{
       #                                                        'state':'wait_confirm'
        #                                                       })
        for line_id in line_ids:
            line_info=line_obj.browse(cr,uid,line_id)
            sheet_obj.create_product_code(cr,uid,[line_info.price_sheet_id.id],line_id=None)
            sheet_info=sheet_obj.browse(cr,uid,line_info.price_sheet_id.id)
            line_obj.write(cr,uid,line_id,{
                                                           'state':'wait_confirm',
                                                           'product_id':sheet_info.product_id,
                                                           })
        return True
    

    
       ####检查是否有合同特批单，如果有的话就要检查特批单是否审批完成，如果没完成则不能投产。
    def check_approval(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get("contract.special.approval")  
        id=obj.search(cr,uid,[('sale_order_new_id','=',my.id)])
        print id,'idid'
        if id:
            
            state=obj.browse(cr,uid,id[0]).state
            if state!='done':
                raise osv.except_osv(_('Error!'),_(u'投产特批单没审批完成,请检查!'))
        else:
            return True
    #####更新待投产数量
    def update_wait_production_count(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('sale.order.new.line')
        for r in my.sale_order_new_line:
            product_qty=r.product_qty
            obj.write(cr,uid,r.id,{'wait_production_count':product_qty})
        return True
    
sale_order_new()

class sale_order_new_line(osv.osv):
    _name='sale.order.new.line'
    _description='sale line information'
    _order='name desc'
    def _line_amount_total(self,cr,uid,ids,field_name,args,context=None):
        res={}
        for id in ids:
            line=self.browse(cr,uid,id)
            sale_order_new=self.pool.get('sale.order.new')
            line_untax=line.price_unit * line.product_qty+line.cost_once
            tax=line.sale_order_new_id.tax
            if field_name=='line_amount_total':
                
                if tax=='17%增值税':
                    total=line_untax*(1-line.discount/100.0)*(1+0.17)
                else:
                    total=line_untax*(1-line.discount/100.0)
            if field_name=='line_tax':
                if tax=='收据'or '':
                    total=0
                else:
                    total=line_untax*0.17
                    print tax,'tax'
                    print line.price_unit,'price_unit'
                    print line.product_qty,'product_qty'
                    print line.discount,'discount'
                    print line.cost_once,'cost_once'
                   
            if field_name=='line_untax_amount_total':
                    total=line_untax
                    
            res[id]=total
        return res      
    
    _columns={
              'sale_order_new_id':fields.many2one('sale.order.new',u'合同号',ondelete='cascade'),
              'name':fields.char(u'订单批次号',size=64,readonly=True),
              'customer_name':fields.related('sale_order_new_id','partner_id',type='many2one',relation='res.partners',string=u'客户'),
              'price_sheet_id':fields.many2one('price.sheet',u'报价单号',domain=[('is_quote','=',False)]),
              'product_id':fields.char(u'档案号',size=32,readonly=True),
              'pcb_info_id':fields.related('price_sheet_id','pcb_info_id',type='many2one',string=u'用户单号',relation='pcb.info',readonly=True),
              'sale_type':fields.related('price_sheet_id','recive_type',string=u"接单类型",type='char',relation='price.sheet',readonly=True),
              'custmer_goodscode':fields.related('pcb_info_id','custmer_goodscode',type='char',relation='pcb.info',string=u'零件号',store=True,readonly=True),
              'change_code':fields.char(u'更改单号',size=20,readonly=True),
              'finish_board_thickness':fields.related('pcb_info_id','finish_board_thickness',type='float',relation='pcb.info',string=u"板厚",store=True,readonly=True),
              'board_material':fields.char(u'板材',size=60,readonly=True),
              'pcs_unit_count':fields.related('pcb_info_id','pcs_unit_count',type='integer',relation='pcb.info',string=u"单拼",store=True,readonly=True),
              'delivery_date':fields.related('price_sheet_id','delivery_date',type='datetime',string=u'发货日期',readonly=True),
              'pcs_length':fields.related('pcb_info_id','pcs_length',type='float',relation='pcb.info',string=u"pcs长cm",store=True,readonly=True),
              'pcs_width':fields.related('pcb_info_id','pcs_width',type='float',string=u"pcs宽cm",relation='pcb.info',store=True,readonly=True),
              'layer_count':fields.related('pcb_info_id','layer_count',type='integer',string=u"层数",relation='pcb.info',store=True,readonly=True),
              'product_qty':fields.related('price_sheet_id','product_number',string=u'数量',type='integer',relation='price.sheet', readonly=True,store=True),
              'wait_production_count':fields.integer(u'待投产数量',readonly=True),
              'cost_ready_s':fields.related('price_sheet_id','cost_ready_s',type='float',string=u'工程准备费',store=True,readonly=True),
              'cost_plot_s':fields.related('price_sheet_id','cost_plot_s',type='float',string=u'菲林费',store=True,readonly=True),
              'cost_test_s':fields.related('price_sheet_id','cost_test_s',type='float',string=u'测试费',store=True,readonly=True),
              'cost_days':fields.related('price_sheet_id','cost_days_s',type='float',string=u'加急费',store=True,readonly=True),
              'cost_other_s':fields.related('price_sheet_id','cost_other_s',type='float',string=u'其他费',store=True,readonly=True),
              'cost_once':fields.related('price_sheet_id','cost_once',type='float',string=u'一次费用',store=True,readonly=True),
              'back_sign_date':fields.char(u'回签发货',size=30),

              'sub_memo':fields.char(u'备注',size=200),
              'is_recive_once_cost':fields.boolean(u'一次性费用'),
              'delivery_date':fields.date(u'合同交期'),
              'product_uom':fields.selection([('PCS','PCS'),('Unit','Unit')],u'单位'),
              'discount':fields.related('price_sheet_id','discount',type='float',string=u'折扣',store=True,readonly=True),
              'price_unit':fields.related('price_sheet_id','cost_pcs_s',type='float',string=u'单价',store=True,readonly=True),
              'line_amount_total':fields.function(_line_amount_total,method=True,string=u'小计(含税)',store=True,readonly=True),
              'line_tax':fields.function(_line_amount_total,method=True,string=u'税款',store=True,readonly=True),
              'line_untax_amount_total':fields.function(_line_amount_total,method=True,string=u'不含税金额',store=True,readonly=True),
              'sequence':fields.integer(u'序号'),
              'mrp_production_new_id':fields.one2many('mrp.production.new','sale_order_new_line_id',u'投产明细',readonly=True),
              'company_name':fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂')],string=u'投产公司'),
              'state': fields.selection([('draft', u'草稿'),('wait_confirm', u'待投产'),('done', u'完成'),('cancel', u'作废'),('wait_change',u'更改')],'单据状态',  readonly=True,),
              'customer_material_code':fields.char(u'客户物料编码',size=50),
              'customer_project_name':fields.char(u'客户工程名称',size=50),
              'customer_order':fields.char(u'客户订单号',size=50),
              'bar_code':fields.char(u'条形码',size=50),
              'scrap_fee':fields.float(u'报废费'),
              'product_name':fields.char(u'产品名称',size=64),
              }
    _defaults={
                'discount':0,
                'state':'draft',
                'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'sale.order.new.line'),
                'product_uom':'PCS'
                }
    
    _sql_constraints = [
        ('price_sheet_id', 'unique (price_sheet_id)', '有些报价单已经被选中,请检查!'),  
     ]
    
    def insert_to_ds(self,cr,uid,id,vals,context=None):
        
        column=[]
        info=self.browse(cr,uid,id)
        pcb_line_obj=self.pool.get('pcb.info.line')
        
        pcb_line_ids=pcb_line_obj.search(cr,uid,[('pcb_info_many_line','=',info.pcb_info_id.id)])
        pcb_info_board_material=''
        pcb_info_test_type=''
        pcb_info_special_process=''
        if pcb_line_ids:
            for pcb_line_id in pcb_line_ids:
                pcb_line_info=pcb_line_obj.browse(cr,uid,pcb_line_id)
                if pcb_line_info.board_material:
                    pcb_info_board_material=pcb_info_board_material+pcb_line_info.board_material+';'
                if pcb_line_info.test_type:
                    pcb_info_test_type=pcb_info_test_type+pcb_line_info.test_type+';'
                if pcb_line_info.special_process:
                    pcb_info_special_process=pcb_info_special_process+pcb_line_info.special_process+';'
                
        column.append(info.price_sheet_id.lead_id.name)
        column.append(info.product_id)
        column.append('')
        column.append('')
        column.append('')
        column.append(info.pcb_info_id.custmer_goodscode)
        column.append(info.pcb_info_id.layer_count)
        column.append(info.pcb_info_id.finish_board_thickness)
        column.append(pcb_info_board_material)
        column.append(info.pcb_info_id.pcs_length)
        
        column.append(info.pcb_info_id.pcs_width)
        column.append(info.pcb_info_id.delivery_type)
        column.append(0)
        column.append(info.product_qty)
        column.append(info.price_unit)
        column.append(info.cost_ready_s)
        column.append(info.cost_plot_s)
        column.append(info.cost_test_s)
        column.append(info.cost_other_s)
        column.append(info.scrap_fee)
        
        column.append(0)
        column.append(info.delivery_date)
        column.append(info.delivery_date)
        column.append(info.back_sign_date)
        column.append(pcb_info_test_type)
        column.append(info.pcb_info_id.surface_treatment)
        column.append(pcb_info_special_process)
        column.append(info.customer_material_code)
        column.append(info.customer_order)
        column.append(info.customer_project_name)
        
        column.append(info.product_name)
        column.append(info.bar_code)
        column.append(info.sub_memo)
        
        
        column.append(info.sale_type)
        column.append(info.sale_order_new_id.partner_id.partner_code)
        column.append(info.sequence)
        column.append(info.name)
        column.append(info.pcb_info_id.source_file_name)
        column.append(info.sale_order_new_id.name)
        column.append(info.sale_order_new_id.sale_company)
        column.append('create')
        column.append('')
        #if not info.sale_order_new_id.name or not info.sequence:
        #       raise osv.except_osv(_('Error!'),_(u'合同编号或序号不存在，请检查！'))
		
        
        print column
        row=[]
        for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
        row=tuple(row)
        print row
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            sql=''' exec pp_TCContracts_OE '%s','%s','%s','%s','%s','%s',%d,%f,'%s',%f,
                                           %f,%d,%f,%d,%f,%f,%f,%f,%f,%f,
                                           %f,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s',%d,'%s','%s','%s','%s','%s',
                                           '%s' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
        except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！')) 
        else:
            conn.commit()
            conn.close() 
            print '更新成功!' 
        return id
    
    
    def create(self,cr,uid,vals,context=None):
       print 'sale_order_line_new_create'
       id=super(sale_order_new_line,self).create(cr,uid,vals,context=context)
       price_sheet_obj=self.pool.get('price.sheet')
       #---------设置序号-------------
       sale_order_new_id=vals['sale_order_new_id']
       print sale_order_new_id
       line_ids=self.search(cr,uid,[('sale_order_new_id','=',sale_order_new_id)])
       self.insert_to_ds(cr,uid,id,vals,context=context)
       print line_ids,'line_id'
       i=1
       for line_id in line_ids:
           line_info=self.browse(cr,uid,line_id)
           price_sheet_obj.write(cr,uid,line_info.price_sheet_id.id,{'is_quote':True})
           self.write(cr,uid,line_id,{'sequence':i})
           i=i+1
       return self.insert_to_ds(cr,uid,id,vals,context=context)
   
   
    def update_to_ds(self,cr,uid,ids,vals,context=None):
        
        column=[]
        if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
        else:
            info=self.browse(cr,uid,ids)
        pcb_line_obj=self.pool.get('pcb.info.line')
        pcb_line_ids=pcb_line_obj.search(cr,uid,[('pcb_info_many_line','=',info.pcb_info_id.id)])
        pcb_info_board_material=''
        pcb_info_test_type=''
        pcb_info_special_process=''
        if pcb_line_ids:
            for pcb_line_id in pcb_line_ids:
                pcb_line_info=pcb_line_obj.browse(cr,uid,pcb_line_id)
                if pcb_line_info.board_material:
                    pcb_info_board_material=pcb_info_board_material+pcb_line_info.board_material+';'
                if pcb_line_info.test_type:
                    pcb_info_test_type=pcb_info_test_type+pcb_line_info.test_type+';'
                if pcb_line_info.special_process:
                    pcb_info_special_process=pcb_info_special_process+pcb_line_info.special_process+';'
                
        column.append(info.price_sheet_id.lead_id.name)
        column.append(info.product_id)
        column.append('')
        column.append('')
        column.append('')
        column.append(info.pcb_info_id.custmer_goodscode)
        column.append(info.pcb_info_id.layer_count)
        column.append(info.pcb_info_id.finish_board_thickness)
        column.append(pcb_info_board_material)
        column.append(info.pcb_info_id.pcs_length)
        
        column.append(info.pcb_info_id.pcs_width)
        column.append(info.pcb_info_id.delivery_type)
        column.append(0)
        column.append(info.product_qty)
        column.append(info.price_unit)
        column.append(info.cost_ready_s)
        column.append(info.cost_plot_s)
        column.append(info.cost_test_s)
        column.append(info.cost_other_s)
        column.append(info.scrap_fee)
        
        column.append(0)
        column.append(info.delivery_date)
        column.append(info.delivery_date)
        column.append(info.back_sign_date)
        column.append(pcb_info_test_type)
        column.append(info.pcb_info_id.surface_treatment)
        column.append(pcb_info_special_process)
        column.append(info.customer_material_code)
        column.append(info.customer_order)
        column.append(info.customer_project_name)
        
        column.append(info.product_name)
        column.append(info.bar_code)
        column.append(info.sub_memo)
        
        
        column.append(info.sale_type)
        column.append(info.sale_order_new_id.partner_id.partner_code)
        column.append(info.sequence)
        column.append(info.name)
        column.append(info.pcb_info_id.source_file_name)
        column.append(info.sale_order_new_id.name)
        column.append(info.sale_order_new_id.sale_company)
        column.append('write')
        column.append('')
        if not info.sale_order_new_id.name or not info.sequence:
               raise osv.except_osv(_('Error!'),_(u'合同编号或序号不存在，请检查！'))
        
        print column
        row=[]
        for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
        row=tuple(row)
        print row
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            sql=''' exec pp_TCContracts_OE '%s','%s','%s','%s','%s','%s',%d,%f,'%s',%f,
                                           %f,%d,%f,%d,%f,%f,%f,%f,%f,%f,
                                           %f,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s',%d,'%s','%s','%s','%s','%s',
                                           '%s' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
        except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
            conn.commit()
            conn.close() 
            print '更新成功!' 
        return True
    
    def write(self,cr,uid,ids,vals,context=None):
        print 'sale_order_line_new_write'
        super(sale_order_new_line,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,vals,context=None)
        else:
            return True
    
    
    def delete_to_ds(self,cr,uid,ids,context=None):
        
        column=[]
        if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
        else:
            info=self.browse(cr,uid,ids)
        pcb_line_obj=self.pool.get('pcb.info.line')
        pcb_line_ids=pcb_line_obj.search(cr,uid,[('pcb_info_many_line','=',info.pcb_info_id.id)])
        pcb_info_board_material=''
        pcb_info_test_type=''
        pcb_info_special_process=''
        if pcb_line_ids:
            for pcb_line_id in pcb_line_ids:
                pcb_line_info=pcb_line_obj.browse(cr,uid,pcb_line_id)
                if pcb_line_info.board_material:
                    pcb_info_board_material=pcb_info_board_material+pcb_line_info.board_material+';'
                if pcb_line_info.test_type:
                    pcb_info_test_type=pcb_info_test_type+pcb_line_info.test_type+';'
                if pcb_line_info.special_process:
                    pcb_info_special_process=pcb_info_special_process+pcb_line_info.special_process+';'
                
        column.append(info.price_sheet_id.lead_id.name)
        column.append(info.product_id)
        column.append('')
        column.append('')
        column.append('')
        column.append(info.pcb_info_id.custmer_goodscode)
        column.append(info.pcb_info_id.layer_count)
        column.append(info.pcb_info_id.finish_board_thickness)
        column.append(pcb_info_board_material)
        column.append(info.pcb_info_id.pcs_length)
        
        column.append(info.pcb_info_id.pcs_width)
        column.append(info.pcb_info_id.delivery_type)
        column.append(0)
        column.append(info.product_qty)
        column.append(info.price_unit)
        column.append(info.cost_ready_s)
        column.append(info.cost_plot_s)
        column.append(info.cost_test_s)
        column.append(info.cost_other_s)
        column.append(info.scrap_fee)
        
        column.append(0)
        column.append(info.delivery_date)
        column.append(info.delivery_date)
        column.append(info.back_sign_date)
        column.append(pcb_info_test_type)
        column.append(info.pcb_info_id.surface_treatment)
        column.append(pcb_info_special_process)
        column.append(info.customer_material_code)
        column.append(info.customer_order)
        column.append(info.customer_project_name)
        
        column.append(info.product_name)
        column.append(info.bar_code)
        column.append(info.sub_memo)
        
        
        column.append(info.sale_type)
        column.append(info.sale_order_new_id.partner_id.partner_code)
        column.append(info.sequence)
        column.append(info.name)
        column.append(info.pcb_info_id.source_file_name)
        column.append(info.sale_order_new_id.name)
        column.append(info.sale_order_new_id.sale_company)
        column.append('unlink')
        column.append('')
        if not info.sale_order_new_id.name:
               raise osv.except_osv(_('Error!'),_(u'合同编号或序号不存在，请检查！'))
        
        print column
        row=[]
        for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    print column[i]
                    row.append(str(column[i]))
                else:
                    row.append(column[i]) 
        row=tuple(row)
        print row
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)   
            cur=conn.cursor() 
            sql=''' exec pp_TCContracts_OE '%s','%s','%s','%s','%s','%s',%d,%f,'%s',%f,
                                           %f,%d,%f,%d,%f,%f,%f,%f,%f,%f,
                                           %f,'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                           '%s','%s','%s','%s',%d,'%s','%s','%s','%s','%s',
                                           '%s' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
        except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
            conn.commit()
            conn.close() 
            print '更新成功!' 
        return True
    
    def unlink(self,cr,uid,ids,context=None): 
       price_sheet_obj=self.pool.get('price.sheet')
       my=self.browse(cr,uid,ids[0])
       if my.state!='draft':
           raise osv.except_osv(_('Error!'),_(u'不是草稿状态，不能删除，请检查！'))
       for id in ids:
           object=self.browse(cr,uid,id)
       sale_order_new_id=object.sale_order_new_id.id
       line_ids=self.search(cr,uid,[('sale_order_new_id','=',sale_order_new_id),('id','=',ids[0])])
       for line_id in line_ids:
           line_info=self.browse(cr,uid,line_id)
           price_sheet_obj.write(cr,uid,line_info.price_sheet_id.id,{'is_quote':False})
       print sale_order_new_id,'sale_order_new_id'
       line_id=self.search(cr,uid,[('sale_order_new_id','=',sale_order_new_id),('id','!=',ids[0])])
       i=1
       for id in line_id:
          
           self.write(cr,uid,id,{'sequence':i})
           i=i+1
       self.delete_to_ds(cr,uid,ids,context=context)
       return super(sale_order_new_line,self).unlink(cr,uid,ids,context=context)
      
sale_order_new_line()


class mrp_production_new(osv.osv):
    _name='mrp.production.new'
    _description='MRP Production New'
    _order = "name desc"
    _type_list=[('new',u'新单'),('repeat',u'复投无更改'),('revise',u'复投有更改'),('eng_panel',u'工程分卡')]
    _columns={
              
        'name':fields.char(u'投产批次号', size=64, readonly=True),
        'sale_order_new_line_id':fields.many2one('sale.order.new.line',u'订单批次号'),
        'order_create_date':fields.datetime(u'投产日期'),
        'delivery_date':fields.date(u'交货日期'),
        'delivery_count':fields.integer(u'交货数量'),
        'product_qty':fields.integer(u'投入数量'),
        'panel_count':fields.integer(u'PNL数量'),
        'pcs_count':fields.integer(u'pcs数量'),
        'customer_name':fields.char(u'客户零件号',size=64),
        'product_id':fields.char(u'档案号',size=32,readonly=True),
        'sale_order_new_ids':fields.char(u'合同号',size=32,readonly=True),
      
        'price_sheet_id':fields.related('sale_order_new_line_id','price_sheet_id',type='many2one',relation='price.sheet',string=u'报价单号',readonly=True,store=True),
        'pcb_info_id':fields.related('price_sheet_id','pcb_info_id',type='many2one',relation='pcb.info',string=u'用户单号',readonly=True,store=True),
        'layer_count':fields.integer(u'层数',readonly=True,),
        'so_user_id':fields.many2one('res.users',u'下单人',readonly=True),
        'standard_days':fields.integer(u'标准天数',readonly=True),
        'partner_id'   :fields.char( u'客户',size=64,readonly=True),
        'ref':fields.char(u'客户代号',size=32,readonly=True),
        'cam_id':fields.many2one('res.users',u'接单人',),
        'type' :fields.selection(_type_list,u'投产类型', size=32,),
        'urgent_type':fields.many2one('select.selection',u'加急类型',domain=[('type','=','urgent_type')]),#加急方式：
        'company_name':fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂')],string=u'投产工厂'),
        'state':fields.selection([('draft',u'待计划投产'),('eng_recive',u'待工程接单'),('cancel',u'取消')],u'单据状态'),
        'store_qty':fields.integer(u'库存unit数',readonly=True),
        'memo':fields.text(u'投产备注'),
        'stop_state':fields.boolean(u'暂停'),
        }
    
    _defaults={
        'state':'draft',
        'so_user_id':lambda self,cr,uid,c:uid,
        'name':lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'mrp.production.new'),
        'order_create_date':fields.date.context_today,
        }
    
    def button_approve(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.stop_state==True:
            raise osv.except_osv(_('Error!'),_(u'投产单已经暂停不能审批！'))
        else:
            self.write(cr,uid,ids[0],{'state':'eng_recive'})
        return True
 
    def button_return(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('sale.order.new.line')
        count=0
        id=my.sale_order_new_line_id.id
        count=my.sale_order_new_line_id.wait_production_count + my.product_qty
        obj.write(cr,uid,id,{'wait_production_count':count,'state':'wait_confirm'})
        self.write(cr,uid,ids[0],{'state':'cancel'})
        #------同步到深圳---------
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)    
            cur=conn.cursor() 
            sql=''' exec PP_back_pinto_OE '%s','' '''  %(my.name)
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
        except:
            raise osv.except_osv(_('Error!'),_(u'反审批失败,请检查单据是否已经投产到工程!'))
        else:
            conn.commit()
            conn.close() 
            print u'更新成功!'
        return True
    
    
    def insert_to_ds(self,cr,uid,id,vals,context=None):
       user_obj=self.pool.get('res.users')
       employee_obj=self.pool.get('employee')
       user_info=user_obj.browse(cr,uid,uid)
       employeecode=user_info.login
       employee_ids=employee_obj.search(cr,uid,[('employeecode','=',employeecode),('company','=','csmtl')])
       if employee_ids:
           employee_info=employee_obj.browse(cr,uid,employee_ids[0])
           employeename=employee_info.employeename
       else:
           employeename=''
       print employeecode,'employeecode'
       print employeename,'employeename'
       if employeename=='':
           raise osv.except_osv(_('Error!'),_(u'下单人不存在，请联系系统部！'))
       
       
       column=[]
       info=self.browse(cr,uid,id)
       column.append(info.product_qty)
       column.append(info.store_qty)
       column.append(info.order_create_date)
       column.append(info.company_name)
       column.append(info.delivery_date)
       column.append(info.product_id)
       column.append('')
       column.append('')
       column.append('')
       column.append(info.name)
       
       column.append('')
       column.append('10')
       column.append(info.memo)
       column.append(info.price_sheet_id.lead_id.name)
       column.append('0')
       column.append('')
       
       column.append(employeename)
       column.append(info.type)
       column.append('create')
       column.append('')
       print column
       if not info.name:
               raise osv.except_osv(_('Error!'),_(u'投产批次号不存在，请检查！'))
       row=[]
       for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    row.append(str(column[i]))
                else:
                    row.append(column[i])  
       row=tuple(row)
       print row
       try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)    
            cur=conn.cursor() 
            sql=''' exec pp_TBOphasein_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s' '''  %row
            print sql.encode('gbk'),'sql TBOphasein'
            cur.execute(sql)    
            print '222221' 
       except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
       else:
            conn.commit()
            conn.close() 
            print u'更新成功!'
       return id
    
    def create(self,cr,uid,vals,context=None):
        print 'mrp_production_new create'
     
        
        id=super(mrp_production_new,self).create(cr,uid,vals,context=context)
        return self.insert_to_ds(cr,uid,id,vals,context=context)
    
    def update_to_ds(self,cr,uid,ids,context=None):
       column=[]
       user_obj=self.pool.get('res.users')
       employee_obj=self.pool.get('employee')
       user_info=user_obj.browse(cr,uid,uid)
       employeecode=user_info.login
       employee_ids=employee_obj.search(cr,uid,[('employeecode','=',employeecode),('company','=','csmtl')])
       if employee_ids:
           employee_info=employee_obj.browse(cr,uid,employee_ids[0])
           employeename=employee_info.employeename
       else:
           employeename=''
       if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
       else:
            info=self.browse(cr,uid,ids)
       
       column.append(info.product_qty)
       column.append(info.store_qty)
       column.append(info.order_create_date)
       column.append(info.company_name)
       column.append(info.delivery_date)
       column.append(info.product_id)
       column.append('')
       column.append('')
       column.append('')
       column.append(info.name)
       
       column.append('')
       column.append('10')
       column.append(info.memo)
       column.append(info.price_sheet_id.lead_id.name)
       column.append('0')
       column.append('')
       
       column.append(employeename)
       column.append(info.type)
       column.append('write')
       column.append('')
       print column
       if not info.name:
           raise osv.except_osv(_('Error!'),_(u'投产批次号不存在，请检查！'))
       row=[]
       for i in range(len(column)):
               
                if type(column[i])==type(u'中文'):
                    row.append(str(column[i]))
                else:
                    row.append(column[i])  
       row=tuple(row)
       print row
       try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)    
            cur=conn.cursor() 
            sql=''' exec pp_TBOphasein_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s' '''  %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)     
       except:
            raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
       else:
            conn.commit()
            conn.close() 
            print '更新成功!'  
       return True    
   
    def write(self,cr,uid,ids,vals,context=None):
        print 'mrp_production_new write'
        super(mrp_production_new,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True  
        
    def unlink(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state!='draft':
               raise osv.except_osv(_('Error!'),_(u'不是草稿状态，不能删除，请检查！'))  
        else:
             return super(mrp_production_new,self).unlink(cr,uid,ids)
        return True
    
mrp_production_new()

