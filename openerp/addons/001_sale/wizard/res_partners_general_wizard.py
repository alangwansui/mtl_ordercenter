#! /usr/bin/python
# -*- coding:utf-8 -*-



from osv import  fields,osv
from tools.translate import _



class res_partners_general_wizard(osv.osv_memory):
    _name='res.partners.general.wizard'
    _description='Res partners general'
    
    _columns={}
    
    
    def create_partners_general(self,cr,uid,ids,context=None): 
        act_id=context.get('active_id')
        obj=self.pool.get('res.partners')
        my=obj.browse(cr,uid,act_id)
        
        if  not my.partner_general_id:
            res_id=self.pool.get('partner.general.requirements').create(cr,uid,{
                    'partner_id':my.id,
                    'responsible_id':uid, })
           
            obj.write(cr,uid,act_id,{'partner_general_id':res_id})
            return { 
                'name':_("Create new partner general info"),
                'view_type':'form',
                'view_mode':'form',
                'res_model':'partner.general.requirements',
                'res_id':res_id,
                'type':'ir.actions.act_window',
            }
            print res_id,'res_id'
        else:
            raise osv.except_osv(_('Error!'),_(u'客户通用信息只能是唯一的!'))
        
        
res_partners_general_wizard()
