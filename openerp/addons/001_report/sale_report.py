#!/user/bin/env python
# -*- encoding: utf-8 -*-
import time,datetime,string
from openerp.report import report_sxw
from osv import osv,orm
import tools
import netsvc
from tools.translate import _

phone={
       'sz':'0755-86630013',
       'bj':'010-84851488/84850949',
       'cs':'0731-82786288-8060',
       'cs-cs':'0731-82786288-8058',
       'cd':'0731-82786288-8046',
       'fz':'0755-86630013',
       'hz':'021-64839025-801/13530649092',
       'nj':'021-64839025-801',
       'sh':'021-64839025-801',
       'wh':'0731-82786288-8046',
       'xa':'029-89195831-8000',
       }

fax={
       'sz':'0755-86029860',
       'bj':'010-84851488',
       'cs':'0731-88422887',
       'cs-cs':'0731-88422887',
       'cd':'0731-88422887',
       'fz':'0755-86029860',
       'hz':'021-64839025转818',
       'nj':'021-64839025转818',
       'sh':'021-64839025转818',
       'wh':'0731-88422887',
       'xa':'029-89195831-8010',
       }

username={
       'sz':u'工行福永支行',
       'bj':u'工行福永支行',
       'cs':u'工行福永支行',
       'cs-cs':u'长沙交行星沙支行',
       'cd':u'工行福永支行',
       'fz':u'工行福永支行',
       'hz':u'工行福永支行',
       'nj':u'工行福永支行',
       'sh':u'工行福永支行',
       'wh':u'工行福永支行',
       'xa':u'工行福永支行',
          }

usercode={
       'sz':'4000022709200289677',
       'bj':'4000022709200289677',
       'cs':'4000022709200289677',
       'cs-cs':'431655000018010025019',
       'cd':'4000022709200289677',
       'fz':'4000022709200289677',
       'hz':'4000022709200289677',
       'nj':'4000022709200289677',
       'sh':'4000022709200289677',
       'wh':'4000022709200289677',
       'xa':'4000022709200289677',
          }

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
##---------用户单-------------
class pcb_info_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(pcb_info_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':self.board_info,
            'route':self.route,
            'special':self.special,
            'test':self.test,
            'accept':self.accept,
            'mark':self.mark,
            'request_with':self.request_with,
            'packing':self.packing,
            'mix_press':self.mix_press,
            'buried_blind_via':self.buried_blind_via,
            'contract_code':self.contract_code,
            })

        def board_info(self,line=None):
            info_board_info=''
            for re in line.board_material:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info_board_info=info_board_info+re+signal
            return info_board_info
        
        def special(self,line):
            info=''
            for re in line.special_process:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info=info+re+signal
            return info
        
        def route(self,line):
            info=''
            for re in line.route_type:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info=info+re+signal
            return info
        
        def test(self,line):
            info=''
            for re in line.test_type:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info=info+re+signal
            return info 
        
        def accept(self,line):
            info_accept=''
            for re in line.accept_standard:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info_accept=info_accept+re+signal
            return info_accept 
        
        def mark(self,line):
            info=''
            for re in line.mark_request:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info=info+re+signal
            return info 
        
        def request_with(self,line):
            info=''
            for re in line.request_with_goods:
                signal=';'
                if re==False:
                    re=''
                info=info+re+signal
            return info 
        
        def packing(self,line):
            info=''
            for re in line.packing_type:
                signal=';'
                if re==False:
                    re=''
                    signal=''
                info=info+re+signal
            return info 
        
        def mix_press(self,line):
            if u'混压' in line.special_process:
                info='■'
            else:
                info='□'
            return info     
        
        def buried_blind_via(self,cr,uid,id):
            info=''
            blind_obj=self.pool.get('blind.buried.via')
            blind_ids=blind_obj.search(cr,uid,[('pcb_info_id','=',id)])
            if blind_ids:
                
                for blind_id in blind_ids:
                    blind_info=blind_obj.browse(cr,uid,blind_id)
                    info=str(blind_info.start)+'-'+str(blind_info.end)+'盲;'
                info=u'盲埋孔层描述:'+info
            return info
            
        def contract_code(self,cr,uid,id):  
           info=''
           sale_order_line_obj=self.pool.get('sale.order.new.line')
           sale_order_obj=self.pool.get('sale.order.new.line')
           sale_order_line_ids=sale_order_line_obj.search(cr,uid,[('pcb_info_id','=',id)])
           if sale_order_line_ids:
               sale_order_line_info=sale_order_line_obj.browse(cr,uid,sale_order_line_ids[0])
               print sale_order_line_info.sale_order_new_id.name,'info.sale_order_new_id.name'
               info=sale_order_line_info.sale_order_new_id.name
           return info
