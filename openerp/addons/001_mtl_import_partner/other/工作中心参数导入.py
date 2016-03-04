import xlrd
import xmlrpclib
import re
import sys
import os


(username,pwd,dbname) =('admin', 'Admin1', 'mtl')
sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')
uid = sock_common.login(dbname, username, pwd)
sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')

xls_file="e:/xls/workcenter.xls"
book=xlrd.open_workbook(xls_file,'r')
sheet=book.sheets()[0]
ncols=sheet.ncols
nrows=sheet.nrows
print ncols,nrows


for line in range(0,nrows):
    line_info=sheet.row(line)
    cell_info=[cell.value for cell in line_info]
    (name,parameter_name,code)=cell_info[0:3]
    ###创建工作中心id
    workcenter_id=sock.execute(dbname,uid,pwd,'mrp.workcenter','search',[('code','=',code)])
    workcenter_name=sock.execute(dbname,uid,pwd,'mrp.workcenter','search',[('name','=',name)])
    if not (workcenter_id and workcenter_name):
        workcenter_id=sock.execute(dbname,uid,pwd,'mrp.workcenter','create',{
            'name':name,
            'code':code,
        })
    else:
        workcenter_id=workcenter_id[0]
    ##导入工作中心参数
    print parameter_name,workcenter_id
    parameter_id=sock.execute(dbname,uid,pwd,'workcenter.parameter.name','search',[('name','=',parameter_name),('mrp_workcenter_id','=',workcenter_id)])
    if parameter_id:
        print 'parameter name have been update'
        continue
    else:
        parameter_name_id=sock.execute(dbname,uid,pwd,'workcenter.parameter.name','create',
        {
            'name':parameter_name,
            'mrp_workcenter_id':workcenter_id,
        })
        if parameter_name_id:
            print 'import parameter name sucess!'
        
    
    



