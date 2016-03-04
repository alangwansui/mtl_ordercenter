#! -*- usr/python -*-
# -*- coding: utf-8 -*-
from datetime import datetime
import time
from osv import fields,osv

class product_category_new(osv.osv):
    _name='product.category.new'
    _columns={
              'name':fields.char(u'名称',size=64,select=True),
              'up_type':fields.many2one('product.category.new',u'上一级类型'),
              'type':fields.selection([('big',u'大类'),('middle',u'中类'),('small',u'小类'),('smaller',u'分类')],string=u'类型',select=True),
              'code':                   fields.char(u'代号',size=64),
    }
	
product_category_new()