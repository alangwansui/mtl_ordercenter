# -*- encoding: utf-8 -*-

from osv import fields,osv
import time,re

class approve_log (osv.osv):
    _name = "purchase.prlog"
    _description="Approve Workflow Logs"
    _columns = {
        'uid'      :fields.many2one('res.users', u'审批人'),
        'info'     :fields.char(u'对应状态', size=32),
        'date'     :fields.datetime(u'审批时间'),
        'res_type' :fields.char(u'主题', size=64),
        'res_id'   :fields.integer(u'资源id'),
        'partner_general_requirements_id':fields.many2one('partner.general.requirements',u'客户通用信息'),

    }
    _defaults = {
        'uid': lambda self, cr, uid, context: uid , 
    }
    
    def addlog(self, cr, uid, res_ids, info=None, res_type=None, ):
        for res_id in res_ids:
            data={
                'res_type' : res_type.__name__ ,   
                'info': info,
                'res_id':res_id,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self.create(cr, uid, data)
        return True

    def addlog_partner_general_requirements(self, cr, uid, res_ids, info=None, res_type=None, ):
        for res_id in res_ids:
            data={
                'res_type' : res_type.__name__ ,   
                'info': info,
                'res_id': res_id,
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'partner_general_requirements_id':res_id,
            }
            self.create(cr, uid, data)
        return True





















approve_log()
