#!usr/bin/env python
# -*- coding: utf-8 -*-
from osv import fields,osv
import datetime
import pymssql
import sys
from tools.translate import _
reload(sys)  
sys.setdefaultencoding('utf8')

import urllib


class employee(osv.osv):
  
    _name='employee'
    _description="employee information"
    _rec_name='employeename'
    
    
    def _get_deptlist(self,cr,uid,context=None):
        dept=self.pool.get('res.department')
        ids=dept.search(cr,uid,[],context=context)
        deptlist=dept.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in deptlist]
 
    def _get_ethniclist(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','ethnic')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def _get_workertypelist(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','workertype')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    #def _get_perfessionlist(self,cr,uid,context=None):
    #    my=self.pool.get('parameter')
    #    ids=my.search(cr,uid,[('type','=','perfession')],context=context) 
    #    ethniclist=my.read(cr,uid,ids,['name'],context)
    #    return [(r['name'],r['name']) for r in ethniclist]
    
    def _get_technicaltitlelist(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','technicaltitle')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def _get_sexlist(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','sex')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def _get_marriage_state_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','marriage')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def _get_diploma_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','diploma')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def politics_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','politic')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist]
    
    def healthy_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','healthy')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist] 
 
    def employee_type_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','employee_type')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist] 
    
    
    def leave_type_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','leave_type')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist] 
    
    def isure_list(self,cr,uid,context=None):
        my=self.pool.get('parameter')
        ids=my.search(cr,uid,[('type','=','issure')],context=context) 
        ethniclist=my.read(cr,uid,ids,['name'],context)
        return [(r['name'],r['name']) for r in ethniclist] 
 
    _columns={
              'employeename':fields.char(u"职员姓名",size=20),
              'employeecode':fields.char(u"职员工号",size=10),
              
              'sex':fields.selection(_get_sexlist,u'性别'),
              'birth_date':fields.date(u'出生日期'),
              'marriage_state':fields.selection(_get_marriage_state_list,u'婚姻状况'),
              'ethnic':fields.selection(_get_ethniclist,u'民族'),
              'diploma':fields.selection(_get_diploma_list,u'文化程度'),
              'department':fields.selection(_get_deptlist,u'所属部门'),
              'politics':fields.selection(politics_list,u'政治面貌'),
              'healthy_state':fields.selection(healthy_list,u'健康状况'),
              'workstartdate':fields.date(u'入职日期'),
              'workertype':fields.selection(_get_workertypelist,u'职务'),
              'employee_type':fields.selection(employee_type_list,u'职员类型'),
              'cellphone':fields.char(u'手机',size=30),
              'perfession':fields.char(u'专业',size=30),
             
              'leave_date':fields.date(u'离职日期'),
              'leave_type':fields.selection(leave_type_list,u'离职类型'),
              'link_phone':fields.char(u'联系电话',size=20),
              'issocialcard':fields.selection(isure_list,u'办理社保'),
              'isoldinsurance':fields.selection(isure_list,u'养老保险'),
              'con_sta_date': fields.date(u'合同开始日期'),
              'con_end_date': fields.date(u'合同结束日期'),
              'code_name':fields.char(u'业务员代码',size=10),
              'technicaltitle':fields.selection(_get_technicaltitlelist,u'职称'),
             
              'family_addr':fields.char(u'家庭住址',size=100),
              'idcardcode':fields.char(u'身份证',size=30),
              'family_tel':fields.char(u'家庭电话',size=30),
              'email':fields.char(u'电子邮箱',size=30),
              'memo':fields.text(u'备注'),
              'birth_place':fields.char(u'出生地',size=30),
              'photo':fields.binary(u'照片'),
              'is_sale_approve':fields.boolean(u'是否资料审核员'),
              'is_saleman':fields.boolean(u'是否业务员'),
              'company':fields.selection([('szmtl',u'深圳牧泰莱'),('csmtl',u'长沙牧泰莱')],u'所属公司'),
 
              }
   
    
    def create_user(self,cr,uid,ids,context=None):
       my=self.browse(cr,uid,ids[0])
       username=my.employeecode
       print username,'username'
       password='Mtloe'+my.employeecode
       print password,'passwords'
       user=self.pool.get('res.users')
       return user.create(cr,uid,{'login':username,'name':my.employeename,'password':password,'company_id':1,})
   
    def write_to_dS(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        employeecode=my.employeecode.encode('utf-8')
        employeename=my.employeename.encode('utf-8')
        server='192.168.10.2'
        user='sa'
        password='719799'
        database='mtlerp-running'
        procname='ppoetods'
        print employeecode,'employeecode'
        print employeename,'employeename'
        print type(employeename)
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            sql='''exec ppoetods '%s','%s' ''' %(employeecode,employeename)
            print sql
            cur.execute('''exec ppoetods '%s','%s' ''' %(employeecode,employeename))
            
        except:
           raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))

        else:
            conn.commit()
            conn.close() 
            raise osv.except_osv(_(u'提示'),_(u'更新成功！'))
        
        return True
    
    
    def import_data(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('employee')
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        conn=pymssql.connect(server=server,user=user, password=passward,database=database)
        cur=conn.cursor()
        sql='''Select isnull(employeecode,''),isnull(employeename,''),isnull(Sex,''),birthdate,isnull(marry,'')
            ,'',isnull(degree,''),isnull(Department,''),'','',contractstartdate,upper(isnull(worktype,'')),''
            ,isnull(phone,''),'','','','','','',''
            ,'','','','',isnull(ID,''),'',''
            ,'','','csmtl' as company
             from srv_cslnk.[mtlcs-running].dbo.em  where Department not like'%深圳%'
            union all
            Select isnull(employeecode,''),isnull(employeename,''),isnull(Sex,''),birthdate,isnull(marry,'')
            ,'',isnull(degree,''),isnull(Department,''),'','',contractstartdate,upper(isnull(worktype,'')),''
            ,isnull(phone,''),'','','','','','',''
            ,'','','','',isnull(ID,''),'',''
            ,'','','szmtl' as company
             from srv_cslnk.[mtlcs-running].dbo.em  where Department  like'%深圳%'
            union all
            Select isnull(a.employeecode,''),isnull(a.employeename,''),isnull(Sex,''),Birthday,isnull(MarriageState,'')
            ,isnull(Ethnic,''),isnull(Diploma,''),isnull(DepartmentName,''),isnull(Politic,''),isnull(HealthyState,''),isnull(WorkStartDate,''),upper(isnull(WorkerType,'')),isnull(EmployeeTypeE,'')
            ,isnull(MobileTelephone,''),isnull(Specialty,''),WorkEndDate,isnull(b.basicdetailname,''),isnull(Telephone,''),isnull(IsSocialCard1,''),isnull(IsOldInsurance1,''),isnull(ContractDate,'')
            ,ContractOverDate,isnull(CodeName,''),isnull(TechnicalTitle,''),isnull(DwellingPlace,''),isnull(IDCardCode,''),isnull(HomeTel,''),isnull(EMailCode,'')
            ,isnull(a.Memo,''),isnull(BirthPlace,''),'szmtl' as company
             from VBEmployeeManage a left join TBBasicDetail b  on a.DimissionType=b.basicdetailcode inner join employee c on a.employeecode=c.employeecode  '''
        cur.execute(sql)
        s=cur.fetchall()
        b=[]
        for row1 in s:
            a=[]
            for i in range(len(row1)):
                if type(row1[i])==type(u'中文'):
                    a.append((''.join(map(lambda x: "%c" % ord(x), list(row1[i]))).decode('gbk')))
                else:
                    a.append(row1[i])
            b.append(a)
        for row in b:  
                info_id=obj.create(cr,uid,{                                                                                                                 
                             'employeecode':row[0],
                             'employeename':row[1],
                             'sex':row[2],
                             'birth_date':row[3],
                             'marriage_state':row[4],
                             'ethnic':row[5],
                              'diploma':row[6],
                              'department':row[7],
                              'politics':row[8],
                              'healthy_state':row[9],
                              'workstartdate':row[10],
                              'workertype':row[11],
                              'employee_type':row[12],
                              'cellphone':row[13],
                              'perfession':row[14],
                             
                              'leave_date':row[15],
                              'leave_type':row[16],
                              'link_phone':row[17],
                              'issocialcard':row[18],
                              'isoldinsurance':row[19],
                              'con_sta_date':row[20],
                              'con_end_date':row[21],
                              'code_name':row[22],
                              'technicaltitle':row[23],
                             
                              'family_addr':row[24],
                              'idcardcode':row[25],
                              'family_tel':row[26],
                              'email':row[27],
                              'memo':row[28],
                              'birth_place':row[29],
                              'company':row[30],
                    })
        conn.close()
                
        return True
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
            if not args:
                args = []
            args = args[:]
            ids = []
            if name:
                ids = self.search(cr, user, [('employeecode', 'ilike', name)]+args, limit=limit, context=context)
                print ids,'ids'
                if not ids:
                    ids = self.search(cr, user, [('employeename', operator, name)]+ args, limit=limit, context=context)
                    print ids,'ids1'
            else:
                ids = self.search(cr, user, args, limit=limit, context=context)
            return self.name_get(cr, user, ids, context=context)
    
 
 
 
 
  
        
        
        
        
employee()





   