
from openerp.osv import osv, fields

class files_name(osv.osv):
    _name = "files_name"

    def get_name(self, cr, uid,pathval,context=None):
        return {"hello": "world"}
    
    _columns = {
        'message': fields.char(string="Name"),
    
        'files':fields.binary("Files"),
        
    }


