#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
import time




class base_follow(osv.osv):
    _name='base.follow'
    _state=('draft','done','refuse')
    _state=[(i,i.title()) for i in _state]  
    
    _columns={
        'name': fields.char('name', size=32, ),
        'state':fields.selection( _state,'State', size=64, required=False, translate=True, readonly=True,),
    } 
    _state_filter={
        'done'     :{'same_dpt':False,  'domain':[('groups_id','=','Supervisor'),]},
    }
    def updata_state(self, cr, uid, ids, state=None, state_filter=None, **args):
        org_state=self.browse(cr,uid,ids[0]).state  
        self.write(cr, uid, ids, {'state':state})
        self.pool.get('purchase.prlog').addlog(cr,uid,ids,org_state,type(self) )
        if ( state_filter and state_filter.get(state,False) ):
            filter=state_filter[state]['same_dpt'] and (state_filter[state]['domain']+[('context_department_id','=',self.browse(cr,uid,ids[0],).dpt_id.id)]) or state_filter[state]['domain']
            ##print     filter
            user_ids=set(  self.pool.get('res.users').search(cr,uid, filter)  )
            if 1 in user_ids:  user_ids.remove(1)
            user_ids=list(user_ids)
            ##print user_ids,'user_id'
            if  user_ids:
                self.send_request(cr, uid, ids, receivers=user_ids )
        return True
        
    def send_request(self,cr,uid,ids, receivers=None,**args):
        obj_request=self.pool.get('res.request')
        my=self.browse(cr, uid, ids[0],)
        res_type=type(self).__name__
        request_ids=[]
        for user_id in receivers:
            id=obj_request.create(cr,uid,{
                   'name'     : '%s  %s'  % (res_type,my.name),
                   'act_to'   :  user_id,
                   'body'     : '%s  %s'  % (res_type, my.state),
                   'ref_doc1' : '%s, %s'  % (res_type, my.id),
            })
            request_ids.append(id)
        obj_request.request_send(cr,uid,request_ids)
        return True
    
base_follow()

class select_selection(osv.osv):
    _name='select.selection'
    _order='type,sequence'
    _columns={
        'name':     fields.char(u'名称', size=2000, translate=True),
        'label':    fields.char(u'标签', size=2000,),
        'type':     fields.char(u'类型', size=128,select=True),
        'sub_type': fields.char(u'共同类型', size=32,select=True),
        'active':   fields.boolean(u'活动', ), 
        'sequence': fields.integer(u'序号'), 
        'thickness':fields.float(u'厚度',digits=(3,3),), 
        'variants_id'   :fields.many2one('select.selection',u'型号',domain=[('type','=','ink_type')]),
        'is_specia_material':fields.boolean(u'特殊材料'),# 是否特殊板材
        'is_htg':       fields.boolean(u'高TG'),                 # 是否htg 板材
        'is_rigid_flexible': fields.boolean(u'刚柔结合板'), 
        'partner_id'   :fields.many2one("res.partners", u'客户',domain=[('supplier','=',True),('user_id','=',2350)]),

    }
    _defaults={
        'active':lambda *a: True,
    }
    #===========================================================================
    # def name_get(self, cr, uid, ids, context=None):
    #    result = []
    #    for my in self.browse(cr, uid, ids, context):
    #        result.append( (my.id, my.name) )
    #    return result
    #===========================================================================
  
    
    
    
    
    
    
    
    def name_search(self, cr,uid, name='', args=None, operator='ilike', context=None, limit=100):
        res=super(select_selection,self).name_search(cr,uid,name=name,args=args,operator=operator,context=context,limit=limit)
        if not res:
            if name:
                print name,'name'
                if 'oz' not in name:
                    name=str(name)+'oz'
                cre_id=self.create(cr,uid,{'name':name,'label':name,'type':'laminar_structure_material','sub_type':'cu'})
                return self.name_get(cr,uid,[cre_id])
        return super(select_selection,self).name_search(cr,uid,name=name,args=args,operator=operator,context=context,limit=limit)
select_selection()










