#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
#
#
# module: addons.001_sql_constraints.ql_constraints
#
# @author:  zhouqiang <alangwansui AT gmail.com>
# @Created on: 2011-11-26 - 下午5:02:23
# @Description: when add new call, dont forget to add depends in openerp
#
'''
from osv import fields, osv
from osv import  osv
import re

class product_product(osv.osv): 
    _inherit = 'product.product'
    _column={
        'default_code' : fields.char('Reference', size=64, require=True),
    }
    
    _sql_constraints = [
        ('default_code', 'unique (default_code)', 'Default_code  must unq!'),        
    ]
product_product()  


##add user password check, the password must includ character and length cant less than six
class res_users(osv.osv): 
    _inherit = 'res.users'
    def _check_password(self, cr, uid, ids, context=None):
        for id in ids:
            password=self.browse(cr, uid, id, context)['password']
            ##print password,   '==>' ,
            small          =re.search('[a-z]', password)
            big            =re.search('[A-Z]', password)
            numb           =re.search('[0-9]', password)
            characteristic =re.search('\W', password)
            flage=int(bool(small)) + int(bool(big)) +int(bool(numb)) +int(bool(characteristic))
            if ( len(password) < 6 or flage < 3 ):
                return False
        return True
      
    _constraints=[
        (_check_password, 'Error !密码最少为6位，密码由大写、小写、数字、符号中的最少3种组成,如：Ab8889,995%%c!', ['password'])
    ]    
res_users()


##res.partner   field   ref   must uniq
class res_partner(osv.osv): 
    _inherit = 'res.partner'
    _sql_constraints = [
        ('ref', 'unique (ref)', 'ref  must unq!'),        
    ]
res_partner() 




 

       




























