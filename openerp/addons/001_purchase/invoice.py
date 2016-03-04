#!usr/bin/env python
# -*- coding: utf-8 -*-
from osv import fields,osv
import datetime
from tools.translate import _

class invoice(osv.osv):
    _name='invoice'
    _description='invoice'
    
    def name_get(self, cr, uid, ids, context=None):
            if context is None:
                context = {}
            if not ids:
                return []
            reads = self.read(cr, uid, ids, ['name','tax_rate'], context=context)
            res = []
            for record in reads:
                name = record['name']
                if record['tax_rate']:
                    name = name+' / '+str(record['tax_rate'])
                res.append((record['id'], name))
            return res
        
    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)     
    
    _columns={
              'name':fields.char(u'名称',size=32,required=True),
              'tax_rate':fields.float(u'税率%',digit=(9,4)),
              'is_add':fields.boolean(u'增值税'),
              'state':fields.selection([('draft',u'草稿'),('done',u'完成'),('cancel',u'作废')],u'状态'), 
              'full_name':fields.function(_dept_name_get_fnc, method=True, type="char", string='全称',store=True),
              }
    _defaults={
               'state':'draft',
               }
    _sql_constraints = [('full_name', 'unique (full_name)', u'此发票已经存在!')]
    
    def button_refuse(self,cr,uid,ids,context=None):
        return self.write(cr,uid,ids[0],{
                                   'state':'cancel'})
    
    def button_approve(self,cr,uid,ids):    
        return self.write(cr,uid,ids[0],{
                                   'state':'done'})
        
    def unlink(self,cr,uid,ids,context=None):
        info=self.browse(cr,uid,ids[0])
        if info.state!='draft':
            raise osv.except_osv(_('Error'),(u'此状态下不能删除'))
        return  super(invoice,self).unlink(cr,uid,ids)
        
invoice()