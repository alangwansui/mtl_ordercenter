#!usr/bin/env python
#-*-coding:utf-8 -*-

from osv import fields,osv
import datetime
import pymssql
import sys
from tools.translate import _
reload(sys)  
sys.setdefaultencoding('utf8')

class parameter(osv.osv):                
    _name="parameter"
    _description="employee related of information"
   
    _type_list=[('ethnic',u'民族'),('workertype',u'职务'),('technicaltitle',u'职称'),('perfession',u'专业'),('sex',u'性别'),('marriage',u'婚姻'),('leave_type',u'离职类别')
                ,('healthy',u'健康状态'),('politic',u'政治面貌'),('diploma',u'文化程度'),('issure',u'是否'),('employee_type',u'职员类型')]
    

       
    _columns={
            'name':fields.char(u"名称",size=32),
            'type':fields.selection(_type_list,string=u'类型'),
              }
    _order='type'
    
    def parameter_import(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('parameter')
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        conn=pymssql.connect(server=server,user=user, password=passward,database=database)
        cur=conn.cursor()
        sql='''select '男' as name1, 'sex' as type union
                select '女' as name1, 'sex' as type union
                select basicdetailname,'marriage' as type from TBBasicDetail where TypeCode='15' union
                select distinct isnull(Ethnic,'') as Ethnic, 'ethnic' as type from TBemployee where isnull(ethnic,'')<>'' union
                select basicdetailname,'leave_type' as type from TBBasicDetail where TypeCode='79' union
                select basicdetailname,'healthy' as type from TBBasicDetail where TypeCode='19' union
                select distinct isnull(TechnicalTitle,'') as TechnicalTitle, 'technicaltitle' as type from TBemployee where isnull(TechnicalTitle,'')<>'' union
                select basicdetailname,'politic' as type from TBBasicDetail where TypeCode='12' union
                select distinct isnull(workertype,'') as workertype, 'workertype' as type from TBemployee union 
                select basicdetailname,'employee_type' as type from TBBasicDetail where TypeCode='18' union
                select basicdetailname,'diploma' as type from TBBasicDetail where TypeCode='14' union
                select '是' as name1, 'issure' as type union
                select '否' as name1, 'issure' as type  ''' 
        cur.execute(sql)
        s=cur.fetchall()
        b=[]
        for row in s:
            b.append([(''.join(map(lambda x: "%c" % ord(x), list(row[i]))).decode('gbk')) for i in range(len(row))])
        for row in b:  
                info_id=obj.create(cr,uid,{                                                                                                                 
                'name':row[0],
                'type':row[1],
                    })

        conn.close()
                
        return True
    
    
    
    
    
parameter()




