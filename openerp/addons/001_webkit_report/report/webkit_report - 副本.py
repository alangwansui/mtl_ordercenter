# -*- encoding: utf-8 -*-
import time
from report import report_sxw
from osv import osv,orm
import tools
import netsvc

class webkit_price_change(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_price_change, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_price_change',
                       'price.change', 
                       'addons/001_webkit_report/report/price_change.mako',
                       parser=webkit_price_change)



class webkit_materiel_evaluation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_materiel_evaluation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_materiel_evaluation',
                       'materiel.evaluation', 
                       'addons/001_webkit_report/report/materiel_evaluation.mako',
                       parser=webkit_materiel_evaluation)


class webkit_equipment_evaluation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_equipment_evaluation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_equipment_evaluation',
                       'equipment.evaluation', 
                       'addons/001_webkit_report/report/equipment_evaluation.mako',
                       parser=webkit_equipment_evaluation)


class webkit_outsource_evaluation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_outsource_evaluation, self).__init__(cr, uid, name, context=context)        
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
report_sxw.report_sxw('report.webkit_outsource_evaluation',
                       'outsource.evaluation', 
                       'addons/001_webkit_report/report/outsource_evaluation.mako',
                       parser=webkit_outsource_evaluation)


class webkit_supply_evaluation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_supply_evaluation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_supply_evaluation',
                       'outsource.evaluation', 
                       'addons/001_webkit_report/report/supply_evaluation.mako',
                       parser=webkit_supply_evaluation)




class webkit_material_usage_statistics(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_material_usage_statistics, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_material_usage_statistics',
                       'outsource.evaluation', 
                       'addons/001_webkit_report/report/material_usage_statistics.mako',
                       parser=webkit_material_usage_statistics)



class webkit_account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_account_invoice, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'sum_supplier':self.supplier_info,
            
        })
    def supplier_info(self,partner_id,inv):
        cr=self.cr
        uid=self.uid
        count_untaxed=0.0
        count_total=0.0
        supply=[]
        print inv
        #print partner_id,partner_id.id
        obj_partner=self.pool.get('res.partner.address')
        obj_invoice=self.pool.get('account.invoice')
        
        partner_address=obj_partner.browse(cr,uid,partner_id.id).street
        partner_phone=obj_partner.browse(cr,uid,partner_id.id).phone
        print partner_address,partner_phone
        ids=obj_invoice.search(cr,uid,[('id','!=','0')])
        #print ids,obj_invoice.browse(cr,uid,ids[0]).partner_id
        for id in ids:
            partner_current_id=obj_invoice.browse(cr,uid,id).partner_id
            #print partner_current_id
            if(partner_current_id.id==partner_id.id):
                count_untaxed+=obj_invoice.browse(cr,uid,id).amount_untaxed
                count_total+=obj_invoice.browse(cr,uid,id).amount_total 
         #       print count_untaxed,count_total
                supply.append([partner_address,partner_phone,count_untaxed,count_total])
        #print supply
                return supply            
        
report_sxw.report_sxw('report.webkit_account_invoice',
                       'account.invoice', 
                       'addons/001_webkit_report/report/account_invoice.mako',
                       parser=webkit_account_invoice)


class webkit_account_invoice_line(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_account_invoice_line, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_account_invoice_line',
                       'outsource.evaluation', 
                       'addons/001_webkit_report/report/account_invoice_line.mako',
                       parser=webkit_account_invoice_line)



class supply_odt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(supply_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'get_address':self.get_address,
            
        })
    
    def get_address(self,partner_id):
        res_obj=self.pool.get('res.partner')
        address_obj=self.pool.get('res.partner.address')
        res_search=res_obj.search(self.cr,self.uid,[('id','=',parther_id)])
        print res_search
        res_address=address_obj.browse(self.cr,self.uid,res_search).street
        return res_address
report_sxw.report_sxw('report.supply_odt',
                       'supply.evaluation', 
                       'addons/001_webkit_report/report/supply_evaluation.odt',
                       parser=supply_odt)
