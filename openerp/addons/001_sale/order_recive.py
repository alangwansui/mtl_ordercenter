#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
import pymssql
from openerp.osv import fields, osv
from openerp.tools.translate import _
import re
import datetime
#import win32ui
#import tkFileDialog  #可跨平台打开文件
import re,os,string,time
import string
server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'

class order_recive(osv.osv):
        _name='order.recive'
        _order = "create_date desc"
        
        def _domain_customer(self,cr,uid,ids,context=None):
            my=self.browse(cr,uid,ids[0])
            obj=self.pool.get('pcb.info')
            partner_ids=my.partner_ids
            re_pcb_info_id=my.re_pcb_info_id
            print re_pcb_info_id,'re_pcb_info_id'
            return True
        def read_file(self, cr, uid, ids, context=None):
            my=self.browse(cr,uid,ids[0])
            if not context: context = {}
            rec = self.browse(cr, uid, ids[0], context)
            data = rec.refile  
            self.write(cr,uid,ids[0],{'note':data.decode('base64')})
            note=my.note
            str='+0800'
            index=note.find(str)
            begin=index-21
            end=index-1
            str=note[begin:end]
            print str,'str'
            dict={'Jan':'1',
                   'Feb':'2',
                   'Mar':'3',
                   'Apr':'4',
                   'May':'5',
                   'Jun':'6',
                   'Jul':'7',
                   'Aug':'8',
                   'Sep':'9',
                   'Oct':'10',
                   'Nov':'11',
                   'Dec':'12',
                   }
            str_list=str.split(' ')
            print str_list,'list'
            time_str=str_list[2]+'-'+dict[str_list[1]]+'-'+str_list[0]+' '+str_list[3]
            time_str=datetime.datetime.strptime(time_str,"%Y-%m-%d %H:%M:%S") 
            print time_str
            print type(time_str)

            self.write(cr,uid,ids[0],{'email_date':time_str,'note':None,})
        
        _columns={
            'name':fields.char(u'接单单号',size=32,readonly=True),
            'is_repeat2order':        fields.boolean(u'复投单生成合同'),#复投单生成合同
            'is_repeat2price':        fields.boolean(u'复投到报价'),#复投到报价
            'recive_confirm':         fields.boolean(u'接受确认'),#接受确认
            'partner_ids':             fields.many2one('res.partners',u'客户',select=True,required=True),
            'partner_code':           fields.related('partner_ids','partner_code',type='char',relation='res.partners',string=u'客户代号',readonly=True),
            'priority':               fields.selection([('high',u'紧急'),('low',u'一般')],u'紧急状况',size=32),#紧急
            'note':                   fields.text(u'备注'),#备注
            'state':                  fields.selection([('draft',u'草稿'),('wait_pcb_info',u'待资料审批'),('wait_price',u'待报价审批'),('wait_sale',u'待合同审批'),('wait_production',u'待投产'),('refuse',u'作废'),('done',u'完成')],u'单据状态',size=32,readonly=True),
            'pcb_info_id':            fields.many2one('pcb.info',u'用户单',readonly=True),
			'recive_id':              fields.many2one('res.users',u'接单人'),#接单记录创建人
            'saleman':                fields.related('partner_ids','user_id',type='char',relation='res.partners',string=u'业务员',readonly=True,store=True),
            'create_date':            fields.datetime(u'创建日期',readonly=True,),#创建日期
			'approve_date':           fields.datetime(u'审批日期'),#审批日期
            'custmer_goodscode':     fields.char (u'零件号',size=64),#零件号
           
            'assessor_id':fields.many2one('employee',u'资料审核员',domain=[('is_sale_approve','=',True)]),
            'sale_type':fields.selection([('new',u'新单'),('repeat',u'复投无更改'),('revise',u'复投有更改')],u'接单类型'),
            'source_type':fields.many2one('select.selection',u'来源方式'),
            'org_file_name':fields.char(u'原文件名', size=64 ,readonly=False), 
            'refile':fields.binary(u'附件',),
            'fname':fields.char(u'附件名',size=128,readonly=True),
            'note':fields.char(u'附件内容'),
            'product_id':  fields.related('pcb_info_id', 'product_id', type='many2one',relation='product.product', string=u'档案号' ,readonly=True ),
            'email_date':fields.char(u'接收邮件时间',size=128,readonly=True),
            'spend_time':fields.float(u'耗时/小时'),
            
            're_pcb_info_id':fields.many2one('pcb.info',u'复投用户单',domain=[('state','=','done')]),
            'special_note':fields.related('partner_ids','special_note',type='text',relation='res.partners',string=u'此客户的特别提醒',store=True,readonly=True),#特别备注
            'user_note':fields.related('re_pcb_info_id','next_note',type='text',relation='pcb.info',string=u'此用户的特别提醒',store=True,readonly=True),
            'goodscode':fields.char(u'东烁档案号',size=32),
            'product_name':       fields.related('re_pcb_info_id','product_id',type='char',relation='pcb.info',string=u'档案号',store=True,readonly=True),
        
        
        }
        
        _sql_constraints=[('custmer_goodscode','unique(custmer_goodscode)','custmer_goodscode value must be unique')]
         
        _defaults={
            'state':lambda *a:'draft',
            'sale_type': lambda *a: 'new',
#            'name': lambda self, cr, uid, context:self.pool.get('ir.sequence').get(cr, uid, 'order.recive'), 
            'name':lambda obj, cr, uid, context:'/',
			'recive_id': lambda  self,cr,uid,c: uid,
            'priority':lambda *a:'low',
#            'create_date':lambda *a:time.strftime('%Y-%m-%d %H:%M:%S'), 
        }
        
        
        def repeat(self,cr,uid,ids,context=None):
            my=self.browse(cr,uid,ids[0])
            if my.sale_type=='repeat':
                self.write(cr,uid,ids[0],{'state':'wait_price'})
            return True

        def done(self,cr,uid,ids,context=None):
            
            self.write(cr,uid, ids,{'state':'done'})
            my=self.browse(cr,uid,ids[0])
            pi_obj=self.pool.get('pcb.info')
            res_partner=self.pool.get('res.partners')
            info=self.pool.get('pcb.info.line')
            gold=self.pool.get('gold.finger')
            partner_id=my.partner_ids.id
            res=res_partner.browse(cr,uid,partner_id)
            print res,'res'
            se=res.partner_general_id
            print se,'se'
            line=se.partner_general_requirements_ids_one
            obj_price=self.pool.get('price.sheet')
            sheet=obj_price.browse(cr,uid,my.id)
            obj=my.re_pcb_info_id
            print obj,'obj'
            sale=self.pool.get('sale.order.change')
            self.read_file(cr,uid,ids,context=None)
            self.write(cr,uid,ids[0],{'refile':None})
