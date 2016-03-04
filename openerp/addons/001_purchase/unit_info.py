#!usr/bin/env python
# -*- coding: utf-8 -*-
from osv import fields,osv
import datetime


class unit_info(osv.osv):
    _name='unit.info'
    _description='unit.info'

    _columns={
              'name':fields.char(u'名称',size=32,required=True),
              'rate_name':fields.many2one('unit.info',u'比例单位名称'),
              'rate':fields.float(u'比例'),
              'is_use':fields.boolean(u'可用'),
              'type':fields.selection([('length',u'长度'),('weigth',u'重量'),('time',u'时间'),('area',u'面积'),('volume',u'容积/体积')],u'类型'),
              
              }
    _defaults={
               'is_use':True,
               }
    _sql_constraints = [('name', 'unique (name)', u'此单位已经存在!')]
unit_info()