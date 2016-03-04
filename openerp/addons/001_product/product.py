# -*- coding: utf-8 -*-

from osv import fields, osv

class product_product (osv.osv):
    _inherit='product.product'
    _description = "extend product"
    def _get_product_info(self,cr,uid,ids,fields_name,arg,context=None):
        res={}
        for p in self.browse(cr, uid, ids, context, ):
            res[p.id]=''.join([p.name_template or '', p.default_code or '', p.variants or '',])
        return res
    
    def _search_product_info(self,cr,uid,obj,fields_name,arg,context):
        s=arg[0][2]
        res_ids=self.search(cr,uid,['|',('name_template','ilike',s),'|',('default_code','ilike',s),('variants','ilike',s)])   
        return [('id','in',res_ids)]
    
    _columns = {
        'product_info':fields.function(_get_product_info,fnct_search=_search_product_info,method=True,type='char',size=128,string='Product info',select=True),
        'board_thickness': fields.float('Board thickness',),
        'board_thickness_unit':fields.many2one('product.uom','Board thickness unit'),
        'include_cu': fields.boolean('Include cu', ),  
        'cu_thickness': fields.char('Cu thickness',size=16),
        'length': fields.float('Length', ),
        'width' : fields.float('Width',  ),
        'size_unit' :fields.many2one('product.uom','Board size unit'), 
        'er': fields.float('Permittivity',),                        #介电常数
        'medium_thickness':fields.float('Mediumthickness',),        #介质厚度
        'resin_percent' :fields.integer('Resin percent'),           #树脂含量
    }
    _defaults = {  
    }
    def create_default_code(self,cr,uid,ids,context=None):
        rec=self.browse(cr,uid,ids[0])
        code_obj=self.pool.get('ir.sequence').get(cr,uid,'product.code')
      
        if rec.categ_id.code:
            new_default_code=rec.categ_id.code+'.'+code_obj
            self.write(cr,uid,ids,{'default_code':new_default_code})
        return True
product_product()

class product_category(osv.osv):
    _inherit='product.category'
    _columns={
              'code':                   fields.char('code',size=128,select=True),
    }
    _sql_constraints=[('code','unique(code)','product category code must be unique')]
product_category()



