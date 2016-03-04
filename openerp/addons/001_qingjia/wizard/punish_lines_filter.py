#!usr/bin/python
# -*- coding:utf-8 -*-

from osv import fields,osv
import time
import datetime
import _mssql

class punish_lines_filter(osv.osv_memory):
    _name='punish.lines.filter'
    punish_state=('draft','w_dpt_confirm','w_responsible','top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','w_punish','done','cancel')
    _state_list=[(i,i.title()) for i in punish_state]
    _columns={
              'state':fields.selection(_state_list,'state',readonly=True,size=32,select=True),
              'start_time':fields.date('start_time',required=True),
              'end_time':fields.date('end_time',required=True),
              'approver_sel':fields.selection([('agree','agree'),('disagree','disagree')],'approver_sel',),
              'if_return':fields.boolean('if_return'),
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(punish_lines_filter, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
       
        _update_arch_lst =''' <form string='punsih search'>
                                                    
                                                    <field name='approver_sel' widget='selection'/>
                                                    <field name='start_time'/>
                                                    <field name='end_time'/>
                                                    <button name="punish_approver_search"  string="approver info search"   icon="gtk-jump-to"  type='object'/>
                                                   
                                                    <button icon='gtk-cancel'  special="cancel" string="Cancel"/>
                                            </form>
                                            '''
        result['arch']=_update_arch_lst
      
        return result
    
    def punish_approver_search(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        app_obj=self.pool.get('punish.approver.lines')
        if not context:
            context={}
        act_ids=context.get('active_ids',False)
        act_model=context.get('active_model',False)
        ser_domain=[('approver_state','=','w_director')]
        if my.start_time and my.end_time:
            ser_domain.append(('create_date','>=',my.start_time))
            ser_domain.append(('create_date','<=',my.end_time))
        elif my.start_time and not my.end_time:
            ser_domain.append(('create_date','=',my.start_time))
        elif my.end_time and not my.start_time:
            ser_domain.append(('create_date','=',my.end_time))
        if my.approver_sel:
            ser_domain.append(('approver_sel','=',my.approver_sel))
        print ser_domain,'domain'
        app_ids=app_obj.search(cr,uid,ser_domain)
        pu_ids=[]
        if app_ids:
            for app_id in app_ids:
                pu_id=app_obj.browse(cr,uid,app_id).punish_lines_id
                if pu_id:
                    pu_ids.append(pu_id.id)
        print pu_ids,'punish_ids'
        return {
                'name':"Convent punish lines",
                'view_mode': 'tree,form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'punish.lines',
                #'res_id': so_id,
                'type': 'ir.actions.act_window',
                #'nodestroy': True,
                'domain':[('id','in',pu_ids)],
                    }
    def ret_punish_lines(self,cr,uid,ids,ret_ids=None,context=None):
        my=self.browse(cr,uid,ids[0])
        pu_obj=self.pool.get('punish.lines')
        return True
            
         
punish_lines_filter()