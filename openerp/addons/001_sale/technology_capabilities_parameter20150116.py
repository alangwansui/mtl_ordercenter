#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
import time
class technology_capabilities_parameter(osv.osv):
    _name='technology.capabilities.parameter'
    
#    def _get_type(self,cr,uid,context=None):
#        obj=self.pool.get('select.selection')
#        ids=obj.search(cr,uid,[('type','=','technology_capabilities')],context=context)
#        res=obj.read(cr,uid,ids,['label','label'],context)
#        return [(r['label'],r['label'])for r in res]
    
    def _get_type_sub(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','technology_capabilities_sub')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_surface_treatment(self,cr,uid,context=None):
        
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','surface_treatment')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_board_material(self,cr,uid,context=None):
        
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','board_material')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_drill_type(self,cr,uid,context=None):
        
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','drill')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_ink_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','ink_type')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_accept_standard(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','accept_standard')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    _get_type=[('board_type',u'板材'),('panel_size',u'拼版尺寸'),('board_thickness',u'板厚'),('min_line_width',u'最小线宽'),('min_line_space',u'最小线距'),
                ('min_hole_line',u'孔到线'),('hole_dia',u'孔径'),('cu_thickness',u'铜厚')]
    
    _columns={
        'name':                   fields.char(u'名称',size=32),

        'item':                   fields.selection(_get_type,u'类型'),
        'sub_item':               fields.selection([('double_board',u'双面板'),('much_board',u'多层板')],string=u'子类型'),
        'level':                  fields.selection([('normal',u'正常'),('midle',u'中'),('difficult',u'难')],u'等级',size=32),
        'min':                    fields.float(u'最小值', digits=(6,4)),
        'max':                    fields.float(u'最大值', digits=(6,4)),
        'note':                   fields.text(u'备注'),
        'surface_treatment':      fields.selection(_get_surface_treatment,u'表面涂覆'),
        'board_material':         fields.char(u'板料',size=128),
        'drill_type':             fields.selection(_get_drill_type,u'钻孔类型'),
        'angle':                  fields.char(u'角度',size=32),
        'ink_type':               fields.selection(_get_ink_type,u'油墨类型'),
        'accept_standard':        fields.selection(_get_accept_standard,u'验收标准'),
        'layer':                  fields.char(u'层数',size=64),
        'v':                      fields.char(u'基数',size=64),
        'res_company':            fields.selection([('szmtl',u'深圳工厂'),('csmtl',u'长沙工厂'),('mtl',u'牧泰莱')],string=u'所属公司'),
        
    }
    
    _defaults={
        'min':lambda *a: 0.0,
        'max':lambda *a: 0.0,
      
    }
    
    
    
technology_capabilities_parameter()



