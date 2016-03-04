#!/usr/bin/python
# -*- coding:utf-8 -*-
from osv import  fields,osv
from tools.translate import _
class crm_lead_wizard(osv.osv_memory):
    _name='crm.lead.wizard'
    _columns={
        'name':fields.char('name',readonly=False,size=16),
    }
    def creat_pcb_info(self,cr,uid,ids,context=None): 
        act_id=context.get('active_id')
        #obj=self.pool.get('crm.lead')
        obj=self.pool.get(context.get('active_model'))
        my=obj.browse(cr,uid,act_id)
        #delivery_leadtime=my.delivery_leadtime
        if my.sale_type in ('new','revise') and not my.pcb_info_id:
            res_id=self.pool.get('pcb.info').create(cr,uid,{
                    'product_id':my.product_id.id,
                    'partner_id':my.partner_id.id,
                    'responsible_id':uid,
          #        'delivery_leadtime':my.delivery_leadtime,
            })
            obj.write(cr,uid,act_id,{'pcb_info_id':res_id})
            return { 
                'name':_("Create new pcb info"),
                'view_type':'form',
                'view_mode':'form',
                'res_model':'pcb.info',
                'res_id':res_id,
                #'domain': [('partner_id','=',my.partner_id.id),('responsible_id','=',uid),('delivery_leadtime','=',delivery_leadtime)],
                #'context':context,
                'type':'ir.actions.act_window',
            }
            
        else:
            raise osv.except_osv(_('Error!'),_('sale type must be new or revise re  or the pcb info exist'))
crm_lead_wizard()

class lead_price_sheet(osv.osv_memory):
    _name='lead.price.sheet'
    _columns={
        'name':fields.char('name',readonly=False,size=16),
    }
    def transform_price_sheet(self,cr,uid,ids,context=None):
        act_id=context.get('active_id',False)
        #lead_obj=self.pool.get('crm.lead')
        lead_obj=self.pool.get(context.get('active_model'))
        lead=lead_obj.browse(cr,uid,act_id)
        if  lead.pcb_info_id and lead.state != 'done':
            ps_id=self.pool.get('price.sheet').create(cr,uid,{
                'pcb_info_id':lead.pcb_info_id.id,
                'lead_id':act_id,
                'responsible_id':uid,
                'product_number':lead.product_number,
                'delivery_leadtime':lead.delivery_leadtime,
            })
          
            if ps_id:
                lead_obj.write(cr,uid,act_id,{'state':'done'})
                return{
                    'name':_('transform pcb info'),
                    'view_type':'form',
                    'view_mode':'form',
                    'res_model':'price.sheet',
                    'type':'ir.actions.act_window',
                    'res_id':ps_id,
                    #'domain':[('res_id','=',ps_id)],  
                }
        else:
            raise osv.except_osv(_('Error!'),_('not pcb_info or state done'))
lead_price_sheet()

class crm_lead_partner(osv.osv_memory):
        _inherit='crm.lead2partner'
        def default_get(self, cr, uid, fields, context=None):
            lead_obj = self.pool.get('crm.lead')
            lead_id=context and context.get('active_ids', []) or []
            partner_obj=self.pool.get('res.partner')
            res={}
            for lead in  lead_obj.browse(cr,uid,lead_id):
                if lead.email_from:
                    res=super(crm_lead_partner, self).default_get(cr, uid, fields, context=context)
                elif not lead.email_from and lead.partner_name:
                    partner_id=partner_obj.search(cr, uid, [('name', '=', lead.partner_name),('user_id','=',lead.user_id.id)], context=context)
                    res=super(crm_lead_partner, self).default_get(cr, uid, fields, context=context)
                    if partner_id:
                        res['partner_id']=partner_id[0]
                    else:
                        res['partner_id']=False
                        res['action']='create'
                        
            return res         
        
        def _create_partner(self, cr, uid, ids, context=None):
            """
            This function Creates partner based on action.
            @param self: The object pointer
            @param cr: the current row, from the database cursor,
            @param uid: the current user’s ID for security checks,
            @param ids: List of Lead to Partner's IDs
            @param context: A standard dictionary for contextual values
    
            @return : Dictionary {}.
            """
            if context is None:
                context = {}
    
            lead_obj = self.pool.get('crm.lead')
            partner_obj = self.pool.get('res.partner')
            contact_obj = self.pool.get('res.partner.address')
            cont_obj=self.pool.get('res.partner.contact')
            job_obj=self.pool.get('res.partner.job')
            partner_ids = []
            partner_id = False
            contact_id = False
            rec_ids = context and context.get('active_ids', [])
    
            for data in self.browse(cr, uid, ids, context=context):
                for lead in lead_obj.browse(cr, uid, rec_ids, context=context):
                    if data.action == 'create':
                        partner_id = partner_obj.create(cr, uid, {
                            'name': lead.partner_name or lead.contact_name or lead.name,
                            'user_id': lead.user_id.id,
                            'comment': lead.description,
							'customer':lead.categ_id.id == 14 and True ,
                            'ref':None,
                        })
                       
                        contact_id = contact_obj.create(cr, uid, {
                            'partner_id': partner_id,
                            'name': lead.contact_name,
                            'phone': lead.phone,
                            'mobile': lead.mobile,
                            'email': lead.email_from,
                            'fax': lead.fax,
                            'title': lead.title and lead.title.id or False,
                            'function': lead.function,
                            'street': lead.street,
                            'street2': lead.street2,
                            'zip': lead.zip,
                            'city': lead.city,
                            'country_id': lead.country_id and lead.country_id.id or False,
                            'state_id': lead.state_id and lead.state_id.id or False,
                        })
                        cont_id=cont_obj.create(cr,uid,{
                            'partner_id':partner_id,
                            'name':lead.contact_name,
                            'mobile':lead.mobile,
                             'phone': lead.phone,
                             'email': lead.email_from,
                        })
                        job_id=job_obj.create(cr,uid,{
                            'address_id':contact_id,
                            'contact_id':cont_id,
                             'state':'current',
                             'phone':lead.phone,
                             'fax':lead.fax,
                             'email': lead.email_from,
                        })
                    else:
                        if data.partner_id:
                            partner_id = data.partner_id.id
                            contact_id = partner_obj.address_get(cr, uid, [partner_id])['default']
    
                    partner_ids.append(partner_id)
    
                    if data.action<>'no':
                        vals = {}
                        if partner_id:
                            vals.update({'partner_id': partner_id})
                        if contact_id:
                            vals.update({'partner_address_id': contact_id})
                        lead_obj.write(cr, uid, [lead.id], vals)
            return partner_ids
crm_lead_partner()
