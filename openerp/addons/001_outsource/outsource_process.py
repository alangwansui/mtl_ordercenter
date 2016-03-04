# -*- coding: utf-8 -*-

from osv import fields, osv
import time

from decimal_precision import decimal_precision as dp

import netsvc
import string
import psycopg2

import xmlrpclib #调用远程服务端对象模块
import re        #正则表达式（过滤条件）
import sys       #与python的内置模块有关
import os         #与python的内置模块有关
from tools.translate import _
import tools
import base64
import ftplib
import psycopg2
import ftplib
import socket  
import smtplib
from email.mime.text import MIMEText 
import shutil   #复制文件
from shutil import copy
import _mssql
import xlrd    #处理电子表格的模块
##process args info
class outsource_args(object):
    args_dic={}
    def __init__(self,prc_type,args_list=None):
        if not args_list:
            args_list=[]
        if prc_type not in outsource_args.args_dic:
            outsource_args.args_dic[prc_type]=args_list
        else:
            if not outsource_args.args_dic[prc_type] and args_list:
                outsource_args.args_dic[prc_type]=args_list
    
    def get_process_args(self,prc_type):
        if not prc_type:
            raise 
        try:
            args=outsource_args.args_dic[prc_type]
            return args
        except KeyError:
            print '%s not found in args_dic' % prc_type
            return False
        
class outsource_data(osv.osv):
    _name='outsource.data'
    _description = "outsource data"
   
    _columns = {
         ##outsource public field
     
        'applicant_id':fields.many2one('res.users','applicant_id'),
        'create_date':fields.datetime('create_date',readonly=True,select=True),#创建时间
       
        #'contact_telephone'
        
        ##public
        
        ##outsource apply field:
        'finish_time':fields.datetime('finish_time'),#回货时间
        'qty_receive':fields.integer('qty_receive'),#回货pcs数量
        'qty_pnl_receive':fields.integer('qty_pnl_receive'),# 回货PNL数量
#        'dpt_id':fields.many2one('hr.department','dpt_id'),
        'dpt_id':fields.related('applicant_id','context_department_id',type='many2one',relation='hr.department',string='dpt_id',readonly=True),
        'applicant_note':fields.text('applicant_note'),
        ##apply
        
        ##outsource process field:
        'process_send_time':fields.datetime('process_send_time'),#外协产品发出时间
        'delivery_time':fields.datetime('delivery_time'),#外协产品收货时间

       
    }
    _defaults = {
                
    }
    
outsource_data()