class outsource_odt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(outsource_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.outsource_odt',
                       'outsource.evaluation', 
                       'addons/001_webkit_report/report/outsource_evaluation.odt',
                       parser=outsource_odt)
                       
class materiel_odt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(materiel_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.materiel_odt',
                       'materiel.evaluation', 
                       'addons/001_webkit_report/report/materiel_evaluation.odt',
                       parser=materiel_odt)
                       
class price_odt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(price_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.price_odt',
                       'price.change', 
                       'addons/001_price_change/report/price_odt.odt',
                       parser=price_odt)                       
class equipment_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(equipment_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            'default_value':self.default_value,
            
        })
    def default_value(self,field):
            print self.localcontext['name_space']
            if not field:
                    field="同意"
                    return field
            else:
                    return field
        
report_sxw.report_sxw('report.equipment_odt',
                       'equipment.evaluation', 
                       'addons/001_webkit_report/report/equipment_evaluation.odt',
                       parser=equipment_odt)


class purchase_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(purchase_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.purchase_odt',
                       'purchase.order', 
                       'addons/001_webkit_report/report/purchase_order.odt',
                       parser=purchase_odt)

class year_supply_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(year_supply_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.year_supply_odt',
                       'supply.year.evaluation', 
                       'addons/001_webkit_report/report/year_supply_evaluation.odt',
                       parser=year_supply_odt)
     
     


                      
class receive_order_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(receive_order_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
           
            'paser_f':self.paser_f,
            
        })
    def paser_f (self,f):
        res=[0,]*10
        f="%.2f" % f
        #print f
        a=f.split(r'.')
        res= res[0:8-len(a[0])] + [i for i in a[0]] + [a[1][j] for j in [0,1] ] 
        return res

        
report_sxw.report_sxw('report.receive_order_odt',
                       'purchase.order', 
                       'addons/001_webkit_report/report/receive_order.odt',
                       parser=receive_order_odt)
##########################################################################

                       
                       
###########stock  report###################################################                       
class supplier_bad_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(supplier_bad_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.supplier_bad_odt',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/supplier_bad.odt',
                       parser=supplier_bad_odt)

                       
class take_delivery_odt(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
       
        super(take_delivery_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.take_delivery_odt',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/take_delivery.odt',
                       parser=take_delivery_odt)
                   

class webkit_manfacture_get(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(webkit_manfacture_get, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.webkit_manfacture_get',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/manfacture_get.mako',
                       parser=webkit_manfacture_get)
                       
class manfacture_get_odt(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(manfacture_get_odt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.manfacture_get_odt',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/manufacture_get_order.odt',
                       parser=manfacture_get_odt)

report_sxw.report_sxw('report.deliver_order_label_odt',
                       'label.line', 
                       'addons/001_webkit_report/report/stockreport/deliver_order.odt',
                       parser=manfacture_get_odt)

report_sxw.report_sxw('report.deliver_order_odt',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/deliver_order.odt',
                       parser=manfacture_get_odt)

report_sxw.report_sxw('report.return_material_odt',
                       'stock.picking', 
                       'addons/001_webkit_report/report/stockreport/return_material.odt',
                       parser=manfacture_get_odt)

######################################Sale report################################
class pcb_info_odt(report_sxw.rml_parse):
    def __init__(self,cr,uid,name='pcb.info.odt',context=None):
        super(pcb_info_odt,self).__init__(cr,uid,name='pcb.info.odt',context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':self.info_convent,
                                  })
    def info_convent(self,record=None):
        info=''
        for rec in record:
            info+=rec.label+';'
        return info
pcb_info=report_sxw.report_sxw('report.pcb_info_odt',
                      'pcb.info',
                      'addons/001_webkit_report/report/salereport/pcb_info.odt',
                      parser=pcb_info_odt)
report_sxw.report_sxw('report.routing_pcb_info_report',
                      'mrp.routing',
                      'addons/001_webkit_report/report/routingreport/pcb_info.odt',
                      parser=pcb_info_odt)    

report_sxw.report_sxw('report.workcenter_pcb_info_report',
                      'mrp.production.workcenter.line',
                      'addons/001_webkit_report/report/mrpreport/pcb_info.odt',
                      parser=pcb_info_odt)    

class single(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(single,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  })
report_sxw.report_sxw('report.single.user',
                      'pcb.info',
                      'addons/001_webkit_report/report/salereport/order1.rml',
                      parser=single)
                      

class price_sheet_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(price_sheet_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':pcb_info.parser(cr,uid).localcontext['info_convent'],
                                  })
report_sxw.report_sxw('report.price_sheet_report',
                      'price.sheet',
                      'addons/001_webkit_report/report/salereport/price_sheet_report.odt',
                      parser=price_sheet_report)

def int_convent_str(value):
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
        uom_list=['万亿','千','百','拾','亿','千','百','拾','万','千','百','拾','元','角','分']
       
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
      
                      
class sale_order_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(sale_order_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':self.info_convent,
                                  'info_get':pcb_info.parser(cr,uid).localcontext['info_convent'],
                                  })
    def info_convent(self,line=None):
        cost_all=0.0
        for rec in line:
            cost_all+=rec.price_sheet_id.cost_all_s
        info_text=int_convent_str(cost_all)
        return cost_all,info_text

             
