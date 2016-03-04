#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from openerp.tools.translate import _

class impdance_info(osv.osv):
    _name='impdance.info'
    _columns={
     'name':           fields.char(u'名称',size=32,select=True),#单据编号
     'partner_id':    fields.many2one('res.partners',u'客户名称',select=True),#客户名称
     'ref':                fields.related('partner_id','partner_code',type='char',string='客户代号',),#客户代号
     'user_id':         fields.many2one('res.users',u'创建人'),#创建人
     'file_name':     fields.char('文件名',size=32),#文件名
     'product_id':    fields.many2one('product.product',u'档案号',select=True),#档案号
     'impdance_type':fields.selection([('alone_port',u'单面'),('difference',u'多面')],u'阻抗类型',),#阻抗类型
     'layer_count':    fields.char(u'板层数',size=32),#层次
     'line_width':       fields.float(u'线宽'),#线宽
     'interval':           fields.float(u'间距'),#间距
     'cu_thickness':  fields.float(u'铜厚'),#铜厚
     'reference_layer':fields.char(u'引用层数',size=32),#参考层
     'impdance_value':fields.float(u'阻抗值'),#阻抗值
     'tolerance':            fields.integer(u'公差'),#公差
     'adjust_content':   fields.char(u'调整内容',size=32),#调整内容
     'layer_cu_thickness_id':fields.many2one('layer.cu.thickness',u'来源'),
}
impdance_info()
    