######################由于时区的问题取当前时间加8小时等于东八区的时间
            d1=datetime.timedelta(hours=8)
            d2=datetime.datetime.now()
            dates=str(d1+d2)[:19]
##########################################
            
            # 只有新单，需要创建用户单
            if my.sale_type=='new' and not my.pcb_info_id and se :
           
                    res_id=pi_obj.create(cr,uid,{    
                    'partner_id':my.partner_ids.id,
                    'responsible_id':my.assessor_id.id,
                    'receive_type':my.priority,
                    'order_recive_id':ids[0],
                    'packing_note':se.solder_colour,
                    'solder_colour':se.solder_colour,
                    'solder_variants':se.solder_variants,
                    'solder_type':se.solder_type,
                    'solder_via':se.solder_via,
                    'silk_colour':se.silk_colour,
                    'silk_variants':se.silk_variants,
                    'silk_type':se.silk_type,
                    'count_unit_package':se.per_quantity,
                    'add_delivery_chapter':se.add_delivery_chapter,
                    'provide_steel_net':se.provide_steel_net,
                    'provide_gerber':se.provide_gerber,
                    'confirm_gerber':se.confirm_gerber,
                    'packing_note':se.packing_note,
                    'delivery_order_request':se.delivery_order_request,
                    'partner_special_request':se.partner_special_request,
                    
                    
                    
                    })
                    
                    for i in line:
                        print i,'int'
                        res_line=info.create(cr,uid,{ 
                                    'pcb_info_many_line':res_id,
                                    'mark_request':i.mark_label,
                                    'request_with_goods':i.goods_label,
                                    'packing_type':i.packing_label
                                    })
                       
                    if res_id:
                        self.write(cr,uid,ids[0],{
                                                  'pcb_info_id':res_id,
                                                  'approve_date':dates,
                                                  })
                        self.spend_time(cr,uid,ids,context=None)
                        return {
                                'name':_("new  pcb_info"),
                                'type': 'ir.actions.act_window',
                                'res_model': 'pcb.info',
                                'view_mode': 'form',
                                'view_id': False,
                                'view_type': 'form',
                                'res_id':res_id,
                                'target': 'new',
                                }
            elif my.sale_type=='new' and not my.pcb_info_id and not se:
                 res_id=pi_obj.create(cr,uid,{    
                    'partner_id':my.partner_ids.id,
                    'responsible_id':my.assessor_id.id,
                    'receive_type':my.priority,
                    'order_recive_id':ids[0],})
                 if res_id:
                        self.write(cr,uid,ids[0],{
                                                  'pcb_info_id':res_id,
                                                  'approve_date':dates,
                                                  })
                        self.spend_time(cr,uid,ids,context=None)
                        return {'name':_("Convent pcb info"),
                            'view_mode': 'form',
                            'view_id': False,
                            'view_type': 'form',
                            'res_model': 'pcb.info',
                            'res_id': res_id,
                            'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'domain': [],
                    }
                       
            ############复投有更改########################
            elif my.sale_type=='revise' and my.re_pcb_info_id:
                res_id=pi_obj.create(cr,uid,{
                                        're_pcb_info_id':obj,
                                        'receive_type':my.priority,
                                        
                                        'source_file_name':obj.source_file_name,
                                        'layer_count':obj.layer_count,
                                        'product_material':obj.product_material,
                                        'inner_cu':obj.inner_cu,
                                        'out_cu':obj.out_cu,
                                        'solder_colour':obj.solder_colour,
                                        'solder_variants':obj.solder_variants,
                                        'solder_type':obj.solder_type,
                                        'solder_via':obj.solder_via,
                                        'contact':obj.contact,
                                        'phone':obj.phone,
                                      
                                        'partner_id':my.partner_ids.id,
                                        'custmer_goodscode':obj.custmer_goodscode,
                                        'basic_board_thickness':obj.basic_board_thickness,
                                        'finish_board_thickness':obj.finish_board_thickness, 
                                        'finish_inner_cu':obj.finish_inner_cu,
                                        'finish_out_cu':obj.finish_out_cu,
                                        'silk_colour':obj.silk_colour,
                                        'silk_variants':obj.silk_variants,
                                        'silk_type':obj.silk_type,
                                        'soft_version':obj.soft_version,
                                        'email':obj.email,
                                        
                                        
                                        
                                        'responsible_id':my.assessor_id.id,
                                        'order_recive_id':ids[0],
                                        'product_id':obj.product_id,
                                        'finish_tol_upper':obj.finish_tol_upper,       
                                        'finish_tol_lower':obj.finish_tol_lower,
                                        'surface_treatment':obj.surface_treatment,
                                        'au_area':obj.au_area,
                                        'surface_treatment_request':obj.surface_treatment_request,
                                        
                                        'allow_scrap_count':obj.allow_scrap_count,
                                        'allow_scrap_percent':obj.allow_scrap_percent,
                                        'plot_count':obj.plot_count,
                                        'vcut_angle':obj.vcut_angle,
                                        
                                        
                                        'csmtl_company':obj.csmtl_company,
                                        'szmtl_company':obj.szmtl_company,
                                        'provide_gerber':obj.provide_gerber,
                                        'provide_steel_net':obj.provide_steel_net,
                                        'confirm_gerber':obj.confirm_gerber,
                                        'pcs_length':obj.pcs_length,
                                        'pcs_width':obj.pcs_width,
                                        'unit_length':obj.unit_length,
                                        'unit_width':obj.unit_width,
                                        'panel_x':obj.panel_x,
                                        'panel_y':obj.panel_y,
                                        'delivery_type':obj.delivery_type,
                            
                            
                            
                                        'min_line_width':obj.min_line_width,
                                        'min_line_space':obj.min_line_space,
                                        'min_hole2line':obj.min_hole2line,
                                        'min_finish_hole':obj.min_finish_hole,
                                        
                                        'pcs_drill_count':obj.pcs_drill_count,
                                        'pcs_slot_count':obj.pcs_slot_count,
                                        'test_point_count':obj.test_point_count,
                                        'multi_panel':obj.multi_panel,
                                        
                                        'drill_density'        :obj.drill_density, 
                                        'test_point_density':obj.test_point_density,
                                        'route_length'    :obj.route_length,  
                                        'flexible_layer_count':obj.flexible_layer_count,
                                        
                                        'fill_core_count':obj.fill_core_count,
                                        'fill_pp_count':obj.fill_pp_count,
                                        'matrial_use_ratio':obj.matrial_use_ratio,
                                        'sepecial_board_size':obj.sepecial_board_size,
                                                
                                                
                                            
                                        'special_process_note':obj.special_process_note,
                                        'packing_note':obj.solder_colour,
                                        'delivery_order_request':obj.delivery_order_request,
                                        'partner_special_request':obj.partner_special_request,
                                        'next_note':obj.next_note,
                                        })   
                for i in obj.pcb_info_many:
                    if i.board_material or i.special_process or i.route_type or i.accept_standard or i.test_type or i.mark_request or i.request_with_goods or i.packing_type:               
                        res_line=info.create(cr,uid,{ 
                                        'pcb_info_many_line':res_id,
                                        'board_material':i.board_material,
                                        'special_process':i.special_process,
                                        'route_type':i.route_type,
                                        'accept_standard':i.accept_standard,
                                        'test_type':i.test_type,
                                        'mark_request':i.mark_request,
                                        'request_with_goods':i.request_with_goods,
                                        'packing_type':i.packing_type,
                                        })
                if obj.gold_finger_id and res_id:
                    
                    go=gold.create(cr,uid,{
                                       
                                        'finger_count':obj.gold_finger_id.finger_count,
                                        'au_thick':obj.gold_finger_id.au_thick,
                                        'ni_thick':obj.gold_finger_id.ni_thick,
                                        'finger_length':obj.gold_finger_id.finger_length,
                                        'finger_width':obj.gold_finger_id.finger_width,
                                        'bevel_edge':obj.gold_finger_id.bevel_edge,
                                        'note':obj.gold_finger_id.note,
                                        
                                        })
                    
                if res_id:
                        self.write(cr,uid,ids[0],{
                                                  'pcb_info_id':res_id,
                                                  'approve_date':dates,
                                                  })
                     
                        
                        self.spend_time(cr,uid,ids,context=None)
                        sale.create(cr,uid,{'pcb_info_id':res_id,
                                            'response_id':uid,
                                            'type':'repeat_change',
                                            'state':'draft'
                                            })
                       
                        return {
                                'name':_("new  pcb_info"),
                                'type': 'ir.actions.act_window',
                                'res_model': 'pcb.info',
                                'view_mode': 'form',
                                'view_id': False,
                                'view_type': 'form',
                                'res_id':res_id,
                                'target': 'new',
                                }
            if my.sale_type=='revise' and my.re_pcb_info_id and obj.gold_finger_id:
                    print res_id.name
                    gold.write(cr,uid,go,{'name':res_id.name})
                        
            ####复投无更改###################
            
            elif my.sale_type=='repeat' and my.re_pcb_info_id:
                print obj.pcs_length,'pcs_length'
                res_id=pi_obj.create(cr,uid,{
                                        're_pcb_info_id':obj,
                                        'receive_type':my.priority,
                                        'source_file_name':obj.source_file_name,
                                        'layer_count':obj.layer_count,
                                        'product_material':obj.product_material,
                                        'inner_cu':obj.inner_cu,
                                        'out_cu':obj.out_cu,
                                        'solder_colour':obj.solder_colour,
                                        'solder_variants':obj.solder_variants,
                                        'solder_type':obj.solder_type,
                                        'solder_via':obj.solder_via,
                                        'contact':obj.contact,
                                        'phone':obj.phone,
                                        
                                        
                                        'partner_id':my.partner_ids.id,
                                        'custmer_goodscode':obj.custmer_goodscode,
                                        'basic_board_thickness':obj.basic_board_thickness,
                                        'finish_board_thickness':obj.finish_board_thickness, 
                                        'finish_inner_cu':obj.finish_inner_cu,
                                        'finish_out_cu':obj.finish_out_cu,
                                        'silk_colour':obj.silk_colour,
                                        'silk_variants':obj.silk_variants,
                                        'silk_type':obj.silk_type,
                                        'soft_version':obj.soft_version,
                                        'email':obj.email,
                                        
                                        
                                        
                                        'responsible_id':my.assessor_id.id,
                                        'order_recive_id':ids[0],
                                        'product_id':obj.product_id,
                                        'finish_tol_upper':obj.finish_tol_upper,       
                                        'finish_tol_lower':obj.finish_tol_lower,
                                        'surface_treatment':obj.surface_treatment,
                                        'au_area':obj.au_area,
                                        'surface_treatment_request':obj.surface_treatment_request,
                                        
                                        'allow_scrap_count':obj.allow_scrap_count,
                                        'allow_scrap_percent':obj.allow_scrap_percent,
                                        'plot_count':obj.plot_count,
                                        'vcut_angle':obj.vcut_angle,
                                        
                                        
                                        'csmtl_company':obj.csmtl_company,
                                        'szmtl_company':obj.szmtl_company,
                                        'provide_gerber':obj.provide_gerber,
                                        'provide_steel_net':obj.provide_steel_net,
                                        'confirm_gerber':obj.confirm_gerber,
                                        'pcs_length':obj.pcs_length,
                                        'pcs_width':obj.pcs_width,
                                        'unit_length':obj.unit_length,
                                        'unit_width':obj.unit_width,
                                        'panel_x':obj.panel_x,
                                        'panel_y':obj.panel_y,
                                        'delivery_type':obj.delivery_type,
                            
                            
                            
                                        'min_line_width':obj.min_line_width,
                                        'min_line_space':obj.min_line_space,
                                        'min_hole2line':obj.min_hole2line,
                                        'min_finish_hole':obj.min_finish_hole,
                                        
                                        'pcs_drill_count':obj.pcs_drill_count,
                                        'pcs_slot_count':obj.pcs_slot_count,
                                        'test_point_count':obj.test_point_count,
                                        'multi_panel':obj.multi_panel,
                                        
                                        'drill_density'        :obj.drill_density, 
                                        'test_point_density':obj.test_point_density,
                                        'route_length'    :obj.route_length,  
                                        'flexible_layer_count':obj.flexible_layer_count,
                                        
                                        'fill_core_count':obj.fill_core_count,
                                        'fill_pp_count':obj.fill_pp_count,
                                        'matrial_use_ratio':obj.matrial_use_ratio,
                                        'sepecial_board_size':obj.sepecial_board_size,
                                                
                                                
                                            
                                        'special_process_note':obj.special_process_note,
                                        'packing_note':obj.solder_colour,
                                        'delivery_order_request':obj.delivery_order_request,
                                        'partner_special_request':obj.partner_special_request,
                                        'next_note':obj.next_note,
                                        'state':'done',
                                        })   
                for i in obj.pcb_info_many:
                    if i.board_material or i.special_process or i.route_type or i.accept_standard or i.test_type or i.mark_request or i.request_with_goods or i.packing_type:               
                        res_line=info.create(cr,uid,{ 
                                        'pcb_info_many_line':res_id,
                                        'board_material':i.board_material,
                                        'special_process':i.special_process,
                                        'route_type':i.route_type,
                                        'accept_standard':i.accept_standard,
                                        'test_type':i.test_type,
                                        'mark_request':i.mark_request,
                                        'request_with_goods':i.request_with_goods,
                                        'packing_type':i.packing_type,
                                        })
                if res_id:
                    s=self.write(cr,uid,ids[0],{
                                                'pcb_info_id':res_id,
                                                'approve_date':dates,})
                    
                    self.spend_time(cr,uid,ids,context=None)
