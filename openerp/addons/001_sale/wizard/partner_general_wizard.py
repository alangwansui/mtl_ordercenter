# !/usr/bin/python
# -*- coding:utf-8 -*-

import time
from osv import osv,fields

general_info_dic={
        'board_material_ids':('board_material','board_material_general_id'),              
        'special_process_ids' :('special_process','special_process_general_id'),
        'route_type_ids'            :('route_type','route_type_general_id'),
        'accept_standard_ids'      :('accept_standard','accept_standard_general_id'),
        'test_type_ids'            :('test_type','test_type_general_id'),
        'mark_request_ids'         :('mark_request','mark_request_general_id'),
        'request_with_goods_ids'   :('request_with_goods','request_with_goods_general_id'),
        'packing_type_ids':('packing_type','packing_type_general_id'),
                  }
sel_info_dic={
        'route_type_general_id': 'route_type_id',
        'test_type_general_id': 'test_type_id',
        'accept_standard_general_id': 'accept_standard_id',
        'request_with_goods_general_id':'request_with_goods_id',
        'packing_type_general_id':'packing_type_id',
        'mark_request_general_id': 'mark_request_id',
        'special_process_general_id':'special_process_id',
        'board_material_general_id':'board_material_id',
              }

class partner_general_wizard(osv.osv_memory):
    _name='partner.general.wizard'
    
    def _get_partner_id(self,cr,uid,context):
        
        return self.pool.get('pcb.info').read(cr,uid,context.get('active_id'),['partner_id'])['partner_id']
    
    def _get_requirements_id(self,cr,uid,context):
        
        partner_id=self._get_partner_id(cr,uid,context)[0]

        requirements= self.pool.get('res.partners').browse(cr,uid,partner_id).partner_general_requirements_ids
        print requirements,'partner_name'
        names=[i.name for i in requirements]
        print names,'names'
        ##part_number='xxxx' need order_recive_id.org_file_name
        
        act_id=context.get('active_id',False)
        print act_id,'act_id'
        
        pi=self.pool.get('pcb.info').browse(cr,uid,act_id)
        
        
        part_number=pi.custmer_goodscode
        
        print part_number
        
        res_id=None
        
        if part_number:
            for req in requirements:
                
                if   req.name in part_number:
                    return req.id 

        return res_id
    
    
    
    _columns={
              'partner_id':fields.many2one('res.partners',u'客户', change_default=True),
              'partner_general_requirements_id':fields.many2one('partner.general.requirements',u'客户通用信息',)
    }
    _defaults={
        'partner_id':lambda self,cr,uid,context:self._get_partner_id(cr,uid,context),
        'partner_general_requirements_id':lambda self,cr,uid,context:self._get_requirements_id(cr,uid,context)
    }


    def get_partner_info(self,cr,uid,ids,context):
        act_id=context.get('active_id')
        act_model=context.get('active_model')
        general_obj=self.pool.get('partner.general.requirements')
        req=self.browse(cr,uid,ids[0]).partner_general_requirements_id
        if  req:
            data=general_obj.copy_data(cr,uid,req.id)
            del data['name'],data['partner_id']
            for key in data.keys():
                if key in general_info_dic.keys():
                    gen_key=general_info_dic[key][1]
                    gen_info=[]
                    
                    for gen_line in data[key]:
                      
                        if gen_line[2]:
                            if gen_key in gen_line[2].keys():
                                gen_line[2][ sel_info_dic[gen_key] ]=gen_line[2][gen_key]
                                del gen_line[2][gen_key]
                            gen_info.append((0,0,gen_line[2])) 
                                 
                    data[ general_info_dic[key][0] ]=gen_info
                    del data[key]
            
            self.pool.get(act_model).write(cr,uid,act_id,data)
            return {'type':'ir.actions.act_window_close'}
        else:
            return False
        
partner_general_wizard()


