#!usr/bin/python
# -*- coding:utf-8 -*-

from osv import fields,osv
import time
import datetime
import _mssql

class employee_job(osv.osv_memory):
    _name='employee.job'
    _columns={
              'start_time':fields.date('start_time',required=True),
              'end_time':fields.date('end_time',required=True),
              'job_line_ids':fields.one2many('employee.job.line','employee_job_id','job_line_ids'),
    }
    
    def on_job_count(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        hr_obj=self.pool.get('hr.employee')
        qjia_obj=self.pool.get('qingjia.record')
        line_obj=self.pool.get('employee.job.line')
        cur_time=datetime.datetime.now()
        datas=[(5,)]
        #查询入厂时间
        end_datetime=datetime.datetime.strptime(my.end_time,'%Y-%m-%d')
        if end_datetime > cur_time:
            my.end_time=cur_time
        
        search_be=hr_obj.search(cr,uid,[('in_factory','<',my.start_time)])
        search_se=hr_obj.search(cr,uid,[('in_factory','>=',my.start_time),('in_factory','<=',my.end_time)])
        in_search=search_be+search_se
    
        start_date=time.strptime(my.start_time,'%Y-%m-%d')
        end_date=time.strptime(my.end_time,'%Y-%m-%d')
        start_time=datetime.date(start_date.tm_year,start_date.tm_mon,start_date.tm_mday)
        end_time=datetime.date(end_date.tm_year,end_date.tm_mon,end_date.tm_mday)
        
         #查询以前出厂时间
        search_obe=hr_obj.search(cr,uid,[('out_factory','<',my.start_time)])
        
        dt_start=start_time
        while start_time <= dt_start <= end_time:
        
            #查询之间出厂时间
            search_ose=hr_obj.search(cr,uid,[('out_factory','>',my.start_time),('out_factory','<',my.end_time)])
            out_search=search_obe + search_ose
            print out_search,'out'
            emp_ids=set(in_search) - (set(out_search))
            #查询请假记录
            qjia_count=0
            start_date='-'.join(map(str,(dt_start.year,dt_start.month,dt_start.day)))
            for emp_id in emp_ids:
                emp_search=qjia_obj.search(cr,uid,[('employee_id','=',emp_id),('start_time','<=',start_date),('end_time','>=',start_date),])
                if emp_search:
                    qjia_count+=1
            #计算在工人员数量,并创建明细
            print qjia_count,'count'
            count=len(emp_ids) - qjia_count
            
            datas.append((0,0,{'job_date':start_date,'count':count,'employee_job_id':ids[0]}))
            
            dt_start+=datetime.timedelta(days=1)
        self.write(cr,uid,ids,{'job_line_ids':datas})
        return True
    
employee_job()

class employee_job_line(osv.osv_memory):
    _name='employee.job.line'
    _columns={
              'employee_job_id':fields.many2one('employee.job','employee_job_id'),
              'job_date':fields.date('job_date'),
              'count':fields.integer('on job coung'),
           
    }
employee_job_line()