class outsource_apply(osv.osv):
    _name='outsource.apply'
    _rec_name='outsource_number'
    _inherit='outsource.data'
    _state_list=[(i,i) for i in ('draft','w_director','w_supervisor','w_quality','plan_director','w_gmanager','w_outsource','w_receive','done')]
    _out_list=[(i,i) for i in ('drill_outsource','flying_probe','shape_gong_side','shape_VCUT','VCUT+ gong_side','other')]
    _columns={
        'outsource_number':fields.char('outsource_number',size=64,required=True,select=True),       
        'outsource_lines_ids':fields.one2many('outsource.process.lines','outsource_apply_id','outsource_lines_ids'),
        'outsource_type':fields.selection(_out_list,'outsource_type',size=32,required=True),
 #       'outsource_type':fields.many2one('select.selection','outsource_type'),
        'state':fields.selection( _state_list,'State', size=64, required=False, translate=True, readonly=True,),
        'director_note':fields.text('director_note'),
        'plan_note':fields.text('plan_note'),
        'outsource_note':fields.text('outsource_note'),
        'gmanager_note':fields.text('gmanager_note'),
        'gmanager_sel':fields.selection([('agree','agree'),('disagree','disagree')],'gmanager_sel',size=32,),
    }

    _defaults = {
                 'state':'draft',
                 'gmanager_sel':lambda *a:'agree',
                'applicant_id':lambda self,cr,uid,context:uid,
                'outsource_number':lambda self,cr,uid,context:self.pool.get('ir.sequence').get(cr,uid,'Outsource.apply'),
    }
    
    def updata_state(self, cr, uid, ids, state=None, state_filter=None, **args):
        org_state=self.browse(cr,uid,ids[0]).state
        rec=self.write(cr, uid, ids, {'state':state})
        self.action_update_state(cr,uid,ids,state)
        
        return True
    
    def action_update_state(self,cr,uid,ids,state=None,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_rec=my.outsource_lines_ids
        line_obj=self.pool.get('outsource.process.lines')
        
        if lines_rec:
            for line in lines_rec:
                if line.state != state:
                    line_id=line.id
                    line=line_obj.write(cr,uid,line_id,{'state':state,})
                   
                    
        return True    
   
    
    def check_outsource_type(self, cr, uid, ids,type_list=None,context=None):
        my=self.browse(cr,uid,ids[0])
        type_ls=['drill_outsource','flying_probe','shape_VCUT','shape_gong_side','VCUT+ gong_side','other',]
        t_list=[]
        f_list=[]
       
        for i in range(6):
            if type_list[i]:
                t_list.append(type_ls[i])
            elif not type_list[i]:
                f_list.append(type_ls[i])
        if my.outsource_type=='flying_probe':
            flg=self.check_product_cost(cr, uid, ids, context)
            if flg:
                if my.outsource_type in t_list and len(t_list) in [1,2,3]:
                    return True
                else:
                    return False
            else:
                if my.outsource_type in t_list and len(t_list) in [1,3,]:
                    return True
                else:
                    return False
            
        else:
            if my.outsource_type in t_list:
                return True
            elif my.outsource_type in f_list:
                return False
            
    def check_approve_position(self,cr,uid,ids,position=None,uid_flg=False,context=None):
        flg=self.check_process_lines(cr,uid,ids,context)
        if flg:
            if (not position):
                raise TypeError('argument position cant be None')
            resp_uid = self.browse(cr,uid,ids[0]).applicant_id.id
            resp_dptid = self.pool.get('res.users').browse(cr,uid,resp_uid).context_department_id
  
            group_ids=self.pool.get('res.groups').search(cr,uid,[('name', '=', position)])
            if uid==1: 
                if uid_flg:
                    return True
                else:
                    return False
            else:
                if (group_ids):
                    dpt_post_list=self.pool.get('res.users').search(cr,uid, [
                                        ('groups_id','=',group_ids[0]),
                                        ('context_department_id','=',resp_dptid.id),                    
                    ])
                    if (dpt_post_list):
                        return True
                return False
   
    def check_product_cost(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines=my.outsource_lines_ids
        flg=False
        if lines:
            for line in lines:
                pcs_cost=line.product_qty * line.pcs_price_units
                pnl_cost=line.qty_pnl * line.pnl_price_units
                if pcs_cost >= 1500.0:
                    flg=True
                elif pnl_cost >=1500.0:
                    flg=True
        else:
            flg=True
                    
        return flg
    
    def check_process_lines(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines=my.outsource_lines_ids
        if not lines:
            raise osv.except_osv(('process lines error:'),('process lines not found!,please check..'))
        return True
    
    def action_outsource_process(self,cr,uid,ids,context=None):
        self.updata_state(cr,uid,ids,state='w_outsource')
        my=self.browse(cr,uid,ids[0])
        process_obj=self.pool.get('outsource.process')
        lines_obj=self.pool.get('outsource.process.lines')
        lines_rec=my.outsource_lines_ids
        line_data=[(5,)]
        
        applicant_id=False
        if uid != 1:
            applicant_id=my.applicant_id.id
        process_type=my.outsource_type
        if lines_rec and len(lines_rec)==1:
            for line in lines_rec:
                line_dic=lines_obj.read(cr,uid,line.id)
                del line_dic['create_date']
                line_dic['outsource_apply_id']=line['outsource_apply_id'].id
                if process_type:
                    line_dic['process_type']=process_type
                line_data.append((0,0,line_dic))

#            process_obj.create(cr,uid,{'applicant_id':applicant_id,'outsource_delivery_ids':line_data})
        
        return True
    
    def check_gmanager_sel(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.gmanager_sel=='disagree':
            #if not my.gmanager_note:
            #   raise osv.except_osv(('note error:'),('note info not found when idea is disagree....'))
            return False
        else:
            return True
        
    def production_read(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        process_obj=self.pool.get('outsource.process.lines')
        if my.outsource_lines_ids:
            for line in my.outsource_lines_ids:
                process_obj.production_read(cr,uid,[line.id],context=context)
                
        return True
    
    
outsource_apply()



class outsource_process (osv.osv):
    _name='outsource.process'
    _inherit='outsource.data'
    _rec_name='outsource_number'
    _order='create_date desc'
    _description = "outsource process"
    _state_list=[(i,i) for i in ('draft','w_document','w_receive','done')]
#    _outsource_types=[(i,i) for i in ('sink_gold','sink_silver','sink_Sn','spray_Sn(have pb)','spray_Sn(nhav pb)','gold_finger_plated',
#                                   'gold_plated','OSP','hot_equating(have pb)','brush_plated_board','plasma_process',
#                                   'hot_equating(not have )','drill_outsource','flying_probe','bf_laminate_pre',
#                                   'shape_VCUT','shape_gong_side','VCUT+ gong_side','other','laser_drill','wire_drawing',)]
  
    def _info_get(self,cr,uid,ids,field_name,args,context=None):
        res={}
        arg_obj=self.pool.get('outsource.cost.argument')
        for id in ids:
            my=self.browse(cr,uid,id)
            do_type='double_board'
            mu_type='much_layer_board'
            do_area=0.0
            mu_area=0.0
          
            
            do_ser=arg_obj.search(cr,uid,[('board_type','=',do_type),('outsource_partner_id','=',my.partner_id.id)])
            mu_ser=arg_obj.search(cr,uid,[('board_type','=',mu_type),('outsource_partner_id','=',my.partner_id.id)])
            delivery_lines=my.outsource_delivery_ids
            if field_name=='double_board_area':    
                wh_reduce=0.0
                lh_reduce=0.0
               
                if do_ser:
                    arg_rec=arg_obj.browse(cr,uid,do_ser[0])
                    wh_reduce=arg_rec.default_width_reduce
                    lh_reduce=arg_rec.default_length_reduce
                
                for line in delivery_lines:
                    if line.board_type ==do_type:
#                        line_area=(line.pnl_width - wh_reduce) * (line.pnl_length - lh_reduce) /(100 *10000)
                        line_area=(line.pnl_width  * line.pnl_length) /(100 *10000)
                        do_area+=(line_area * line.qty_pnl)
                        
                res[id]=do_area 
            elif field_name=='multilayer_other_area':
                whm_reduce=0.0
                lhm_reduce=0.0
                if mu_ser:
                    arg_rec=arg_obj.browse(cr,uid,mu_ser[0])
                    whm_reduce=arg_rec.default_width_reduce
                    lhm_reduce=arg_rec.default_length_reduce
                for line in delivery_lines:
                    if line.board_type == mu_type:
#                        line_area=(line.pnl_width - whm_reduce) * (line.pnl_length - lhm_reduce) /(100 *10000)
                        line_area=(line.pnl_width * line.pnl_length) /(100 *10000)
                        mu_area+=(line_area * line.qty_pnl)  
                res[id]=mu_area
            
        return res
             
    _columns = {
        'outsource_number':fields.char('outsource_number',size=64,required=True,select=True,readonly=True), #外协加工单号
#        'outsource_process_types':fields.selection(_outsource_types,'outsource_process_types',size=32,required=True),   #工艺类型   
        'process_type':fields.many2one('select.selection','process_type',select=True,required=True),#201402外协工艺类型
        'type':fields.related('process_type','type',type='char',relation='select.selection',string='type'),#工艺类型
        'outsource_lines_ids':fields.one2many('outsource.process.lines','outsource_process_id','outsource_lines_ids'),
        'outsource_delivery_ids':fields.one2many('outsource.delivery.lines','outsource_process_id','outsource_delivery_ids'),
        'if_send':fields.boolean('if_send',readonly=True),#是否已下载附件
        'send_state':fields.selection([('have_send','have_send'),('not_send','not_send')],'send_state',readonly=True,select=True),#邮件发送状态
        'responsible_id':fields.many2one('res.users','responsible_id',readonly=True),
        'delivery_id':fields.many2one('res.users','take delivery people'),
        
        'delivery_type':fields.selection([('delivery_company','delivery_company'),('customer_pick','customer_pick')],'delivery_type',required=True),
        'partner_id'   :fields.many2one("res.partner", 'Supplier', size=16, select=True,domain=[('supplier','=',True)],required=True),
        'address':         fields.related('partner_id','address',type='one2many',relation='res.partner.address',string='address',readonly=True),
        'street':    fields.related('partner_id','street',type='char',relation='res.partner.address',string='street',readonly=True),
        'contact_name':    fields.related('address','name',type='char',string='contact_name',readonly=True),
        'phone':fields.related('address','phone',type='char',string='phone',readonly=True),
        'fax':fields.related('address','fax',type='char',string='fax',readonly=True),
        'if_print_dispatch':fields.boolean('if_print_dispatch'),
        'dispatch_state':fields.selection([('wait_dispatch','wait_dispatch'),('already_dispatch','already_dispatch')],'dispatch_state',readonly=True),
        'process_content':fields.text('process_note'),
        'process_require':fields.text('process_require'),
        'reason_apply':fields.text('reason_apply'),
        'double_board_area':fields.function(_info_get,method=True,type='float',string='double_board_area'),
        'multilayer_other_area':fields.function(_info_get,method=True,type='float',string='multilayer_other_area'),
        'return_number':fields.char('return_number',size=32),#返回单号
        'delivery_time':fields.datetime('delivery_time',readonly=True),#收货时间
        'user_id':fields.many2one('res.users','user_id',readonly=True),#收货人
        'receive_boards':fields.boolean('receive_boards'),#是否全部回货
        'attachment_ids': fields.many2many('ir.attachment','send_attachment_outsource_rel', 'wizard_outsource_id', 'attachment_id', 'Attachments'),#附件
		'state':fields.selection(_state_list,'State', size=64,track_visibility='onchange', translate=True, readonly=True,select=True),
    }
    _defaults={
        'state':'draft',
        'responsible_id':lambda self,cr,uid,context:uid,
        'outsource_number':lambda self,cr,uid,context:self.pool.get('ir.sequence').get(cr,uid,'Outsource.process'),
        'delivery_type':lambda *a:'customer_pick',
        'send_state':lambda *a:'not_send',
        'if_send':lambda *a:False,
        }
    
    
    def updata_state(self, cr, uid, ids, state=None, context=None):
        
        
        self.check_if_send(cr,uid,ids,context)
        org_state=self.browse(cr,uid,ids[0]).state
        self.check_delivery_line(cr,uid,ids,state=state)
        rec=self.write(cr, uid, ids, {'state':state})
        self.action_update_states(cr, uid, ids, state)
        
        if state=='done':
                    self.write(cr,uid,ids[0],{'delivery_time':time.strftime("%Y-%m-%d %H:%M:%S"),'user_id':uid,})
        return True
    def action_update_states(self,cr,uid,ids,state=None,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_rec=my.outsource_delivery_ids
        line_obj=self.pool.get('outsource.delivery.lines')
        if lines_rec:
            for line in lines_rec:
                if line.state != state:
                    line_id=line.id
                    line=line_obj.write(cr,uid,line_id,{'state':state,})
                    
        return True   

    
    def check_if_send(self, cr, uid, ids, state=None, context=None):
        # 检查是否更新发送外协文件
        my=self.browse(cr,uid,ids[0])
        type=my.process_type.type
        if_send=my.if_send
        print if_send,'if_send'
        s=['drill_outsource','flying_probe','VCUT+ gong_side','shape_gong_side','shape_VCUT']
        if type  in s: 
            print my.state,'state'
            if my.state=='w_document' and if_send==True:
                return True
            elif my.state=='w_document' and if_send==False:
                    raise osv.except_osv(_('错误消息'),_('审批前请检查是否下载附件了!'))
                    

        return True
    def check_type(self,cr,uid,ids,state=None,context=None):
        #审批时检查工艺类型
        my=self.browse(cr,uid,ids[0])
        type=my.process_type.type
        print type,'type'
        s=['drill_outsource','flying_probe','VCUT+ gong_side','shape_gong_side','shape_VCUT']
        if type  in s: 
            print type ,'ok'
            return True
        else:
            print type ,'false'
            return False
        return True
    def copy(self, cr, uid, id, default=None, context=None):
     
        if not default:
            default = {}
        default.update({
            'state':'draft',
            'outsource_delivery_ids':[],
            'name': self.pool.get('ir.sequence').get(cr, uid, 'outsoruce.delivery.lines'),
        })
        return super(outsource_process, self).copy(cr, uid, id, default, context)
             
    
    def check_delivery_line(self,cr,uid,ids,state=None,context=None):
        my=self.browse(cr,uid,ids[0])
        if state =='w_receive':
            if my.outsource_delivery_ids:
                return True
            else:
                raise osv.except_osv(('lines error:'),('process lines not found,please create'))
    
    def action_update_state(self,cr,uid,ids,state=None,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_rec=my.outsource_delivery_ids
        delivery_obj=self.pool.get('outsource.delivery.lines')
        lines_obj=self.pool.get('outsource.process.lines')
        wkf_ser=netsvc.LocalService('workflow')
        print wkf_ser,'wkf'
        if lines_rec:
            for line in lines_rec:
                if line.state != state:
                    if line.process_lines_id and not line.production_id:
                        line_id=line.process_lines_id.id
                        lines_obj.write(cr,uid,line_id,{'state':state})
                    
                    wkf_ser.trg_validate(uid,'outsource.delivery.lines',line.id,'button_approve',cr)              
        return True
    
    def production_read(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        delivery_obj=self.pool.get('outsource.delivery.lines')
        if my.outsource_delivery_ids:
            for line in my.outsource_delivery_ids:
                delivery_obj.production_read(cr,uid,[line.id],context=context)
                
        return True
    
    def process_cost_compute(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        delivery_obj=self.pool.get('outsource.delivery.lines')
        if my.outsource_delivery_ids:
            for line in my.outsource_delivery_ids:
                delivery_obj.process_cost_compute(cr,uid,[line.id],context=context)
        return True  
        
    
    def plasma_amount(self,cr,uid,ids,context=None):
        #等离子明细总金额的汇总
        my=self.browse(cr,uid,ids[0])
        delivery_obj=self.pool.get('outsource.delivery.lines')
        arg=self.pool.get('outsource.cost.argument')
        id=my.id
        print id,'id'
        connection=psycopg2.connect(database="pcb", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
        cursor=connection.cursor()
        cursor.execute('''select count(id) from outsource_delivery_lines where outsource_process_id=%s ''' %id)#搜素总明细条数
        counts=cursor.fetchall()
        b=counts[0]
        count=b[0]
        print count,'count'
        cursor.execute('''select partner_id,process_type from outsource_process where id=%s ''' % id)#搜索供应商ID和工艺类型
        partner=cursor.fetchone()
        partner_id=partner[0]
        print partner_id,'partner_id'
        process_type=partner[1]
        print process_type,'process_types'
        cursor.execute('''select board_type from outsource_delivery_lines where outsource_process_id=%s ''' % id)#搜索板类型
        board=cursor.fetchone()
        board_type=board
        print board_type,'board_type'
        board_types=board_type[0]
        print board_types,'board_types'
      
        cursor.execute('''select type from select_selection where id=%s ''' % process_type)
        type=cursor.fetchone()
        process_types=type[0]
        print process_types,'process_types'
        cursor.execute('''select default_lowest_cost,price_units from outsource_cost_argument where outsource_partner_id=%s and process_type=%s and board_type=%s  ''',(partner_id,process_types,board_types))
        #搜索最低默认值和单价
        default_min_cost=cursor.fetchall()
        default_min_costs=default_min_cost[0]
        default_min_base=default_min_costs[0]
        price=default_min_costs[1]
        print price,'price'
        print default_min_costs,default_min_base,'default_min_costs'
        cursor.execute('''update outsource_delivery_lines set pnl_price_units=%s,cost_total=pnl_length*pnl_width/1000000*qty_pnl_receive*%s where outsource_process_id=%s'''% (price,price,id))
        #更新PNL单价和总金额
        cursor.execute('''select sum(cost_total) from outsource_delivery_lines where outsource_process_id=%s ''' % id)#汇总总价格
        cost_total=cursor.fetchall()
        cost=cost_total[0]
        c=cost[0]
        print c,'cc'  
    
        if c < default_min_base :
            cost_base=default_min_base/count
            print cost_base,'cost_base'
            cursor.execute('''update outsource_delivery_lines set cost_total=%s where outsource_process_id=%s ''' % (cost_base,id))
            # 更新实际总价格
        connection.commit()#获取信息
        cursor.close() #关闭游标
        connection.close()
        return True       
        
        
    def approve_line(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        delivery_obj=self.pool.get('outsource.delivery.lines')
        id=my.id
        print id,'id'
        connection=psycopg2.connect(database="pcb", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
        cursor=connection.cursor()
        cursor.execute('''update outsource_delivery_lines set receive_board=True where outsource_process_id in(select id from outsource_process where receive_boards='t' and id=%s) ''' %id)
        cursor.execute('''update outsource_delivery_lines set qty_pnl_receive=qty_pnl,state='done',finish_time=now() where outsource_process_id=%s and board_types='big_board' and receive_board='t' and state!='done'  ''' %id)
        cursor.execute('''update outsource_delivery_lines set qty_receive=product_qty,state='done',finish_time=now() where outsource_process_id=%s and board_types='small_board' and receive_board='t' and state !='done'  ''' %id)
        cursor.execute('''update outsource_delivery_lines set state='w_receive',finish_time=null,qty_receive=null,qty_pnl_receive=null where outsource_process_id=%s and receive_board='f' ''' %id)
        connection.commit()#获取信息
        cursor.close() #关闭游标
        connection.close()
        return True      
##################################################20140720
##################################################20140720        
    #用FTP下载工程资料
    def download_attendment(self,cr,uid,ids,context):
        my=self.browse(cr,uid,ids[0])
        outsource_number=my.outsource_number
        partner_id=my.partner_id.name
        print partner_id
        partner_email=my.partner_id.email
        print partner_email,'email'
        id=my.id
        connection=psycopg2.connect(database="pcb", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
        cursor=connection.cursor()
        cursor.execute('''select product_id from outsource_delivery_lines where outsource_process_id=%s ''' %id)
        product_id=cursor.fetchall()
        cursor.execute('''select pcb_remove from outsource_delivery_lines where outsource_process_id=%s ''' %id)
        pcb_removes=cursor.fetchall()
#        if my.pcb_remove==True:
        pcb_remove=pcb_removes[0]
        pcb_remov=pcb_remove[0]
        cursor.execute('''update outsource_process set if_send='True' where id=%s ''' %id)
        connection.commit()#获取信息
        cursor.close() #关闭游标
        connection.close()
 #       se=self.pool.get('select.selection')
        object=self.pool.get('outsource.process').browse(cr,uid,id)
        type=object.process_type.type
        outsource_type=object.process_type.name
        print type,'type',outsource_type
        if type in ['drill_outsource','flying_probe','VCUT+ gong_side','shape_gong_side','shape_VCUT']:
           
            #钻孔类型
            if type=='drill_outsource':
                for products in product_id:
                    product=products[0]
                    print product,'product_name'
                    m=re.match('([MDS])(\d+)',product)
                    w=m.group(1)
                    print w,'w'
                    d=m.group(2)
                    print d,'d'
                    number=((int(d)/10000)+1)*10000
                    #FTP下载和上传实例
                    HOST='192.168.10.20'  
                    if w=='M':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='D':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='S':
                        DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                        print DIRN,'dirn'
                    else:
         #               raise osv.except_osv(_("add error"),_("No found the %s ") %product)
                        print's'
                    FILE='D%s.RAR' %product  
                    
                    load='e:/ftp_server/'
                    partner_name='%s' %partner_id
                    new_path = os.path.join(load,partner_name)
                    if not os.path.isdir(new_path):
                        os.makedirs(new_path)
                    localfile='%s/%s' %(new_path,FILE)
                    print localfile,'localfile'
                    try:  
                        f=ftplib.FTP(HOST)  
                    except (socket.error,socket.gaierror),e:  
                        print 'ERROR:cannot reach "%s"'% HOST  
                    print '***connected to host "%s"' % HOST  
                    try:  
                        f.login(user='test',passwd='test')  
                    except ftplib.error_perm:  
                        print 'ERROR:cannot login anonymously'  
                        f.quit()  

                    print '***Logged in as "test"'   
                    print f.getwelcome()
                    try:
                        f.cwd(DIRN)
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
          #              raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        print 'ERROR:cannot cwd to "%s"' %DIRN
                        f.quit()
                    try:  
                        f.retrbinary('RETR %s' % FILE,open(localfile,'wb').write,1024)#下载文件，打开文件对象
                    except ftplib.error_perm:  
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
           #             raise osv.except_osv(_("错误消息："),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product))
           
                    else:  
                        print '***Downloaded "%s" to CWD' % FILE

                    
            #飞针测试类型
            elif type=='flying_probe' :  #PCB移植
                print pcb_remov,'pcb_remov'
                
                if pcb_remov== True:
                    print pcb_remov,'pcb_remov 3'
                    for products in product_id:
                        product=products[0]
                        m=re.match('([MDS])(\d+)',product)
                        w=m.group(1)
                        print w,'w'
                        d=m.group(2)
                        print d,'d'
                        number=((int(d)/10000)+1)*10000
                        #FTP下载和上传实例
                        HOST='192.168.10.20'  
                        if w=='M':
                            DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                            print DIRN,'dirn'
                        elif w=='D':
                            DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                            print DIRN,'dirn'
                        elif w=='S':
                            DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                            print DIRN,'dirn'
                            
                        load='e:/ftp_server/'
                        partner_name='%s' %partner_id
                        FILE='K%s.RAR' %product  
#                       localfile='f:/ftp/%s' %FILE
                        new_path = os.path.join(load,partner_name)
                        if not os.path.isdir(new_path):
                            os.makedirs(new_path)
                        localfile='%s/%s' %(new_path,FILE)
                        localfile2='e:/ftp_download/%s'%FILE
                        try:  
                            f=ftplib.FTP(HOST)  
                        except (socket.error,socket.gaierror),e:  
                            print 'ERROR:cannot reach "%s"'% HOST  
                        print '***connected to host "%s"' % HOST  
                        try:  
                            f.login(user='test',passwd='test')  
                        except ftplib.error_perm:  
                            print 'ERROR:cannot login anonymously'  
                            f.quit()  
                        print '***Logged in as "test"'   
                        print f.getwelcome()
                        try:
                            f.cwd(DIRN)
                        except ftplib.error_perm:
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                            print 'ERROR:cannot cwd to "%s"' %DIRN
                            f.quit()
                        print 'cwd to "%s" and "%s"' %(DIRN,product)
                        try:  
                            #下载文件，打开文件对象
                            f.retrbinary('RETR %s' % FILE,open(localfile2,'wb').write,1024) 
                        except ftplib.error_perm:  
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        else:  
                            print '***Downloaded "%s" to CWD' % FILE
                            f.close()
                    
                        #已经将要下载的文件下载到了本地磁盘
                        #解压和压缩文件
                        command ='unrar  x e:/ftp_download/%s e:/ftp_download/ /y' %FILE
                        print command,'command'
                        os.system(command) 
                        y='*drl*.GBR'
                        box='*box*.GBR'
                        gts='*GTS.GBR'
                        command1 ='rar a e:\\ftp_download\\%s-DRL-BOX-GTS.rar e:\\ftp_download\\%s' %(product,box)
                        print command1,'command1'
                        os.system(command1)
                        command2 ='rar a e:\\ftp_download\\%s-DRL-BOX-GTS.rar e:\\ftp_download\\%s' %(product,y)
                        os.system(command2)
                        command3 ='rar a e:\\ftp_download\\%s-DRL-BOX-GTS.rar e:\\ftp_download\\%s' %(product,gts)
                        os.system(command3)
                        #删除
                        command ='del e:\\ftp_download\\*.GBR /Q'
                        os.system(command)
                        command1 ='del e:\\ftp_download\\K*.* /Q'
                        os.system(command1)
                        command2 ='del e:\\ftp_download\\*.ME /Q'
                        os.system(command2)
                        command3 ='del e:\\ftp_download\\*.tgz /Q'
                        os.system(command3)
                        command4 ='del e:\\ftp_download\\*.txt /Q'
                        os.system(command4)
                        try:
                            load2="e:/ftp_download/%s-DRL-BOX-GTS.rar"%product
                            load3="e:/ftp_server/%s/%s-DRL-BOX-GTS.rar"%(partner_name,product)
                            shutil.copy(load2,load3) 
                        except:
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise  osv.except_osv(_("错误消息："),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product))
                 
                else: #飞针测试类型
                    print 'is not remove'
                    for products in product_id:
                        product=products[0]
                        m=re.match('([MDS])(\d+)',product)
                        w=m.group(1)
                        print w,'w'
                        d=m.group(2)
                        print d,'d'
                        number=((int(d)/10000)+1)*10000
                        #FTP下载和上传实例
                        HOST='192.168.10.20'  
                        if w=='M':
                            DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                            print DIRN,'dirn'
                        elif w=='D':
                            DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                            print DIRN,'dirn'
                        elif w=='S':
                            DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                            print DIRN,'dirn'
                        FILE='K%s.RAR' %product  
                        FILE1='T%s.RAR' %product
                        FILE2='J%s.RAR' %product  
                        load='e:/ftp_server/'
                        partner_name='%s' %partner_id
                        new_path = os.path.join(load,partner_name)
                        if not os.path.isdir(new_path):
                            os.makedirs(new_path)
                        localfile='%s/%s' %(new_path,FILE)
                        localfile0='e:/ftp_download/%s'%FILE

                        try:  
                            f=ftplib.FTP(HOST)  
                        except (socket.error,socket.gaierror),e:  
                            print 'ERROR:cannot reach "%s"'% HOST  
                        print '***connected to host "%s"' % HOST  
                        try:  
                            f.login(user='test',passwd='test')  
                        except ftplib.error_perm:  
                            print 'ERROR:cannot login anonymously'  
                            f.quit()  

                        print '***Logged in as "test"'   
                        print f.getwelcome()
                        try:
                            f.cwd(DIRN)
                        except ftplib.error_perm:
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                            print 'ERROR:cannot cwd to "%s"' %DIRN
                            f.quit()
                        print 'cwd to "%s" and "%s"' %(DIRN,product)
                        try:  
                            #下载文件，打开文件对象
                            f.retrbinary('RETR %s' % FILE,open(localfile0,'wb').write,1024) 
                        except ftplib.error_perm: 
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        try:  #find TM file
                            
                            
                            localfile10='e:/ftp_server/%s/%s'%(partner_name,FILE1)
                            localfile1=open('%s'%localfile10,'wb')
                            f.retrbinary('RETR %s' % FILE1,localfile1.write,1024)
          
                        except ftplib.error_perm:
                            localfile1.close()
                            command='e:\\ftp_server\\%s\\%s'%(partner_name,FILE1)
                            s=os.remove(command)  #删除FILE1
                            print s,'s'
                            localfile20='e:/ftp_server/%s/%s'%(partner_name,FILE2)
                            localfile2=open('%s'%localfile20,'wb')
                            try:  # find JM file

                                f.retrbinary('RETR %s' % FILE2,localfile2.write,1024)
                 
                          
                            except ftplib.error_perm: 
                                self.send_eng_email(cr,uid,ids,outsource_type,product,context) 
                                print "cannot read file %s " %FILE2
                            
                        else:  
                            print '***Downloaded "%s" to CWD' % FILE
                            f.close()
                        
                            
                        #已经将要下载的文件下载到了本地磁盘
                        #解压和压缩文件
                        command ='unrar x e:\\ftp_download\\%s e:\\ftp_download\\ /y' %FILE
                        print command,'comm'
                        os.system(command) 
                        print command,'comm1'
                        y='drl.GBR'
                        yo='*drl*.GBR'
                        command1 ='rar a e:\\ftp_download\\%s-%s.rar e:\\ftp_download\\%s' %(product,y,yo)
                        os.system(command1) 
                        try:
                            load='e:\\ftp_download\\%s-%s.rar'%(product,y)
                            load1='e:\\ftp_server\\%s\\%s-%s.rar'%(partner_name,product,y)
                            shutil.copy(load,load1) #复制文件
                        except:
                            self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                            raise  osv.except_osv(_("错误消息："),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product))
                        #删除
                        command6 ='del e:\\ftp_download\\*.* /Q'
                        os.system(command6)
                        #open打开，读取：'r'和'rb'的区别在于二进制文件(r表示只读,b表示二进制)
                       
               
             #外形类型
            elif type=='shape_gong_side':
                for products in product_id:
                    product=products[0]
                    m=re.match('([MDS])(\d+)',product)
                    w=m.group(1)
                    print w,'w'
                    d=m.group(2)
                    print d,'d'
                    number=((int(d)/10000)+1)*10000
                    #FTP下载和上传实例
                    HOST='192.168.10.20'  
                    if w=='M':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='D':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='S':
                        DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                        print DIRN,'dirn'
                    FILE='K%s.RAR' %product 
                    
                    partner_name='%s' %partner_id
                    load='e:/ftp_server/'
                    new_path = os.path.join(load,partner_name)
                    if not os.path.isdir(new_path):
                        os.makedirs(new_path) 
#                    localfile='e:/ftp_download/%s/%s' %(partner_name,FILE)
                    localfile='e:/ftp_download/%s' %FILE
                    try:  
                        f=ftplib.FTP(HOST)  
                    except (socket.error,socket.gaierror),e:  
                        print 'ERROR:cannot reach "%s"'% HOST  
                    print '***connected to host "%s"' % HOST  
                    try:  
                        f.login(user='test',passwd='test')  
                    except ftplib.error_perm:  
                        print 'ERROR:cannot login anonymously'  
                        f.quit()  
                    print '***Logged in as "test"'   
                    print f.getwelcome()
                    try:
                        f.cwd(DIRN)
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        print 'ERROR:cannot cwd to "%s"' %DIRN
                        f.quit()
                    print 'cwd to "%s" and "%s"' %(DIRN,product)
                    try:  
                    #下载文件，打开文件对象
                        f.retrbinary('RETR %s' % FILE,open(localfile,'wb').write,1024) 
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context) 
                        raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
          
                    else:  
                        print '***Downloaded "%s" to CWD' % FILE
                        f.close()
                        
                    #已经将要下载的文件下载到了本地磁盘
                    #解压和压缩文件
                    command ='unrar x e:\\ftp_download\\%s e:\\ftp_download\\ /y' %FILE
                    os.system(command) 
                    y='*drl*.GBR'
                    yo='*box*.GBR'
                    command6 ='rar a e:\\ftp_download\\%s-DRL-BOX.rar e:\\ftp_download\\%s' %(product,yo)
                    os.system(command6)
                    command5 ='rar a e:\\ftp_download\\%s-DRL-BOX.rar e:\\ftp_download\\%s' %(product,y)
                    os.system(command5) 
                    try:
                        load='e:\\ftp_download\\%s-DRL-BOX.rar'%product
                        load1='e:\\ftp_server\\%s\\%s-DRL-BOX.rar'%(partner_name,product)
                        shutil.copy(load,load1) #复制文件
                    except:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise  osv.except_osv(_("错误消息："),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product))
                    command2 ='del e:\\ftp_download\\*.* /Q'
                    os.system(command2)
                  #VCUT类型
            elif type=='shape_VCUT':
                for products in product_id:
                    product=products[0]
                    m=re.match('([MDS])(\d+)',product)
                    w=m.group(1)
                    print w,'w'
                    d=m.group(2)
                    print d,'d'
                    number=((int(d)/10000)+1)*10000
                    #FTP下载和上传实例
                    HOST='192.168.10.20'  
                    if w=='M':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='D':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='S':
                        DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                        print DIRN,'dirn'
                    FILE='K%s.RAR' %product  
                  
                    partner_name='%s' %partner_id
                    load='e:/ftp_server/'
                    new_path = os.path.join(load,partner_name)
                    if not os.path.isdir(new_path):
                        os.makedirs(new_path) 
                    localfile='e:/ftp_download/%s' %FILE
                    FILE1='V%s.RAR' %product
                    localfile1='e:/ftp_download/%s' %FILE1
                    try:  
                        f=ftplib.FTP(HOST)  
                    except (socket.error,socket.gaierror),e:  
                        print 'ERROR:cannot reach "%s"'% HOST  
                    print '***connected to host "%s"' % HOST  
                    try:  
                        f.login(user='test',passwd='test')  
                    except ftplib.error_perm:  
                        print 'ERROR:cannot login anonymously'  
                        f.quit()  
                    print '***Logged in as "test"'   
                    print f.getwelcome()
                    try:
                        f.cwd(DIRN)
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        print 'ERROR:cannot cwd to "%s"' %DIRN
                        f.quit()
                    print 'cwd to "%s" and "%s"' %(DIRN,product)
                    try:  
                    #下载文件，打开文件对象
                        f.retrbinary('RETR %s' % FILE,open(localfile,'wb').write,1024) 
                    except ftplib.error_perm: 
                        print  "cannot read file %s " %product
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise osv.except_osv(_("add error"),_("cannot read file K%s ") %product)
                    try:  
                        f.retrbinary('RETR %s' % FILE1,open(localfile1,'wb').write,1024) 
                        print 'download'
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context) 
                        raise osv.except_osv(_("add error"),_("cannot read file V%s ") %product)
                   
                    else:  
                        print '***Downloaded "%s" to CWD' % FILE
                        f.close()
                    
                    #已经将要下载的文件下载到了本地磁盘
                    #解压和压缩文件
                    command ='unrar x e:\\ftp_download\\%s e:\\ftp_download\\ /y' %FILE
                    os.system(command) 
                    y='*drl*.GBR'
                    yo='*box*.GBR'
                    command ='rar a e:\\ftp_download\\%s-BOX.rar e:\\ftp_download\\%s' %(product,yo)
                    os.system(command)
                    try:
                        load='e:\\ftp_download\\%s-BOX.rar'%product
                        load1='e:\\ftp_server\\%s\\%s-BOX.rar'%(partner_name,product)
                        shutil.copy(load,load1) #复制文件
                        load2='e:\\ftp_download\\%s'%FILE1
                        load3='e:\\ftp_server\\%s\\%s'%(partner_name,FILE1)
                        shutil.copy(load2,load3) #复制文件
                    except:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise  osv.except_osv(_("错误消息："),_("需发放%s文件找不到,请联系工程部确认无误后再发送!"%product))
                    #删除
                    command4 ='del e:\\ftp_download\\*.* /Q'
                    os.system(command4)
                      #VCUT+外形类型
          
                
            elif type=='VCUT+ gong_side':
                for products in product_id:
                    product=products[0]
                    m=re.match('([MDS])(\d+)',product)
                    w=m.group(1)
                    print w,'w'
                    d=m.group(2)
                    print d,'d'
                    number=((int(d)/10000)+1)*10000
                    #FTP下载和上传实例
                    HOST='192.168.10.20'  
                    if w=='M':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='D':
                        DIRN='ENG/ENGBAKUP/%s/%s/%s' %(w,number,product)
                        print DIRN,'dirn'
                    elif w=='S':
                        DIRN='ENG/ENGBAKUP/%s/%s/' % (w,product)
                        print DIRN,'dirn'
                    partner_name='%s' %partner_id
                    load='e:/ftp_server/'
                    new_path = os.path.join(load,partner_name)
                    if not os.path.isdir(new_path):
                        os.makedirs(new_path) 
                    FILE='K%s.RAR' %product  
                    localfile='e:/ftp_download/%s' %FILE
                    FILE1='V%s.RAR' %product
                    localfile1='e:/ftp_download/%s' %FILE1
                    try:  
                        f=ftplib.FTP(HOST)  
                    except (socket.error,socket.gaierror),e:  
                        print 'ERROR:cannot reach "%s"'% HOST  
                    print '***connected to host "%s"' % HOST  
                    try:  
                        f.login(user='test',passwd='test')  
                    except ftplib.error_perm:  
                        print 'ERROR:cannot login anonymously'  
                        f.quit()  
                    print '***Logged in as "test"'   
                    print f.getwelcome()
                    try:
                        f.cwd(DIRN)
                    except ftplib.error_perm:
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise osv.except_osv(_("add error"),_("cannot read file %s ") %product)
                        print 'ERROR:cannot cwd to "%s"' %DIRN
                        f.quit()
                    print 'cwd to "%s" and "%s"' %(DIRN,product)
                    sub=product
                    try:  
                    #下载文件，打开文件对象
                        f.retrbinary('RETR %s' % FILE,open(localfile,'wb').write,1024) 
                    except ftplib.error_perm: 
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context) 
                        raise osv.except_osv(_("add error"),_("cannot read file K%s ") %product)
                    try:  
                        f.retrbinary('RETR %s' % FILE1,open(localfile1,'wb').write,1024) 
                    except ftplib.error_perm: 
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context) 
                        raise osv.except_osv(_("add error"),_("cannot read file V%s ") %product)
                    else:  
                        print '***Downloaded "%s" to CWD' % FILE
                        f.close()
                    
                    #已经将要下载的文件下载到了本地磁盘
                    #解压和压缩文件
                    command ='unrar x e:\\ftp_download\\%s e:\\ftp_download\\ /y' %FILE
                    os.system(command) 
                    
                    y='*drl*.GBR'
                    yo='*box*.GBR'
                    command ='rar a e:\\ftp_download\\%s-DRL-BOX.rar e:\\ftp_download\\%s' %(product,yo)
                    os.system(command)
                    ommand ='rar a e:\\ftp_download\\%s-DRL-BOX.rar e:\\ftp_download\\%s' %(product,y)
                    os.system(command)
                    try:
                        load='e:\\ftp_download\\%s-DRL-BOX.rar'%product
                        load1='e:\\ftp_server\\%s\\%s-DRL-BOX.rar'%(partner_name,product)
                        shutil.copy(load,load1)
                        load2='e:\\ftp_download\\%s'%FILE1
                        load3='e:\\ftp_server\\%s\\%s'%(partner_name,FILE1)
                        shutil.copy(load2,load3) #复制文件
                    except:
                        
                        self.send_eng_email(cr,uid,ids,outsource_type,product,context)
                        raise  osv.except_osv(_("错误消息："),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product))
                    #删除
                    command3 ='del e:\\ftp_download\\*.* /Q'
                    os.system(command3)
        else:
            raise  osv.except_osv(_("错误消息："),_("这种工艺类型不需要下载及发送邮件 ! "))
        
        self.send_email(cr,uid,ids,context)
        return True
       
    
    def send_email(self,cr,uid,ids,context):
        my=self.browse(cr,uid,ids[0])
        outsource_number=my.outsource_number
        partner_id=my.partner_id.name
        id=my.id
        send_state=my.send_state
        print partner_id
        partner_email=my.partner_id.email
        print partner_email,'email'
        mailto_list=['ithelp@mtlpcb.com','%s'%partner_email] 
        #####################
        #设置服务器，用户名、口令以及邮箱的后缀
        mail_host="smtp.mxhichina.com"
        mail_user="sz-ouyanghs@mtlpcb.com"
        mail_pass="mtl147258"
        content="您好! 外发加工文件已上传到服务器ftp://58.20.0.106 ，请及时下载，谢谢！"
        sub='致: '+'%s'%partner_id + ','+'外协加工单号: '+'%s'%outsource_number +'外发文件已上传'
        msg = MIMEText(content,_charset='utf-8') 
        msg['Subject'] = sub 
        msg['From'] = mail_user
        msg['To'] = ";".join(mailto_list) 
        try: 
            s = smtplib.SMTP() 
            s.connect(mail_host) 
            s.login(mail_user,mail_pass) 
            s.sendmail(mail_user, mailto_list, msg.as_string()) 
            s.close() 
            print ' 邮件发送成功! '
        except: 
            raise osv.except_osv(_("send error:"),_("this email send error that check the problem please !") )
            print "False" 
        else:
            connection=psycopg2.connect(database="pcb", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
            cursor=connection.cursor()
            cursor.execute(''' update outsource_process set send_state='have_send' where id='%s'  ''' %id )
            connection.commit()#获取信息
            cursor.close() #关闭游标
            connection.close()
            raise osv.except_osv(_("发送成功!!!"),_("文件上传及通知邮件发送成功!"))
        return True
    
    def send_eng_email(self,cr,uid,ids,outsource_type,product,context):
        my=self.browse(cr,uid,ids[0])
        outsource_number=my.outsource_number
        partner_id=my.partner_id.name
        print partner_id
        partner_email=my.partner_id.email
        print partner_email,'email'
        mailto_list=["sz-ouyanghs@mtlpcb.com",'ithelp@mtlpcb.com'] 
        #####################
        #设置服务器，用户名、口令以及邮箱的后缀
        mail_host="smtp.mxhichina.com"
        mail_user="sz-ouyanghs@mtlpcb.com"
        mail_pass="mtl147258"
        content="您好! 外发加工档案号%s文件找不到 ，请工程部及时处理，并及时发送给外协供应商，谢谢!"%product
        sub='致:  工程部' + ','+'外协加工单号: '+'%s'%outsource_number +'工艺类型：%s,档案号%s文件找不到，请工程部及时处理!'%(outsource_type,product)
        msg = MIMEText(content,_charset='utf-8') 
        msg['Subject'] = sub 
        msg['From'] = mail_user
        msg['To'] = ";".join(mailto_list) 
        try: 
            s = smtplib.SMTP() 
            s.connect(mail_host) 
            s.login(mail_user,mail_pass) 
            s.sendmail(mail_user, mailto_list, msg.as_string()) 
            s.close() 
            print ' 邮件发送成功! '
        except: 
            raise osv.except_osv(_("错误信息:"),_("需发放%s文件找不到，请联系工程部确认无误后再发送!"%product) )
            print "False" 
        return True
        
        
        
outsource_process()

class outsource_process_lines(osv.osv):
    _name='outsource.process.lines'
    _rec_name='production_id'
    _inherit='outsource.data'
    _state_list=[(i,i) for i in ('draft','w_director','w_supervisor','w_quality','plan_director','w_gmanager','w_outsource','w_receive','done')]
    _bd_type=[(i,i) for i  in ('general_board','aluminum_board','double_board','much_layer_board','cu_board')]
    _bd_mal=[(i,i) for i in ('pp1078-1080','pp1080-2116')]
    
    def _info_get(self,cr,uid,ids,field_name,args,context=None):
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            if field_name=='scrap_pnl_qty':
                if my.qty_pnl:
                    my.board_types=='big_board'
                    res[id]=my.qty_pnl - my.qty_pnl_receive
                    my.qty_receive==0
                    
                else:
                    res[id]=False
            elif field_name=='scrap_qty':
                if my.product_qty:
                    my.board_types=='small_board'
                    res[id]= my.product_qty - my.qty_receive 
                    my.qty_pnl_receive==0
                   
                else:
                    res[id]=False
            elif field_name=='total_count':
                if my.product_qty and my.points_count:
                    res[id]=my.qty_receive * my.points_count
                else:
                    res[id]=False
        return res
         
    _columns={
 
        'outsource_apply_id':fields.many2one('outsource.apply','outsource_apply_id',ondelete='cascade'),
        'outsource_process_id':fields.many2one('outsource.process','outsource_process_id',ondelete='cascade'),
        'production_id':fields.char('production_id',size=64,select=True,required=True),
        'product_id':fields.char('product_id',size=64,select=True),
        'product_unit':fields.char('product_unit',size=32),
        'product_qty':fields.integer('product_qty(pcs)'),#pcs数量
        #'at_makepcsqty':fields.integer('at_makepcsqty'),#pcs数量
        'qty_unit':fields.integer('qty_unit'),#unit 数量
        'qty_pnl':fields.integer('qty_pnl'),#pnl 数量
         'pcs_unit_count':fields.integer('pcs_unit_count'),#排版unit数
        'qty_pnl_pcs':fields.integer('qty_pnl_pcs'),#排版数
        'width':fields.float('width',digits_compute=dp.get_precision('Account'),),
        'length':fields.float('length',digits_compute=dp.get_precision('Account'),),
        'pnl_width':fields.float('pnl_width',digits_compute=dp.get_precision('Account'),),
        'pnl_length':fields.float('pnl_length',digits_compute=dp.get_precision('Account'),),
        'pnl_unit':fields.char('pnl_unit',size=32),
        'current_workcenter_id':fields.char('current_workcenter_id',size=32),
        #'current_workcenter_id':fields.many2one('mrp.workcenter','current_workcenter_id'),
        #'related_workcenter_id':fields.many2one('mrp.workcenter','related_workcenter_id',),
        'process_args':fields.char('process_args',size=256),
        #'process_args':fields.text('process_args'),
        'process_content':fields.text('process_note'),
        'process_require':fields.text('process_require'),
        'director_note':fields.text('note'),
        'gmanager_note':fields.text('gmanager_note'),
        'product_area':fields.float('product_area'),#产品面积
        'pcs_price_units':fields.float('pcs_price_units', digits=(4,4),),
        'pnl_price_units':fields.float('pnl_price_units', digits=(4,4),),
        'cost_total':fields.float('cost_total', digits_compute=dp.get_precision('Account'),),#加工总费用
        'delivery_date':fields.date('delivery_date',select=True),#交货日期20140215
        'board_thickness':fields.float('board_thickness'),#板厚
        'board_type':fields.selection(_bd_type,'board_type'),
        'attachment_id':fields.many2one('ir.attachment','attachment_id'),#附件
        'eng_file':fields.binary('eng_file'),#工程文件
        'eng_filename':fields.char('eng_filename',size=32),#文件名
        #'product_id':fields.many2one('product.product','product_id'),
        #'production_id':fields.many2one('mrp.production','production_id'),
        #'product_unit':fields.many2one('product.uom','produc_unit',),
        
        ##outsource drill field:
        'larse_hole_dia':fields.float('larse_hole_dia'),#激光钻孔孔径
        'board_material':fields.selection(_bd_mal,'board_material'),#材质
        'min_hole_dia':fields.float('min_hole_dia',digits_compute=dp.get_precision('Account'),),#最小孔径
        'hole_count':fields.integer('hole_count'),#总孔数
        'layer_count':fields.integer('layer_count'),#层数
        'cu_thickness':fields.char('cu_thickness',size=16),
        'drills_file':fields.binary('drills_file'),#钻孔文件
        'drills_filename':fields.char('drills_filename',size=32),#文件名
        'slot_hole_count':fields.integer('slot_hole_count'),#钻槽孔数
        'join_hole_count':fields.integer('join_hole_count'),#连接孔数
        'special_hole_count':fields.integer('special_hole_count'),#异形孔数
        'top_area':fields.float('top_area'),
        'bottom_area':fields.float('bottom_area'),
        ##drill
        
        ##outsource flying probe field:
        'points_count':fields.integer('points_count'),#pcs测试点数
        'total_count':fields.function(_info_get,method=True,type='float',string='total_count'),
        'if_first_test':fields.boolean('if_first_test'),#首测
        'if_retest':fields.boolean('if_retest'),#复测
        'if_low_resistance':fields.boolean('if_low_resistance'),#是否低阻测试
        'if_fpc_sample':fields.boolean('if_fpc_sample'),
        'pcb_remove':fields.boolean('pcb_remove'),#PCB移植
        ##flying
        
        ##outsource shape_vcut  field:
        'cutter_size':fields.float('cutter_size'),#刀具大小
        'gong_size':fields.float('gong_size(m)'),#锣程
        'vcut_size':fields.float('vcut_size(m)'),#v程
        'v_cutter_count':fields.float('v_cutter_count'),#跳刀数
        
        ##shape gong side fields:
        'gong_slot_count':fields.integer('gong_slot_count'),#锣槽数
        'sink_hole_count':fields.integer('sink_hole_count'),#沉孔数
        'horn_hole_count':fields.integer('horn_hole_count'),#喇叭孔数
        'plate_hole_count':fields.integer('plate_hole_count'),#盘中孔
        ##shape 
       
         #'partner_address':fields.related('partner_id',''),
        'if_have_duizhang':fields.boolean('if_have_duizang'),
        #'duizhang_amount':fields.float('duizhang_amount', digits_compute=dp.get_precision('Account'),),
        'duizhang_time':fields.datetime('duizhang_time'),
        'if_have_payment':fields.boolean('if_have_payment'),
        #'payment_amount':fields.float('payment_amount', digits_compute=dp.get_precision('Account'),),
        'payment_time':fields.datetime('payment_time'),
        'state':fields.selection( _state_list,'State', size=64, required=False, translate=True, readonly=True,),
        'apply_state':fields.related('outsource_apply_id','state',type='char',string='apply_state'),
        'scrap_qty':fields.function(_info_get,method=True,type='integer',string='scrap_qty'),# 报废pcs数量
         'scrap_pnl_qty':fields.function(_info_get,method=True,type='integer',string='scrap_pnl_qty'),#报废pnl数量
        'reason_cancel':fields.char('reason_cancel',size=256),
        'reason_apply':fields.text('reason_apply'),
        'default_min_cost':fields.float('default_min_cost'),
        'slot_size':fields.float('slot_size'),
        'board_types':fields.selection([('big_board','big_board'),('small_board','small_board')],'board_types'),#
        'sink_sliver_type':fields.selection([('normal_board','normal_board'),('special_board','special_board')],'sink_sliver_type'),#沉银板类型
        'length_pp':fields.integer('length_pp'),#长PP片
        'width_pp':fields.integer('width_pp'),#宽PP片
        'laminate_cu_thickness':fields.char('laminate_cu_thickness', size=32),#层压铜厚
    }
    
    _defaults = {
                 'state':lambda *a:'draft',
                 'product_unit':lambda *a:'mm',
                 'pnl_unit': lambda *a:'mm',
                 'sink_sliver_type':lambda *a:'normal_board',
                 
    }
    
    def  production_read(self,cr,uid,ids, context=None):
        my=self.browse(cr,uid,ids[0])
        server='192.168.10.2'
        user='sa'
        passward='719799'
        #database='121109'
        database='mtlerp-running'
        batch=my.production_id
        wk_code=my.current_workcenter_id
        conn = _mssql.connect(server=server , user=user, password=passward,database=database)    
        wk_conn = _mssql.connect(server=server , user=user, password=passward,database=database)    
        sum_conn=_mssql.connect(server=server , user=user, password=passward,database=database)    
        slot_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        plate_hole_conn=_mssql.connect(server=server , user=user, password=passward,database=database) 
        join_conn=_mssql.connect(server=server , user=user, password=passward,database=database) 
        cu_thick_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        gong_size_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        pcs_unit_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        gold_finger_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        pro_arg_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        needdate_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        pp_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        laminate_cu_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        laminate_board_conn=_mssql.connect(server=server , user=user, password=passward,database=database)
        
        #conn.execute_query('''select * from VIwip where batchcode='121025224101' '''  )        
        
        w_ser=(   'goodscode','goodslength','goodswidth',
                        'Mlength','Mwidth','Mqty','NowWCode',
                        'layercount','goodsheight',
                        'PCSQty','qtyp',batch)
        
     
        conn.execute_query('''select id from VIwip_OE where batchcode='%s' ''' %batch)
        ser_flg=abs(conn.rows_affected)
        conn.execute_query('''select id from TPTechnicsFlowM where batchcode='%s' ''' %batch)
        ser_flg_end=abs(conn.rows_affected)
        if ser_flg_end:
            if ser_flg: 
                conn.execute_query('''select %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s from VIwip_OE where batchcode='%s' ''' %w_ser )
                
            else:
                conn.execute_query('''select %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s from VIwip_OE_End where batchcode='%s' ''' %w_ser)
                
            up_dic={}
#            l_hole=u'连孔'
            l_hole=u'liankong'
            for row in conn:
                print row,'rowwww'
                    
                wk_conn.execute_query('''select CutleDia,workcentercode from VBGoodsParaRead where goodscode='%s' and paratype='T02'  and workcentercode='w22' ''' %(row['goodscode'],))
                sum_conn.execute_query('''select sum(ParaQty) from VBGoodsParaRead where workcentercode='w22' and goodscode='%s' ''' % row['goodscode'])
                slot_conn.execute_query('''select sum(ParaQty) from VBGoodsParaRead where Unthread=1 and  goodscode='%s' ''' % row['goodscode'])
                plate_hole_conn.execute_query('''select sum(ParaQty) from VBGoodsParaRead where workcentercode='W15' and goodscode='%s' ''' % row['goodscode'])#盘中孔
                join_conn.execute_query('''select sum(ParaQty) from VBGoodsParaRead where Memo like'%s' and  goodscode='%s' ''' % (row['goodscode'],l_hole))
                cu_thick_conn.execute_query('''select case when FOCopper='/' and LayerCount=1 then OuterCopper+'0.5' when  FOCopper='/' and LayerCount<>1 then OuterCopper  else FOCopper end from VPTechnicsFlowM where SubBatchCode='%s' ''' % batch)
                gong_size_conn.execute_query('''select CutPerimeter from VBengTest where BillState='40' and IsExtr='1' and goodscode='%s' ''' % row['goodscode'])
                pcs_unit_conn.execute_query('''select PS*SU from VPTechnicsFlowM where SubBatchCode='%s' ''' % batch)
                gold_finger_conn.execute_query('''select SGoldFingerCount from VBproduction where goodscode='%s' ''' % row['goodscode'])
                pro_arg_conn.execute_query('''select TechnicPara from TPTechnicsFlowS where billcode in (select billcode from TPTechnicsFlowM where batchcode='%s') and workcentercode='%s' ''' % (batch,wk_code))
                needdate_conn.execute_query('''select needdate from TPTechnicsFlowM where batchcode='%s' ''' %batch)
#                pp_conn.execute_query('''select max(number) from TBGoodsBOMS where  id in (select max(id) from TBgoodsBoMs where goodstype='PP' and Mgoodscode='%s' union select min(id) from TBgoodsBoMs where goodstype='PP' and Mgoodscode='%s') '''%(row['goodscode'],row['goodscode']))
                pp_conn.execute_query('''select dbo.F_GetPP('%s') ''' %(row['goodscode']))
                laminate_cu_conn.execute_query(''' select InnerCopper from TBGoodsBOMS where Mgoodscode='%s' and GoodsCode='gtl' ''' % row['goodscode'])#层压铜厚
                laminate_board_conn.execute_query(''' select GoodsHeight1 from VBProductionSub where goodscode='%s' ''' % row['goodscode'])#层压板厚
                min_hole=None
                hole_count=None
                sum_count=None
                slot_hole_count=None
                join_hole_count=None
                cu_thick=None
                gong_size=None
                plate_hole_count=None
                pcs_unit_count=None
                finger_count=None
                process_args=None
                needdate=None
                length_pp=None
                laminate_cu_thickness=None
                laminate_board_thickness=None
                def get_field_info(conn,field_name=None,des=None):
                    for cn_info in conn:
                        if field_name:
                            print cn_info[field_name],field_name
                            return cn_info[field_name]
                        else:
                            print cn_info[0],des
                            return cn_info[0]
                min_hole=get_field_info(wk_conn,field_name='CutleDia')
    #               hole_count=get_field_info(sum_conn,des='count')
                hole_count=get_field_info(sum_conn,des='count')
                slot_hole_count=get_field_info(slot_conn,des='slot info')
                plate_hole_count=get_field_info(plate_hole_conn,des='plate hole info')
                join_hole_count=get_field_info(join_conn,des='join hole info')
                gong_size=get_field_info(gong_size_conn,des='gong size info')
                cu_thick=get_field_info(cu_thick_conn,des='cu thick info') + 'oz'
                pcs_unit_count=get_field_info(pcs_unit_conn,des='pcs unit info')
                finger_count=get_field_info(gold_finger_conn,des='gold finger info')
                process_args=get_field_info(pro_arg_conn,des='args info')
                needdate=get_field_info(needdate_conn,des='delivery date')
                length_pp=get_field_info(pp_conn,des='length pp')
                laminate_cu_thickness=get_field_info(laminate_cu_conn,des='laminate cu thickness')
                laminate_board_thickness=get_field_info(laminate_board_conn,des='laminate board thickness')
                    #===============================================================
                    # for wk_info in wk_conn:
                    #    print wk_info['CutleDia'],'CutleDia'
                    #    min_hole=wk_info['CutleDia']
                    #    
                    # for count_info in sum_conn:
                    #    hole_count=count_info[0]
                    #    print count_info,'countttt'
                    # for slot_info in slot_conn:
                    #    slot_hole_count=slot_info[0]
                    #    print slot_info,'slot info'
                    # for join_info in join_conn:
                    #    join_hole_count=join_info[0]
                    #    print join_info,'join hole info'
                    # for cu_info in cu_thick_conn:
                    #    cu_thick=str(cu_info[0]) + 'oz'
                    #    print cu_info,'cu thick info'
                    #    
                    # for gong_info in gong_size_conn:
                    #    gong_size=gong_info[0]
                    #    print gong_info,'gong size info'
                    # for unit_info in pcs_unit_conn:
                    #    pcs_unit_count=unit_info[0]
                    #    print unit_info,'pcs unit info'
                    # for finger_info in gold_finger_conn:
                    #    finger_count=finger_info[0]
                    #    print finger_info,'gold finger info'
                    # 
                    # for arg_info in pro_arg_conn:
                    #    process_args=arg_info[0]
                    #    print arg_info,'args info'
                    #===============================================================
                if row:
                    up_dic['length']=row['goodslength'] *10
                    up_dic['width']=row['goodswidth'] *10
                    up_dic['product_id']=row['goodscode']
                    up_dic['product_qty']=row['PCSQty']
                    up_dic['qty_unit']=row['qtyp']
                    up_dic['pnl_length']=row['Mlength'] *10-15  
                    up_dic['pnl_width']=row['Mwidth'] *10-15  
                    up_dic['qty_pnl']=row['Mqty']
                        
                    up_dic['layer_count']=row['layercount']
                    up_dic['board_thickness']=row['goodsheight']
                    up_dic['delivery_date']=needdate
                    up_dic['current_workcenter_id']=row['NowWCode']
                    up_dic['min_hole_dia']=min_hole
                    up_dic['hole_count']=hole_count
                    up_dic['slot_hole_count']=slot_hole_count
                    up_dic['plate_hole_count']=plate_hole_count
                    up_dic['join_hole_count']=join_hole_count
                    up_dic['cu_thickness']=cu_thick
                    up_dic['length_pp']=length_pp
                    up_dic['laminate_cu_thickness']=laminate_cu_thickness
                    up_dic['laminate_board_thickness']=laminate_board_thickness
                        #up_dic['gong_size']=gong_size
                    up_dic['pcs_unit_count']=pcs_unit_count
                    up_dic['finger_count']=finger_count

            conn.close()
            self.write(cr,uid,ids,up_dic)
        else:
            raise osv.except_osv(('search error:'),('production_id info not found!'))
           
        return True
    
outsource_process_lines()

class outsource_delivery_lines(osv.osv):
    _name='outsource.delivery.lines'
    _inherit='outsource.process.lines'
    _state_list=[(i,i) for i in ('draft','w_document','w_receive','done')]
    _c_type=[(i,i) for i in ('cvl','fpc','fpc_3m','soft_hard_fpc','double_fpc','fpc_3m_double','3m_cut','laser_cut')]
#    _process_list=[(i,i) for i in ('sink_gold','sink_silver','sink_Sn','spray_Sn(have pb)','spray_Sn(nhav pb)','gold_finger_plated',
#                                   'gold_plated','OSP','hot_equating(have pb)','brush_plated_board','plasma_process',
#                                   'hot_equating(not have )','drill_outsource','flying_probe','bf_laminate_pre',
#                                   'shape_VCUT','shape_gong_side','VCUT+ gong_side','other','laser_drill','wire_drawing',)]
     
    def _info_get_area(self,cr,uid,ids,field_name,args,context=None):
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            if field_name=='product_area':
                if my.pnl_width and my.pnl_length:
                    area=(my.pnl_width/10) *(my.pnl_length/10)/10000
                    res[id]=area
                else:
                    res[id]=0.0
            elif field_name =='receive_area': 
#                if my.pnl_width and my.pnl_length and my.qty_pnl:
                    pd_area=(my.pnl_width/10) *(my.pnl_length/10)/10000
                    if my.board_types=='small_board' :
                        areas=(my.length * my.width)/1000000 * my.qty_receive
                        print areas,'area'
                    elif my.board_types=='big_board' :
                        areas=pd_area * my.qty_pnl_receive   
#                        print areas,'area1' 
                    res[id]=areas
#                else:
#                    res[id]=0.0
        return res
    
    def _info_gets(self,cr,uid,ids,field_name,args,context=None):
                
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            if field_name=='top_bot_area':
                area=(my.top_area + my.bottom_area)/2
                res[id]=area
            else:
                res[id]=0.0
        return res
    
    def _info_inch(self,cr,uid,ids,field_name,args,context=None):
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            if field_name=='pnl_length_inch':
                inch=(my.pnl_length+15)/25.4
                res[id]=inch
            elif field_name=='pnl_width_inch':
                inch=(my.pnl_width+15)/25.4
                res[id]=inch
            else:
                res[id]=0.0
        return res
    

    _columns={
        #'name':fields.char('name',size=32),
#        'process_type':fields.selection(_process_list,'outsource_process_type',size=32,select=True),
        
        'process_lines_id':fields.many2one('outsource.process.lines','process_lines_id',ondelete='cascade'),
#        'production_id':fields.related('process_lines_id','production_id',type='char',relation='outsource.process.lines',string='production_id'),
#        'width':fields.related('process_lines_id','width',type='float',relation='outsource.process.lines',string='width'),
        'process_args_info':fields.char('process_args_info',size=256),
        'outsource_process_id':fields.many2one('outsource.process','outsource_process_id',ondelete='cascade'),
        'partner_id':fields.related('outsource_process_id','partner_id',type='many2one',relation='res.partner',string='partner_id'),#外协商
        'responsible_id':fields.related('outsource_process_id','responsible_id',type='many2one',relation='res.users',string='responbile_id'),#外协发货人
        'process_send_time':fields.related('outsource_process_id','process_send_time',type='datetime',string='process_send_time'),#外协发货时间
        'outsource_number':fields.related('outsource_process_id','outsource_number',type='char',string='outsource_number',size=32),#本公司外协单号
        'create_dates':fields.related('outsource_process_id','create_date',type='datetime',string="create_dates"),
        'process_types':fields.related('outsource_process_id','process_type',type='many2one',relation='select.selection',string='process_types',select=True),
        'process_type':fields.related('outsource_process_id','type',type='char',relation='select.selection',string='process_type',readonly=True),
        'return_numbers':fields.related('outsource_process_id','return_number',type='char',relation='outsource.process',string='return_numbers',readonly=True),#返回单号
        'responsible_ids':fields.related('outsource_process_id','responsible_id',type='many2one',relation='hr.employee',string='responsible_ids'),#我司送货人
        'create_date':fields.related('outsource_process_id','create_date',type='datetime',string='create_date'),#外协外发日期
        'delivery_time':fields.related('outsource_process_id','delivery_time',type='datetime',string='delivery_time',readonly=True),#外协产品收货时间
        'delivery_id':fields.related('outsource_process_id','user_id',type='many2one',relation='res.users',string='take delivery people'),#收货人
#        'outsource_types':fields.related('outsource_process_id','outsource_process_types',type='selection',relation='outsource.process',string='outsource_types',),
        'receive_number':fields.char('receive_number',size=32),#回货单号
        'receive_area':fields.function(_info_get_area,method=True,type='float',string='receive_area'),#回货面积
        'top_bot_area':fields.function(_info_gets,method=True,type='float',string='top_bot_area'),#top和bot面积平均值
        'pnl_length_inch':fields.function(_info_inch,method=True,type='float',string='pnl_length_inch'),#PNL长inch
        'pnl_width_inch':fields.function(_info_inch,method=True,type='float',string='pnl_width_inch'),#PNL宽inch
#        'type_new':fields.function(_outsource_type,method=True,type='char',string='type_new',size=32),
        'receive_note':fields.char('receive_note',size=32),
        #'current_workcenter_id':fields.many2one('mrp.workcenter','current_workcenter_id'),
        'qty_receive':fields.integer('qty_receive'),#回货 数量
        'qty_pnl_receive':fields.integer('qty_pnl_receive'),#回货pnl数量
        ##process args info
        'nickel_thickness':fields.float("nickel_thickness(u')"),#镍厚
        'gold_thickness':fields.float("gold_thickness(u')"),#金厚
        'pcb_remove':fields.boolean('pcb_remove'),#PCB移植
        'gold_finger_norms':fields.integer('gold_finger_norms'),#金手指规格数
        'gold_finger_width':fields.float('gold_finger_width'),
        'gold_finger_height':fields.float('gold_finger_height'),
        'finger_count':fields.integer( 'finger_count',),
        'gold_finger_width2':fields.float('gold_finger_width2'),
        'gold_finger_height2':fields.float('gold_finger_height2'),
        'finger_count2':fields.integer( 'finger_count2',),
        'gold_finger_width3':fields.float('gold_finger_width3'),
        'gold_finger_height3':fields.float('gold_finger_height3'),
        'finger_count3':fields.integer( 'finger_count3',),
        'gold_finger_width4':fields.float('gold_finger_width4'),
        'gold_finger_height4':fields.float('gold_finger_height4'),
        'finger_count4':fields.integer( 'finger_count4',),
        'gold_finger_width5':fields.float('gold_finger_width5'),
        'gold_finger_height5':fields.float('gold_finger_height5'),
        'finger_count5':fields.integer( 'finger_count5',),
        'gold_finger_width6':fields.float('gold_finger_width6'),
        'gold_finger_height6':fields.float('gold_finger_height6'),
        'finger_count6':fields.integer( 'finger_count6',),
        'gold_fingers':fields.integer('gold_finger'),#喷锡金手指数量
        'pcs_unit_count':fields.integer('pcs_unit_count'),#排版unit数
        'gold_description':fields.char('gold_description',size=32),
        'red_tape_length':fields.float('red_tape_length(inch)'),#红胶带长度
        'red_tape_article':fields.float('red_tape_article'),#红胶带条数
        
        'product_area':fields.function(_info_get_area,method=True,type='float',string='product_area'),#产品面积
        'plate_hole_count':fields.integer('plate_hole_count'),#盘中孔
        'state':fields.selection(_state_list,'process state',readonly=True,required=True),
        'reason_cancel':fields.char('reason_cancel',size=256),
        'if_cancel':fields.boolean('if_cancel'),
        
        'responsible_id':fields.many2one('res.users','responsible_id'),
        
        'delivery_type':fields.selection([('delivery_company','delivery_company'),('customer_pick','customer_pick')],'delivery_type'),
        'process_send_time':fields.datetime('process_send_time'),#外协产品发出时间
   
        'outsource_partner_id'   :fields.many2one("res.partner", 'Outsource Supplier', size=16, select=True,domain=[('supplier','=',True)]),
        'dispatch_state':fields.selection([('wait_dispatch','wait_dispatch'),('already_dispatch','already_dispatch')],'dispatch_state',readonly=True),
        'if_have_tax':fields.boolean('if_have_tax'),
        'account_tax_id':fields.many2one('account.tax','account_tax_id'),#单价税率
        ##表面处理：
        'film_thickness':fields.float('film_thickness'),#膜厚
        'norms_mark':fields.char('norms_mark',size=256),
         ##沉银
         'silver_thickness':fields.float('silver_thickness'),  #银厚
         'board_types':fields.selection([('big_board','big_board'),('small_board','small_board')],'board_types'),#大小板类
         'sn_thickness':fields.float('sn_thickness'),#锡厚
         'if_fault':fields.boolean('if_fault'),#对账一致
         'if_have_duizhangs':fields.boolean('if_have_duizhangs'),#是否已对账
         'note':fields.text('note'),#备注
         'wire_draw_types':fields.selection([('sand_blast','sand_blast'),('wire_draw','wire_draw'),('oxide_anodes','oxide_anodes'),('sand_oxide','sand_oxide'),('wire_oxide','wire_oxide')],'wire_draw_types'),
         'meter':fields.float('meter'),# 米
         'cut_type':fields.selection(_c_type,'cut_type'),#切割类型
         'repair_type':fields.selection([('brush_finger','brush_finger'),('repair_line','repair_line'),('brush_gold','brush_gold')],'repair_type'),#修金板类型
         'osp_type':fields.selection([('normal','normal'),('special','special')],'osp_type'),#osp类型
         'pd_thick':fields.float('pd_thick'),#钯厚
         'receive_board':fields.boolean('receive_board'),#是否回货
         'finish_time':fields.datetime('finish_time'),# 回货时间
         'laminate_types':fields.selection([('normal_board','normal_board'),('special_board','special_board'),('high_tg','high_tg'),('middle_tg','middle_tg')],'laminate_types'),#层压板类型
         'length_pp':fields.integer('length_pp'),#长PP片
         'width_pp':fields.integer('width_pp'),#宽PP片
         'aoi_test_count':fields.integer('aoi_test_count'),#aoi测试面数
         'laminate_cu_thickness':fields.char('laminate_cu_thickness', size=32),#层压铜厚
         'laminate_board_thickness':fields.float('laminate_board_thickness'),#层压板厚
        #'price_units_single':fields.fields.function(_info_get,method=True,type='float',string='product_area'),#产品面积,#单面单价
    }

    _defaults={
        'state':lambda *a:'draft',
        'board_types':lambda *a:'big_board',
        'repair_type':lambda *a:'brush_gold',
        'osp_type':lambda *a:'normal',
        'silver_thickness':lambda *a:9,
               }
    def updata_state(self,cr,uid,ids,state=None,context=None):
        
        my=self.browse(cr,uid,ids[0])
        line_obj=self.pool.get('outsource.process.lines')
        if state=='cancel':
            if my.process_lines_id:
                line_id=my.process_lines_id.id
                if not my.reason_cancel:
                    raise osv.except_osv(('reason error:'),('cancel reason not found!,please input..'))
                line_obj.write(cr,uid,line_id,{'state':'cancel','reason_cancel':my.reason_cancel})
        self.write(cr,uid,ids,{'state':state})
        return True
    
    def onchange_if_cancel(self,cr,uid,ids,field_value,reason,context=None):
        if field_value:
            if reason:
                return {'value':{'state':'cancel'}}
            else:
                return {'value':{'if_cancel':False}}
                raise osv.except_osv(('reason error:'),('cancel reason not found,please input cancel reason...'))
        else:
            return {'value':{}}
     
    def onchange_process_lines_id(self,cr,uid,ids,res_id,context=None):
        lines_obj=self.pool.get('outsource.process.lines') 
        lines_rec={}
        if res_id:
            process_type=lines_obj.browse(cr,uid,res_id).outsource_apply_id.outsource_type
            print process_type
            lines_rec=lines_obj.read(cr,uid,res_id)
            print lines_rec
            lines_rec['process_type']=process_type
            print lines_rec['process_type']
        return{'value':lines_rec}
        
      
        
        
        
        
        
        
    
    def onchange_process_type(self,cr,uid,ids,field_value,context=None):
        print field_value,'process_type'
        type_dic={ 
        'sink_silver':['length','width','product_qty','silver_thickness','top_area','bottom_area','board_types'],
        'sink_Sn':['length','width','product_qty','board_thickness','top_area','bottom_area','board_types'],
#        'sink_Sn':['length','width','product_qty','board_types'],
        
        'other':[],
        'hot_equating(have pb)':[],
        'hot_equating(not have )':[],
        'brush_plated_board':[],
        'OSP':['top_area','bottom_area','qty_pnl','board_types'],
#20131209        'sink_gold':['gold_thickness','nickel_thickness','top_area','bottom_area','qty_pnl'],
        'sink_gold':['qty_pnl'],
        'drill_outsource':['board_thickness','layer_count','hole_count','min_hole_dia','cu_thickness','slot_hole_count','join_hole_count','special_hole_count'],
        'gold_finger_plated':['gold_finger_width','gold_finger_height','finger_count','gold_thickness','qty_pnl','pcs_unit_count','nickel_thickness'],
        'gold_plated':['gold_finger_width','gold_finger_height','finger_count','gold_thickness','qty_pnl','pcs_unit_count','nickel_thickness'],
        'spray_Sn(have pb)':['pnl_length','pnl_width','qty_pnl','red_tape_length','red_tape_article'],
        'spray_Sn(nhav pb)':['pnl_length','pnl_width','qty_pnl','red_tape_length','red_tape_article'],
        'flying_probe':['if_fpc_sample','if_low_resistance','board_thickness','pnl_length','pnl_width','if_retest','points_count'],
        'shape_VCUT':['v_cutter_count','vcut_size','board_type','board_thickness'],
        'shape_gong_side':['board_type','board_thickness','gong_slot_count','cutter_size','sink_hole_count','horn_hole_count'],
        'VCUT+ gong_side':['board_type','board_thickness','v_cutter_count','vcut_size','gong_slot_count','cutter_size','sink_hole_count','horn_hole_count'],
        'plasma_process':['board_type'],
        'laser_drill':['board_material','qty_pnl'],
        'wire_drawing':['pnl_width','pnl_length'],
        'bf_laminate_pre':['pnl_width','pnl_length'],
        'cutting':['pnl_width','pnl_length'],#切割
        'repait_gold':['qty_receive','qty_pnl_receive'],#修金板

            }
        trans_obj=self.pool.get('ir.translation')
        args=''
        if field_value:
            temp_list=[]
            for field_name in type_dic[field_value]:       
                res_name=self._name+','+field_name
                types='field'
                lang='zh_CN'
                source=self._columns[field_name].string
                trans=trans_obj. _get_source( cr, uid, res_name, types, lang, source)
                if trans:
                    temp_list.append(trans)
                else:
                    temp_list.append(field_name)
            args=';'.join(temp_list)
        return {'value':{'process_args_info':args}}
    
    def process_cost_compute(self,cr,uid,ids,context=None):
        
        my=self.browse(cr,uid,ids[0])
        cost_base=0.0
        pcs_price_units=None
        pnl_price_units=None
        price_base=0.0
        price_bases=0.0
        default_min_cost=0.0
        pros_type=my.process_type
        if pros_type =='sink_gold':
            price_base,cost_base,default_min_cost=self.action_sink_gold(cr,uid,ids,process_type=pros_type,context=context)
        elif pros_type =='OSP':
            price_base,cost_base,default_min_cost=self.action_osp(cr,uid,ids,process_type=pros_type,context=context)   
            
        elif pros_type == 'drill_outsource':
             price_base,cost_base,default_min_cost=self.action_drill_outsource(cr,uid,ids,context=context)
        elif pros_type == 'gold_finger':
             price_base,cost_base,default_min_cost=self.action_gold_finger_plated(cr,uid,ids,context=context)
        elif pros_type in ['spray_Sn have pb','spray_Sn nhav pb']:
             price_base,cost_base,default_min_cost=self.action_spray_sn(cr,uid,ids,sn_type=pros_type,context=context)
        elif pros_type == 'flying_probe':
             price_base,cost_base,default_min_cost=self.action_fly_needle(cr,uid,ids,context=context)
        elif pros_type in ['shape_VCUT']:
             price_base,cost_base,default_min_cost=self.action_shape_vcut(cr,uid,ids,context=context)
        elif pros_type in['shape_gong_side','VCUT+ gong_side']:
             price_base,cost_base,default_min_cost=self.action_gong_side(cr,uid,ids,sh_type=pros_type,context=context)
        elif pros_type == 'plasma_process':
             price_base,cost_base,default_min_cost=self.action_plasma_process(cr,uid,ids,context=context)
        elif pros_type == 'laser_drill':
             price_base,cost_base,default_min_cost=self.action_laser_drill(cr,uid,ids,context=context)
        elif pros_type == 'wire_drawing':
             price_base,cost_base,default_min_cost=self.action_wire_drawing(cr,uid,ids,context=context)
        elif pros_type == 'bf_laminate_pre':
             price_base,cost_base,default_min_cost=self.action_bf_laminating_process(cr,uid,ids,context=context)
        elif pros_type == 'sink_silver':
             price_base,cost_base,default_min_cost=self.action_sink_silver(cr,uid,ids,context=context)
        elif pros_type =='cutting':
            price_base,cost_base,default_min_cost=self.action_cutting(cr,uid,ids,context=context)     
        elif pros_type == 'sink_Sn':
             price_base,cost_base,default_min_cost=self.action_sink_sn(cr,uid,ids,context=context)
        elif pros_type == 'repair_gold':
            price_base,cost_base,default_min_cost=self.action_repair_gold(cr,uid,ids,context=context)
        elif pros_type =='laminate' :
            price_base,cost_base,default_min_cost=self.action_laminate(cr,uid,ids,context=context)
        elif pros_type =='aoi' :
            price_base,cost_base,default_min_cost=self.action_aoi(cr,uid,ids,context=context)  
        elif pros_type =='sliver_plating':
            price_base,cost_base,default_min_cost=self.action_sliver_plating(cr,uid,ids,context=context)    
            
        if my.board_types=='small_board':
            price_base==pcs_price_units
            self.write(cr,uid,ids,{'pcs_price_units':price_base,})
        elif my.board_types=='big_board':
            price_base==pnl_price_units
            self.write(cr,uid,ids,{'pnl_price_units':price_base,})
        else:
            self.write(cr,uid,ids,{'pnl_price_units':price_base,})    
        print cost_base,'process cost_total'
        self.write(cr,uid,ids,{'cost_total':cost_base,'default_min_cost':default_min_cost})
        return True     
    
    def action_sink_gold(self,cr,uid,ids,process_type=None,arg_category=None,context=None):
        ##化学镍金(沉金费用计算):pnl单价 or pcs单价 ?
        ##最低消费 min_cost: 52.0 (condition:cost_base <=52.0)
        ##默认金厚：1.5u'', 镍厚：145u''
        ##加价基本镍厚:150u'', 加价值:50u'',总价加价比例:10%

        price_base=None
        cost_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        pd_thick=my.pd_thick
        ser_domain=[('process_category','=','chemical_process_c')]
        ni_thickness=my.nickel_thickness
        gd_thickness=my.gold_thickness
#20131209         check_args=['nickel_thickness','gold_thickness','top_area','bottom_area']
        
        
        
        
        
#20131209         self.check_cost_args(cr, uid, ids,check_args,context=context)
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
      
        if process_type:
             ser_domain.append(('process_type','=',process_type))   
      
        ser_domain.append((('nickel_thickness','=',145)))
        if gd_thickness:
            ser_domain.append(('gold_thickness','=',gd_thickness))
        if pd_thick:
            ser_domain.append(('pd_thickness','=',pd_thick))


#20131209        else:
#20131209            raise osv.except_osv(('gold_thickness error:'),('gold_thickness not found,please check!'))
        ##:search base price in outsource_cost_argument
        print ser_domain,'domain'
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        arg_rec=None
#20131209         if len(arg_ser)>1 :
#20131209             raise osv.except_osv(('args error:'),('search args record must be uniqueness,please check!')) 
        if not arg_ser:
             raise osv.except_osv(('args error:'),('search args record not found,please check! %s') % (ser_domain)) 
#20131209         else:
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        reduce_length=arg_rec.default_length_reduce
        reduce_width=arg_rec.default_width_reduce  
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id
        default_lowest_cost=arg_rec.default_lowest_cost
        
        ##:>40::=[1+-40%)/40%]X
        if my.top_area and my.bottom_area:
            rat_area=my.top_area + my.bottom_area
            if rat_area >40 and price_base:
                price_base=(1+(rat_area/2 -20)/20 ) * price_base
            print 'price_base:',price_base
                
                
        
      
        ##
        if my.qty_pnl_receive and price_base:
#            cost_base=price_base * my.qty_pnl * (my.pnl_length - reduce_length)  * (my.pnl_width - reduce_width)/1000000
             cost_base=price_base * my.qty_pnl_receive * (my.pnl_length  * my.pnl_width)/1000000
        ##pcs
        #if my.product_qty:
            #cost_base=price_base * my.product_qty
            
        ##:>150 : 
        base_ratio=0.1 # 10%
        add_ratio=0.0
        print price_base,'price_base',cost_base
        if my.nickel_thickness ==150:
            add_ratio=base_ratio
        elif my.nickel_thickness >150:
            quot=(my.nickel_thickness - 150) / 50 ##           
            add_ratio=base_ratio * (1+quot)
        
        ## 
        cost_base=cost_base * (1+add_ratio)
        if cost_base and cost_base < default_lowest_cost:
            cost_base=default_lowest_cost
        default_min_cost=default_lowest_cost
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id,'pnl_price_units':price_base})
        return price_base,cost_base,default_min_cost
      
    def action_drill_outsource(self,cr,uid,ids,context=None):
        ##多种孔径:取最小孔径(min_hole: >=5.0 每孔:0.03元  孔数: <1000:default :1000
        ##加价基本铜厚:2oz ,加价比例:0.1(10%),加价铜厚值:1oz
        ##  钻槽孔,连孔,异形孔:孔数2倍计算
        ##双面板:min_cost:50 多层板:min_cost:70
        ##层数加价: 以双面板为基准,每增加2层,单价增加比例:0.1(10%)
        ##板厚加价: 以1.6mm为基准,每增加0.4mm,单价增加比例:0.1(10%)
        cost_base=0.0
        price_base=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        arg_rec=None
        bod_ths=my.board_thickness
        layer_count=my.layer_count
        hole_count=my.hole_count
        hole_value=my.min_hole_dia
        partner_id=my.partner_id.id
        ##search partner drill_outsource cost
        if bod_ths >1.60:
            bod_ths=1.60
        if layer_count>10 and my.partner_id.id == 5727:
            layer_count=10
        if layer_count >2 and my.partner_id.id != 5727:
            layer_count=2
            print layer_count,'layer_count'
        elif layer_count <4 and my.partner_id.id == 5727:
            layer_count=4
            print layer_count,'layer_count'
        if hole_value <0.2 and my.partner_id.id == 5727:
            hole_value=0.2
        if hole_value and bod_ths:
            print hole_value,bod_ths,'ths'
#            arg_ser=arg_obj.search(cr,uid,[('min_hole_value','<=',hole_value),('max_hole_value','>=',hole_value),
#                                                            ('min_board_thickness','<=',bod_ths),('max_board_thickness','>=',bod_ths),
#                                                            ('layer_count','=',layer_count),('hole_count','=',1000),('outsource_partner_id','=',my.outsource_process_id.partner_id.id)])
            
            ser_domain=[('min_hole_value','<=',hole_value),('max_hole_value','>=',hole_value),
                                                            ('min_board_thickness','<=',bod_ths),('max_board_thickness','>=',bod_ths),
                                                            ('layer_count','=',layer_count),('hole_count','=',1000),]
            if my.outsource_process_id.partner_id:
                ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
                arg_ser=arg_obj.search(cr,uid,ser_domain)
                print arg_ser,'arg_ser'
            if len(arg_ser) >1:
                 raise osv.except_osv(('drill args error:'),('drill args search must be unique,please check! %s')%(ser_domain))
            elif not arg_ser:
                 raise osv.except_osv(('drill args error:'),('drill args search not found,please check! %s')%(ser_domain))
            else:
                arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_base,'price_base'   
        ##铜厚加价:基本铜厚2oz,增加值:1oz,单价加价比例:0.1
        print my.cu_thickness,'thick'
        cu_add=0.0
        if my.cu_thickness:
            add_ratio=0.0
#            if '/oz' in my.cu_thickness:
#                cu_val=my.cu_thickness.split('/oz')[0]
            if 'oz' in my.cu_thickness:
             
                cu_val1=my.cu_thickness.split('oz')[0]
                if cu_val1=='1/2' :
                    cu_val1='0.5'
                if cu_val1=='H/H' :
                    cu_val1='0.5'
                if cu_val1=='1/3' :
                    cu_val1='0.33'
                if cu_val1=='2/3' :
                    cu_val1='0.67'
                if cu_val1=='3/2' :
                    cu_val1='1.5'
                if cu_val1=='1/1':
                    cu_val1='1'
                if cu_val1=='1.2/1.2':
                    cu_val1='1'
                if cu_val1=='2/2' :
                    cu_val1='2'
                if cu_val1=='1.5/1.5' :
                    cu_val1='1.5'
                if cu_val1=='3/3' :
                    cu_val1='3'
                if cu_val1=='4/4' :
                    cu_val1='4'
                if cu_val1=='5/5' :
                    cu_val1='5'
                if cu_val1=='6/6' :
                    cu_val1='6'
                if cu_val1=='7/7' :
                    cu_val1='7'
                if cu_val1=='8/8' :
                    cu_val1='8' 
                if cu_val1=='4/2' :
                    cu_val1='2'
                if cu_val1=='2/1' :
                    cu_val1='1'    
                if cu_val1=='3/1':
                    cu_val1='1'       
                cu_val=string.atof(cu_val1)  #string.atofint
            
                print 'cu_val:',cu_val
        #5703深辉; 5731 丰恒源;5713优钻;5727宏腾
            if cu_val >2 and my.partner_id.id != 5727 and my.partner_id.id != 5731:
                add_ratio=(cu_val -2) * 0.1
                cu_add+=price_base * add_ratio
            elif cu_val >1 and my.partner_id.id == 5727:
                add_ratio=(cu_val -1) * 0.1
                cu_add+=price_base * add_ratio
            elif cu_val >2 and my.partner_id.id == 5731:
                add_ratio=(cu_val -2)
                cu_add+=price_base * 1.1**add_ratio-price_base
                
            
        ##多层板加价:基本层数2层,增加值:2层,单价加价比例:0.1
        layer_add=0.0
        if my.layer_count:
            if my.layer_count >2 and my.partner_id.id != 5727 and my.partner_id.id != 5731 :
                add_ratio=((my.layer_count -2)/ 2) * 0.1
                layer_add+=price_base * add_ratio
            elif my.layer_count>10 and my.partner_id.id == 5727:
                add_ratio=((my.layer_count -10)/ 2) * 0.1
                layer_add+=price_base * add_ratio
            elif my.layer_count>2 and my.partner_id.id == 5731:
                add_ratio=((my.layer_count -2)/ 2)
                layer_add+=price_base * 1.1**add_ratio - price_base
                
            
        ##板厚加价:基本板厚1.6mm,增加值:0.4mm,单价加价比例:0.1
        board_add=0.0
        if my.board_thickness > 1.60 and my.partner_id.id != 5727 and my.partner_id.id != 5731:
            val_add=my.board_thickness - 1.6
            if (val_add / 0.4):
                add_ratio=(val_add / 0.4) * 0.1
                board_add+=price_base * add_ratio
        elif my.board_thickness > 1.60 and my.partner_id.id == 5727:
                val_add=my.board_thickness - 1.6
                if (val_add / 0.4):
                    add_ratio=(val_add / 0.4) * 0.2
                    board_add+=price_base * add_ratio 
                    
        elif my.board_thickness > 1.60 and my.partner_id.id == 5731:
                val_add=my.board_thickness - 1.6
                if (val_add / 0.4):
                    add_ratio=(val_add / 0.4)
                    board_add+=price_base * 1.1**(add_ratio) - price_base    
        ##加价后单价:
        print board_add,cu_add,layer_add,'add_value:board_add,cu_add,layer_add'
        price_base+=(cu_add +   layer_add +   board_add)
        
        ##钻槽孔、连孔、异形孔:孔数 *2
        hole_other=(my.slot_hole_count + my.join_hole_count + my.special_hole_count) * 2
        hole_count+=hole_other
        
        ##min_hole_dia:>5.0 :price_units:0.03/个 并且孔数:>1000时:计算
        if hole_count <1000:
                hole_count=1000
        if my.min_hole_dia >5.0 and my.partner_id.id != 5727:
            price_base=0.03

            
        cost_base=price_base * hole_count * my.qty_pnl_receive /1000
        print price_base,'price_base',hole_count,'hole_count',my.qty_pnl_receive,'qty_pnl','cost_base',cost_base
        default_min_cost=0.0
       
        if my.layer_count <=2 and my.qty_pnl_receive !=0 :
            if cost_base <50.0:
                cost_base=50.0
                default_min_cost=50
        elif my.layer_count>2 and my.partner_id.id == 5703 and my.qty_pnl_receive !=0 or my.partner_id.id == 5734 and my.qty_pnl_receive !=0:
            if cost_base <50.0:
                cost_base=50.0
                default_min_cost=50
                
        else:
            if  my.layer_count >2 and cost_base <70.0 and my.qty_pnl_receive !=0 and my.partner_id.id != 5703 and my.partner_id.id != 5734:
                cost_base=70.0
                default_min_cost=70
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id,'pnl_units':price_base})
        return price_base,cost_base,default_min_cost
    
    def action_gold_finger_plated(self,cr,uid,ids,context=None):
        ##金手指费用计算
        ##pcs支数:金手指长X宽/7(mm2)XPCS总支数/排版unit数
        ##单价:根据金厚和PCS支数 search:outsource.cost.argument ; 
        ##单价：qty_pnl_pcs <=8:单价=所查单价+2.65/拼板数
        ##总价=单价X排版Unit数XPNL数
        ##镍厚加价:基本镍厚:150u'',基本比例:0.1(10%)  增加值:50,总价增加比例:0.05(5%)
        ##金厚:<20u''  每笔档案号min_cost:200元; >=20u'' 每笔档案号min_cost:300元
        price_base=0.0
        cost_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_type','=','gd_finger_plated')]
       
        
        ##search gold_finger price_units in outsource.cost.argument 
        ## gold_finger area:
#        check_args=['nickel_thickness','gold_thickness']
        
#        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
        fig_count_all=0
        fig_width=['gold_finger_width']
        fig_height=['gold_finger_height']
        fig_count=['finger_count']
        ## 多种金手指规格:     
       
        for i in range(2,7):
            wth=fig_width[0] + str(i)
            hgh=fig_height[0] + str(i)
            cnt=fig_count[0] + str(i)
            fig_width.append(wth)
            fig_height.append(hgh)
            fig_count.append(cnt)
        print wth,hgh,cnt,'cnnt'
        for i in range(0,6):
            rec_dic=self.read(cr,uid,ids[0],[ fig_width[i],fig_height[i],fig_count[i] ])
            
            fg_area=rec_dic[fig_width[i]] * rec_dic[fig_height[i]]
            fg_cnt=(fg_area / 7) * rec_dic[fig_count[i]] / my.pcs_unit_count
         
#2014-03-10            fig_count_all+=fg_cnt    累计金手指支数
        fig_count_all=my.finger_count
        if fig_count_all >300:
            fig_count_all=300
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        if fig_count_all:
           
            temp_list=[('au_thick_min','<',my.gold_thickness),
                                ('au_thick_max','>=',my.gold_thickness),
                                ('finger_count_min','<=',fig_count_all),
                                ('finger_count_max','>=',fig_count_all)]
            ser_domain+=temp_list  
        else:
            raise osv.except_osv(('gold_finger args or gold_thickness info error:'),('gold_finger args or gold_thickness info not found,please check!'))
        print fig_count_all,'fig_count_all',ser_domain
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        print 'arg_ser',arg_ser
        arg_rec=None
        if len(arg_ser) >1:
            raise osv.except_osv(('gold finger args error:'),('gold finger args search must be unique,please check! %s')% (ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('gold finger args error:'),('gold finger args search not found,please check! %s')% (ser_domain))
        else:
            arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        if my.finger_count>300:
            print my.finger_count,'fig_count_all'
            price_base=price_base/300 * my.finger_count
            
        if my.pcs_unit_count <=8:
            #单价=所查单价+2.65/拼板数
            if price_base:
                price_base+=2.65 / my.pcs_unit_count
        
        ##计算总价:单价X排版Unit数XPNL数
        print 'price_base',price_base
        if my.qty_pnl_receive and price_base and my.pcs_unit_count:
            cost_base=price_base * my.pcs_unit_count * my.qty_pnl_receive
        print 'cost_base',cost_base
        ##镍厚加价:基本镍厚:150u'',基本比例:0.1(10%)  增加值:50,总价增加比例:0.05(5%)
        if my.nickel_thickness:
            ratio_base=0.1
            ratio_add=0.05
            rat_total_add=0.0
            if my.nickel_thickness ==150:
                rat_total_add=ratio_base
            elif my.nickel_thickness > 150:
                quot=(my.nickel_thickness -150) / 50
                if quot:
                    rat_total_add=ratio_base + quot * ratio_add
            if rat_total_add:
                cost_base=cost_base * (1+rat_total_add)
            print 'cost_base',cost_base
       
            ##check:min_cost  on gold_thickness
        default_min_cost=0.0
        if my.gold_thickness <20:
            if cost_base <200:
                cost_base=200
            default_min_cost=200
        elif my.gold_thickness >=20:
            if cost_base  <300:
                cost_base=300
            default_min_cost=300
       
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    def action_sink_sn(self,cr,uid,ids,context=None):
        ##沉锡费用计算:板厚在：0.4--2.0mm,top\bot面积<=20%,默认60元/M2
        ##top/bot面积：>20%,按比例加收；板厚:>2.0mm,加工费加收20%
        ##每pcs面积：<100mm * 100mm;按：100mm * 100mm
        ##最低收费：60元/款。
        price_base=0.0
        red_tape_price=None
        cost_base=0.0
        default_min_cost=0.0
        tl_area=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_type','=','sink_Sn'),('sink_sn_type','=',False)]
        ser_domain+=[('min_sn_thick','<=',my.sn_thickness),('max_sn_thick','>=',my.sn_thickness),('board_type_new','=',my.board_types)]
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        bd_thk=my.board_thickness
        tb_val=my.bottom_area + my.top_area
        pcs_area=my.width * my.length
        
#20131209       check_args=['top_area','bottom_area']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
        print 'server domain',ser_domain
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        arg_rec=None
#20131209       if len(arg_ser) >1:
#20131209            raise osv.except_osv(('sink sn args error:'),('sink sn args search must be unique,please check!'))
        if not arg_ser:
            raise osv.except_osv(('sink sn args error:'),('sink sn args search not found,please check! %s')% (ser_domain))
#20131209        else:
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        default_lowest_cost=arg_rec.default_lowest_cost
        if_have_tax=arg_rec.if_have_tax
        board_ty=arg_rec.board_type_new
#        reduce_width=arg_rec.default_width_reduce
#       reduce_length=arg_rec.default_length_reduce
        red_tape_price=arg_rec.red_tape_price
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id
        print 'price_base',price_base
        if my.board_types=='small_board':
            if pcs_area < 10000 and my.qty_receive:
                tl_area=my.product_area * my.qty_pnl_receive
            else:
                tl_area=(my.length * my.width) /(100 *10000) * my.qty_receive
                print tl_area,'tl_area'
     
        elif my.board_types=='big_board':
            pnl_area=(my.pnl_width * my.pnl_length)/1000000*my.qty_pnl_receive
            print pnl_area,'pnl_area'
        #cost_base=price_base * tl_area
        
        if tb_val > 20:
            price_base=price_base *  (1+(tb_val-20)/100)
            print 'top_bottom add cost',price_base
       
        if arg_rec.board_type_new:
            if my.board_types=='small_board':
                board_ty=='small_board'
                cost_base=price_base * tl_area
            elif my.board_types=='big_board':
                board_ty=='big_board'
                cost_base=price_base * pnl_area
        if bd_thk > 2.0:
            bd_add_cost=cost_base * 0.2
            cost_base+=bd_add_cost
            print 'board_thick add cost',bd_add_cost
        if my.red_tape_article and red_tape_price:
            red_tape_cost=my.red_tape_article * red_tape_price
            cost_base+=red_tape_cost
            print 'red_tape_cost add ',red_tape_cost   
            
        if cost_base < default_lowest_cost:
            cost_base=default_lowest_cost
            default_min_cost=cost_base
        return price_base,cost_base,default_min_cost
       
    
    def action_sink_silver(self,cr,uid,ids,context=None):
        ##沉银费用计算
        price_base=0.0
        red_tape_price=None
        cost_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','chemical_process_a'),('process_type','=','sink_silver')]
        ser_domain+=[('min_silver_thick','<=',my.silver_thickness),('max_silver_thick','>=',my.silver_thickness),('board_type_new','=',my.board_types),('sink_sliver_type','=',my.sink_sliver_type)]
        tl_area=None
        total_pnl_area=None
        price_units=None
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        print 'ser_domain' ,ser_domain
        
#20131209        check_args=['top_area','bottom_area']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
        arg_ser=arg_obj.search(cr,uid,ser_domain)
#20131209        if len(arg_ser) >1:
#20131209            raise osv.except_osv(('sink silver args error:'),('sink silver args search must be unique,please check!'))
        if not arg_ser:
           raise osv.except_osv(('sink silver args error:'),('sink silver args search not found,please check! %s')% (ser_domain))
#20131209        else:
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        
        if arg_rec:
            ## get default reduce length,width,price_units,red_tape_price
            reduce_length=arg_rec.default_length_reduce
#            reduce_width=arg_rec.default_width_reduce
#            red_tape_price=arg_rec.red_tape_price
            price_base=arg_rec.price_units
            if_have_tax=arg_rec.if_have_tax
            board_ty=arg_rec.board_type_new
            default_min_costs=arg_rec.default_lowest_cost
            tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
            
            pcs_area=my.width * my.length
            pnl_area=(my.pnl_width * my.pnl_length)
           
            if my.board_types=='small_board':
                    board_ty=='small_board'
                    pcs_area  and my.qty_receive
#                    tl_area=pcs_area/(100 * 10000) * my.product_qty
                    tl_area=pcs_area/(100 * 10000) * my.qty_receive
                        
            elif my.board_types=='big_board':
                 board_ty=='big_board'
                 pnl_area  and my.qty_pnl_receive
#                 total_pnl_area=pnl_area/1000000*my.qty_pnl
                 total_pnl_area=pnl_area/1000000*my.qty_pnl_receive
            print total_pnl_area,'total_pnl_area',tl_area,'pcs_area'
            #pnl_area=(my.pnl_length - reduce_length)  * (my.pnl_width - reduce_width) * my.qty_pnl / (100 *10000)
            ##pnl_area:<0.1m2  default:1.8元/pnl (have pb); pnl_area:<0.1m2  default:3.9元/pnl (not_have pb)
            
            ##count top and bottom:(top + bottom)/2 >25:应收单价=基本单价 * 4(/25%) * area  
            tb_area=my.top_area + my.bottom_area
            if tb_area /2 > 25:
                price_base=price_base * 4 * (tb_area/100)
                print 'reality price units',price_base
#            cost_base=tl_area * price_base
            
            
            if arg_rec.board_type_new:   
                if my.board_types=='small_board':
                    board_ty=='small_board'
                    cost_base=tl_area * price_base
                    print cost_base,'small_board_cost'
                elif my.board_types=='big_board':
                    board_ty=='big_board'
                    cost_base=total_pnl_area * price_base
                    print cost_base,'big_board_cost'
            print cost_base,'really_cost_base',price_base,'price_units'
            
            ##set尺寸加价：
            if my.board_types=='small_board' and pcs_area < 76 * 127:
                set_area_add=tl_area * 15
                cost_base+=set_area_add
                print 'set add cost',set_area_add
            ##贴胶费
            if my.red_tape_article:
                red_tape_add=red_tape_price * my.red_tape_article
                cost_base+=red_tape_add
                print 'red tape add cost',red_tape_add
                print 'price_units',price_base,'really_cost_base',cost_base,
 #           else:
 #               raise osv.except_osv(('red_tape  info error:'),('red_tape info not found,please check!'))
            if 0<cost_base < default_min_costs:
                cost_base=default_min_costs
                default_min_cost=default_min_costs
        return price_base,cost_base,default_min_cost 
    
    def action_osp(self,cr,uid,ids,process_type=None,price_base=None,context=None):
        
        
        price_base=None
        cost_base=0.0
        default_min_cost=0.0
        tl_area=0.0
        my=self.browse(cr,uid,ids[0])
        osp_type=my.osp_type
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','chemical_process_d'),('process_type','=','OSP'),('osp_type','=',osp_type)]
        ser_domain+=[('board_type_new','=',my.board_types)]
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        bd_thk=my.board_thickness
        tb_val=my.bottom_area + my.top_area
        pcs_area=my.width * my.length
        
#20131209        check_args=['top_area','bottom_area']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
        print 'server domain',ser_domain
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        arg_rec=None
#        if len(arg_ser) >1:
#            raise osv.except_osv(('osp args error:'),('osp args search must be unique,please check!'))
        if not arg_ser:
            raise osv.except_osv(('osp args error:'),('osp args search not found,please check! %s')% (ser_domain))
#20131209        else:
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        board_ty=arg_rec.board_type_new
#        reduce_width=arg_rec.default_width_reduce
#        reduce_length=arg_rec.default_length_reduce
        if_have_tax=arg_rec.if_have_tax
        default_min_cost=arg_rec.default_lowest_cost
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id
        print 'price_base',price_base
        if my.board_types=='small_board':
            tl_area=(my.length * my.width) /(100 *10000) * my.qty_receive
            print tl_area,'tl_area'
     
        elif my.board_types=='big_board':
            pnl_area=pnl_area=(my.pnl_width * my.pnl_length)/1000000*my.qty_pnl_receive
            print pnl_area,'pnl_area'
#cost_base=price_base * tl_area
#        if tb_val > 20:
#            price_base=price_base * 5 * (tb_val/100)
#            print 'top_bottom add cost',price_base
        if arg_rec.board_type_new:
            if my.board_types=='small_board':
                board_ty=='small_board'
                cost_base=price_base * tl_area
            elif my.board_types=='big_board':
                board_ty=='big_board'
                cost_base=price_base * pnl_area
#        if bd_thk > 2.0:
#            bd_add_cost=cost_base * 0.2
#            cost_base+=bd_add_cost
#            print 'board_thick add cost',bd_add_cost
            
        if 0<cost_base < default_min_cost:
            cost_base=default_min_cost
            
        return price_base,cost_base,default_min_cost 
    
    
    
    def action_spray_sn(self, cr, uid, ids, sn_type=None, context=None):


        ##喷锡费用计算
        ##有铅喷锡:18元/平米,每款最低消费1.8元;无铅喷锡：39元/平米，每款最低消费3.9元
        ##贴耐高温红胶带：按条计算，0.1元/英寸，不足0.3元按0.3元计算
        price_base=0.0
        red_tape_price=None
        cost_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','chemical_process_b'),('process_type','=','sink_Sn')]
        
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        if sn_type:
            ser_domain.append(('sink_Sn_type','=',sn_type))
         
        ##search partner sink sn args
#20131209        check_args=['red_tape_length','red_tape_article']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
        arg_rec=None
        print 'ser_domain' ,ser_domain
        arg_ser=arg_obj.search(cr,uid,ser_domain)
#20131209       if len(arg_ser) >1:
#20131209            raise osv.except_osv(('sink sn args error:'),('%s args search must be unique,please check!' % sn_type))
        if not arg_ser:
           raise osv.except_osv(('sink sn args error:'),('%s args search not found,please check! %s')% (ser_domain))
#20131209        else:
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        
        if arg_rec:
            ## get default reduce length,width,price_units,red_tape_price
#            reduce_length=arg_rec.default_length_reduce
#            reduce_width=arg_rec.default_width_reduce
            red_tape_price=arg_rec.red_tape_price
            price_base=arg_rec.price_units
            price_min=arg_rec.price_min
            if_have_tax=arg_rec.if_have_tax
            tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        
            pnl_area=(my.pnl_length  * my.pnl_width)/ (100 *10000)
            ##pnl_area:<0.1m2  default:1.8元/pnl (have pb); pnl_area:<0.1m2  default:3.9元/pnl (not_have pb)
            print pnl_area,price_base,'area,price_units'
            if pnl_area <0.1:
                if sn_type =='spray_Sn have pb':
                    default_min_cost=cost_base=price_min * my.qty_pnl_receive
                elif sn_type =='spray_Sn nhav pb':
                    default_min_cost=cost_base=price_min * my.qty_pnl_receive
            else:
                cost_base=pnl_area * price_base * my.qty_pnl_receive
            ##count red_tape cost: red_tape_length,red_tape_article
            print 'cost_base',cost_base
            if my.red_tape_article:
                ##红胶带费用=红胶带条数*红胶带单价
              
                red_tape_cost=red_tape_price *  my.red_tape_article
                ##cost_base add red_tape_cost
                cost_base+=red_tape_cost
                print 'red_tape_cost',red_tape_cost
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})       
        return price_base,cost_base,default_min_cost
                
    def action_fly_needle(self,cr,uid,ids,context=None):
        ##飞针费用计算:基本费+测试费(单价 * 测试点数)
        cost_base=0.0
        price_base=0.0
        sub_process_type=None
        fly_board_type=None
        
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        
        ser_domain=[('process_category','=','machine_process'),('process_type','=','flying_probe')]
        
        ##sub_process_type:'nomal_sample','double_gt_15','multilayer_gt_15','bdthick_lt_04','FPC_sample',
        ## 'length_gt_660','length_gt_900','low_resistance'
        ##count product sub_process_type:
        area_type=None
        fpc_type=None
        lower_type=None #低阻类型
        bdthick_type=None
        length_type=None
        pcb_remove_type=None
        fly_board_types=None
        if my.receive_area<1.5:
            area_type='nomal_sample'
        elif my.receive_area >=1.5 and my.partner_id.id!=5726 :
            if my.layer_count <=2:
                area_type='double_gt_15'
            elif my.layer_count >2 :
                area_type='multilayer_gt_15'
        else:
            area_type='above_15'
            
                
        if my.if_fpc_sample:
            fpc_type='FPC_sample'
        if my.if_low_resistance:
            lower_type='low_resistance'
        if my.board_thickness <=0.4:
            bdthick_type='bdthick_lt_04'
        length_list=[my.pnl_length,my.pnl_width]
        if max(length_list) >=900:
            length_type='length_gt_900'
        elif 610 <= max(length_list) <900 :
            length_type='length_gt_610'
        if my.pcb_remove:
            pcb_remove_type='pcb_remove'
            if  my.layer_count==2:
                fly_board_types='double_board'
            elif my.layer_count==4:
               fly_board_typs='four_board' 
            elif my.layer_count>=6:
                fly_board_types='six_board'
        
        if length_type:
            sub_process_type=length_type
            
        elif pcb_remove_type:
            sub_process_type=pcb_remove_type
        
        elif lower_type:
            sub_process_type=lower_type
        elif fpc_type:
            sub_process_type=fpc_type
        elif bdthick_type:
            sub_process_type=bdthick_type
        elif area_type:
            sub_process_type=area_type
        print sub_process_type,'type'
        if sub_process_type:
            ser_domain.append(('sub_process_type','=',sub_process_type))
        if fly_board_type:
            ser_domain.append(('fly_board_type','=',fly_board_types))
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
#        if len(arg_ser) >1:
#            raise osv.except_osv(('flying probe args error:'),('flying probe args search must be unique,please check!'))
        if not arg_ser:
            raise osv.except_osv(('flying probe args error:'),('flying probe args search not found,please check! %s')% (ser_domain))
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        print 'arg_rec',arg_rec
        bs_cost=arg_rec.basic_cost 
        lowest_cost=arg_rec.default_lowest_cost
        retest_free=arg_rec.if_retest_free
        price_base=arg_rec.price_units
#        fly_test_type=arg_rec.fly_test_type
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print ser_domain,bs_cost,price_base,'domain--base_cost--price_units'
        if my.board_types=='small_board':
           ts_cost=price_base * my.points_count * my.qty_receive
        elif my.board_types=='big_board':
            ts_cost=price_base * my.points_count * my.qty_pnl_receive
        print 'price_base',price_base,'points_count',my.points_count,'test_cost',ts_cost,'qty_receive',my.qty_receive,'qty_pnl_receive',my.qty_pnl_receive
        pcb_remove_cost=price_base * my.qty_receive
        print 'pcb_remove_cost',pcb_remove_cost
#        if my.if_retest and retest_free:
        if my.if_retest and retest_free :
            bs_cost=0.0
        else:
            bs_cost=bs_cost
        print bs_cost,'bs_cost'
        if my.pcb_remove:
            cost_base=pcb_remove_cost
        else:
            cost_base=bs_cost + ts_cost
        if cost_base < lowest_cost:
            cost_base=lowest_cost
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})   
        return price_base,cost_base,lowest_cost
  
    def action_shape_vcut(self,cr,uid,ids,context=None):
        ##外形VCUT费用计算
        ##如何确定板类型:用户输入
        cost_base=0.0
        price_base=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        board_thickness=my.board_thickness
        if board_thickness>2 and my.partner_id.id==5732:
             board_thickness=2
             print board_thickness,'board_thickness'
        ser_domain=[('process_category','=','machine_process'),('process_type','=','shape_VCUT')]
       
      
        bd_type=my.board_type
        
