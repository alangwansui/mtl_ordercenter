# -*- coding: utf-8 -*-
##############################################################################
#  'author': 'Wulf Chow',
#  'date'  :  2012-4-16
#  'maile' :   <alangwansui at gmail.com>
##############################################################################

{
    'name': '001 sale order new ',
    'version': '8.0.1',
    'category': 'MTL Modules/',
    'description': """some description for :""",
    'author': 'Roy',
    'website': 'http://www.mtlpcb.com/',
    'depends': ['base','sale','product','mrp','001_base','001_res_partners'],
    'init_xml': [],
    'data': [
                   
        
      
        'sale_order_new_view.xml',
        'sale_order_new_wkf.xml',
        'wizard/sale_order_new_line_wizard_view.xml',
        'frame_sale_order_view.xml',
        'frame_sale_order_wkf.xml',
        'contract_special_approval_view.xml',
 #       'contract_special_approval_wkf.xml',
     ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
    
}