#                    pi_obj.write(cr,uid,res_id,{'state':'done'})
                    res_id=obj_price.create(cr,uid,{
                                        'product_number' :1,
                                        'partner_id':my.partner_ids.id,
                                        'pcb_info_id':res_id,
                                        'responsible_id':uid,
                                        'delivery_leadtime':1,
                                        'lead_id':my.id,
                                        'recive_type':my.sale_type,
                                        })   
 
                    return {
                                'name':_("new  price sheet"),
                                'type': 'ir.actions.act_window',
                                'res_model': 'price.sheet',
                                'view_mode': 'form',
                                'view_id': False,
                                'view_type': 'form',
                                'res_id':res_id,
                                'target': 'new',
                                }
            elif my.sale_type!='new' and not my.re_pcb_info_id:
                raise osv.except_osv(_('Error!'),_('接单类型不是新单需选择复投用户单!'))
                
            else:
                raise osv.except_osv(_('Error!'),_('接单类型必须是新单!'))
            self.spend_time(cr,uid,ids,context=None)
            print my.pcb_info_id.id,'my.pcb_info_id.id'
            return True
            
#----------------------数据写入东烁---------------------------------      
        def insert_to_ds(self,cr,uid,id,vals,context=None):  
             column=[]
             customer_type=''
            # partner_obj=self.pool.get('res.partners')
             
             info=self.browse(cr,uid,id)

             if info.re_pcb_info_id.order_recive_id:
                 recive_name=info.re_pcb_info_id.order_recive_id.name
             else:
                 recive_name=''
             if info.saleman:
                 saleman_employeecode=info.saleman
             else:
                 saleman_employeecode=''
             if info.assessor_id:
                assessor_code=info.assessor_id.employeecode
             else:
                assessor_code=''
             sepcial_note=''
             if info.special_note:
                 sepcial_note=sepcial_note+info.special_note
             if info.user_note:
                 sepcial_note=sepcial_note+info.user_note
             column.append(info.partner_ids.name)
             column.append(info.partner_ids.partner_code)
             column.append(info.fname)
             column.append(0)
             column.append('')
             column.append(0)
             column.append(recive_name)
             column.append(info.sale_type)
             column.append('')
             column.append(assessor_code)
             column.append(0)
             column.append('')
             column.append('')
             column.append(sepcial_note)
             column.append('')
             
             column.append(info.name)
             column.append('create')
             column.append('')
             column.append(saleman_employeecode)
             if not info.name:
                 raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
             row=[]
             for i in range(len(column)):
                 if type(column[i])==type(u'中文'):
                     print column[i]
                     row.append((column[i]).encode('utf-8'))
                 else:
                     row.append(column[i])    
             row=tuple(row)
    
             try:
                conn=pymssql.connect(server=server,user=user,password=password,database=database)
                cur=conn.cursor()
                
                sql='''exec pp_TBproduction_JD_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                                  '%s','%s','%s','%s','%s','%s','%s','%s','%s' ''' %row
                sql=sql.decode('utf-8')
                print sql
                cur.execute(sql) 
             except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
             else:
                
                conn.commit()
                conn.close() 
                print u'更新成功'
             return id

        def create(self,cr,uid,vals,context=None):
          print 'order.recive','create'
          if vals.get('name','/')=='/':
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'order.recive') or '/'
         
          id=super(order_recive,self).create(cr,uid,vals,context=context)
          return id and self.insert_to_ds(cr,uid,id,vals,context=context) 
      
        def update_to_ds(self,cr,uid,ids,context=None):
             column=[]
             if type(ids)==type(column):
                info=self.browse(cr,uid,ids[0])
             else:
                info=self.browse(cr,uid,ids)
             if info.re_pcb_info_id.order_recive_id:
                recive_name=info.re_pcb_info_id.order_recive_id.name
             else:
                recive_name=''
             print info.re_pcb_info_id.order_recive_id,'info.re_pcb_info_id.order_recive_id'
             print recive_name,'recive_name'
             if info.saleman:
                 saleman_employeecode=info.saleman
             else:
                 saleman_employeecode=''
             if info.assessor_id:
                assessor_code=info.assessor_id.employeecode
             else:
                assessor_code=''
             sepcial_note=''
             if info.special_note:
                 sepcial_note=sepcial_note+info.special_note
             if info.user_note:
                 sepcial_note=sepcial_note+info.user_note
             column.append(info.partner_ids.name)
             column.append(info.partner_ids.partner_code)
             column.append(info.fname)
             column.append(0)
             column.append('')
             column.append(0)
             column.append(recive_name)
             column.append(info.sale_type)
             column.append('')
             column.append(assessor_code)
             column.append(0)
             column.append('')
             column.append('')
             column.append(sepcial_note)
             column.append('')
             
             column.append(info.name)
             column.append('write')
             column.append('')
             column.append(saleman_employeecode)
             if not info.name:
                 raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
             row=[]
             for i in range(len(column)):
                 if type(column[i])==type(u'中文'):
                     print column[i]
                     row.append((column[i]).encode('utf-8'))
                 else:
                     row.append(column[i])    
             row=tuple(row)
    
             try:
                conn=pymssql.connect(server=server,user=user,password=password,database=database)
                cur=conn.cursor()
                
                sql='''exec pp_TBproduction_JD_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                                  '%s','%s','%s','%s','%s','%s','%s','%s','%s' ''' %row
                sql=sql.decode('utf-8')
                print sql
                cur.execute(sql) 
             except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
             else:
                
                conn.commit()
                conn.close() 
                print u'更新成功'
                return True
            
        def write(self,cr,uid,ids,vals,context=None):
            print 'order.recive','write'
            super(order_recive,self).write(cr,uid,ids,vals,context=context)
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
             if info.re_pcb_info_id.order_recive_id:
                     recive_name=info.re_pcb_info_id.order_recive_id.name
             else:
                     recive_name=''
             column=[]
             if type(ids)==type(column):
                info=self.browse(cr,uid,ids[0])
             else:
                info=self.browse(cr,uid,ids)
             if info.re_pcb_info_id.order_recive_id:
                recive_name=info.re_pcb_info_id.order_recive_id.name
             else:
                recive_name=''
             print info.re_pcb_info_id.order_recive_id,'info.re_pcb_info_id.order_recive_id'
             print recive_name,'recive_name'
             if info.saleman:
                 saleman_employeecode=info.saleman
             else:
                 saleman_employeecode=''
             if info.assessor_id:
                assessor_code=info.assessor_id.employeecode
             else:
                assessor_code=''
             sepcial_note=''
             if info.special_note:
                 sepcial_note=sepcial_note+info.special_note
             if info.user_note:
                 sepcial_note=sepcial_note+info.user_note
             column.append(info.partner_ids.name)
             column.append(info.partner_ids.partner_code)
             column.append(info.fname)
             column.append(0)
             column.append('')
             column.append(0)
             column.append(recive_name)
             column.append(info.sale_type)
             column.append('')
             column.append(assessor_code)
             column.append(0)
             column.append('')
             column.append('')
             column.append(sepcial_note)
             column.append('')
             
             column.append(info.name)
             column.append('unlink')
             column.append('')
             column.append(saleman_employeecode)
             if not info.name:
                 raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
             row=[]
             for i in range(len(column)):
                 if type(column[i])==type(u'中文'):
                     print column[i]
                     row.append((column[i]).encode('utf-8'))
                 else:
                     row.append(column[i])    
             row=tuple(row)
    
             try:
                conn=pymssql.connect(server=server,user=user,password=password,database=database)
                cur=conn.cursor()
                
                sql='''exec pp_TBproduction_JD_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                                  '%s','%s','%s','%s','%s','%s','%s','%s','%s' ''' %row
                sql=sql.decode('utf-8')
                print sql
                cur.execute(sql) 
             except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
             else:
                
                conn.commit()
                conn.close() 
                print u'更新成功'
                return True
        
        def unlink(self, cr, uid, ids, context=None):
            my=self.browse(cr,uid,ids[0])
            if my.state!='draft':
                 raise osv.except_osv(_('Error!'),_(u'状态完成时不能删除！'))
            else:
                print 'order.revie','unlink'
                self.delete_to_ds(cr,uid,ids,context=None)
                return super(order_recive,self).unlink(cr,uid,ids)

        