pcb_info=report_sxw.report_sxw('report.pcb_info_report',
        'pcb.info',
        '/addons/001_report/report/pcb_info_report.odt',
        parser=pcb_info_report)   


#-------------报价单------------------
class price_sheet_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(price_sheet_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'tolerance':self.tolerance,
            })
            
        def tolerance(self,value):
           tolerance_info=''
           if value:
               if value.finish_tol_upper==value.finish_tol_lower:
                   tolerance_info='±'+str(value.finish_tol_upper)
               else:
                   tolerance_info='+'+str(value.finish_tol_upper)+'/-'+str(value.finish_tol_lower)
           return tolerance_info
report_sxw.report_sxw('report.price_sheet_report',
        'price.sheet',
        '/addons/001_report/report/price_sheet_report.odt',
        parser=price_sheet_report)

#-----------------销售订单---------------
      
class sale_order_new_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
       
       
        
report_sxw.report_sxw('report.sale_order_new_report',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report.odt',
        parser=sale_order_new_report)

#-----------------长沙销售订单---------------
      
class sale_order_new_report_cs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_cs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone['cs-cs']
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax['cs-cs']
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username['cs-cs']
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode['cs-cs']
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_cs',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_cs.odt',
        parser=sale_order_new_report_cs)


 #-----------------101客户销售订单---------------
      
