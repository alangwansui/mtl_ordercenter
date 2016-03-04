# -*- coding: utf-8 -*-
##############################################################################
#  'author': 'Wulf Chow',
#  'date'  :  2012-4-16
#  'maile' :   <alangwansui at gmail.com>
##############################################################################

{
    'name': '001 sale',
    'version': '8.0.1',
    'category': 'MTL Modules/',
    'description': """some description for :""",
    'author': 'Roy',
    'website': 'http://www.mtlpcb.com/',
    'depends': ['base','sale','product','mrp','001_base','001_sale_order'],
    'init_xml': [],
    'data': [
                   

        'order_recive_view.xml',
        'order_recive_wkf.xml',  
        'pcb_info_view.xml',
        'pcb_info_wkf.xml',
        'price_sheet_view.xml',
        'partner_general_requirements_view.xml',
 #       'price_sheet_wkf.xml',
		'wizard/res_partners_general_wizard_view.xml',
        'wizard/partner_general_wizard_view.xml',
        'config_cost_argument_view.xml',        
        'sale_order_change_view.xml',
#        'sale_order_change_wkf.xml',
        'technology_capabilities_parameter_view.xml',
        'impdance_view.xml',
        'res_users_view.xml',
        'unconventional_review_view.xml',
        'unconventional_review_wkf.xml',
        'pcb_code_view.xml',
        'security/sales_security.xml',
        'security/ir.model.access.csv'
     ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
    'certificate': '',
    
}