report_sxw.report_sxw('report.sale_order_report',
                      'sale.order',
                      'addons/001_webkit_report/report/salereport/sale_order_report.odt',
                      parser=sale_order_report)

class contract_production_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(contract_production_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  })
report_sxw.report_sxw('report.contract_production_order',
                      'mrp.production',
                      'addons/001_webkit_report/report/salereport/contract_production.rml',
                      parser=contract_production_report)
 #############################mrp production report############################
class mrp_production_order(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(mrp_production_order,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_print':self.info_print,
                                  })
    def info_print(self,info_line):
        info=''
        for record in info_line:
            if record.is_print:
                info=info+record.parameter_id.name+':'+(True and record.value or '') or ''
            elif not record.is_print:
                continue
        return info
report_sxw.report_sxw('report.mrp.production.odt',
                      'mrp.production',
                      'addons/001_webkit_report/report/mrpreport/mrp_production.odt',
                      parser=mrp_production_order)

report_sxw.report_sxw('report.mrp_production_income_odt',
                       'mrp.production', 
                       'addons/001_webkit_report/report/stockreport/mrp_production_income.odt',
                       parser=manfacture_get_odt)

class mrp_routing_drill_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(mrp_routing_drill_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':self.info_convent,
                                  })
       
    def info_convent(self,record=None,is_slot=None,is_npth=None):
        count1=0
        count2=0
        count3=0
        count4=0
        rec=[[],[],[],[]]
        res={}
        for info in record:
            if info.type_name=='first':
                count1+=info.count
                rec[0].append(info)
            elif info.type_name=='second':
                count2+=info.count
                rec[1].append(info)
            elif info.type_name=='position':
                rec[2].append(info)
                count3+=info.count
            elif info.type_name=='control_depth':
                count4+=info.count
                rec[3].append(info)  
            else:
                continue
            res.update({'f':rec[0],'s':rec[1],'p':rec[2],'c':rec[3]})
        is_slot=is_slot and '√' or ''
        is_npth=is_npth and '√' or ''
        return count1,count2,is_slot,is_npth,count3,count4,res

report_sxw.report_sxw('report.mrp_routing_drill_report',
                    'mrp.production',
                      'addons/001_webkit_report/report/mrpreport/routing_drill.odt',
                      parser=mrp_routing_drill_report)

