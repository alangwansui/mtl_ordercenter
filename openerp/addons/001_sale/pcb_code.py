#!/usr/bin/python
# -*- coding: utf-8 -*-


import time
from osv import osv,fields
from tools.translate  import _
import netsvc
import datetime

class pcb_sequence_code (osv.osv):

    _name='pcb.sequence.code'
 
    _order = 'id'
    _description = "Nothing"
    
    _columns = {
        'name'  : fields.char(u'名称', size=64,readonly=True),
        'type':fields.char(u'类型',size=64,readonly=True),
        
    }

    _defaults = {
        'name': lambda *a: None,
    }
    def unlink(self, cr, uid, ids, context=None):
        my=self.browse(cr,uid,ids[0])
        if my.name or my.type:
                raise osv.except_osv(_('Error!'),_(u'档案号编码不能删除！'))
        else:
            return True
pcb_sequence_code()