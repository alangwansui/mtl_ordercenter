# -*- coding: utf-8 -*-
from osv import fields, osv
import time

class print_dispatch_form(osv.osv_memory):
    _name='print.dispatch.form'
    _columns={}
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(print_dispatch_form, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
       
        _update_arch_lst =''' <form string='print dispatch form'>
                                                    <button name="dispatch_car_print" string="print dispatch car "   icon="gtk-print"  type='object'/>
                                                    <button name="article_release_print"  string="print article release"   icon="gtk-print"  type='object'/>
                                                    <button icon='gtk-cancel'  special="cancel" string="Cancel"/>
                                            </form>
                                            '''
        result['arch']=_update_arch_lst
      
        return result
    
    def dispatch_car_print(self,cr,uid,ids,context=None):
        if not context:
            context={}
        act_ids=context.get('active_ids',False)
        act_model=context.get('active_model',False)
        data={'ids':act_ids}
        rec=self.pool.get(act_model).read(cr,uid,ids)
        data['form']=rec
        return{
           'type':'ir.actions.report.xml',
           'report_name':'dispatch_car_report',
           'datas':data,
           'nodestroy':True,
           }
     
    def article_release_print(self,cr,uid,ids,context=None):
        if not context:
            context={}
        act_ids=context.get('active_ids',False)
        act_model=context.get('active_model',False)
        data={'ids':act_ids}
        rec=self.pool.get(act_model).read(cr,uid,ids)
        data['form']=rec
   
        return{
           'type':'ir.actions.report.xml',
           'report_name':'article_release_report',
           'datas':data,
           'nodestroy':True,
           }
        return True
print_dispatch_form()  