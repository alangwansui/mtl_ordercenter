# -*- encoding: utf-8 -*-



from datetime import datetime
import time
from osv import fields,osv
import xmlrpclib
import xlrd


class aps(osv.osv):
	_name='aps'
	_description='APS'
	
	def _get_silk(self,cr,uid,context=None):
		obj=self.pool.get('select.selection')
		ids=obj.search(cr,uid,[('type','=','silk_colour')],context=context)
		res=obj.read(cr,uid,ids,['name','name'],context)
		return [(r['name'],r['name'])for r in res]
	
	 

	
	
	def _lang_get(self, cr, uid, context=None):
		lang_pool = self.pool.get('res.lang')
		ids = lang_pool.search(cr, uid, [], context=context)
		res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
		return [(r['code'], r['name']) for r in res]
	
	
	_columns={
		'name':fields.char('单号',size=64),
		'order_name':fields.integer('order_name',size=64),
		'code':fields.integer('code'),
		'state':fields.selection([('draft','Draft'),('done','Done')]),
		'lang': fields.selection(_lang_get, u'语言',),
		'aps_line_ids':fields.one2many('aps.line','aps_line_id','aps_line_ids'),
		'silk_type':fields.selection(_get_silk,'silk_type',),
		'silk_types':fields.char('silk_types',size=64),
		'silk_variants':fields.char('silk_variants',size=64),
	
	}

	_defaults={
			'state':'draft',}
	
	
	def button_approve(self,cr,uid,ids,context=None):
		
		return self.write(cr,uid,ids,{'order_name':'12345'})
	
	def create_aps(self,cr,uid,ids,context=None):
		my=self.browse(cr,uid,ids[0])
		(username,pwd,dbname) =('admin', 'admin', 'pcb')     #用户名、密码、数据库
		sock_common = xmlrpclib.ServerProxy ('http://localhost:8069/xmlrpc/common')  #建立连接目标机器
		uid = sock_common.login(dbname, username, pwd)                             #登入数据库并返回用户ID
		sock = xmlrpclib.ServerProxy('http://localhost:8069/xmlrpc/object')        #远程调用服务端的对象                                           #打开文件
		book=xlrd.open_workbook("c:/test/test.xls")                                  #打开要导入的电子表格
		sheet=book.sheets()[0]                                                #导入工作表1
		ncols=sheet.ncols                                                     #取表的总列数
		nrows=sheet.nrows                                                     #取表的总行数
		outsources=my.id
		print nrows,ncols
		for line_number in range(1,nrows):                                    #循环读取每行的数据
			row=sheet.row(line_number)                                        #取当前行的数据
			lis=[cell.value for cell in row]                                  #取每行单元格数据，并用列表保存
			(code,employee_name,dpt,date,date_one,date_two,date_three,date_four,date_five,date_six,date_seven,date_eight)=lis[0:12]
  
			print code
			info_id=sock.execute(dbname, uid, pwd,  'aps.line', 'create', {
            'aps_line_id':outsources,
            'code':code,
            'employee_name':employee_name,
            'dpt':dpt,
            'date':date,
            'date_one':date_one,
            'date_two':date_two,
            'date_three':date_three,
            'date_four':date_four,
            'date_five':date_five,
            'date_six':date_six,
            'date_seven':date_seven,
            'date_eight':date_eight,
          
            })
			
		return True


	def create_time(self,cr,uid,ids,context=None):
		my=self.browse(cr,uid,ids[0])
		print my.id
		aps_line_ids=my.aps_line_ids
		obj=self.pool.get('aps.line')
		ids=obj.search(cr,uid,[('aps_line_id','=',my.id)])
		se=obj.browse(cr,uid,ids[0])
		print se,'se',
		for r in aps_line_ids:
			
			print r.date_three
		
			date_three=r.date_three
			
			s=time.strptime(date_three,"%Y-%m-%d %X")
			print s,'s'
		date_five=aps_line_ids.date_five
		if date_three<='08:00:00':
			date_three=='08:00:00'
		if date_five<='13:30:00':
			date_five=='13:30:00'
		
		
		return True
	
	def onchange_silk_type(self,cr,uid,ids,silk_type,context=None):
			vals={'silk_types':silk_type}
			return {'value':vals,}
	
	def onchange_order_name(self,cr,uid,ids,order_name,context=None):
		vals={'code':order_name}
		return {'value':vals}
	
	
	
aps()










class aps_line(osv.osv):
	_name='aps.line'
	
	def _get_silks(self,cr,uid,context=None):
		obj=self.pool.get('select.selection')
		ids=obj.search(cr,uid,[('type','=','silk_colour')],context=context)
		res=obj.read(cr,uid,ids,['name','name'],context)
		return [(r['name'],r['name'])for r in res]
	_columns={
			
			'aps_line_id':fields.many2one('aps','aps_line_id',ondelete='cascade'),
			'sequence':fields.integer(u'序号'),
			'note':fields.integer('note'),
			'mark_request':fields.many2many('select.selection','aps_line_rel','name','label','mark_request'),
			'silk_type':fields.selection(_get_silks,'silk_type',),
			'code':fields.char(u'工号',size=32),
			'employee_name':fields.char(u'姓名',size=64),
			'dpt':fields.char(u'部门',size=32),
			'date':fields.char(u'日期',size=64),
			'date_one':fields.char(u'星期',size=64),
			'date_two':fields.char(u'日班编号',size=64),
			'date_three':fields.char(u'早上班',size=64),
			'date_four':fields.char(u'早下班',size=64),
			'date_five':fields.char(u'午上班',size=64),
			'date_six':fields.char(u'午下班',size=64),
			'date_seven':fields.char(u'晚上班',size=64),
			'date_eight':fields.char(u'晚下班',size=64),
			'total_time':fields.char(u'总工时',size=64),
			'jia_ban':fields.char(u'加班工时',size=64),
			
			
			
			
			}
	
	

