#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Mssql_read_col():
	''' read the line in _mssql , obj must be a line in execute_query,
	    example :  for i in conn:	
						obj=mssql_read_col.mssql_read_col(i)
						col=obj.read_line()
	''' 
	def __init__(self,row):
		self.row=row
		
	def gb2312ToUtf8(self,strtemp):
		if strtemp is None:
			return ''
		strtemp = strtemp.decode('gb2312','ignore')
		strtemp = strtemp.encode('utf-8', 'ignore')
		strtemp = strtemp.strip();  
		return strtemp 

	def read_line(self,key_is_lower=False):
		col={}  
		for k,v in self.row.items():
			if (  type(k) == type('str')   ):
				if ( key_is_lower ):
					k=k.lower()
				if (   type(v) == type('str')    ):
					v=self.gb2312ToUtf8(v)
				else:
					pass
				col[k]=v
		return col
		

# for i in conn:
	# a=None
	# x=mssql_read_col(i)
	# for k,v in x.read_line().items():
		# print k,v
	
	

	