#########################接收邮件时间
        def recive_email(self,cr,uid,ids,context=None):
             # 1表示打开文件对话框
            dlg = None#  win32ui.CreateFileDialog(1)
            dlg.DoModal()
            filename = dlg.GetPathName()  # 获取选择的文件名称
            my=self.browse(cr,uid,ids[0])
            note=my.note
            str='Date:'
            index=note.find(str)
            begin=index-32
            end=index-7
            s=note[begin:end]
            print s,'s'
            str_list=s.split(' +080')[0]
            print str,'str'
            dict={'Jan':'1',
                   'Feb':'2',
                   'Mar':'3',
                   'Apr':'4',
                   'May':'5',
                   'Jun':'6',
                   'Jul':'7',
                   'Aug':'8',
                   'Sep':'9',
                   'Oct':'10',
                   'Nov':'11',
                   'Dec':'12',
                   }
 #           str_list=str.split(' ')
            print str_list
            time_str=str_list[2]+'-'+dict[str_list[1]]+'-'+str_list[0]+' '+str_list[3]
            time_str=datetime.datetime.strptime(time_str,"%Y-%m-%d %H:%M:%S") 
            self.write(cr,uid,ids[0],{'email_date':time_str,'note':None,})
            return True
               
  
            
        
        def spend_time(self,cr,uid,ids,context=None):
            my=self.browse(cr,uid,ids[0])
            start_time=my.email_date
            end_time=my.approve_date
            if not start_time:
                raise osv.except_osv(_('Error!'),_(u'附件文件名不能为空！'))
            end_times=datetime.datetime.fromtimestamp(time.mktime(time.strptime(end_time,"%Y-%m-%d %H:%M:%S")))
            print end_times,'end_times'
            start_times = datetime.datetime.fromtimestamp(time.mktime(time.strptime(start_time,"%Y-%m-%d %H:%M:%S")))
            print start_times,'start_times'
            total_time=round((end_times-start_times).seconds/3600.0,2)+(end_times-start_times).days*24
            print total_time,'total_time'
            self.write(cr,uid,ids[0],{'spend_time':total_time})
            return True
        #####导入东烁用户单
        def import_data(self,cr,uid,ids,context=None):
            
            info=self.browse(cr,uid,ids[0])
            print info.partner_ids,'info.partner_ids.partner_code'
            if not info.goodscode:
                raise osv.except_osv(_('Error!'),_('请输入档案号!'))
            pcb_info_obj=self.pool.get('pcb.info')
            partner_obj = self.pool.get('res.partners')
            line_obj=self.pool.get('pcb.info.line')
            gold_finger_obj=self.pool.get('gold.finger')
            
            
            pcb_info_ids=pcb_info_obj.search(cr,uid,[('product_id','=',info.goodscode),('partner_id','=',info.partner_ids.id)])
            print pcb_info_ids,'pcb_info_ids'
            if pcb_info_ids:
                raise osv.except_osv(_('Error!'),_('此档案号已经存在,无须再导入!'))
            server='192.168.10.2'
            user='sa'
            password='719799'
            database='mtlerp-running'
            b=[]
            conn = pymssql.connect(server=server , user=user, password=password,database=database)
            cur = conn.cursor()       
            sql=''' select  CustmerName,GoodsName,GoodsMaterial,LayerCount,OuterCopper,InnerCopper,GoodsHeight,Tolerance,OtherRequest1,SGoldFingerCount,
                    SGoldFingerAngle,CoatRequest,OtherRequest,HoleLayer,ManuFacturer,FColor,FType,ViaFType,TechnicModelCode,CColor,
                    CType,IsSmdAllow,ShapeType,TestEquipType,TestStandard,TagRequest,PackingType,ReportRequest,SU,RejectAllow,
                    CustmerGoodsCode,SoftwareVer,ShapeRulerType,GoodsLength,RequestNo,GoodsWidth,MType,GoodsSLength,GoodsSWidth,CustmerFaxCode,
                    CustmerHandler,CustmerTel,VcutDegree,GoodsCode,SubMemo,IsMemoPrompt,ColorTypeC,ColorTypeF,BaseBoard,FOCopper,
                    FICopper,xSU,ySU,IsET,RejectAllow1,Blend,MinLineWid,MinBetween,MinSegregate,MinAperture,
                    UpdateGoodsCode,HalfWholeDepth,HalfWholeTance,PackingQty,NeedToSolve,BoardOrigin,IsGangWang,IsGerber,IsSureGerber,SGoldFingerCopper,
                    TestQty,Lightbqyt,otherholeqty,NotchQty1,allholeqty,custmercode,billcode
                    from VBproduction_OE where custmercode1='%s' and goodscode='%s'  ''' %(info.partner_ids.partner_code,info.goodscode)
                    
            print sql,'sql'
            cur.execute(sql) 
            s=cur.fetchall()
            print s
            if not s:
               raise osv.except_osv(_('Error!'),_('档案号或客户代号在东烁中不存在,请检查!')) 
            b=[]
            for row1 in s:
                a=[]
                
                for i in range(len(row1)):
                    type1=type(u'中文')
                    
                    if type(row1[i])==type1:
                        a.append((''.join(map(lambda x: "%c" % ord(x), list(row1[i]))).decode('gbk')))
                    else:
                        a.append(row1[i])
                b.append(a)
            
            for row in b:  
                    print row[76].encode('gbk'),'row[76].encode(gbk)'
                    partner_ids=partner_obj.search(cr,uid,[('ds_code','=',row[75])])
                   
                    gold_finger_id=gold_finger_obj.create(cr,uid,{
                                                                  'name':row[76],
                                                                  'finger_count':row[9],
                                                                  'bevel_edge':row[10],
                                                                  'note':row[69],
                                                                  })
                    id=pcb_info_obj.create(cr,uid,{
                                           'name':row[76],
                                           'source_file_name':row[1],
                                           'layer_count':row[3],
                                           'product_material':row[65],
                                           'inner_cu':row[5],
                                           'out_cu':row[4],
                                           'solder_colour':row[15],
                                           'solder_variants':row[47],
                                           'solder_type':row[16],
                                           'solder_via':row[17],
                                           'contact':row[40],
                                           'phone':row[41],
                                           
                                           'partner_id':partner_ids[0],
                                           'custmer_goodscode':row[30],
                                           'basic_board_thickness':row[48],
                                           'finish_board_thickness':row[6],
                                           'finish_inner_cu':row[50],
                                           'finish_out_cu':row[49],
                                           'silk_colour':row[19],
                                           'silk_variants':row[46],
                                           'silk_type':row[20],
                                          # 'soft_version':row[31],
                                           'email':row[39],
                                           
                                           
                                           'product_id':row[43],
                                           'ds_tolerance':row[7],
                                           'surface_treatment':row[8],
                                           'surface_treatment_request':row[11],
                                           'gold_finger_id':gold_finger_id,
                                           'allow_scrap_count':row[29],
 #                                          'allow_scrap_percent':row[54],
                                           'vcut_angle':row[42],
                                           
                                           
                                           'provide_gerber':row[67],
                                           'provide_steel_net':row[66],
                                           'confirm_gerber':row[68],
                                           'pcs_length':row[37],
                                           'pcs_width':row[38],
                                           'unit_length':row[33],
                                           'unit_width':row[35],
                                           'panel_x':row[51],
                                           'panel_y':row[52],
                                           
                                           'special_process_note':row[44],
                                           
                                           
                                           'min_line_width':row[56],
                                           'min_line_space':row[57],
                                           'min_hole2line':row[58],
                                           'min_finish_hole':row[59],
                                           
                                           
                                           'pcs_drill_count':row[74],
                                           'pcs_slot_count':row[73],
                                           'test_point_count':row[70],
                                           
                                           })
                    
                    line_obj.create(cr,uid,{
                                            'pcb_info_many_line':id,
                                            'board_material':row[2],
                                            'special_process':row[12],
                                            'route_type':row[23],
                                            'accept_standard':row[24],
                                            'test_type':row[23],
                                            'mark_request':row[25],
                                            'request_with_goods':row[27],
                                            'packing_type':row[26],
                                            })
    
                    
                    ###创建档案号时同时创建一张档案号清单
                    self.pool.get('pcb.list').create(cr,uid,{'name':row[43],
                                                     'pcb_info_id':id,
                                                     'partner_id':partner_ids[0],
                                                     })
            conn.commit()
            cur.close()
            conn.close()
            return True
            
    
order_recive()