#20131209        check_args=['board_type','v_cutter_count','vcut_size']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)

        ser_domain+=[('board_type','=',bd_type),('min_board_thickness','<=',board_thickness),('max_board_thickness','>=',board_thickness)]
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
        ##search partner args in ser_domain
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if not arg_ser:
            raise osv.except_osv(('vcut probe args error:'),('vcut probe args search not found,please check! %s')% (ser_domain))
        
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        price_cutter=arg_rec.price_cutter
        lowest_cost=arg_rec.default_lowest_cost
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print ser_domain,price_base,price_cutter,'domain--price_units--price_cutter'
        
        
        
        #旭弘科科技 板厚大于2MM每增加0.2MM单价上浮10%
        if my.board_thickness>2 and my.partner_id.id==5732:
            price_add=(my.board_thickness- 2)/0.2 *0.1
            price_base+=price_add
        #  锦鹏供应商
        cost_base=0.0
        
        if my.v_cutter_count>50:
            cost_cutter=0.2 * my.v_cutter_count*my.qty_pnl_receive
        else:
            cost_cutter=price_cutter * my.v_cutter_count*my.qty_pnl_receive 
        
        print cost_cutter,'cost_cutter'
        cost_vcut=price_base * my.vcut_size*my.qty_pnl_receive
        cost_base=cost_cutter + cost_vcut
        print cost_vcut,'cost_vcut'
        if cost_base < lowest_cost:
            cost_base=lowest_cost
            print cost_base,'cost_base',
        
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,lowest_cost
    
    def action_gong_side(self,cr,uid,ids,sh_type=None,context=None):
        ##外形锣边费用计算
        ##价格的要素：槽孔数、板材、锣程、板厚、锣刀大小
        ##普通板：锣程小于1英寸的，按每条0.015元/条计算。
        ##铝基板：锣程小于1英寸的，按每条0.2元/条计算
        ##沉孔、喇叭孔：0.5元/个 （应该写明个数）
        cost_base=0.0
        price_base=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        bd_type=my.board_type
        bd_thick=my.board_thickness
        slot_hole_count=my.gong_slot_count
        gong_size=my.gong_size ##锣程
        cut_size=my.cutter_size  ##锣刀大小
        slot_price=0.0
        if bd_thick>2 and my.partner_id.id==5732:
             bd_thick=2
        ser_domain=[('process_category','=','machine_process'),
                                ]
        gong_side_cost=0.0
        vcut_cost=0.0
      
        if my.outsource_process_id.partner_id:
            ser_domain.append(('outsource_partner_id','=',my.outsource_process_id.partner_id.id))
       
