#!/usr/bin/python
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
import _mssql
import Mssql_read_col

import sys
reload(sys)
##sys.setdefaultencoding('utf8')



class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _dpt_list=[('2501','business_dpt'),('2502','finance_dpt'),('2503','wardhouse_dpt'),
              ('2504','product_dpt'),('2505','manager_dpt'),('2506','plan_dpt'),('2507','eng_dpt'),]##eng_dpt:工程技术部
    _columns = {       
     'dpt_code': fields.char('dpt_code', size=256),     
     'ref2': fields.char('ref2', size=256),  
     'dpt_responsible':fields.char('dpt_responsible',size=256),
     'dpt_address':fields.char('dpt_adress',size=256),
     'dpt_telephone':fields.char('dpt_telephone',size=256),
     'dpt_type':fields.selection(_dpt_list,'dpt_type',readonly=True),
    'dpt_note':fields.char('dpt_note',size=256),
    }
     
hr_department()

class import_partner(osv.osv):
    _name = "import.partner"
    _description = "客户导入"

    _columns = {
        'server': fields.char('服务器', size=64, required=True, select=True),
        'user': fields.char('用户名', size=256, required=True, select=True),
        'password': fields.char('密码', size=256, required=True, select=True),
        'database': fields.char('数据库', size=256, required=True, select=True),
        'sqlrequery': fields.text('查询语句'),
        'type': fields.selection([('customer','客户'),('supplier','供应商'),('department','部门'),\
                                  ('employee','职员'),('group','用户组'),\
                                  ('user','用户'),('production','产品'),('pcb','PCB'),('country_state','地区')], '导入类型'),
        'result':  fields.text('查询结果语句')
    }
    _defaults = {
        'server': lambda *a:'192.168.0.2',
        'user': lambda *a: 'sa',
        'password': lambda *a: '719799',
        'database': lambda *a:'mtltest',
        'sqlrequery': lambda *a:'SELECT top 10 * FROM tblog order by id desc'
    }
     
    def gb2312ToUtf8(self,strtemp):
        if strtemp is None:
            return ''
        strtemp = strtemp.decode('gb2312','ignore')
        strtemp = strtemp.encode('utf-8', 'ignore')
        strtemp = strtemp.strip();  
        return strtemp       
  
    def get_city(self, cr, uid, ids, context, strtemp):
        obj_country_state= self.pool.get('res.country.state')
        strleftaddr = strtemp
        strprovince = ""
        strcity = ""
        #默认一个省，不能是空，否则报错
        state_id = self.pool.get('res.country.state').search(cr, uid, [("name",'=','广东省')],context=context)[0]
        #company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳市牧泰莱电路%')],context=context)[0]
        #isfind = False
        if(strleftaddr.decode('utf-8').find('深圳') > -1):
            strprovince = '广东省'
            strcity = '深圳市'
            #state_id = 67
            return (strprovince,strcity,state_id)
        state_ids =  obj_country_state.search(cr, uid, [("country_id",'=',46)],context=context)
        states = obj_country_state.browse(cr, uid, state_ids, context=context)
        for state in states:           
            pos=strleftaddr.decode('utf-8').find(state.name)
            if(pos>-1):
                state_id = state.id
                pos+=len(state.name)
                strprovince = state.name
                #strleftaddr=straddress[pos:len(strleftaddr)]
                if(state.name.decode('utf-8').find('市') > -1):
                    strcity = strprovince
                    return (strprovince,strcity,state_id)
                strleftaddr=strleftaddr.decode('utf-8')[pos:len(strleftaddr)].encode('utf-8')
                break
                #isfind = True   
        pos=strleftaddr.decode('utf-8').find('市')
        if(pos>-1):
            pos+=1
            strcity = strleftaddr.decode('utf-8')[0:pos].encode('utf-8')
            #strleftaddr=strleftaddr.decode('utf-8')[pos:len(strleftaddr)].encode('utf-8') 
        #print strprovince,strcity           
        return (strprovince,strcity,state_id)

    def import_customer(self, cr, uid, ids, context,t):
        obj_partener         = self.pool.get('res.partner')
        obj_partener_contact = self.pool.get('res.partner.contact')
        obj_partener_address = self.pool.get('res.partner.address')
        obj_partener_job     = self.pool.get('res.partner.job')  
        obj_employee         = self.pool.get('hr.employee') 
        obj_users            = self.pool.get('res.users')
        
        #obj_country_state    = self.pool.get('res.country.state')  
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        ###conn.execute_query('SELECT top 60  * FROM tbcustmer ')
        conn.execute_query('SELECT   * FROM TBCustmer WHERE  (CustmerClass = ''2001'') ' ) 
        
        
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line()
            
            #===================================================================
            ####分开导入CustmerClass=2001，无需通过客户代号来区别 客户和供应商，
            # my_customer,my_supplier=None,None
            # if (  ord(col['CustmerCode'][0]) >= 48 and  ord(col['CustmerCode'][0]) <= 57 ):
            #    my_customer,my_supplier=True,False
            # else:
            #    my_customer,my_supplier=False,True
            #===================================================================
                
            my_comment=None
            if ( col['Memo']  and  not col['OtherInfo'] ):
                my_comment=col['Memo']
            if ( not col['Memo']  and  col['OtherInfo'] ):
                my_comment=col['OtherInfo']
            if ( col['Memo']  and  col['OtherInfo'] ):
                my_comment='%s   %s' % (col['Memo'], col['OtherInfo'])
                
            ##search  user_id
            user_id=None
            user_ids=obj_users.search(cr, uid, [("login",'=',col['HandlerCode'])],context=context)
            if (  user_ids  ):
                user_id=user_ids[0]
            
            
            
            
            partner_id = obj_partener.create(cr, uid, {
                'name'           :col['CustmerName'],
                'ref'            :col['CustmerCode'],
                'user_id'        :user_id,                  ###需要一务员的 user_id, 由于user暂未导入，暂时用admint 
                'website'        :col['WebCode'], 
                'customer'       :True,   
                'supplier'       :False,
                'comment'        :my_comment,
                'credit_limit'   :col['CreditAMT'],
                'date'           :col['CreateDate'], 
                'employee'       :False,
                'active'         :True,
                #'partner_weight,                          
                #'debit_limit'                             
                #'debit'                                                       
                #'partner_latitude'                        
                #'partner_longitude'                       
                #'credit'                                  
                ##'last_reconciliation_date'                        
                ##'date_localization'                                                                                                                  
                #'ean13'                                                                                                        
                ##'vat'                                                                                                                              
                                                
            })
            print partner_id,  '         ', col['CustmerName']
            
            
            if(  col['DelAddr'] ):#添加默认发货地址
                strcity,stateid=import_partner.get_city(self, cr, uid, ids, context, col['RegistAddr'])[1:3]
                address_id = obj_partener_address.create(cr, uid, {
                        'partner_id'  : partner_id,
                        'name'        : col['LinkMan'],        
                        'phone'       : col['LinkTel'],        
                        'mobile'      : col['LinkMobil'],                       
                        'email'       : col['EMailCode'],     
                        'fax'         : col['FaxCode'],         
                        'title'       : '',
                        'type'        : 'delivery',                 
                        'street'      : col['DelAddr'],             
                        'street2'     : col['RegistAddr'],            
                        'zip'         : col['ZipCode'],            
                        'city'        : strcity,
                        'state_id'    :stateid, 
                        'country_id'  : '46'
                })  
            #================================添加联系人
            conn1 = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])     
            conn1.execute_query('SELECT  * FROM TCCustmerLinkman WHERE CustmerCode=%s order by isdefault  desc', col['CustmerCode'] )
            default_address_id=-1;
            for row1 in conn1:
                rank=Mssql_read_col.Mssql_read_col(row1).read_line()                
                strfunction = '采购员'
                if(  rank['DepartmentName']  ):
                    strfunction = rank['DepartmentName']  
                    
                strsex = 5      
                if (  rank['Sex'] ):
                    if(  rank['Sex'].find('女')>=0   ):
                        strsex = 3  
                    
                if (  rank['LinkmanName'] ): 
                    if(  rank['LinkmanName'].find('女士')>=0  ):
                        strsex = 3                     
                    
                if ( rank['LinkmanName'] ):
                    if(  rank['LinkmanName'].find('小姐')>=0  ):
                        strsex = 4
                          
                contact_id = obj_partener_contact.create(cr, uid, {
                        'partner_id' : partner_id,
                        'name'       : rank['LinkmanName'],
                        'phone'      : rank['LinkTel'],
                        'birthdate'  : rank['Birthday'],
                        'title'      : strsex,                #5先生 3女士  
                        'comment'    : rank['Memo'],
                        'website'    : col['WebCode'],        ###col not rank               
                        'mobile'     : rank['LinkMobil'],
                    })
                strdefault='other'
                if(  rank['IsDefault']  ): #如果是默认地址,地址必须存在
                    strdefault='default'
                    if(   len(rank['SendAddr']) == 0    ):# < 2): #为空时度为1
                        rank['SendAddr']=col['RegistAddr']

                if(  rank['SendAddr']  ): #如果地址为空，则不添加地址
                    strcity=''
                    strcity,stateid=import_partner.get_city(self, cr, uid, ids, context,rank['SendAddr'])[1:3]
                    address_id = obj_partener_address.create(cr, uid, {
                            'partner_id'   : partner_id,
                            'name'         : rank['LinkmanName'],
                            'phone'        : rank['LinkTel'],
                            'mobile'       : rank['LinkMobil'],                        
                            'email'        : rank['EmailCode'],
                            'fax'          : rank['FaxCode'],
                            'title'        : '',
                            'type'         : strdefault, #default,contact，invoice，delivery，other
                            'city'         : strcity,
                            'street'       : rank['SendAddr'],
                            'street2'      : col['DelAddr'], #第二地址全选为送货地址
                            'zip'          : '',
                            'city'         : strcity,
                            'state_id'     : stateid, 
                            'country_id'   : '46'
                        })  
                if( rank['IsDefault'] ):
                    default_address_id=address_id;   
                #所有联系人默认都往默认地址中增加   
                if(default_address_id>=0):
                    obj_partener_job.create(cr, uid, {
                            'address_id': default_address_id,
                            'contact_id': contact_id,
                            'email'     : rank['EmailCode'],  
                            'function'  : strfunction,
                            'phone'     : rank['LinkTel'],   
                            'other'     : rank['Memo'],                         
                            'state'     : 'current'
                        })            
                ##print "ID=%d, Name=%s" % (row1['id'], rank['LinkmanName'])
                #print "ID=%d, Name=%s" % (row1['id'], rank['LinkMobil'])
                #print "ID=%d, Name=%s" % (row1['id'], rank['LinkTel']) 
            conn1.close()          
            default_address_id=-1;
        conn.close()   
        

            
    def import_supplier(self, cr, uid, ids, context,t):
        obj_partener          = self.pool.get('res.partner')
        obj_partener_contact  = self.pool.get('res.partner.contact')
        obj_partener_address  = self.pool.get('res.partner.address')
        obj_partener_job      = self.pool.get('res.partner.job')    
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT  * FROM TBCustmer\
                            WHERE  (CustmerClass = \'2002\') AND (CustmerCode >= \'G001\')\
                            AND (CustmerCode < \'G021\')')  
                       
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line()
            
            my_comment=None
            if ( col['Memo']  and  not col['OtherInfo'] ):
                my_comment=col['Memo']
            if ( not col['Memo']  and  col['OtherInfo'] ):
                my_comment=col['OtherInfo']
            if ( col['Memo']  and  col['OtherInfo'] ):
                my_comment='%s   %s' % (col['Memo'], col['OtherInfo'])
                
            print col['CustmerCode'] ,'======'
            
            
            
            partner_id = obj_partener.create(cr, uid, {
                'name'         : col['CustmerName'],
                'ref'          : col['CustmerCode'],#此字段暂存系统客户代号
                'user_id'      : uid,
                'customer'     :False,   
                'supplier'     :True,
                ##'ean13'        : col['CustmerCode1'], 
                'website'      : col['WebCode'],    
                'comment'      : my_comment,
                'employee'     :False,
                'active'       :True, 
                'date'         :col['CreateDate'], 
                ##'credit_limit'   :col['CreditAMT'],
             })
            
   
            
            strcity,stateid=import_partner.get_city(self, cr, uid, ids, context,col['RegistAddr'])[1:3]
            address_id = obj_partener_address.create(cr, uid, {
                'partner_id'     : partner_id,
                'name'           : col['LinkMan'],
                'phone'          : col['LinkTel'],
                'mobile'         : col['LinkMobil'],                        
                'email'          : col['EMailCode'],
                'fax'            : col['FaxCode'],
                'title'          : '',
                'type'           : 'default', #default,contact，invoice，delivery，other
                'street'         : col['RegistAddr'],
                'street2'        : col['DelAddr'], 
                'zip'            : col['ZipCode'],
                'city'           : strcity,
                'state_id'       :stateid, 
                'country_id'     : '46'
            })  
            strfunction = '业务员'
            strsex = 5         
            if(  col['LinkMan'].find('女')>=0 or col['LinkMan'].find('女士')>=0  ):
                strsex = 3   
            if(col['LinkMan'].find('小姐')>=0):
                strsex = 4   
            contact_id = obj_partener_contact.create(cr, uid, {
                    'partner_id'    : partner_id,
                    'name'          : col['LinkMan'],
                    'phone'         : col['LinkTel'],
                    'title'         : strsex,          #5先生 3女士  
                    #'comment'      : strtemp11,
                    'website'       : col['WebCode'],                       
                    'mobile'        : col['LinkMobil']
            })

            obj_partener_job.create(cr, uid, {
                  'address_id'  : address_id,
                  'contact_id'  : contact_id,
                  'email'       : col['EMailCode'],
                  'function'    : strfunction,
                  'phone'       : col['LinkTel'],   
                  #'other': strtemp11,                         
                  'state'       : 'current'
            })                   
        conn.close()      

    def import_department(self, cr, uid, ids, context,t,departid,parentid):
        obj_dept = self.pool.get('hr.department')
        ## company judge
        company_id = None
        if (t['database'] == 'mtltest' or t['database'] == 'mtlerp-running'): 
            company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%牧泰莱电路%')],context=context)[0]
        else:
            pass
        
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT top 500  * FROM TBDepartment where ParentId = \'%d\'',departid)
        #=======================================================================
        # departids_dict = {}
        # if (departid==-1):
        #    mstrtemp1=''
        #=======================================================================
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line()
             
            print parentid,col['DepartmentName'],col['ParentId']
            ##dpt creat
            dpt_code_search=obj_dept.search(cr, uid, [("dpt_code",'=',col['DepartmentCode'])],context=context)
            if (not dpt_code_search):
                departmentid = obj_dept.create(cr, uid, {
                    'name'            :col['DepartmentName'],
                    'note'            :col['Address'],
                    'parent_id'       :parentid,
                    'company_id'      :company_id, 
                    'dpt_code'        :col['DepartmentCode'],     
                    'manager_id'      :False
                 })            
                import_partner.import_department(self, cr, uid, ids, context,t,col['id'],departmentid)
            else:
                print 
                continue
        conn.close()      
              
         
    def import_employee(self, cr, uid, ids, context,t):   
        obj_empl            =self.pool.get('hr.employee')
        obj_resource        =self.pool.get('resource.resource')
        obj_marital_status  =self.pool.get('hr.employee.marital.status')
        obj_hr_job          =self.pool.get('hr.job')
        obj_partner_address =self.pool.get('res.partner.address')
        obj_department      =self.pool.get('hr.department')
        obj_users           =self.pool.get('res.users')
        obj_company_users_rel=self.pool.get('res.company.users.rel')
        
        # company judge
        
        company_id = None
        if (t['database'] == 'mtltest' or t['database'] == 'mtlerp-running'): 
            company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳工厂%')],context=context)[0]
        else:
            ##mtlcs   长沙牧泰莱
            pass

        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT   *  FROM TBEmployee   order  by  id  ')
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line()
            if (not col['EmployeeName']):
                continue   
            print col['EmployeeName'], 'begin to insert'
            
            #===================================================================
            # ##company_id judge
            # company_id = None
            # if (col['EmpCompany'] == 0):
            #    company_id = 1
            # elif (col['EmpCompany'] == 1):
            #    company_id = 2
            # else:
            #    pass
            #===================================================================
        
            ## gender  judge   
            gender= col['Sex'] 
            if ( gender=='男' ):
                gender='male'
            elif( gender=='女' ) :
                gender='female'
            else:
                gender=None
                
            ##marital judge
            marital          = col['MarriageState']
            
            if (marital=='已婚' ):
                marital=obj_marital_status.search(cr, uid, [("name",'=','Married')],context=context)[0]
            elif(marital=='未婚'):
                marital=obj_marital_status.search(cr, uid, [("name",'=','Single')],context=context)[0]
            elif(marital=='离婚'):
                marital=obj_marital_status.search(cr, uid, [("name",'=','Divorced')],context=context)[0]
            else:
                marital=obj_marital_status.search(cr, uid, [("name",'=','Single')],context=context)[0]
                
            ##address_home  search or creat
            address_home_id = None
            if ( col['DwellingPlace'] ):
                addres_search=obj_partner_address.search(cr, uid, [("street",'=',col['DwellingPlace'])],context=context)
                if ( len(addres_search) == 0  ):     
                    address_home_id=obj_partner_address.create(cr, uid, {
                        'name'            :col['EmployeeName'],
                        'street'          :col['DwellingPlace'],
                        'phone'           :col['HomeTel']
                    })
                else:
                    address_home_id=addres_search[0]
            
            ##job search or creat
            job_id = None
            if (  col['WorkerType']  ):
                job_search=obj_hr_job.search(cr, uid, [("name",'=',col['WorkerType'])],context=context)
                if (not job_search ):
                    job_id=obj_hr_job.create(cr, uid, {
                        'name'        :col['WorkerType'],
                        'company_id'  :company_id,
                    })                 
                else:
                    job_id=job_search[0]
                    
            ##department search 
            department_id = None
            department_search=obj_department.search(cr, uid, [("dpt_code",'=',col['DepartmentCode'] )],context=context)
            if (len(department_search) > 0 ):
                department_id=department_search[0]
                
            ##judge login name ,  shenzhen ==>employee_code  changsha ==> employee_code + 50000
            login=col['EmployeeCode']
            if ( col['EmpCompany'] == 1 ):
                login=str(int(login) + 50000)
            password ='MTLem' + login     
            
            #creat user  'user_id'
            user_id=obj_users.create(cr,uid,{
                    'name'               :col['EmployeeName'],
                    'login'              :login,
                    'password'           :password,
                    ##'new_password'       :None,
                    'signature'          :col['EmployeeName'],
                    'company_id'         :company_id,
                    'email'              :col['EMailCode'],   ## 
                    'company_ids'        :None,               ##
                    # action_id          :    custom defin menu  
                    # active   
                    # menu_id
                    # menu_tips          
                    'address_id'           :address_home_id, 
                    'context_department_id':department_id,
                    # groups_id

             })
            
            ##resource ,   employee name creat
            resource_id = obj_resource.create(cr, uid, {
                'name'             : col['EmployeeName'],
                'user_id'          :user_id,
                'resource_type'    :'user',
                'time_efficiency'  :1,
                'company_id'       :company_id,
                'active'           :True,
                #'code': 
                #'time_efficiency' : 
                #'calendar_id' :
            }) 
            
            
            ##employee creat
            obj_empl.create(cr, uid, {
                'department_id'    :department_id,   
                'company_id'       :company_id,  
                'gender'           :gender,
                'resource_id'      :resource_id, 
                'manager_id'       :False,
                'mobile_phone'     :col['MobileTelephone'], 
                'identification_id':col['IDCardCode'],
                'marital'          :marital,
                'birthday'         :col['Birthday'],
                'otherid'          :col['EmployeeCode'],    ##此字段用于存放 员工工号  
                'place_of_birth'   :col['BirthPlace'],
                'job_id'           :job_id,
                'work_email'       :col['EMailCode'],
                'address_home_id'  :address_home_id,
                'notes'            :col['Memo'],  
                'work_phone'       :col['Telephone'],
                 ## 'state'       
                ################################char
                # sinid
                # ssnid
                # vehicle
                # work_location
                # manager
                ######################################date
                # evaluation_date
                # medic_exam 
                ######################################float
                # advantages_gross
                # advantages_net
                # basic
                # gross
                # net
                # children
                # vehicle_distance
                ###########################################many2many
                # category_ids
                #############################many2one
                # address_id    Working Address
                # analytic_account    Analytic Account
                # bank_account_id    Bank Account Number
                # coach_id    Coach
                # contract_id    Contract
                # country_id    Nationality
                # employee_account    Employee Account
                # evaluation_plan_id    Evaluation Plan
                # journal_id    Analytic Journal
                # marital    Marital Status
                # parent_id    Manager
                # partner_id    unknown
                # passport_id    Passport No
                # product_id    Product
                # property_bank_account    Bank Account
                # salary_account    Salary Account     
                ###################################################one2many
                # child_ids    Subordinates
                # contract_ids    Contracts
                # line_ids    Salary Structure
                # slip_ids    Payslips
                #===============================================================================
            })  
            print col['EmployeeName'], 'end to insert'           
        conn.close()  
    def import_groups(self, cr, uid, ids, context,t):
        obj_groups=self.pool.get('res.groups')
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT  *  FROM   TSRole   order  by  id')
        for row in conn:
            col={}
            col['name']   =import_partner.gb2312ToUtf8(self,row['RoleName'])
            col['comment'] =import_partner.gb2312ToUtf8(self,row['RoleCode'])
            print col['name'],col['comment']
            ##groups creat
            groups_search=obj_groups.search(cr, uid, [("name",'=',col['name'] )],context=context)
            if (not groups_search):
                obj_groups.create(cr, uid, {
                    'name'   :col['name'],
                    'comment' :col['comment'],                               
                })
            else:
                ##if exists name, update  data
                obj_groups.write(cr, uid, groups_search[0], {
                            'comment':col['comment']}
                )
        conn.close() 
    
    def import_user(self, cr, uid, ids, context,t):
        obj_users           =self.pool.get('res.users')
        obj_groups          =self.pool.get('res.groups')
        obj_employee        =self.pool.get('hr.employee')
        #obj_resource        =self.pool.get('resource.resource')
        ## company judge
        company_id = None
        if (t['database'] == 'mtltest' or t['database'] == 'mtlerp-running'): 
            company_id=company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳工厂%')],context=context)[0]
        else:
            pass
        
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT  top 1000 *  FROM   TSUser   order  by  id')  
        for row in conn:
            col={} 
            col['UserCode']       =import_partner.gb2312ToUtf8(self,row['UserCode'])
            col['UserName']       =import_partner.gb2312ToUtf8(self,row['UserName'])
            col['RoleCode']       =import_partner.gb2312ToUtf8(self,row['RoleCode'])
            col['EmployeeCode']   =import_partner.gb2312ToUtf8(self,row['EmployeeCode'])
            col['Password']       =import_partner.gb2312ToUtf8(self,row['Password'])
            col['name']           =None
                      
            ##search name, name cant be None
            emp_seacrh=obj_employee.search(cr, uid, [("otherid",'=',col['EmployeeCode']) ],context=context)
            if (emp_seacrh):
                oo=obj_employee.browse(cr, uid, emp_seacrh[0])
                col['name']= oo.resource_id.name
            else:
                col['name']='NoName'
            ##search login,login must unique,then creat
            user_search=obj_users.search(cr, uid, [("login",'=',col['UserName']) ],context=context)
            if (not user_search):
                use_id=obj_users.create(cr, uid, {
                    'name'               :col['name'],  
                    'login'              :col['UserName'], 
                    'password'           :888888, 
                    'new_password'       :888888, 
                    'signature'          :col['name'],    
                    'company_id'         :company_id,
                    ##'MeMo'               :col['RoleCode'],                                                             
                })
                ##use_id relating to groups  search 
                group_ids=obj_groups.search(cr, uid, [("comment", '=',  col['RoleCode'])],context=context)
                if (group_ids):
                    print use_id,group_ids[0]
                    cr.execute('INSERT INTO  res_groups_users_rel (uid,gid)  VALUES (%s,%s )',(use_id, group_ids[0])  )
            else:
                pass ##maybe write a update obj_users 
        conn.close()  
        
    def  import_product(self, cr, uid, ids, context,t):
        obj_product       =self.pool.get('product.product')
        #obj_packaging     =self.pool.get('product.packaging')
        obj_uom           =self.pool.get('product.uom')
        ##obj_uom_categ     =self.pool.get('product.uom.categ')
        obj_category      =self.pool.get('product.category')
        
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])            
        conn.execute_query('SELECT  top 500 *  FROM   TBGoods')  # order  by  id
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line()
            
            
            
            ##search uom  goodsunit,if not creat
            col['uom_id']=None
            uom_ids=obj_uom.search(cr, uid, [("name",'=',col['GoodsUnit']) ],context=context)
            if (uom_ids):
                col['uom_id']=uom_ids[0]
            else:
                col['uom_id']=obj_uom.create(cr, uid,{                              
                    'name'                     : col['GoodsUnit'],  ## fields.char('Name', size=64, required=True, translate=True),
                    'category_id'              : 1,  ## fields.many2one('product.uom.categ', 'UoM Category', required=True, ondelete='cascade',
                    'factor'                   : 1.0,  ## fields.float('Ratio', required=True,digits=(12, 12),
                    #'factor_inv'               : None,  ## fields.function(_factor_inv, digits_compute=dp.get_precision('Product UoM'),
                    'rounding'                 : 0.01,  ## fields.float('Rounding Precision', digits_compute=dp.get_precision('Product UoM'), required=True,
                    'active'                   : True,  ## fields.boolean('Active', help="By unchecking the active field you can disable a unit of measure without deleting it."),
                    'uom_type'                 : 'reference',  ## fields.selection([('bigger','reference','smaller'),
                })
            print col['uom_id'],
                
            ##search categ_id  with  col['StoreHouseCode']
            col['categ_id']=None
            categ_dict={
                'B':       'material'        ,         
                'C':       'consumable'        ,   
                'D':       'other'  ,    
                'E':       'other'  ,        
                'F':       'consumable'       ,
                'G':       'auxiliary'    ,            
                'A':       'material'          ,
                'H':       'office'          ,
                'other':   'other'  ,
            }
            search_name=None
            if ( col['StoreHouseCode'] ):
                search_name=categ_dict[  col['StoreHouseCode']  ]
            else:
                search_name=categ_dict['other']
            col['categ_id']=obj_category.search(cr, uid, [ ("name",'=', search_name) ],context=context)[0]
             
            
            if obj_product.search(cr, uid, [ ("default_code",'=', col['GoodsCode']) ],context=context)  :
                continue
            product_id=obj_product.create(cr, uid,{
#                'qty_available'      :None,
#                'virtual_available'  :None,
#                'incoming_qty'       :None,              ##function
#                'outgoing_qty'       :None,              ##function        
                'price'              :col['GoodsPrice'],
#                'lst_price'          :None,
#                'code'               :None,
#                'partner_ref'        :None,
                'default_code'       :col['GoodsCode'],  ##引用 
#                'active'             :None,
                'variants'           :col['GoodsSpec'],  ##型号
                ##'product_tmpl_id'    :None,            ##name has defined 
#                'ean13'              :None,
                ##'packaging'          :None,            ##one2many  product_packaging
#                'price_extra'        :None,
#                'price_margin'       :None,
#                'pricelist_id'       :None,
#                'name_template'      :None,
                
                ##product_template
                'name'               :col['GoodsName'] ,
#                'product_manager'    :None,
#                'description'        :None,
#                'description_purchase':None,
#                'description_sale'   :None,
                'type'               :'product',        ##[('product','Stockable Product'),('consu', 'Consumable'),('service','Service')]
                'supply_method'      :'buy',       ## [('produce','Produce'),('buy','Buy')]
#                'sale_delay'         :None,
#                'produce_delay'      :None,
                'procure_method'     :'make_to_stock',  ##[('make_to_stock','Make to Stock'),('make_to_order','Make to Order')]
#                'rental'             :None,
                'categ_id'           :col['categ_id'],
#                'list_price'         :None,
#                'standard_price'     :None,
#                'volume'             :None,
#                'weight'             :None,
#                'weight_net'         :None,
                'cost_method'        :'standard',  ##[('standard','Standard Price'), ('average','Average Price')]
#                'warranty'           :None,
                'sale_ok'            :False,                 
                'purchase_ok'        :True,             
#                'state'              :None,
                'uom_id'             :col['uom_id'],
                'uom_po_id'          :col['uom_id'],
                'uos_id'             :col['uom_id'],
#                'uos_coeff'          :None,
                ###'mes_type'           :None,   ##(('fixed', 'Fixed'), ('variable', 'Variable'))
#                'seller_delay'       :None,
#                'seller_qty'         :None,
#                'seller_id'          :None,
#                'seller_ids'         :None,
#                'loc_rack'           :None,
#                'loc_row'            :None,
#                'loc_case'           :None,
#                'company_id'         :None,             
            })
            
            #===================================================================
            # packaging_id=obj_packaging.creatcreate(cr, uid,{
            #    'sequence'              : None,        
            #    'name'                  : None,        
            #    'qty'                   : None,        
            #    'ul'                    : None,        
            #    'ul_qty'                : None,        
            #    'rows'                  : None,        
            #    'product_id'            : product_id,        
            #    'ean'                   : None,        
            #    'code'                  : None,        
            #    'weight'                : None,        
            #    'weight_ul'             : None,        
            #    'height'                : col['GoodsHeight'],        
            #    'width'                 : col['GoodsWidth'],        
            #    'length'                : col['GoodsLength'],                                                                                                          
            # })
            #===================================================================
            
            print   product_id,  col['GoodsName'],  cr,  uid  
            
        conn.close() 
    def import_pcb(self, cr, uid, ids, context,t):
        obj_pcb           =self.pool.get('product.product.pcb')
        obj_category      =self.pool.get('product.category')
        obj_uom           =self.pool.get('product.uom')
        obj_custmer       =self.pool.get('res.partner')
        
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],database=t['database'])  
        select_sql="select top 10 a.* from TBProduction a right join (select max(id) id from TBProduction group by goodscode) b on b.id = a.id where a.id is not null and a.goodscode <> '' "
        conn.execute_query(select_sql)  
        
        categ_id=obj_category.search(cr, uid, [ ("name",'=', 'pcb') ],context=context)[0]
        for row in conn:
            col=Mssql_read_col.Mssql_read_col(row).read_line(True)
                        
            col['uom_id']=None
            uom_ids=obj_uom.search(cr, uid, [("name",'=',col['unit']) ],context=context)
            if (uom_ids):
                col['uom_id']=uom_ids[0]
            else:
                col['uom_id']=obj_uom.create(cr, uid,{                              
                    'name'                     : col['unit'],  ## fields.char('Name', size=64, required=True, translate=True),
                    'category_id'              : 1,  ## fields.many2one('product.uom.categ', 'UoM Category', required=True, ondelete='cascade',
                    'factor'                   : 1.0,  ## fields.float('Ratio', required=True,digits=(12, 12),
                    #'factor_inv'               : None,  ## fields.function(_factor_inv, digits_compute=dp.get_precision('Product UoM'),
                    'rounding'                 : 0.01,  ## fields.float('Rounding Precision', digits_compute=dp.get_precision('Product UoM'), required=True,
                    'active'                   : True,  ## fields.boolean('Active', help="By unchecking the active field you can disable a unit of measure without deleting it."),
                    'uom_type'                 : 'reference',  ## fields.selection([('bigger','reference','smaller'),
                })          
            
            if ( obj_pcb.search(cr, uid, [("goodscode",'=',col['goodscode']) ],context=context)  ):
                print 'the coodscode %s  has exists, next '  %   col['goodscode']
                continue   ##mabye to updata 
            
            custmer_id=None
            custmer_ids=obj_custmer.search(cr, uid, [("name",'=',col['custmername']) ],context=context)
            if ( custmer_ids ):
                custmer_id=custmer_ids[0]
                
            pcb_id=obj_pcb.create(cr, uid,{
                'price'              :col['price'],
                'default_code'       :col['goodsname'],  ##引用 
                'variants'           :col['goodsspec'],  ##型号
                'name'               :col['goodscode'],
                'type'               :'product',        ##[('product','Stockable Product'),('consu', 'Consumable'),('service','Service')]
                'supply_method'      :'buy',       ## [('produce','Produce'),('buy','Buy')]
                'procure_method'     :'make_to_stock',  ##[('make_to_stock','Make to Stock'),('make_to_order','Make to Order')]
                'categ_id'           :categ_id,
                'cost_method'        :'standard',  ##[('standard','Standard Price'), ('average','Average Price')]
                'sale_ok'            :True,                 
                'purchase_ok'        :False,             
                'uom_id'             :col['uom_id'],
                'uom_po_id'          :col['uom_id'],
                'uos_id'             :col['uom_id'],
                'company_id'         :1,  
                'goodscode'          :col['goodscode'], 
                
                'amt'                   :col['amt'],  
                'aperturetype'          :col['aperturetype'        ],
                'baseboard'             :col['baseboard'           ],
                'billcheckercode'       :col['billcheckercode'     ],
                'billcode'              :col['billcode'            ],
                'billdate'              :col['billdate'            ],
                'billmakedate'          :col['billmakedate'        ],
                'billstate'             :col['billstate'           ],
                'billtypecode'          :col['billtypecode'        ],
                'blend'                 :col['blend'               ],
                'boardorigin'           :col['boardorigin'         ],
                'ccolor'                :col['ccolor'              ],
                'coatrequest'           :col['coatrequest'         ],
                'colortypec'            :col['colortypec'          ],
                'colortypef'            :col['colortypef'          ],
                'computername'          :col['computername'        ],
                'consigneename'         :col['consigneename'       ],
                'ctype'                 :col['ctype'               ],
                'currencycode'          :col['currencycode'        ],
                'custmercode'           :col['custmercode'         ],
                'custmerfaxcode'        :col['custmerfaxcode'      ],
                'custmergoodscode'      :col['custmergoodscode'    ],
                'custmerhandler'        :col['custmerhandler'      ],
                'custmername'           :custmer_id ,
                'custmerregistaddr'     :col['custmerregistaddr'   ],
                'custmertel'            :col['custmertel'          ],
                'custmertname'          :col['custmertname'        ],
                'cutperimeter'          :col['cutperimeter'        ],
                'dealqty'               :col['dealqty'             ],
                'drillholecount'        :col['drillholecount'      ],
                'ecmholeqty'            :col['ecmholeqty'          ],
                'ecndealcode'           :col['ecndealcode'         ],
                ## 'enghandler'            :col['enghandler'          ],
                'fcolor'                :col['fcolor'              ],
                'ficopper'              :col['ficopper'            ],
                'filenum'               :col['filenum'             ],
                'filesize'              :col['filesize'            ],
                'focopper'              :col['focopper'            ],
                'formernum'             :col['formernum'           ],
                'freeqty'               :col['freeqty'             ],
                'ftype'                 :col['ftype'               ],
                'gbillcode'             :col['gbillcode'           ],
                'goodsheight'           :col['goodsheight'         ],
                'goodslength'           :col['goodslength'         ],
                'goodsmaterial'         :col['goodsmaterial'       ],
                'goodsplength'          :col['goodsplength'        ],
                'goodspwidth'           :col['goodspwidth'         ],
                'goodsqty'              :col['goodsqty'            ],
                'goodsslength'          :col['goodsslength'        ],
                'goodssname'            :col['goodssname'          ],
                'goodsswidth'           :col['goodsswidth'         ],
                'goodswidth'            :col['goodswidth'          ],
                'halfwholedepth'        :col['halfwholedepth'      ],
                'halfwholetance'        :col['halfwholetance'      ],
                'handledeptcode'        :col['handledeptcode'      ],
                'handlercode'           :col['handlercode'         ],
                'handlername'           :col['handlername'         ],
                'holelayer'             :col['holelayer'           ],
                'imagecode'             :col['imagecode'           ],
                'innercopper'           :col['innercopper'         ],
                'innerversionno'        :col['innerversionno'      ],
                'isbasicprice'          :col['isbasicprice'        ],
                'isdealecn'             :col['isdealecn'           ],
                'isdealprice'           :col['isdealprice'         ],
                'isecn'                 :col['isecn'               ],
                'iset'                  :col['iset'                ],
                'isgangwang'            :col['isgangwang'          ],
                'isgerber'              :col['isgerber'            ],
                'ismemoprompt'          :col['ismemoprompt'        ],
                'isnewgoods'            :col['isnewgoods'          ],
                'ispadallow'            :col['ispadallow'          ],
                'isprice'               :col['isprice'             ],
                'isresicontrol'         :col['isresicontrol'       ],
                'isresitest'            :col['isresitest'          ],
                'issmdallow'            :col['issmdallow'          ],
                'issuregerber'          :col['issuregerber'        ],
                'isturn'                :col['isturn'              ],
                'isviablock'            :col['isviablock'          ],
                'lastdealdate'          :col['lastdealdate'        ],
                'layercount'            :col['layercount'          ],
                'layerseqtype'          :col['layerseqtype'        ],
                'lightbqyt'             :col['lightbqyt'           ],
                'longspell'             :col['longspell'           ],
                'manufacturer'          :col['manufacturer'        ],
                'mgoodscode'            :col['mgoodscode'          ],
                'minaperture'           :col['minaperture'         ],
                'minbetween'            :col['minbetween'          ],
                'minlinewid'            :col['minlinewid'          ],
                'minsegregate'          :col['minsegregate'        ],
                'mtype'                 :col['mtype'               ],
                'needtosolve'           :col['needtosolve'         ],
                'notchqty'              :col['notchqty'            ],
                'oldbillstate'          :col['oldbillstate'        ],
                'oldpdmstate'           :col['oldpdmstate'         ],
                'ordertypename'         :col['ordertypename'       ],
                'orificetype'           :col['orificetype'         ],
                'otheramt'              :col['otheramt'            ],
                'otherfee'              :col['otherfee'            ],
                'otherholeqty'          :col['otherholeqty'        ],
                'otherrequest'          :col['otherrequest'        ],
                'otherrequest1'         :col['otherrequest1'       ],
                'otherrequest2'         :col['otherrequest2'       ],
                'otherrequest3'         :col['otherrequest3'       ],
                'outercopper'           :col['outercopper'         ],
                'outerversionno'        :col['outerversionno'      ],
                'packingqty'            :col['packingqty'          ],
                'packingtype'           :col['packingtype'         ],
                'pdmcount'              :col['pdmcount'            ],
                'pdmstate'              :col['pdmstate'            ],
                'printremark'           :col['printremark'         ],
                'ps'                    :col['ps'                  ],
                'pu'                    :col['pu'                  ],
                'qty'                   :col['qty'                 ],
                'quotememo'             :col['quotememo'           ],
                'rejectallow'           :col['rejectallow'         ],
                'rejectallow1'          :col['rejectallow1'        ],
                'reportrequest'         :col['reportrequest'       ],
                'requestno'             :col['requestno'           ],
                'resilayer'             :col['resilayer'           ],
                'rltvbillcode'          :col['rltvbillcode'        ],
                'sdoamt'                :col['sdoamt'              ],
                'sfromtype'             :col['sfromtype'           ],
                'sgoldfingerangle'      :col['sgoldfingerangle'    ],
                'sgoldfingercopper'     :col['sgoldfingercopper'   ],
                'sgoldfingercount'      :col['sgoldfingercount'    ],
                'shaperulertype'        :col['shaperulertype'      ],
                'shapetype'             :col['shapetype'           ],
                'shipdate'              :col['shipdate'            ],
                'shipday'               :col['shipday'             ],
                'shiptype'              :col['shiptype'            ],
                'softwarever'           :col['softwarever'         ],
                'sphotoamt'             :col['sphotoamt'           ],
                'sphotonum'             :col['sphotonum'           ],
                'sphotoprice'           :col['sphotoprice'         ],
                'squcmprice'            :col['squcmprice'          ],
                'su'                    :col['su'                  ],
                'submemo'               :col['submemo'             ],
                'tagrequest'            :col['tagrequest'          ],
                'technicmodelcode'      :col['technicmodelcode'    ],
                'tempoutqty'            :col['tempoutqty'          ],
                'testequiptype'         :col['testequiptype'       ],
                'testqty'               :col['testqty'             ],
                'teststandard'          :col['teststandard'        ],
                'tolerance'             :col['tolerance'           ],
                'unit'                  :col['unit'                ],
                'unitprice'             :col['unitprice'           ],
                'updategoodscode'       :col['updategoodscode'     ],
                'vcutdegree'            :col['vcutdegree'          ],
                'viaftype'              :col['viaftype'            ],
                'widthspell'            :col['widthspell'          ],
                'xsu'                   :col['xsu'                 ],
                'ysu'                   :col['ysu'                 ],           
            })   
            
            print   pcb_id,  col['goodscode']      
        conn.close()
        
    def import_country_state(self, cr, uid, ids, context,t): 
        obj_state = self.pool.get('res.country.state')
        
        data_file='E:/tool/workspace/openerp-server-603/bin/addons/001_mtl_import_partner/country_state.txt'
        fh=file(data_file, 'r')
        for line in fh:
            code,name=line.split()
            
            if (code[2:4] == '00' and  code[4:6] == '00' ):
                
                ids=obj_state.search(cr, uid, [("name",'=',name ) ],context=context)
                if (not ids):
                    print name
                    obj_state.create(cr, uid,{              
                        'code'       :  code,
                        'country_id' :  46,
                        'name'       :  name,                 
                    })
                    
        fh.close()
          
    def action_draft(self, cr, uid, ids, context=None):
        
        if context is None:
            context = {}
        qjds = self.read(cr, uid, ids,['server','user','password','database','type','sqlreqery'], context=context)   
        #unlink_ids = []
        for t in qjds:       
            if(t['type'] == 'customer'):
                import_partner.import_customer(self, cr, uid, ids,context,t)
            elif(t['type'] == 'supplier'):
                import_partner.import_supplier(self, cr, uid, ids,context,t)
            elif(t['type'] == 'department'):
                import_partner.import_department(self, cr, uid, ids, context,t,-1,False)               
            elif(t['type'] == 'employee'):
                import_partner.import_employee(self, cr, uid, ids,context,t)
            elif(t['type'] == 'group'):
                import_partner.import_groups(self, cr, uid, ids,context,t)
            elif(t['type'] == 'user'):
                import_partner.import_user(self, cr, uid, ids,context,t)
            elif(t['type'] == 'production'):
                import_partner.import_product(self, cr, uid, ids,context,t)   
            elif(t['type'] == 'pcb'):
                import_partner.import_pcb(self, cr, uid, ids,context,t)  
            elif(t['type'] == 'country_state'):
                import_partner.import_country_state(self, cr, uid, ids,context,t) 
                ##country_state                  
                                   
        return True  
   
   
import_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:  product_product_pcb
