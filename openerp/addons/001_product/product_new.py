# -*- coding: utf-8 -*-

from osv import fields, osv
import string
class product_new (osv.osv):
    _name='product.new'
    _description = "extend product"
 
    _columns = {
        'name':fields.char(u'名称',size=64),
        'type':fields.char(u'型号',size=128),
        'code':fields.char(u'物料编号',size=128,readonly=True),
        'first_type':fields.many2one('product.category.new',u'大类',domain=[('type','=','big')]),
        'second_type':fields.many2one('product.category.new',u'中类',domain=[('type','=','middle')]),
        'third_type':fields.many2one('product.category.new',u'小类',domain=[('type','=','small')]),
        'fourth_type':fields.many2one('product.category.new',u'分类',domain=[('type','=','smaller')]),
        'board_thickness': fields.float(u'板厚',),
        'board_thickness_unit':fields.many2one('product.uom','Board thickness unit'),
        'include_cu': fields.boolean('Include cu', ),  
        'cu_thickness': fields.char('Cu thickness',size=16),
        'length': fields.float(u'长', ),
        'width' : fields.float(u'宽',  ),
      
        'er': fields.float('Permittivity',),                        #介电常数
        'medium_thickness':fields.float('Mediumthickness',),        #介质厚度
        'resin_percent' :fields.integer('Resin percent'),           #树脂含量
    }
    _defaults = {  
    }
    _sql_constraints = [
        ('code', 'unique (code)', 'name  must unique!'), ]
    def create_product_number(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.code:
            raise osv.except_osv(_('Error!'),_(u'物料编码已经生成！'))
            
        else:
            obj=self.pool.get('product.new.list')
            m='0001'
            code_obj=self.pool.get('ir.sequence').get(cr,uid,'product.new')
            numbers=my.first_type.code+'.'+my.second_type.code+'.'+my.third_type.code+'.'+my.fourth_type.code
            
            if obj.search(cr,uid,[('code','=',numbers)]):
                obj_id=max(obj.search(cr,uid,[('code','=',numbers)]))
                code_number=obj.browse(cr,uid,obj_id).code_number
                print 'ok'
                length=len(code_number)-int(code_number)
                print length,'l'
                print int(code_number)
                default_code=str(int(code_number)+1)
                print default_code,'code'
                d=default_code.zfill(len(code_number))
                print d,'d'
               
                number=numbers+'.'+d
                obj.write(cr,uid,obj_id,{'code_number':d,
                                         'name':number,})
            else:
                number=numbers+'.'+m
                obj.create(cr,uid,{'code':numbers,
                              'code_number':number[12:16],
                              'name':number,
                           })
            print number[12:16],'coco'
            self.write(cr,uid,my.id,{'code':number})
           

        return True
 

product_new()


class product_new_list(osv.osv):
    _name='product.new.list'
    _description = "product new list"
 
   
    _columns={
             'name':fields.char(u'物料编码',size=128),
             'code':fields.char(u'代号',size=128),
             'code_number':fields.char(u'编码序号',size=128),
            
             }

    _defaults = {  
    }
    _sql_constraints = [
        ('name', 'unique (name)', 'name  must unique!'), ]
product_new_list()