class mrp_routing_plot_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(mrp_routing_plot_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':self.info_convent,
                                  'info_mark':self.info_mark,
                                  })
    def info_mark(self,mark=None):
        value=''
        for info in mark:
            value=value+info.name+';'
        print value
        return value
    def info_convent(self,black_postive=(),black_negative=(),yellow_postive=(),yellow_negative=()):
        bp_info=black_postive and (black_postive[0] and '↑' or '' or black_postive[1] and '↓' or '') or ''
       
        bn_info=black_negative and (black_negative[0] and '↑' or '' or black_negative[1] and '↓' or '') or ''
       
        yp_info=yellow_postive and (yellow_positive[0] and '↑' or '' or yellow_positive[1] and '↓' or '') or ''
      
        yn_info=yellow_negative and (yellow_negative[0] and '↑' or '' or yellow_negative[1] and '↓' or '') or ''
       
        return bp_info,bn_info,yp_info,yn_info

report_sxw.report_sxw('report.mrp_routing_plot_report',
                      'mrp.production',
                      'addons/001_webkit_report/report/mrpreport/routing_plot.odt',
                      parser=mrp_routing_plot_report)

class mrp_laminar_structure_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(mrp_laminar_structure_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  })
    
report_sxw.report_sxw('report.mrp_laminar_structure_report',
                      'mrp.production',
                      'addons/001_webkit_report/report/mrpreport/laminar_structure.odt',
                      parser=mrp_laminar_structure_report)
class mrp_board_cutting_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(mrp_board_cutting_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  })

report_sxw.report_sxw('report.mrp_board_cutting_report',
                      'mrp.production',
                      'addons/001_webkit_report/report/mrpreport/board_cutting.rml',
                      parser=mrp_board_cutting_report)

#################account report################################################
class mtl_duizhang_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(mtl_duizhang_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'info_convent':self.info_convent,
                                  })
    
    def info_convent(self,value):
        info_text=int_convent_str(value)
        return info_text
report_sxw.report_sxw('report.mtl_duizhang_report_odt',
                      'mtl.duizhang',
                      'addons/001_webkit_report/report/accountreport/invoice_read.odt',
                      parser=mtl_duizhang_report)
    
####################################################    
###########################human_resource report################################
class reward_lines_report(report_sxw.rml_parse):
    
    def __init__(self,cr,uid,name,context):
        super(reward_lines_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                  'get_rec_info':self.get_rec_info,
                                  })  
    def get_rec_info(self):
        cr=self.cr
        uid=self.uid
        rec_dic={}
        new_ids=[]
        for obj in self.objects:
            if obj.product_description:
                if obj.product_description in rec_dic:
                    rec_dic[obj.product_description].append(obj.id)
                else:
                    rec_dic[obj.product_description]=[obj.id]
            else:
                if 'n' in rec_dic:
                    rec_dic['n'].append(obj.id)
                else:
                    rec_dic['n']=[obj.id]
        for rec_ids in rec_dic.values():
            new_ids.extend(rec_ids)
        rec_list=self.pool.get('reward.lines').browse(cr,uid,new_ids)
        self.objects=rec_list[:]
        
        return rec_list
     
report_sxw.report_sxw('report.reward_lines_report_odt',
                      'reward.lines',
                      'addons/001_webkit_report/report/human_resource/reward_lines.odt',
                      parser=reward_lines_report)
   

class punish_lines_info_report(report_sxw.rml_parse):
    def __init__(self,cr,uid,name,context):
        super(punish_lines_info_report,self).__init__(cr,uid,name,context=context)
        self.localcontext.update({
                                  'cr':cr,
                                  'time':time,
                                  'uid':uid,
                                   'get_rec_info':self.get_rec_info,
                                  })
        
    def get_rec_info(self):
        cr=self.cr
        uid=self.uid
        rec_dic={}
        new_ids=[]
        for obj in self.objects:
            pro_name=obj.punish_lines_id.product_description
            if pro_name:
                if pro_name in rec_dic:
                    rec_dic[pro_name].append(obj.id)
                else:
                    rec_dic[pro_name]=[obj.id]
            else:
                    if 'n' in rec_dic:
                        rec_dic['n'].append(obj.id)
                    else:
                        rec_dic['n']=[obj.id]
        for rec_ids in rec_dic.values():
            new_ids.extend(rec_ids)
        print new_ids
        rec_list=self.pool.get('punish.lines.info').browse(cr,uid,new_ids)
        self.objects=rec_list[:]
        
        return rec_list    
