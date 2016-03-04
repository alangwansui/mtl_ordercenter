
# -*- coding: utf-8 -*-
##############################################################################
#  'author': 'Roy',
#  'date'  :  2014-10-24

##############################################################################

{
    'name': '001_purchase',
    'version': '7.0.1',
    'category': 'MTL Modules/',
    'description': """some description for :""",
    'author': 'Roy',
    'website': 'http://www.mtlpcb.com/',
    'depends': ['base','001_product',],
    'init_xml': [],
    'data': [
             
             'unit_info_view.xml',
             'invoice_view.xml',
             'invoice_wkf.xml',
             'vendor_view.xml',
			 'supplier_product_view.xml',
			 'purchase_apply_view.xml',
             ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    
  
}