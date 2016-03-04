#!usr/bin/python
# -*- coding:utf-8 -*-

from osv import fields,osv
from decimal_precision import decimal_precision as dp
class sale_unnormal(osv.osv):
        _name="sale.unnormal"
        _description="Sale unnormal"
 
        _columns={
                  "name":fields.char(u"名称",size=64),
                  "sequence":fields.integer(u"序号"),
                  
                  "min_value":fields.float(u"最小值"),
                  "max_value":fields.float(u"最大值"),
                  "active":fields.boolean(u"活动"),
                  }
        
        _defaults={
                   
                   }
       
       
       
       
       
       
       
sale_unnormal()