class sale_order_new_report_101(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_101,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
               
report_sxw.report_sxw('report.sale_order_new_report_101',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_101.odt',
        parser=sale_order_new_report_101)

 
#-----------------1349客户销售订单---------------
      
class sale_order_new_report_1349(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_1349,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_1349',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_1349.odt',
        parser=sale_order_new_report_1349)

#-----------------867客户销售订单---------------
      
class sale_order_new_report_867(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_867,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_867',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_867.odt',
        parser=sale_order_new_report_867)


#-----------------2219客户销售订单---------------
      
class sale_order_new_report_2219(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_2219,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone['cs-cs']
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax['cs-cs']
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username['cs-cs']
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode['cs-cs']
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_2219',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_2219.odt',
        parser=sale_order_new_report_2219)


#-----------------1675客户销售订单---------------
      
class sale_order_new_report_1675(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_1675,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_1675',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_1675.odt',
        parser=sale_order_new_report_1675)

#-----------------销售订单---------------
      
class sale_order_new_report_scrap(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_scrap,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone[value]
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax[value]
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username[value]
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode[value]
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
       
       
        
report_sxw.report_sxw('report.sale_order_new_report_scrap',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_scrap.odt',
        parser=sale_order_new_report_scrap)

#-----------------长沙销售订单---------------
      
class sale_order_new_report_cs_scrap(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_new_report_cs_scrap,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'board_info':pcb_info.parser(cr,uid,name,context).localcontext['board_info'],
            'special':pcb_info.parser(cr,uid,name,context).localcontext['special'],
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'accept':pcb_info.parser(cr,uid,name,context).localcontext['accept'],
            'packing':pcb_info.parser(cr,uid,name,context).localcontext['packing'],
            'mark':pcb_info.parser(cr,uid,name,context).localcontext['mark'],
            'int_convent_str':self.int_convent_str,
            'sale_type':self.sale_type,
            'order_date':self.order_date,
            'phone':self.phone,
            'fax':self.fax,
            'username':self.username,
            'usercode':self.usercode,
            'sign_addr':self.sign_addr,
            
            })
#------------------转换成金额大写函数----------------
        def int_convent_str(self,value):
                value="%.2f" % value
                info_text=''
                count=0
                info1,info2=str(value).split('.')
                info=info1+info2
                lf=len(info)
                info_rev=list(info)
                info_rev.reverse()
             
                upper_list=['零','壹','贰','叁','肆','伍','陆','柒','捌','玖']
                upper_int= [str(i) for i in range(0,10)]
                uom_list=['万亿','仟','佰','拾','亿','仟','佰','拾','万','仟','佰','拾','元','角','分']
               
                for val in info:
                    if val=='0':
                        if lf in [1,2]:
                            info_a=upper_list[upper_int.index(val)]+uom_list[-lf]
                            info_text+=info_a 
                        elif lf in [3,7,11,15]:
                            info_b=uom_list[-lf]
                            info_text+=info_b 
                        else:
                            if lf not in [4,8,]:
                                if count==0 or (count - lf) > 1:
                                    info_e=upper_list[upper_int.index(val)]
                                    count=lf      
                                    info_text+=info_e
                                elif count - lf==1:
                                    count=lf   
                    else:
                        info_f=upper_list[upper_int.index(val)]+uom_list[-lf]
                        info_text+=info_f
                    lf-=1
                 
                return info_text
       #--------接单类型-----------------
        def sale_type(self,value):
              info=''
              if value=='new':
                  info=u'新单'
              if value=='repeat':
                  info=u'复投无更改'
              if value=='revise':
                  info=u'复投有更改'
              return info     
            
    #------订单日期------------------
        def order_date(self,value): 
            if value:
                value=datetime.datetime.strptime(value,'%Y-%m-%d %H:%M:%S')
                year=str(value.year)
                if len(str(value.month))<2:
                    month='0'+str(value.month)
                else:
                    month=str(value.month)
                if len(str(value.day))<2:
                    day='0'+str(value.day)
                else:
                    day=str(value.day)
                order_date_info=year+u'年'+month+u'月'+day+u'日'
                
            return order_date_info
     
        def phone(self,value):
          info_phone=''
          if value:
             info_phone=phone['cs-cs']
          return info_phone
      
        def fax(self,value):
            info_fax=''
            if value:
                info_fax=fax['cs-cs']
            return info_fax
        def username(self,value):
            info_username=''
            if value:
                info_username=username['cs-cs']
            return info_username
        
        def usercode(self,value):
            info_usercode=''
            if value:
                info_usercode=usercode['cs-cs']
            return info_usercode
        
        def sign_addr(self,value):
            sign_addr_info=''
            if value:
                sign_addr_info=sign_addr[value]
            return sign_addr_info
        
report_sxw.report_sxw('report.sale_order_new_report_cs_scrap',
        'sale.order.new',
        '/addons/001_report/report/sale_order_new_report_cs_scrap.odt',
        parser=sale_order_new_report_cs_scrap)


#-------------非常规报表------------------

class unconventional_review_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(unconventional_review_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'is_sure':self.is_sure,
            'next_dpt':self.next_dpt,
            'ex_pr':self.ex_pr,
            'des_app_time':self.des_app_time
            })
