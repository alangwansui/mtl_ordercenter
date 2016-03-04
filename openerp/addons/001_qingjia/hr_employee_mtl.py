#/usr/bin/python
# -*- coding:utf-8 -*-
from osv import fields,osv
import time
from datetime import datetime
class hr_employee_mtl(osv.osv):
    _inherit='hr.employee'
    
    def _info_get(self,cr,uid,ids,field_name,agrs,context=None):
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            if field_name=='job_age':
                if my.birthday:
                    job_year=datetime.strptime(my.birthday,'%Y-%m-%d').year
                    cur_yaar=datetime.today().year
                    res[id]=int(cur_yaar - job_year)
                else:
                    res[id]=False
            elif field_name=='work_years':
                if my.in_factory:
                    in_year=datetime.strptime(my.in_factory,'%Y-%m-%d').year
                    cur_yaar=datetime.today().year
                    res[id]=int(cur_yaar - in_year)
                else:
                    res[id]=False
                    
            elif field_name=='birth_month':
                if my.birthday:
                    in_month=datetime.strptime(my.birthday,'%Y-%m-%d').month
                    res[id]=in_month
                else:
                    res[id]=False
            elif field_name=='this_month':
                cur_time=time.strftime('%Y-%m-%d')
                cur_month=datetime.strptime(cur_time,'%Y-%m-%d').month
          
                if my.birthday:
                    in_month=datetime.strptime(my.birthday,'%Y-%m-%d').month
                   
                    if cur_month == in_month:
                        res[id]=True
                    else:
                        res[id]=False
                else:
                    res[id]=False
        return res
    def check_job_number(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.job_number:
            number_ser=self.search(cr,uid,[('job_number','=',my.job_number),('id','!=',ids[0])])
            
            if number_ser:
                return False
            else:
                return True
            
    def check_on_job(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.if_on_job:    
            if my.employee_state=='on_job':
                return True
            else:
                return False
        else:
            if my.employee_state=='leaving_job':
                return True
            else:
                return False
     
    def _search_month_info(self,cr,uid,obj,fields_name,arg,context):
      
        s=arg[0][2]
        cur_time=time.strftime('%Y-%m-%d')
        cur_month=datetime.strptime(cur_time,'%Y-%m-%d').month
                    
        res_ids=self.search(cr,uid,[('birth_month','=',cur_month),('if_on_job','=',True)])
       
        return [('id','in',res_ids)]   
            
    _columns={
              'job_number':fields.char('job_number',size=32),#职员代号
              'in_factory':fields.date('in_factory_date'),
              'out_factory':fields.date('out_factory_date'),
              'home_address':fields.char('home_address',size=64),
              'home_telephone':fields.char('home_telephone',size=32),
              'employee_state':fields.selection([('on_job','on_job'),('leaving_job','leaving_job')],'employee_state',change_default=True),
              'job_code':fields.char('job_code',size=16),#代号
              'job_name':fields.char('job_name',size=16),#职称
              'job_age':fields.function(_info_get,type='integer',method=True,string='job_age'),
              'work_years':fields.function(_info_get,type='integer',method=True,string='work_years'),
              'culture_level':fields.char('culture_level',size=16),
              'identification_address':fields.char('Identification_address',size=128,required=True),
              'country_id':fields.many2one('res.country.state','country_id',required=True),#所属地区
              'job_type':fields.selection([('regular','regular'),('not_regular',('not_regular'))],'job_type',),# 正式工，试用工
              'major':fields.char('major',size=16),#职员专业
              #'today_birthday':fields.boolean('today_birthday'),
              'contract_date_start':fields.date('contract_date_start'),
              'contract_date_end':fields.date('contract_date_end',select=True),
              'deal_dpt_id':fields.many2one('hr.department','deal_dpt_id'),# 经手部门
              'if_yanglao_insure':fields.boolean('if_yanglao_insure'),#是否办理养老保险
              'if_social_security':fields.boolean('if_social_security'),#是否办理社保
              'nation':fields.char('nation',size=32),
              'birth_month':fields.function(_info_get,method=True,type='char',string='birth_month',size=16,store=True),
              'this_month':fields.function(_info_get,fnct_search=_search_month_info,method=True,type='boolean',string='this_month',size=16),
              'if_on_job':fields.boolean('if_on_job'),
    }

    _defaults={
            'employee_state':lambda *a:'on_job',
            'if_on_job':lambda *a:True,
    }
    
    _constraints=[(check_job_number,'unique error: job_number must be unique!',['job_number']),
                  (check_on_job,'employee state error: on_job or leaving_job please check!',['employee_state'])]
    
    def onchange_on_job(self,cr,uid,ids,field_value,context=None):
        res={}
        res_id=None
  
        if ids:   
            my=self.browse(cr,uid,ids[0])
           
            res_obj=self.pool.get('res.users')
            if my.user_id:
                res_id=my.user_id.id
            else:
                company_id=my.company_id and my.company_id.id or False
                dep_id=my.department_id and my.department_id.id or False
                res_search=res_obj.search(cr,uid,[('name','=',my.name),('company_id','=',company_id),('context_department_id','=',dep_id)])
                res_id=res_search and res_search[0]
            if field_value:
                
                if res_id:
                    self.pool.get('res.users').write(cr,uid,res_id,{'active':True})
                return {'value':{'employee_state':'on_job'}}
              
            else: 
                if res_id:          
                    self.pool.get('res.users').write(cr,uid,res_id,{'active':False})
                return {'value':{'employee_state':'leaving_job'}}
   
    def create_users(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        user_obj=self.pool.get('res.users')
        res_obj=self.pool.get('resource.resource')
        
        if not my.resource_id.user_id:
           
            user_id=user_obj.create(cr,uid,{
                'name':my.name,
                'login':my.job_number,
                'password':'Mtloe'+my.job_number,
                'context_department_id':my.department_id.id ,
            })
            
            if user_id:
                res_obj.write(cr,uid,my.resource_id.id,{'user_id':user_id})
                
        return True
              
        
hr_employee_mtl()