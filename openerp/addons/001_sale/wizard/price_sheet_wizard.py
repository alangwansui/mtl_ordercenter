# !/usr/bin/python
# -*- coding:utf-8 -*-

import time
from osv import osv,fields
from tools.translate  import _

class split_line(osv.osv_memory):
    _name='split.line'
    _order='id'
    _columns={
      'name'  :         fields.char('name', size=16, required=False, select=True,),
      'number':         fields.integer('Number',size=32),
      'cost'  :         fields.float('Cost'),
      'split_id':       fields.many2one('price.sheet.split', 'split_id', ),
    }
split_line()


class price_sheet_split(osv.osv_memory):
    _name='price.sheet.split'
    _order='id'
    _columns={
        'name'              :fields.char('name', size=16, required=False, select=True,),
        'split_line_ids'    :fields.one2many('split.line','split_id', 'split_line_ids'),          
    }
    def do_split(self,cr,uid,ids,context):
        ps_obj=self.pool.get('price.sheet')
        me=self.browse(cr, uid, ids[0],)
        parent_ps=ps_obj.browse(cr,uid,context.get('active_id') )
        sum_number=sum([line.number for line in  me.split_line_ids])
        sum_cost=sum([line.cost for line in  me.split_line_ids])
        
        if sum_number != parent_ps.product_number_s or sum_cost != parent_ps.cost_all_s:
            raise osv.except_osv(_('Warning !'),_('childs number and cost sum must eq cost_all_s'))  
        else:
            child_ids=[]
            for line in me.split_line_ids:
                child_id=ps_obj.create(cr,uid,{
                    'product_number_s':line.number,
                    'cost_all_s'      :line.cost,
                    'product_number' :parent_ps.product_number,
                    'pcb_info_id'    :parent_ps.pcb_info_id.id,
                    'parent_id'      :parent_ps.id,                                                                              
                }) 
                child_ids.append(child_id)
                
        return {
            'domain': "[('id','in', [" + ','.join(map(str, child_ids)) + "])]",
            'name': 'price sheet',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'price.sheet',
            'view_id':   False,
            'type': 'ir.actions.act_window',      
        }
price_sheet_split()