#--------是否能做----------------------
        def is_sure(self,cr,uid,id,value):
            sure_info='□'+u'能'+' □'+u'否'
            department_obj=self.pool.get('res.department')
            line_object=self.pool.get('unconventional.review.line')
            department_ids=department_obj.search(cr,uid,[('name','=',value)])
            line_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0]),('state','=','done')])
            if line_ids:
                    line_dept_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0]),('ok_final_affirm','=',True)])
                    if line_dept_ids:
                        sure_info='■'+u'能'+' □'+u'否'
                    else:
                        sure_info='□'+u'能'+' ■'+u'否'
            else:
                sure_info='□'+u'能'+' □'+u'否'
            return sure_info
#--------是否需要下一个部门评审----------------------           
        def next_dpt(self,cr,uid,id,value):
           next='□'+u'是______'
           department_obj=self.pool.get('res.department')
           line_object=self.pool.get('unconventional.review.line')
           department_ids=department_obj.search(cr,uid,[('name','=',value)])
           line_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0])]) 
           if line_ids:
                line_id=line_ids[0]
                max_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id)])
                max_id=max(max_ids)
                
                if max_id!=line_id:
                    next_id=min(line_object.search(cr,uid,[('unconventional_review_id','=',id),('id','>',line_id)]))
                    
                    next_info=line_object.browse(cr,uid,next_id)
                    
                    department_info=department_obj.browse(cr,uid,next_info.department_id.id)
                   
                    next='■'+u'是       '+department_info.name
                else:
                    next='□'+u'是______'
           return next 
            
#-------------仅限样品加工 or 研发立项-------------
        def ex_pr(self,cr,uid,id,value):
           ex_pr_info='□'+u'是______'
           department_obj=self.pool.get('res.department')
           line_object=self.pool.get('unconventional.review.line')
           department_ids=department_obj.search(cr,uid,[('name','=',value)])
           line_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0])])
           if line_ids:
                if value==u'工程部':
                    line_dept_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0]),('is_limit_example','=',True)])
                    
                    if line_dept_ids:
                        ex_pr_info='■'+u'是______'
                    else:
                        ex_pr_info='□'+u'是______'
                if value==u'工艺部':
                    line_dept_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0]),('ok_create_project','=',True)])
                    if line_dept_ids:
                        ex_pr_info='■'+u'是______'
                    else:
                        ex_pr_info='□'+u'是______' 
           return ex_pr_info
#------对应部门意见、评审人、评审时间-------------
        def des_app_time(self,cr,uid,id,value,var):
            des_app_time_info=''
            department_obj=self.pool.get('res.department')
            line_object=self.pool.get('unconventional.review.line')
            department_ids=department_obj.search(cr,uid,[('name','=',value)])
            line_ids=line_object.search(cr,uid,[('unconventional_review_id','=',id),('department_id','=',department_ids[0])])
            if line_ids:
                line_info=line_object.browse(cr,uid,line_ids[0])  
                if var=='des':
                    des_app_time_info=line_info.review_note
                if var=='app':
                    des_app_time_info=line_info.review_users_id.name
                if var=='time':
                    des_app_time_info=line_info.review_date
            return des_app_time_info    
        
                                            
report_sxw.report_sxw('report.unconventional_review_report',
        'unconventional.review',
        '/addons/001_report/report/unconventional_review_report.odt',
        parser=unconventional_review_report) 


#-------------合同投产通知单------------------
class mrp_production_new_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(mrp_production_new_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'test':pcb_info.parser(cr,uid,name,context).localcontext['test'],
            'type':self.type,
            'delivery_type':self.delivery_type,
            'qty':self.qty,
            })
        
        def type(self,value,number):
              info='□'
              if value:
                  if value=='new' and number==1 :
                      info='■'
                  if value=='repeat' and number==2:
                      info='■'
                  if value=='revise' and number==3:
                      info='■'
              return info    
        def delivery_type(self,value,number):
                info='□'
                if value:
                    if value==1 and number==1:
                        info='■'
                    if value>1 and number==2:
                        info='■'
                return info    
        def qty(self,cr,uid,pcb_info_id,qty,number):
           info=''
           if pcb_info_id.delivery_type:
               if pcb_info_id.delivery_type==1 and number=='s':
                   info=str(qty)+'PCS'
               if pcb_info_id.delivery_type!=1 and number=='m': 
                   info=str(qty)+'PCS X '+str(pcb_info_id.delivery_type)+'Unit'
           return info
               
           
            