report_sxw.report_sxw('report.punish_lines_info_report_odt',
                      'punish.lines.info',
                      'addons/001_webkit_report/report/human_resource/punish_lines.odt',
                      parser=punish_lines_info_report)









#外协喷锡
class outsource_spary_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_spary_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_spary_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_spary_report.odt',
        parser=outsource_spary_report)

class outsource_spary_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_spary_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_spary_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_spary_report_pcs.odt',
        parser=outsource_spary_report_pcs) 



        

#外协沉金
class outsource_sink_gold_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_gold_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_gold_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_gold_report.odt',
        parser=outsource_sink_gold_report)


class outsource_sink_gold_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_gold_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_gold_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_gold_report_pcs.odt',
        parser=outsource_sink_gold_report_pcs)




		
#外协钻孔		
class outsource_drill_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_drill_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_drill_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_drill_report.odt',
        parser=outsource_drill_report)	



class outsource_drill_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_drill_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_drill_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_drill_report_pcs.odt',
        parser=outsource_drill_report_pcs)    


	
		
		
		
class outsource_fly_test_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_fly_test_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_fly_test_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_fly_test_report.odt',
        parser=outsource_fly_test_report)



class outsource_fly_test_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_fly_test_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_fly_test_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_fly_test_report_pcs.odt',
        parser=outsource_fly_test_report_pcs)





			
		
		
class outsource_gold_finger_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_gold_finger_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_gold_finger_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_gold_finger_report.odt',
        parser=outsource_gold_finger_report)


class outsource_gold_finger_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_gold_finger_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_gold_finger_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_gold_finger_report_pcs.odt',
        parser=outsource_gold_finger_report_pcs)    


			
		
		
		
class outsource_route_vcut_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_route_vcut_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_route_vcut_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_route_vcut_report.odt',
        parser=outsource_route_vcut_report)	



class outsource_route_vcut_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_route_vcut_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_route_vcut_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_route_vcut_report_pcs.odt',
        parser=outsource_route_vcut_report_pcs)    




class outsource_sink_sn_sliver_osp_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_sn_sliver_osp_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_sn_sliver_osp_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_sn_sliver_osp_report.odt',
        parser=outsource_sink_sn_sliver_osp_report)	

class outsource_sink_sn_sliver_osp_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_sn_sliver_osp_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_sn_sliver_osp_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_sn_sliver_osp_report_pcs.odt',
        parser=outsource_sink_sn_sliver_osp_report_pcs)





#沉银
class outsource_sink_sliver_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_sliver_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_sliver_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_sliver_report.odt',
        parser=outsource_sink_sliver_report)	




class outsource_sink_sliver_report_pcs(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_sink_sliver_report_pcs,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_sink_sliver_report_pcs',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_sink_sliver_report_pcs.odt',
        parser=outsource_sink_sliver_report_pcs)    

#修金板
class outsource_repair_gold_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_repair_gold_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_repair_gold_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_repair_gold_report.odt',
        parser=outsource_repair_gold_report) 		
		
		
#层压
class outsource_laminate_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_laminate_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })  
report_sxw.report_sxw('report.outsource_laminate_report',
        'outsource.process',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_laminate_report.odt',
        parser=outsource_laminate_report) 		
		









		
		
		
		
		
		

####外协对账表
class outsource_duizhang_report(report_sxw.rml_parse):
        def __init__(self,cr,uid,name,context):
            super(outsource_duizhang_report,self).__init__(cr,uid,name,context=context)
            self.localcontext.update({
            'time':time,
            'cr':cr,
            'uid':uid,
        
            })

        
        
