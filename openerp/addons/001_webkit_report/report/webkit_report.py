# -*- encoding: utf-8 -*-
import time
from report import report_sxw
from osv import osv,orm
import tools
import netsvc

class res_partners_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(res_partners_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
            
        })
        
report_sxw.report_sxw('report.res_partners_report',
                       'res.partners', 
                       'addons/001_webkit_report/report/res_partners_report.odt',
                       parser=res_partners_report)



