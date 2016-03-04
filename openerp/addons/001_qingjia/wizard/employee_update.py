#!usr/bin/python
# -*- coding:utf-8 -*-

from osv import fields,osv
import time
import datetime
import _mssql
import wizard
import pooler
from tools.translate import _

class employee_info_update(wizard.interface):
    #_name='employee.info.update'
    #_columns={
     #         'creat_date':fields.datetime('create_date',readonly=True),
    
   # }
    
    #===========================================================================
    # def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    #    result = super(employee_info_update, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
    #   
    #    _update_arch_lst =''' <form string='employee update'>
    #                                                <button icon='gtk-cancel'  special="cancel" string="Cancel"/>
    #                                                <button name="action_update_info" string="Update employee info" colspan="1" type="object" icon="gtk-go-forward"/>
    #                                        </form>
    #                                        '''
    #    result['arch']=_update_arch_lst
    #  
    #    return result
    #===========================================================================
     
    def action_update_info(self,cr,uid,data,context=None):
        #my=self.browse(cr,uid,ids[0])
        dpt_obj=pooler.get_pool(cr.dbname).get('hr.department')
        emp_obj=pooler.get_pool(cr.dbname).get('hr.employee')
        
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        field_list=[]
        field_dic={}
        code_all=[]
        #emp_file="E:\import_data\mtlerp_running\emp_field.txt"
        #fp=file(emp_file,'w')
        
        
        conn = _mssql.connect(server=server , user=user, password=passward,database=database)    
        #funcode_con= _mssql.connect(server=server , user=user, password=passward,database=database)    
        field_con= _mssql.connect(server=server , user=user, password=passward,database=database)  
        rec_conn= _mssql.connect(server=server , user=user, password=passward,database=database)    
        address_conn= _mssql.connect(server=server , user=user, password=passward,database=database)    
        leave_conn=_mssql.connect(server=server , user=user, password=passward,database=database) 
        code_conn=_mssql.connect(server=server , user=user, password=passward,database=database) 
        
        code_conn.execute_query('''select EmployeeCode from TBEmployee order by EmployeeCode''')
        for code in code_conn:
            code_all.append(code['EmployeeCode'])
            print code,'code'
        emp_ser=emp_obj.search(cr,uid,[])
       
        empcode_all=[]
        leavcode_all=[]
        onjobcode_all=[]
          
        for emp_code in code_all:
            leave_conn.execute_query('''Select WorkEndDate,WorkingConditions from VBEmployeeManage where ISNULL(EmpCompany,'0')='0' and EmployeeCode='%s' '''% emp_code )
     
            if abs(leave_conn.rows_affected):
                leav_dic={}
                for leave in leave_conn:
                    if unicode(leave['WorkingConditions']) =='否':
                        leav_dic[emp_code]={'if_on_job':False,'employee_state':'leaving_job','out_factory':unicode(leave['WorkEndDate'])}
 #                       print leav_dic,'leave_info'
                        break
                    else:
                        onjobcode_all.append(emp_code)
     
        
        for emp_id in emp_ser:
            emp_code=emp_obj.browse(cr,uid,emp_id).job_number
            if_on_job=emp_obj.browse(cr,uid,emp_id).if_on_job 
            if emp_code in leavcode_all:
                if if_on_job:
                    emp_obj.write(cr,uid,leavcode_all[emp_code])
                
        
        for emp_code in onjobcode_all:
            conn.execute_query('''select * from TBEmployee  where EmployeeCode=%s ''' % emp_code)
            rec_conn.execute_query('''select * from TBEmployee  where EmployeeCode=%s ''' % emp_code)
            
            for r in conn:
                field_list=[ key for key in r.keys() if type(key) .__name__ !='int']
                break
        
            ##search tablename info to file txt
            #=======================================================================
            # for field in field_list:
            #    field_con.execute_query(
            #        " select fieldname,displaylabel from TSFunctionFieldSet where fieldname='%s' "%field)
            #    for field in field_con:
            #        field_dic[field['fieldname']]=unicode(field['displaylabel'])
            #        break
            # print len(field_dic.keys())
            # 
            #=======================================================================
            
            ##ready update
           
            
            def res_search(obj,cr,uid,obj_name,field,value,if_cre=None,job_ser=None):
                #res_obj=obj.pool.get(obj_name)
                res_obj=pooler.get_pool(cr.dbname).get(obj_name)
                res_id=False
                if '长沙' in value:
                    value='湖南'
                elif '湖南省' in value:
                    value='湖南'
                elif '深圳' in value:
                    value='广东'
                elif '陕西' in value:
                    value='陕西省'
                
                if not job_ser:
                    res_sear=res_obj.search(cr,uid,[(field,'ilike',value)])
                else:
                    res_sear=res_obj.search(cr,uid,[(field,'=',value)])
    
                if res_sear:
                    res_id=res_sear[0]
                else:
                    if if_cre and obj_name=='res.country.state':
                        country_id=res_obj.pool.get('res.country').search(cr,uid,[('code','=','CN')])[0]
                        res_id=res_obj.create(cr,uid,{field:value,'code':value,'country_id':country_id})
                    elif if_cre and obj_name=='hr.job':
                        res_id=res_obj.create(cr,uid,{field:value,})
                    
                return res_id
            
            emp_map_dic={
                                      'EmployeeCode': 'job_number',
                                      'EmployeeName': 'name',
                                      'Sex': 'gender',
                                       'CodeName':'job_code',
                                       'TechnicalTitle':'job_name',
                                       'Departmentname':'department_id',
                                       'WorkerType':'job_id',
                                       'Diploma':'culture_level',
                                       'WorkStartDate':'in_factory',
                                       'HomeTel':'home_telephone',
                                      'MobileTelephone': 'mobile_phone',
                                       #'work_phone':None,
                                       'IDCardCode':  'identification_id',
                                        'DwellingPlace': 'home_address',
                                       'identification_address':'idAddress',  
                                       'country_id':'BirthPlace',
                                       'EmployeeType':'job_type',
                                       'Specialty':'major',
                                       'Birthday':'birthday',
                                       'WorkEndDate':'out_factory',
                                       'notes':'Memo',
                                      'MarriageState': 'marital',
                                       'ContractDate':'contract_date_start',
                                       'ContractOverDate':'contract_date_end',
                                       #'deal_dpt_id':dpt_obj.search(cr,uid,[('dpt_code','=',line[34])])[0],'DepartmentCode '
                                       'IsOldInsurance':'if_yanglao_insure',
                                       'IsSocialCard':'if_social_security',
                                       'Ethnic':'nation',
                                       'EMailCode':'work_email',
                                       }
            
            diploma_dic={
                                    '1401' :   '博士',
                                    '1402' :   '研究生',
                                    '1403' :   '本科',
                                    '1404' :   '大专',
                                    '1405':   '中专',
                                    '1406':    '硕士',
                                    '1407':    '高中',
                                    '1408':    '初中',
                                    '1409':    '小学',
                                    }
          
            field_list.remove('StateCode')
            field_list.append('idAddress')
            
            for record in rec_conn:
                #record在mssql查询到的字段值里循环
                process_dic={}
                if dpt_obj.search(cr,uid,[('dpt_code','=',record['DepartmentCode'])]):
                    process_dic['department_id']=dpt_obj.search(cr,uid,[('dpt_code','=',record['DepartmentCode'])])[0]
                else:
                    process_dic['department_id']=False
                process_dic['job_id']=res_search(self,cr,uid,'hr.job','name',unicode(record['WorkerType'] or '','gbk'),True,True)
                process_dic['if_yanglao_insure']=unicode(record['IsOldInsurance']) == '是' and True or False
                process_dic['if_social_security']=unicode(record['IsSocialCard']) == '是' and True or False
                process_dic['marital']=unicode(record['MarriageState']) =='已婚' and 2 or 1
                process_dic['job_type']=unicode(record['EmployeeType']) =='正式工' and 'regular' or 'not_regular'
                process_dic['gender']=unicode(record['Sex']) =='男'  and 'male' or 'female'
                process_dic['identification_address']=None
                #deal_dpt_id=dpt_obj.search(cr,uid,[('dpt_code','=',line[34])])[0]
                process_dic['country_id']=res_search(self,cr,uid,'res.country.state','name',unicode(record['BirthPlace']),True)
                process_dic['culture_level']=unicode(diploma_dic[record['Diploma']])
                
                address_conn.execute_query('''select idAddress from TBpidpublic where idarea='%s' ''' %record['IDCardCode'][0:6])
                for address in address_conn:
                    process_dic['identification_address']=unicode(address['idAddress'])
                    break
                
                emp_ser=emp_obj.search(cr,uid,[('job_number','=',record['EmployeeCode'])])
               
                if not emp_ser:
                    update_dic={}
                    
                    for field in field_list:
                        #field在字符类型里循环
                        if field in emp_map_dic:
                            #field字段在东烁对应OE里的字段
                            if emp_map_dic[field] not in process_dic: 
                                if type(record[field]).__name__ =='str':
                                    update_dic[emp_map_dic[field]]=unicode(record[field])
                                else:
                                    update_dic[emp_map_dic[field]]=record[field]     
                   
                    process_dic.update(update_dic)
                    emp_id=emp_obj.create(cr,uid,process_dic)
                else:
                    w_update={}
                    for field in field_list:
                        #field在字符类型里循环，字符类型不等于整形的
                        if field in emp_map_dic:
                            
                            if emp_map_dic[field] not in process_dic.keys():
                                foe_val=emp_obj.read(cr,uid,emp_ser[0],[emp_map_dic[field]])[emp_map_dic[field]]
                                if type(record[field]).__name__ =='str':
                                    
                                    if foe_val !=unicode(record[field]):
                                        w_update[emp_map_dic[field]]=unicode(record[field])
                                else:
                                 
                                    if record[field]:
                                        if str(foe_val) not in str(record[field]):
                                            w_update[emp_map_dic[field]]=record[field]
                                    
                            elif emp_map_dic[field] in process_dic.keys(): 
                                foe_value=emp_obj.read(cr,uid,emp_ser[0],[emp_map_dic[field]])[emp_map_dic[field]]
                               
                                if record[field]:
                                 
                                    if type(foe_value).__name__=='tuple':
                                        if foe_value[0] != process_dic[ emp_map_dic[field] ]:
                                            w_update[emp_map_dic[field]]=process_dic[ emp_map_dic[field] ]
                                    else:
                                       
                                        if foe_value not in [   process_dic[ emp_map_dic[field] ] ]:
                                            w_update[emp_map_dic[field]]=process_dic[ emp_map_dic[field] ]
                    if 'name' in w_update:
                        del w_update['name']            
                    print w_update,'w_update'
                    emp_id=emp_obj.write(cr,uid,emp_ser[0],w_update)
                                
        return True
    
    def open_action_update(self,cr,uid,data,context):
        self.action_update_info(cr,uid,data,context)
        return {
            'domain': [],
            'name': _('Employee update'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.update.message',
            'type': 'ir.actions.act_window',
            'target':'new',
                }
    
    states = {
        'init' :{
            'actions' : [],
            'result': {'type':'action', 'action':open_action_update, 'state':'end'}
                }
                    }
employee_info_update('employee_info_update_wiz')

class employee_update_message(osv.osv_memory):
    _name='employee.update.message'
    _columns={}
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(employee_update_message, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
       
        _update_arch_lst =''' <form string='employee update'>
                                                    <label string='Employee update sucess.....'/>
                                                    <button icon='gtk-cancel'  special="cancel" string="Cancel"/>
                                            </form>
                                            '''
        result['arch']=_update_arch_lst
      
        return result
employee_update_message() 

class employee_password_search(osv.osv_memory):
    _name='employee.password.search'
    _columns={
              'employee_id':fields.many2one('hr.employee','employee_id'),
              'job_number':fields.char('job_number',size=32),
              'employee_info':fields.char('employee_info',size=64),
              }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        result = super(employee_password_search, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar, submenu)
       
        _update_arch_lst =''' <form string='employee update'>
                                                    <label string='Employee info search .....'/>
                                                    <newline/>
                                                    <field name='employee_id' on_change='onchange_employee_id(employee_id)'/>
                                                    <field name='job_number'/>
                                                    <newline/>
                                                    <label string='Employee info:'/>
                                                    <newline/>
                                                    <field name='employee_info'/>
                                                    <newline/>
                                                    <button icon='gtk-cancel'  special="cancel" string="Cancel"/>
                                                    <button icon='gtk-jump-to'   string='employee search' name='employee_info_search' type='object' />
                                            </form>
                                            '''
        result['arch']=_update_arch_lst
      
        return result
    
    def onchange_employee_id(self,cr,uid,ids,res_id,context=None):
        emp_obj=self.pool.get('hr.employee')
        if res_id:
            emp_rec=emp_obj.browse(cr,uid,res_id)
            if emp_rec.job_number:
                return {'value':{'job_number':emp_rec.job_number}}
            
    def employee_info_search(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        user_obj=self.pool.get('res.users')
        emp_obj=self.pool.get('hr.employee')
        if my.job_number:
            number=my.job_number
            emp_ser=emp_obj.search(cr,uid,[('job_number','=',number)])
            user_id=user_obj.search(cr,uid,[('login','=',number)])
            if user_id and emp_ser:
                emp_info=user_obj.browse(cr,uid,user_id[0]).password
                self.write(cr, uid, ids,{'employee_info':emp_info,'employee_id':emp_ser[0]}) 
        return True
            
employee_password_search()  
 