report_sxw.report_sxw('report.outsource_duizhang_report',
        'outsource.duizhang',
        '/addons/001_webkit_report/report/outsource_process_report/outsource_duizhang_report.odt',
        parser=outsource_duizhang_report)        















#################routing report################################################
#===============================================================================
# class routing_drill_report(report_sxw.rml_parse):
#    
#    def __init__(self,cr,uid,name,context):
#        super(routing_drill_report,self).__init__(cr,uid,name,context=context)
#        self.localcontext.update({
#                                  'cr':cr,
#                                  'time':time,
#                                  'uid':uid,
#                                  'info_convent':self.info_convent,
#                                  })
#       
#    def info_convent(self,record=None,is_slot=None,is_npth=None):
#        count1=0
#        count2=0
#        for info in record:
#            if info.type_name=='first':
#                count1=count1+info.count
#            elif info.type_name=='second':
#                count2=count2+info.count
#            else:
#                continue
#        is_slot=is_slot and '√' or ''
#        is_npth=is_npth and '√' or ''
#        return count1,count2,is_slot,is_npth
# 
# report_sxw.report_sxw('report.routing_drill_report',
#                      'mrp.routing',
#                      'addons/001_webkit_report/report/mrpreport/routing_drill.odt',
#                      parser=routing_drill_report)
# 
# class routing_plot_report(report_sxw.rml_parse):
#    def __init__(self,cr,uid,name,context):
#        super(routing_plot_report,self).__init__(cr,uid,name,context=context)
#        self.localcontext.update({
#                                  'cr':cr,
#                                  'time':time,
#                                  'uid':uid,
#                                  'info_convent':self.info_convent,
#                                  'info_mark':self.info_mark,
#                                  })
#    def info_mark(self,mark=None):
#        value=''
#        for info in mark:
#            value=value+info.name+';'
#        print value
#        return value
#    def info_convent(self,black_postive=(),black_negative=(),yellow_postive=(),yellow_negative=()):
#        bp_info=black_postive and (black_postive[0] and '↑' or '' or black_postive[1] and '↓' or '') or ''
#       
#        bn_info=black_negative and (black_negative[0] and '↑' or '' or black_negative[1] and '↓' or '') or ''
#       
#        yp_info=yellow_postive and (yellow_positive[0] and '↑' or '' or yellow_positive[1] and '↓' or '') or ''
#      
#        yn_info=yellow_negative and (yellow_negative[0] and '↑' or '' or yellow_negative[1] and '↓' or '') or ''
#       
#        return bp_info,bn_info,yp_info,yn_info
# report_sxw.report_sxw('report.routing_plot_report',
#                      'mrp.routing',
#                      'addons/001_webkit_report/report/mrpreport/routing_plot.odt',
#                      parser=routing_plot_report)
#                      
# 
# class laminar_structure_report(report_sxw.rml_parse):
#    def __init__(self,cr,uid,name,context):
#        super(laminar_structure_report,self).__init__(cr,uid,name,context=context)
#        self.localcontext.update({
#                                  'cr':cr,
#                                  'time':time,
#                                  'uid':uid,
#                                  })
#    
# report_sxw.report_sxw('report.laminar_structure_report',
#                      'mrp.routing',
#                      'addons/001_webkit_report/report/mrpreport/laminar_structure.odt',
#                      parser=laminar_structure_report)
#                      
# class board_cutting_report(report_sxw.rml_parse):
#    def __init__(self,cr,uid,name,context):
#        super(board_cutting_report,self).__init__(cr,uid,name,context=context)
#        self.localcontext.update({
#                                  'cr':cr,
#                                  'time':time,
#                                  'uid':uid,
#                                  })
# report_sxw.report_sxw('report.board_cutting_report',
#                      'mrp.routing',
#                      'addons/001_webkit_report/report/mrpreport/board_cutting.odt',
#                      parser=board_cutting_report)
#===============================================================================
#################################################################################