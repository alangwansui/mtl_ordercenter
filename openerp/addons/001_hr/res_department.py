#!usr/bin/env pytyon
# -*- coding:utf-8 -*-

from osv import fields,osv
import datetime
import pymssql
import sys
from tools.translate import _
reload(sys)  
sys.setdefaultencoding('utf8')

class res_department(osv.osv):
    _name="res.department"
    _description="department_information"
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    _columns={
              "name":fields.char(u"部门名称",size=30),
              'complete_name': fields.function(_dept_name_get_fnc, method=True, type="char", string='部门名称',store=True),
              "responsiblename":fields.char(u"负责人",size=20),
              "link_phone":fields.char(u"联系电话",size=20),
              "department_address":fields.char(u"部门地址",size=30),
              'parent_id':fields.many2one('res.department',u'上级部门'),
              'child_id':fields.one2many('res.department','parent_id',u'下级部门'),
              }
    def res_department_import(self,cr,uid,ids,context=None):
      obj=self.pool.get('res.department')
      server='192.168.10.2'
      user='sa'
      password='719799'
      database='mtlerp-running'
      
      conn=pymssql.connect(server=server,user=user,password=password,database=database)
     
      cur=conn.cursor()
      sql=''' select isnull(a.departmentname,'') as departmentname ,isnull(a.address,'')as address,isnull(a.telephone,'') as telephone,isnull(b.employeename,'') from TBdepartment a left join TBemployee b on  a.DepartmentManager=b.employeecode '''
      cur.execute(sql)
      s=cur.fetchall()
     
      b=[]
      for row in s:
           b.append([(''.join(map(lambda x: "%c" % ord(x), list(row[i]))).decode('gbk')) for i in range(len(row))])
           print row,'row'
      for row in b:  
           info_id=obj.create(cr,uid,{                                                                                                                 
                'name':row[0],
                'department_address':row[1],
                'link_phone':row[2],
                'responsiblename':row[3],
                    })

      conn.close()
                
      return True 
             
res_department()