report_sxw.report_sxw('report.mrp_production_new_report',
        'mrp.production.new',
        '/addons/001_report/report/mrp_production_new_report.odt',
        parser=mrp_production_new_report)  


#-------------合同更改通知单------------------
class sale_order_change_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(sale_order_change_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
            'is_sure':self.is_sure,
            'des_app_time':self.des_app_time,
            's':self.s,
            'p':self.p
            })
#------对应部门意见、评审人、评审时间-------------
        def des_app_time(self,cr,uid,id,value,var):
            des_app_time_info=''
            department_obj=self.pool.get('res.department')
            line_object=self.pool.get('so.change.records')
            department_ids=department_obj.search(cr,uid,[('name','=',value)])
            line_ids=line_object.search(cr,uid,[('sale_order_change_id','=',id),('dpt_id','=',department_ids[0])])
            if line_ids:
                line_info=line_object.browse(cr,uid,line_ids[0])  
                if var=='des':
                    des_app_time_info=line_info.note
                if var=='app':
                    des_app_time_info=line_info.responsible_name.name
                if var=='time':
                    des_app_time_info=line_info.finish_date
            return des_app_time_info    

#--------是否能做----------------------
        def is_sure(self,cr,uid,id,value):
            sure_info='□'+u'能'+' □'+u'否'
            department_obj=self.pool.get('res.department')
            line_object=self.pool.get('so.change.records')
            department_ids=department_obj.search(cr,uid,[('name','=',value)])
            line_ids=line_object.search(cr,uid,[('sale_order_change_id','=',id),('dpt_id','=',department_ids[0]),('state','=','done')])
            if line_ids:
                    line_dept_ids=line_object.search(cr,uid,[('sale_order_change_id','=',id),('dpt_id','=',department_ids[0]),('is_sure','=',True)])
                    if line_dept_ids:
                        sure_info='■'+u'能'+' □'+u'否'
                    else:
                        sure_info='□'+u'能'+' ■'+u'否'
            else:
                sure_info='□'+u'能'+' □'+u'否'
            return sure_info       

#---------品质损失及库存板处理----------------
        def p(self,cr,uid,id,value):
          info=''
          department_obj=self.pool.get('res.department')
          line_object=self.pool.get('so.change.records')
          department_ids=department_obj.search(cr,uid,[('name','=','品质部')])
          line_ids=line_object.search(cr,uid,[('sale_order_change_id','=',id),('dpt_id','=',department_ids[0])])
          if line_ids:
              line_info=line_object.browse(cr,uid,line_ids[0])    
              if value=='loss':
                  info=info+line_info.change_loss
              if value=='store':
                  info=info+line_info.deal_board
          return info
      
        def s(self,cr,uid,id,value):
          info=''
          department_obj=self.pool.get('res.department')
          line_object=self.pool.get('so.change.records')
          department_ids=department_obj.search(cr,uid,[('name','=','订单中心')])
          line_ids=line_object.search(cr,uid,[('sale_order_change_id','=',id),('dpt_id','=',department_ids[0])])
          if line_ids:
              line_info=line_object.browse(cr,uid,line_ids[0])                                    
              if value=='tool_loss':
                  info=info+line_info.tool_loss
              if value=='product_loss':
                  info=info+line_info.produt_loss
              if value=='rework_cost':
                  info=info+str(line_info.rework_cost)
              if value=='consultation':
                  info=info+line_info.consultation
          return info
                  
          
          
report_sxw.report_sxw('report.sale_order_change_report',
        'sale.order.change',
        '/addons/001_report/report/sale_order_change_report.odt',
        parser=sale_order_change_report)  