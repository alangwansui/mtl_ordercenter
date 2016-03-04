#!usr/bin/python
# -*- coding:utf-8 -*-

from osv import osv,fields
import time
from datetime import datetime
from dateutil import rrule

class qingjia_calendar(osv.osv):
    _name='qingjia.calendar'
 
    _columns={
              'start_date':fields.datetime('start_date'),
              'end_date':fields.datetime('end_date'),
              'calendar_line_ids':fields.one2many('qingjia.calendar.line','qingjia_calendar_id','calendar_line_ids'),
              'state':fields.selection([('arrange','arrange'),('not arrange','not arrange')],'state',readonly=True)
    }
    
    _defaults={
           
    }
    
    def plan_arrange(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        line_obj=self.pool.get('qingjia.calendar.line')
        holidays=[]
        datas=[]
    
        start_date=time.strptime(my.start_date,'%Y-%m-%d %H:%M:%S')
        end_date=time.strptime(my.end_date,'%Y-%m-%d %H:%M:%S')
        dt=datetime(start_date.tm_year,start_date.tm_mon,start_date.tm_mday)
        unt=datetime(end_date.tm_year,end_date.tm_mon,end_date.tm_mday)
     
        days=rrule.rrule(rrule.DAILY,dtstart=dt,until=unt,byweekday=[6])
        ge=days._iter()
        for i in range(days.count()):
            date_info=ge.next()
            date_list=map(str,(date_info.year,date_info.month,date_info.day))
            date='-'.join(date_list)
            holidays.append(date)
    
        for day in holidays:
            line_search=line_obj.search(cr,uid,[('date','=',day),('type','=','holiday'),('state','=','arrange')])
            if line_search:
                datas.append((4,line_search[0]))
            else:
                datas.append((0,0,{'date':day,'type':'holiday','state':'arrange','name':'holiday'}))
     
        self.write(cr,uid,ids,{'calendar_line_ids':datas})
        return True
    
qingjia_calendar()

class qingjia_calendar_line(osv.osv):
    _name='qingjia.calendar.line'
    _columns={
            'qingjia_calendar_id':fields.many2one('qingjia.calendar','qingjia_calendar_id'),
            'name':fields.char('type',size=64),
            'date':fields.datetime('date'),
            'type':fields.selection([('work','Work'),('holiday','Holiday')],'type',),
            'state':fields.selection([('arrange','arrange'),('not arrange','not arrange')],'state'),
            'is_holiday':fields.boolean('is_holiday'),
            'note':fields.char('note',size=128),
    }
    
    _defaults={'type':'work'}
    
    def onchange_type(self,cr,uid,ids,res,context=None):
        if res:
            print res,'res'
            return {'value':{'name':res}}
        
qingjia_calendar_line()
    