#20131209        check_args=['board_type','cutter_size']
#20131209        self.check_cost_args(cr, uid, ids,check_args,context=context)
        
       
        ser_domain+=[('board_type','=',bd_type),('process_type','=','shape_gong_side'),('min_board_thickness','<=',bd_thick),
                    ('max_board_thickness','>=',bd_thick),('min_cutter_size','<=',cut_size),('max_cutter_size','>=',cut_size)]
       
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        print ser_domain,'domain'
#20131209        if len(arg_ser) >1:
#20131209            raise osv.except_osv(('shape_gong_side args count error:'),('shape_gong_side args search must be unique,please check!'))
        if not arg_ser:
            raise osv.except_osv(('shape_gong_side args error:'),('shape_gong_side args search not found,please check! %s')%(ser_domain))
    
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        ##search partner price_units ; general_board:普通板 ，aluminum_board:铝基板
        price_base=arg_rec.price_units##锣程单价
       
        glowest_cost=arg_rec.default_lowest_cost
        if_have_tax=arg_rec.if_have_tax
        slot_price=arg_rec.slot_price
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_base,glowest_cost,'price_units--lowest_cost'
#        if my.gong_slot_count :
#            if bd_type == 'general_board':
#                slot_price=0.015
#            elif bd_type == 'aluminum_board':
#                slot_price=0.2
        #旭弘科科技 板厚大于2MM每增加0.2MM单价上浮10%
        if my.board_thickness>2 and my.partner_id.id==5732:
            price_add=(my.board_thickness- 2)/0.2 *0.1
            price_base+=price_add
        ##gong_size cost:
        gong_cost=price_base * my.gong_size * my.qty_pnl_receive
        ##siot_size cost
        slot_cost=slot_price * my.gong_slot_count * my.qty_pnl_receive
        ##sink_hole and horn_hole cost:0.5 元/个
        sink_horn_cost= (my.sink_hole_count + my.horn_hole_count)  * 0.5
        ##gong_side cost
        gong_side_cost=gong_cost + sink_horn_cost + slot_cost
        print slot_cost,'slot_cost' 
        print gong_side_cost,'gong_side_cost',glowest_cost
        if gong_side_cost < glowest_cost:
            gong_side_cost=glowest_cost
        ##VCUT cost
        vcut_cost=0.0
        
        if sh_type =='shape_gong_side':
            cost_base=gong_side_cost
        elif sh_type =='VCUT+ gong_side':
            ch_args=['v_cutter_count','vcut_size']
    #20131209        self.check_cost_args(cr, uid, ids,ch_args,context=context)
            vg_ser_domain=[('board_type','=',bd_type),('min_board_thickness','<=',bd_thick),
                    ('max_board_thickness','>=',bd_thick),('process_type','=','shape_VCUT'),('outsource_partner_id','=',my.outsource_process_id.partner_id.id)]
            
            varg_ser=arg_obj.search(cr,uid,vg_ser_domain)
            print vg_ser_domain,'domain'
