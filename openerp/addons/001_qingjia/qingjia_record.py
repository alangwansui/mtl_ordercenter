#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime

class qingjia_record(osv.osv):
    _name='qingjia.record'
    _type_tuple=('year_jia','shi_jia','bing_jia','tiaox_jia')
    _qingjia_type=[(i,i.title()) for i in _type_tuple]
    _state=('draft','w_dpt_director','w_dpt_manage','w_manager','w_personnel','done','cancel')
    _state_list=[(i,i.title()) for i in _state]
    
    def count_tian_shu(self,cr,uid,ids,context=None):
        record=self.browse(cr,uid,ids[0])
        qjcalen_obj=self.pool.get('qingjia.calendar.line')
       
        qjcalen_ids=qjcalen_obj.search(cr,uid,[('date','>=',record.start_time),('date','<=',record.end_time),('type','=','holiday'),('state','=','arrange')])
   
        print record.end_time , record.start_time
       
        if record.start_time and record.end_time:
            e_time=record.end_time.split('-')
            s_time=record.start_time.split('-')
            ye,me,de=tuple(map(int,e_time))
            ys,ms,ds=tuple(map(int,s_time)) 
            t=(datetime(ye,me,de) - datetime(ys,ms,ds)).days - len(qjcalen_ids)
            
            self.write(cr,uid,ids,{'tianshu_total':t})
            
    _columns={
              'employee_id':fields.many2one('hr.employee','employee_id',required=True,select=True),
              'dpt_id':fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='dpt_id',readonly=True),
              'start_time':fields.date('start_time',select=True,required=True),
              'end_time':fields.date('end_time',select=True,required=True),
              'tianshu_total':fields.integer('tianshu_total',readonly=True),
              'qingjia_type':fields.selection(_qingjia_type,'qingjia_type',required=True,select=True),
              'note':fields.text('note'),
              'state':fields.selection(_state_list,'state',readonly=True,select=True),
              'test':fields.char('test',size=64),
    }
    _defaults={
               'state': lambda *a:'draft',
    }
    _sql_constraints=[('test','unique(test)','test value must be unique')]
    
    def updata_state(self,cr,uid,ids,state=None,context=None):
        self.write(cr,uid,ids,{'state':state})
        record=self.browse(cr,uid,ids[0])
        
        return True
    
    def check_tian_shu(self,cr,uid,ids):
        record=self.browse(cr,uid,ids[0])
        if record.tianshu_total > 3:
            return True
        else:
            return False
qingjia_record()

 