#20140307            if len(varg_ser) >1:
#20140307                 raise osv.except_osv(('shape_VCUT args count error:'),('shape_VCUT args search must be unique,please check!'))
            if not varg_ser:
                raise osv.except_osv(('shape_VCUT args error:'),('shape_VCUT args search not found,please check! %s')%(ser_domain))
        
            varg_rec=arg_obj.browse(cr,uid,varg_ser[0])
            ##search partner price_units ; general_board:普通板 ，aluminum_board:铝基板
            v_price_base=varg_rec.price_units##V程单价
            v_price_cutter=varg_rec.price_cutter##跳刀单价
            vlowest_cost=varg_rec.default_lowest_cost
            if_have_tax=varg_rec.if_have_tax
            tax_id=varg_rec.account_tax_id and varg_rec.account_tax_id.id 
            print v_price_base,vlowest_cost,'price_units--lowest_cost'
            if my.v_cutter_count>50 and my.partner_id.id!='5732' :
                vcut_cost=my.vcut_size * v_price_base * my.qty_pnl_receive+ 0.2 * my.v_cutter_count * my.qty_pnl_receive
            elif my.partner_id.id==5732 and my.board_thickness>2 :
                    price_add=(my.board_thickness- 2)/0.2 *0.1
                    v_price_base+=price_add
                    vcut_cost=my.vcut_size * v_price_base * my.qty_pnl_receive+ v_price_cutter * my.v_cutter_count * my.qty_pnl_receive
            else:
                vcut_cost=my.vcut_size * v_price_base * my.qty_pnl_receive+ v_price_cutter * my.v_cutter_count * my.qty_pnl_receive
            if vcut_cost <  vlowest_cost:
                vcut_cost=vlowest_cost
            cost_base=gong_side_cost + vcut_cost
        
        #self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,0       
        
      
    
    def action_laser_drill(self,cr,uid,ids,context=None):
        ##激光钻孔费用计算
        ##每款20PNL以内的，按1200元/款计算
        ##超过20PNL的，按2000元/款计算
        cost_base=0.0
        default_min_cost=0.0
        price_base=0.0
        my=self.browse(cr,uid,ids[0])
        
      #=========================================================================
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','machine_process'),('process_type','=','laser_drill'),('hole_count','=',1000)]
        
        prc_rec=my.outsource_process_id
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if my.larse_hole_dia:
            ser_domain.append(('min_larse_hole','<=',my.larse_hole_dia))
            ser_domain.append(('max_larse_hole','>=',my.larse_hole_dia))
        if my.board_material:
            ser_domain.append(('board_material','=',my.board_material))
       
        ser_domain.append(('if_have_tax','=',my.if_have_tax))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        print ser_domain,'domain'
        if len(arg_ser) >1:
            raise osv.except_osv(('laser_drill args error:'),('laser_drill args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('laser_drill args error:'),('laser_drill args search not found,please check! %s')%(ser_domain))
       
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_units=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_units,'price_units'
        cost_base=price_units * my.qty_pnl_receive
      #=========================================================================
        if my.qty_pnl_receive <= 20:
            #if cost_base <1200:
                #cost_base=1200
                cost_base=default_min_cost=1200
        else:
            #if cost_base < 2000:
                #cost_base=2000
                cost_base=default_min_cost=2000
        #self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    def action_wire_drawing(self,cr,uid,ids,context=None):
        ##表面处理：拉丝费用计算
        ##1元/平方分米

        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        wire_draw_types=my.wire_draw_types
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','machine_process'),('process_type','=','wire_drawing'),('wire_draw_type','=',wire_draw_types)]
        
        prc_rec=my.outsource_process_id
       
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if my.norms_mark:
            ser_domain.append(('norms_mark','=',my.norms_mark))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        print ser_domain,'domain'
        if len(arg_ser) >1:
            raise osv.except_osv(('wire_drawing args error:'),('wire_drawing args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('wire_drawing args error:'),('wire_drawing args search not found,please check! %s')%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_dm2
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_base,'price_units(dm2)'
       
        if my.board_types=='big_board':
            cost_base=price_base * (my.pnl_length * my.pnl_width)/10000 * my.qty_pnl_receive
            print 'cost_base',cost_base
        elif my.board_types=='small_board':
            cost_base=price_base * (my.length * my.width)/10000 * my.qty_receive
            print 'cost_base',cost_base
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    def action_bf_laminating_process(self,cr,uid,ids,context=None):
        ##表面处理：阳极氧化(层压前表面处理)费用计算
        ##3元/平方分米

        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','machine_process'),('process_type','=','bf_laminate_pre')]
        
        prc_rec=my.outsource_process_id
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if my.norms_mark:
            ser_domain.append(('norms_mark','=',my.norms_mark))
        if my.film_thickness:
            ser_domain.append(('min_film_thickness','<=',my.film_thickness))
            ser_domain.append(('max_film_thickness','>=',my.film_thickness))
        print ser_domain,'domain'
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('bf_laminating_process args error:'),('bf_laminating_process args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('bf_laminating_process args error:'),('bf_laminating_process args search not found,please check! %s')%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_dm2
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_base,'price_units(dm2)'
        if my.product_area:
            cost_base=price_base * my.product_area *100 * my.qty_pnl_receive
            
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    
    
    def action_cutting(self,cr,uid,ids,context=None):
        #切割以每PNL为单价计算价格
        #若CVL尺寸超过250mm需加价,300mm加价2.5元，350mm加5元
        #若FPC尺寸超过250mm需加价，300mm加价5元，350mm加10元
        #激光切割价格按每分钟来计算价格
        
        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        ser_domain=[('process_category','=','machine_process'),('process_type','=','cutting')]
        prc_rec=my.outsource_process_id
        cut_type=my.cut_type
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if cut_type:
            ser_domain.append(('cutting_type','=',cut_type))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('cutting args error:'),('cutting args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('cutting args error:'),('cutting args search not found,please check! %s')%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        default_min_cost=arg_rec.default_lowest_cost
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        print price_base,'price_units'
        
        if cut_type=='laser_cut':
            cost_base=price_base * my.meter *  my.qty_pnl_receive
        else:
            
            if my.pnl_length>250 and my.pnl_width>250 :
                cost_base=(my.pnl_width/250.00) * price_base * my.qty_pnl_receive + (my.pnl_length/250.00) * price_base * my.qty_pnl_receive
            elif my.pnl_length<=250 and my.pnl_width>250 :
                cost_base=(my.pnl_width/250.00) * price_base * my.qty_pnl_receive
            
            elif  my.pnl_length>250 and my.pnl_width<=250 :
                cost_base=(my.pnl_length/250.00) * price_base * my.qty_pnl_receive
            elif my.pnl_length<250 and my.pnl_width<250 :
                cost_base=price_base * my.qty_pnl_receive
                print cost_base,'cost_base'
        if cost_base<default_min_cost:
             cost_base=default_min_cost
           
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    
    
    def action_repair_gold(self,cr,uid,ids,context=None):
        #修金板计算方式总价=数量*单价
        
        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        board_type=my.board_types
        ser_domain=[('process_category','=','machine_process'),('process_type','=','repair_gold'),('board_type_new','=',board_type)]
        prc_rec=my.outsource_process_id
        repair_type=my.repair_type
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if repair_type:
            ser_domain.append(('repair_type','=',repair_type))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('repair gold args error:'),('repair gold args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('repair gold args error:'),('repair gold args search not found,please check! %s')%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        if my.board_types=='small_board':
            cost_base=my.qty_receive * price_base
        elif my.board_types=='big_board':
            cost_base=my.qty_pnl_receive * price_base
        
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    
    def action_laminate(self,cr,uid,ids,context=None):
        #层压计算价格计算板厚大于2mm每增加0-0.4加工费加收10%，单边长超过600mm时加工费加收10%单边PP片>=3张时加工费加收10%
        #铜厚为10ZS时每平米加收30，样板每款加收25；2OZ时每平米加收100，样板每款加收50；3OZ时每平米加收180，样板每款加收80
        #高TG板单价加收30%，中TG板单价加收10%
        price_base=0.0
        cost_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        board_thickness=my.laminate_board_thickness
        layer_count=my.layer_count
        
        arg_obj=self.pool.get('outsource.cost.argument')
        board_type=my.board_types
        ser_domain=[('process_category','=','laminate_process'),('process_type','=','laminate')]
        prc_rec=my.outsource_process_id
        laminate_types=my.laminate_types
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        if laminate_types:
            ser_domain.append(('laminate_type','=',laminate_types))
        if layer_count<4:
            layer_count=4
        print layer_count,'layer_count'
        if layer_count:
            ser_domain.append(('layer_count','=',layer_count))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('laminate args error:'),('laminate args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('laminate args error:'),('laminate args search not found,please check! %s' )%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        default_min_cost=arg_rec.default_lowest_cost
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        if my.laminate_types=='high_tg'  :
            board_add=price_base*0.3
            price_base+=board_add
            print board_add,'board_add'
        if my.laminate_types=='middle_tg':
            board_add=price_base*0.1
            price_base+=board_add
        if board_thickness >= 2 :
            cost_add=(board_thickness-2)/0.4 * 0.1 * price_base
            print cost_add,'board_add'
            price_base+=cost_add
        if my.pnl_length>600:
            cost_add=cost_base * 0.1
            
            price_base+=cost_add
        if my.pnl_width>600:
            cost_add=price_base * 0.1
            price_base+=cost_add
        if my.length_pp>=3:
            cost_add=price_base * 0.1
            price_base+=cost_add
            print cost_add,'PP_add'
            
            
        cu_add=0.0
        cu_val=0.0
        if my.laminate_cu_thickness:
                add_ratio=0.0            
            
             
                cu_val1=my.laminate_cu_thickness[0]
                if cu_val1=='1/2' :
                    cu_val1='0.5'
                if cu_val1=='H/H' :
                    cu_val1='0.5'
                if cu_val1=='1/3' :
                    cu_val1='0.33'
                if cu_val1=='2/3' :
                    cu_val1='0.67'
                if cu_val1=='3/2' :
                    cu_val1='1.5'
                if cu_val1=='1/1':
                    cu_val1='1'
                if cu_val1=='1.2/1.2':
                    cu_val1='1'
                if cu_val1=='2/2' :
                    cu_val1='2'
                if cu_val1=='1.5/1.5' :
                    cu_val1='1.5'
                if cu_val1=='3/3' :
                    cu_val1='3'
                if cu_val1=='4/4' :
                    cu_val1='4'
                if cu_val1=='5/5' :
                    cu_val1='5'
                if cu_val1=='6/6' :
                    cu_val1='6'
                if cu_val1=='7/7' :
                    cu_val1='7'
                if cu_val1=='8/8' :
                    cu_val1='8'  
                if cu_val1=='H':
                    cu_val1='0.5'  
                    
                cu_val=string.atof(cu_val1)  #用string.atof可以用于数字很长的转换，而int不能转换带小数的
            
                print 'cu_val:',cu_val
        area=(my.pnl_length+15) * (my.pnl_width+15)/1000000 * my.qty_pnl_receive
        print area,'area'
        if cu_val :
            if cu_val == 1.0:                    # 铜厚为1OZ
               
                    cu_add=30
                    print cu_add,'cu_add'
                    price_base+=cu_add
                
                    
            elif cu_val == 2.0 :                    # 铜厚为2OZ
                 
                    cu_add=100
                    print cu_add,'cu_add'
                    price_base+=cu_add
                
                    
            elif cu_val == 3.0 :
            
                    cu_add=180
                    print cu_add,'cu_add'
                    price_base+=cu_add
        if my.board_types=='small_board':
            cost_base=(my.length * my.width)/1000000 * my.qty_receive * price_base
        elif my.board_types=='big_board':
            cost_base=(my.pnl_length+15) * (my.pnl_width+15)/1000000 * my.qty_pnl_receive * price_base
            print price_base,cost_base,'price_base','cost_base' 
       
        if cu_val :
            if cu_val == 1.0 and cost_base < default_min_cost:  
                    cu_add=25
                    print cu_add,'cu_add'
                    cost_base+=cu_add
            elif cu_val == 2.0 and cost_base < default_min_cost:
                    cu_add=50
                    print cu_add,'cu_add'
                    cost_base+=cu_add
            elif cu_val == 3.0 and cost_base < default_min_cost:
                    cu_add=80
                    cost_base+=cu_add 
                    print cu_add,'cu_add'
            
                
        if cost_base< default_min_cost:
            cost_base=default_min_cost   
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost
    
    def action_aoi(self,cr,uid,ids,context=None):
        #AOI计算方式总价=2*单价
        
        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        board_type=my.board_types
        ser_domain=[('process_category','=','machine_process'),('process_type','=','aoi')]
        prc_rec=my.outsource_process_id
        repair_type=my.repair_type
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('aoi args error:'),('aoi args search must be unique,please check! %s')%(ser_domain))
        elif not arg_ser:
            raise osv.except_osv(('aoi args error:'),('aoi args search not found,please check! %s')%(ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        
        cost_base=my.aoi_test_count * price_base
        area=(my.pnl_length * my.pnl_width)/1000000 * my.qty_pnl_receive
        if_first_test=my.if_first_test
        print if_first_test,'if_first_test'
        
        print area,'area'
        if if_first_test:
            if area>=1.5:
                basic_cost=my.aoi_test_count * 60
                print basic_cost,'basic_cost'
                cost_base+=basic_cost
            elif area<1.5:
                if my.layer_count<4:
                    my.layer_count=4
                basic_cost=(my.layer_count -2)/2 * 50 + 50
                print basic_cost,'basic_cost'
                cost_base+=basic_cost
                print cost_base,'cost_base'
        
        
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost    
    
    
    
    def action_sliver_plating(self,cr,uid,ids,context=None):
        
        cost_base=0.0
        price_base=0.0
        default_min_cost=0.0
        my=self.browse(cr,uid,ids[0])
        arg_obj=self.pool.get('outsource.cost.argument')
        board_type=my.board_types
        nickel_thickness=my.nickel_thickness
        silver_thickness=my.silver_thickness
        tb_area=my.top_area+my.bottom_area
        ser_domain=[('process_category','=','machine_process'),('process_type','=','sliver_plating'),('nickel_thickness_min','<=',nickel_thickness),('nickel_thickness_max','>=',nickel_thickness),
                    ('min_silver_thick','<=',silver_thickness),('max_silver_thick','>=',silver_thickness),('area_min','<=',tb_area),('area_max','>=',tb_area)]
        print ser_domain,'ser_domain'
        prc_rec=my.outsource_process_id
        if prc_rec.partner_id:
            ser_domain.append(('outsource_partner_id','=',prc_rec.partner_id.id))
        arg_ser=arg_obj.search(cr,uid,ser_domain)
        if len(arg_ser) >1:
            raise osv.except_osv(('sliver plating args error:'),('sliver plating args search must be unique,please check!'))
        elif not arg_ser:
            raise osv.except_osv(('sliver plating args error:'),('sliver plating args search not found,please check! %s')% (ser_domain))
        
        arg_rec=arg_obj.browse(cr,uid,arg_ser[0])
        price_base=arg_rec.price_units
        if_have_tax=arg_rec.if_have_tax
        tax_id=arg_rec.account_tax_id and arg_rec.account_tax_id.id 
        default_lowest_cost=arg_rec.default_lowest_cost
        cost_base=(my.pnl_length * my.pnl_width)/1000000 * my.qty_pnl_receive  * price_base
        if cost_base < default_lowest_cost:
                cost_base=default_lowest_cost
                print cost_base,'cost_base'
        self.write(cr,uid,ids,{'if_have_tax':if_have_tax,'account_tax_id':tax_id})
        return price_base,cost_base,default_min_cost 
        
    
############################################################20131209        
#20131209    def check_cost_args(self,cr,uid,ids,field_list=None,context=None):
#20131209        f_list=[]
#20131209        for field in field_list:
#20131209            re_info=self.read(cr,uid,ids[0],[field])
#20131209            if not re_info[field] or re_info[field] <0:
#20131209                f_list.append(field)
#20131209        if f_list:
#20131209            temp_list=[]
#20131209            trans_obj=self.pool.get('ir.translation')
#20131209            for field_name in f_list:       
#20131209                res_name=self._name+','+field_name
#20131209                types='field'
#20131209                lang='zh_CN'
#20131209                source=self._columns[field_name].string
#20131209                trans=trans_obj. _get_source( cr, uid, res_name, types, lang, source)
#20131209                if trans:
#20131209                    temp_list.append(trans)
#20131209                else:
#20131209                    temp_list.append(field_name)
#20131209            args=';'.join(temp_list)
#20131209            raise osv.except_osv(('field info error'),('%s field info not found,please check!' % args))
#20131209        return True
################################################################20131209
    #===========================================================================
    # def  production_read(self,cr,uid,ids, context=None):
    #    my=self.browse(cr,uid,ids[0])
    #    server='192.168.10.2'
    #    user='sa'
    #    passward='719799'
    #    #database='121109'
    #    database='mtlerp-running'
    #    batch=my.production_id
    #    
    #    conn = _mssql.connect(server=server , user=user, password=passward,database=database)    
    #    #conn.execute_query('''select * from VIwip where batchcode='121025224101' '''  )        
    #    w_ser=('goodscode','goodslength','goodswidth',
    #                    'atmakepcsqtym','qtyp',batch)
    #    conn.execute_query('''select * from VIwip where billstate='30' and batchcode='%s' ''' %batch)
    #    ser_flg=abs(conn.rows_affected)
    #    if ser_flg:
    #        conn.execute_query('''select %s,%s,%s,%s,%s from VIwip where billstate='30' and batchcode='%s' ''' %w_ser )
    #    
    #        up_dic={}
    #        for row in conn:
    #            if row:
    #                up_dic['length']=row['goodslength']
    #                up_dic['width']=row['goodswidth']
    #                up_dic['product_id']=row['goodscode']
    #                up_dic['product_qty']=row['atmakepcsqtym']
    #                up_dic['qty_unit']=row['qtyp']
    #        self.write(cr,uid,ids,up_dic)
    #    else:
    #        raise osv.except_osv(('search error:'),('production_id info not found!'))
    #       
    #    return True
    #===========================================================================
    
    def action_receive_update(self,cr,uid,ids,context=None):
        receive_ser=self.search(cr,uid,[('state','=','w_receive')])
        
        return True
    
outsource_delivery_lines()

class outsource_duizhang(osv.osv):
    _name='outsource.duizhang'
    _inherit='outsource.data'
    _order='create_date desc'
    _rec_name='outsource_number'
    _duizhang_list=[(i,i) for i in ('draft','outsource_check')]
    _state_list=[(i,i) for i in ('draft','outsource_check','outsource_confirm','done')]
    _columns={
              'outsource_number':fields.char('outsource_number',size=64,required=True,select=True),       
              'duizhang_lines_ids':fields.one2many('outsource.duizhang.line','outsource_duizhang_id','outsource_duizhang_lines'),
              'period_id':fields.many2one('account.period','period_id'),
              'end_date':fields.date('end_date'),
              'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id'),
              'total_amount':fields.float('total_amount', digits_compute=dp.get_precision('Account')),
              'state':fields.selection(_state_list,'state',size=32,readonly=True),
              'partner_id'   :fields.many2one("res.partner", 'Supplier', size=16, select=True,domain=[('supplier','=',True)]),
              'address':         fields.related('partner_id','address',type='one2many',relation='res.partner.address',string='address',readonly=True),
              'street':    fields.related('partner_id','street',type='char',relation='res.partner.address',string='street',readonly=True),
              'contact_name':    fields.related('partner_id','name',type='char',relation='res.partner.address',string='contact_name',readonly=True),
              'phone':fields.related('partner_id','phone',type='char',relation='res.partner.address',string='phone',readonly=True),
              'fax':fields.related('partner_id','fax',type='char',relation='res.partner.address',string='fax',readonly=True),
              'duizhang_lines_partner_ids':fields.one2many('outsource.partner.line','duizhang_partner_id','duizhang_partner_lines'),
              'duizhang_file':fields.binary('duizhang_file'),
              'file_name':fields.char('file_name',size=32),
              'duizhang_type':fields.selection(_duizhang_list,'duizhang_type',),
              'outsource_duizhangs_lines_ids':fields.many2many('outsource.delivery.lines','duizhangs_lines_ids','duizhang_id','outsource_number','outsource_duizhangs_lines_ids'),
              'outsource_type':fields.many2one('select.selection','outsource_type'),#外协工艺类型
              'type':fields.related('outsource_type','type',type='char',relation='select.selection',string='type'),#工艺类型
              'outsource_label':fields.related('outsource_type','label',type='char',relation='select.selection',string='outsource_label'),#工艺类型
              'start_time':fields.datetime('start_time'),#开始日期
              'end_time':fields.datetime('end_time'),#结束日期
              'create_dates':fields.date('create_dates',readonly=True),#创建时间
              
                        }
    _defaults={
               'state':lambda *a:'draft',
                'applicant_id':lambda self,cr,uid,context:uid,
                'outsource_number':lambda self,cr,uid,context:self.pool.get('ir.sequence').get(cr,uid,'outsource.duizhang'),
                'create_dates':lambda *a:time.strftime('%Y-%m-%d'),
               }
    
    def updata_state(self, cr, uid, ids, state=None, state_filter=None, **args):
        org_state=self.browse(cr,uid,ids[0]).state
        rec=self.write(cr, uid, ids, {'state':state})
        return True
    
    
    def update_if_fault(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        type=my.outsource_type.id
        print type,'type'
        start_time=my.start_time
        end_time=my.end_time
        partner_id=my.partner_id.id
        connection=psycopg2.connect(database="test", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
        cursor=connection.cursor()
        cursor.execute('''update outsource_delivery_lines set if_fault='f' where create_date>='%s' and create_date<'%s' and outsource_process_id in(select id from outsource_process where process_type=%s and partner_id='%s') and state='done' '''%(start_time,end_time,type,partner_id))
        connection.commit()#获取信息
        cursor.close() #关闭游标
        connection.close()
        return True
    
    
    
    def create_lines(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        period_obj=self.pool.get('account.period')
        line_obj=self.pool.get('outsource.delivery.lines')
        partner_id=my.partner_id.id
        start_time=my.start_time
        end_time=my.end_time
        type=my.type
        domain=[('state','=','done'),('partner_id','=',partner_id),('if_fault','=',False),('process_type','=',type)]
#        domain=[('state','=','w_receive'),('partner_id','=',partner_id),('if_fault','=',False)]
        domain_date=[]
        if my.start_time and my.end_time:
            domain_date=[('create_date','>=',start_time),('create_date','<=',end_time)]
        elif my.start_time and not my.end_time:
            domain_date=[('create_date','>=',start_time)]
        elif my.end_time and not my.start_time:
            domain_date=[('create_date','<=',end_time)]
        cre_domain=domain + domain_date
        duizhang_line_id=line_obj.search(cr,uid,cre_domain)
   
        lines_data=[(2,l.id) for l in my.duizhang_lines_ids]
       
        for duizhangs_lines_id in duizhang_line_id:
                duizhang_line=line_obj.browse(cr,uid,duizhangs_lines_id)
                lines_data.append([0,0,{
                                        'duizhangs_lines_id':duizhang_line.id,
                                        'qty_receive':duizhang_line.qty_receive,
                                        'qty_pnl_receive':duizhang_line.qty_pnl_receive,
                                       
                                        }])
                print 'lines_data',lines_data
        self.write(cr,uid,my.id,{'duizhang_lines_ids':lines_data,})
        return True
    
    
    
    def open_duizhang_liness(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        (username,pwd,dbname) =('admin', 'Admin23', 'test')     #用户名、密码、数据库
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')  #建立连接目标机器
        uid = sock_common.login(dbname, username, pwd)                             #登入数据库并返回用户ID
        sock= xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/object')  #建立连接目标机器

      
        book=xlrd.open_workbook("f:/openerp/mm.xls")                                  
        sheet=book.sheets()[0]                                               
        ncols=sheet.ncols                                                     
        nrows=sheet.nrows                                                     
        print nrows,ncols
#        obj = self.pool.get('outsource.duizhang')
 #       outsource_number=obj.name_get(cr, uid, ids ) #name_get得出的字段值和id       
#        outsources=outsource_number[0]  #取出id
        outsources=my.id
        print outsources,'id'
        for line_number in range(1,nrows):                                    
            row=sheet.row(line_number)
            lis=[cell.value for cell in row]                                  
            (oursource_numbers,product_ids,qty,price,amount,pnl_length,pnl_width,return_numbers,send_date,total_area,finger_count,pnl_units_count)=lis[0:12]
  
    

#            if (outsources):  
        
            info_id=sock.execute(dbname, uid, pwd,  'outsource.partner.line', 'create', {
#                    'duizhang_partner_id':outsources[0],
                    'outsource_numbers':oursource_numbers,
                    'product_ids':product_ids,
                    'qty':qty,
                    'price':price,
                    'amount':amount,
                    'return_numbers':return_numbers,
                    'pnl_length':pnl_length,
                    'pnl_width':pnl_width,
                    'send_date':send_date,
                    'total_area':total_area,
                    'finger_count':finger_count,
                    'pnl_units_count':pnl_units_count,

                    })
            
            print product_ids,qty,price,amount
        return True
       
    
    def open_duizhang_lines(self,cr,uid,ids,context):
        
        my=self.browse(cr,uid,ids[0])
        (username,pwd,dbname) =('admin', 'admin', 'new')     #用户名、密码、数据库
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')  #建立连接目标机器
        uid = sock_common.login(dbname, username, pwd)                             #登入数据库并返回用户ID
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')        #远程调用服务端的对象

        file=open("f:/openerp/mm.txt","w")                                             #打开文件
        book=xlrd.open_workbook("f:/openerp/mm.xls")                                  #打开要导入的电子表格
        sheet=book.sheets()[0]                                                #导入工作表1
        ncols=sheet.ncols                                                     #取表的总列数
        nrows=sheet.nrows                                                     #取表的总行数
        outsources=my.id
        print nrows,ncols

        for line_number in range(1,nrows):                                    #循环读取每行的数据
            row=sheet.row(line_number)                                        #取当前行的数据
            lis=[cell.value for cell in row]                                  #取每行单元格数据，并用列表保存
            (outsource_numbers,product_ids,qty,price,amount,pnl_length,pnl_width,return_numbers,send_date,total_area,finger_count,pnl_units_count)=lis[0:12]
  

            info_id=sock.execute(dbname, uid, pwd,  'outsource.partner.line', 'create', {
            'duizhang_partner_id':outsources,
            'outsource_numbers':outsource_numbers,
            'product_ids':product_ids,
            'qty':qty,
            'price':price,
            'amount':amount,
            'return_numbers':return_numbers,
            'pnl_length':pnl_length,
            'pnl_width':pnl_width,
            'send_date':send_date,
            'total_area':total_area,
            'finger_count':finger_count,
            'pnl_units_count':pnl_units_count,
            })
                    
        return True

    
    
    
    
    
    def check_duizhang_lines(self,cr,uid,ids,context=None):
        return True
    
    def check_data(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        line_obj=self.pool.get('outsource.delivery.lines')
        partner_id=my.partner_id.id
        start_time=my.start_time
        end_time=my.end_time
        type=my.type
        domain=[('state','=','done'),('partner_id','=',partner_id),('process_type','=',type)]
        duizhang_line_id=line_obj.search(cr,uid,domain)
        delivery_lines=line_obj.browse(cr,uid,duizhang_line_id[0])
        create_date=delivery_lines.create_date
        connection=psycopg2.connect(database="test", user="postgres", password="xt456@", host="127.0.0.1", port="5432")
        cursor=connection.cursor()
#        cursor.execute(''' update outsource_delivery_lines set if_fault='True' where id in(select a.id from (select a.id,a.production_id,a.product_id,a.pcs_price_units,a.pnl_price_units,a.qty_receive,a.qty_pnl_receive,a.cost_total,b.outsource_number,b.return_number from outsource_delivery_lines a left join outsource_process b on a.outsource_process_id=b.id)a,(select  production_process_id,product_ids,price,sum(qty) as qty,sum(amount)as amount,outsource_numbers,return_numbers from outsource_partner_line group by production_process_id,product_ids,price,outsource_numbers,return_numbers)b where a.product_id=b.product_ids and (a.pcs_price_units=b.price or a.pnl_price_units=b.price) and (a.qty_receive=b.qty or a.qty_pnl_receive=b.qty) and a.cost_total=b.amount and a.outsource_number=b.outsource_numbers and a.return_number=b.return_numbers)and if_fault<>'True' and if_have_duizhang<>'True'  ''')
#        cursor.execute(''' update outsource_partner_line set if_faults='True' where id in(select b.id from (select a.production_id,a.product_id,a.pcs_price_units,a.pnl_price_units,a.qty_receive,a.qty_pnl_receive,a.cost_total,b.outsource_number,b.return_number,a.if_fault from outsource_delivery_lines a left join outsource_process b on a.outsource_process_id=b.id)a,outsource_partner_line b where a.product_id=b.product_ids and (a.pcs_price_units=b.price or a.pnl_price_units=b.price) and a.outsource_number=b.outsource_numbers and a.return_number=b.return_numbers and a.if_fault='True' and b.if_faults<>'True')''')
        cursor.execute(''' update outsource_delivery_lines set if_fault='True' where id in(select a.id from (select a.id,a.production_id,a.product_id,a.pcs_price_units,a.pnl_price_units,a.qty_receive,a.qty_pnl_receive,a.cost_total,b.outsource_number,b.return_number from outsource_delivery_lines a left join outsource_process b on a.outsource_process_id=b.id)a,(select  production_process_id,product_ids,price,sum(qty) as qty,sum(amount)as amount,outsource_numbers,return_numbers from outsource_partner_line group by production_process_id,product_ids,price,outsource_numbers,return_numbers)b where a.product_id=b.product_ids and (a.qty_receive=b.qty or a.qty_pnl_receive=b.qty) and cast(a.cost_total as decimal(18,1)) =cast(b.amount as decimal(18,1)) and a.outsource_number=b.outsource_numbers)and if_fault<>'True' and if_have_duizhang<>'True' and create_date>='%s' and create_date<='%s' ''' % (start_time,end_time) )
        cursor.execute(''' update outsource_partner_line set if_faults='True' where id in(select b.id from (select a.production_id,a.product_id,a.pcs_price_units,a.pnl_price_units,a.qty_receive,a.qty_pnl_receive,a.cost_total,b.outsource_number,b.return_number,a.if_fault from outsource_delivery_lines a left join outsource_process b on a.outsource_process_id=b.id)a,outsource_partner_line b where a.product_id=b.product_ids and a.outsource_number=b.outsource_numbers and a.if_fault='True' and b.if_faults<>'True')''')
        connection.commit()#获取信息
        cursor.close() #关闭游标
        connection.close()
        
        return True
    
    
    
    
outsource_duizhang()

class outsource_duizhang_line(osv.osv):
    _name='outsource.duizhang.line'
    _inherit='outsource.data'
    _columns={
              
              'duizhangs_lines_id':fields.many2one('outsource.delivery.lines','duizhangs_lines_id',domain=[('state','=','done')]),
              'outsource_duizhang_id':fields.many2one('outsource.duizhang','outsource_duizhang_id'),
              
#              'process_lines_id':fields.many2one('outsource.process.lines','process_lines_id'),
              'outsource_apply_id':fields.related('duizhangs_lines_id','outsource_apply_id',type='many2one',relation='outsource.apply',string='outsource_apply_id',),
              'outsource_number':fields.related('outsource_apply_id','outsource_number',type='char',string='outsource_number',readonly=True),#外协申请单据编号
              'amount':fields.related('duizhangs_lines_id','cost_total',type='float',string='amount'),
              'if_have_duizhang':fields.boolean('if_have_duizang'),
              #'duizhang_amount':fields.float('duizhang_amount', digits_compute=dp.get_precision('Account'),),
              'duizhang_time':fields.datetime('duizhang_time'),
              'if_have_payment':fields.boolean('if_have_payment'),
              #'payment_amount':fields.float('payment_amount', digits_compute=dp.get_precision('Account'),),
              'payment_time':fields.datetime('payment_time'),
              
              'product_id':fields.related('duizhangs_lines_id','product_id',type='char',string='product_id',select=True),
              'product_unit':fields.char('product_unit',size=32),
              'product_qty':fields.related('duizhangs_lines_id','product_qty',type='integer',string='product_qty',select=True),
              'pnl_qty':fields.related('duizhangs_lines_id','qty_pnl',type='integer',string='pnl_qty',select=True),
              'pnl_width':fields.related('duizhangs_lines_id','pnl_width',type='float',string='pnl_width',select=True),
              'pnl_length':fields.related('duizhangs_lines_id','pnl_length',type='float',string='pnl_length',select=True),
              'pcs_width':fields.related('duizhangs_lines_id','width',type='float',string='pcs_width',select=True),
              'pcs_length':fields.related('duizhangs_lines_id','length',type='float',string='pcs_length',select=True),
              'pcs_price_units':fields.related('duizhangs_lines_id','pcs_price_units',type='float',string='pcs_price_units',select=True),
              'pnl_price_units':fields.related('duizhangs_lines_id','pnl_price_units',type='float',string='pnl_price_units',select=True),
              'return_number':fields.related('duizhangs_lines_id','return_numbers',type='char',string='return_number'),       
              'if_fault':fields.related('duizhangs_lines_id','if_fault',type='boolean',string='if_fault'),##是否有错误
              'outsource_number':fields.related('duizhangs_lines_id','outsource_number',type='char',string='outsource_number'),#外协单号
                        }
    _defaults={
               
               'applicant_id':lambda self,cr,uid,context:uid,
               }

outsource_duizhang_line()




class outsource_partner_line(osv.osv):  #外协商对账单明细
    _name="outsource.partner.line"
    _inherit="outsource.data"
    _order='send_date desc'

    _columns={
              'duizhang_partner_id':fields.many2one('outsource.duizhang','outsource_partner_id',ondelete='cascade'),
              'process_lines_ids':fields.many2one('outsource.duizhang','process_lines_ids',domain=[('state','=','draft')],select=True,ondelete='cascade'),
              'outsource_number':fields.related('duizhang_partner_id','outsource_number',type='char',string='outsource_number',select=True),#对账单号
              'product_ids':fields.char('product_ids',size=32),#档案号
              'amount':fields.float('amount', digits_compute=dp.get_precision('Account')),#金额
              'if_have_duizhangs':fields.boolean('if_have_duizangs'),#是否已经对账
              'notes':fields.char('notes',size=32),#备注
              'duizhang_times':fields.related('duizhang_partner_id','create_date',type='date',string='duizhang_times'),#对账时间
              'qty':fields.integer('qty'),#pcs数量
              'production_process_id':fields.char('production_process_id',size=32),#生产批次号
              'layercount':fields.integer('layercount'),#层数
              'price':fields.float('price',digits=(4,4),),#PCS单价
              'outsource_numbers':fields.char('outsource_numbers',size=32,select=True),#加工单号
              'return_numbers':fields.char('return_numbers',size=32),#返回单号
              'send_date':fields.char('send_date',size=32),#发货日期
              'memo':fields.text('memo'),#备注
              'if_faults':fields.boolean('if_faults',default=False),#  对账是否一致
              'pcs_length':fields.float('pcs_length',digits_compute=dp.get_precision('Account'),),#PCS长(mm)
              'pcs_width':fields.float('pcs_width',digits_compute=dp.get_precision('Account'),),#PCS宽(mm)
              'pnl_length':fields.float('pnl_length',digits_compute=dp.get_precision('Account'),),#PNL长(mm)
              'pnl_width':fields.float('pnl_width',digits_compute=dp.get_precision('Account'),),#PNL宽(mm)
              'total_area':fields.float('total_area'),#  面积
              'finger_count':fields.integer('finger_count'),#金手指数量
              'pnl_units_count':fields.integer('pnl_units_count'),#排版数
              'outsource_type':fields.related('duizhang_partner_id','outsource_label',type='char',relation='select.selection',string='outsource_type'),# 工艺类型
         
                }



    def open_duizhang_lines(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        (username,pwd,dbname) =('admin', 'admin', 'new')     #用户名、密码、数据库
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')  #建立连接目标机器
        uid = sock_common.login(dbname, username, pwd)                             #登入数据库并返回用户ID
        sock= xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/object')  #建立连接目标机器     
        book=xlrd.open_workbook("f:/openerp/mm.xls")                                  
        sheet=book.sheets()[0]                                               
        ncols=sheet.ncols                                                     
        nrows=sheet.nrows                                                     
        print nrows,ncols
        outsources=my.id
        print outsources,'id'
        for line_number in range(1,nrows):                                    
            row=sheet.row(line_number)
            lis=[cell.value for cell in row]   
            (outsource_numbers)=lis[0:1]                               
            info_id=sock.execute(dbname, uid, pwd,  'outsource.partner.line', 'create', {

            'outsource_numbers':outsource_numbers, })
            
          
#        return True
    def button_approve(self,cr,uid,ids,context):
        (username,pwd,dbname) =('admin', 'admin', 'new')     #用户名、密码、数据库
        sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')  #建立连接目标机器
        uid = sock_common.login(dbname, username, pwd)                             #登入数据库并返回用户ID
        sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')        #远程调用服务端的对象

        file=open("f:/openerp/mm.txt","w")                                             #打开文件
        book=xlrd.open_workbook("f:/openerp/mm.xls")                                  #打开要导入的电子表格
        sheet=book.sheets()[0]                                                #导入工作表1
        ncols=sheet.ncols                                                     #取表的总列数
        nrows=sheet.nrows                                                     #取表的总行数

        print nrows,ncols

        for line_number in range(1,nrows):                                    #循环读取每行的数据
            row=sheet.row(line_number)                                        #取当前行的数据
            lis=[cell.value for cell in row]                                  #取每行单元格数据，并用列表保存
            (outsource_numbers,product_ids,qty,price,amount,pnl_length,pnl_width,return_numbers,send_date,total_area,finger_count,pnl_units_count)=lis[0:12]
  

            info_id=sock.execute(dbname, uid, pwd,  'outsource.partner.lines', 'create', {

            'outsource_numbers':outsource_numbers,
            'product_ids':product_ids,
            'qty':qty,
            'price':price,
            'amount':amount,
            'return_numbers':return_numbers,
            'pnl_length':pnl_length,
            'pnl_width':pnl_width,
            'send_date':send_date,
            'total_area':total_area,
            'finger_count':finger_count,
            'pnl_units_count':pnl_units_count,
            })
                    
              



outsource_partner_line()



              