
# -*- coding: utf-8 -*-
##############################################################################

##############################################################################

{
    'name': '001_outsource',
    'version': '0.1',
    'category': 'MTL Modules/',
    'description': """outsource manager""",
    'author': 'oyhs',
    'website': 'http://www.mtlpcb.com/',
    'depends': ['base','product', 'hr','mrp'],
    'init_xml': [],
    'update_xml': [
     
       'outsource_process_view.xml',
       'outsource_chemical_process_view.xml',
	   'outsource_process_wkf.xml',
       'outsource_apply_wkf.xml',
       'outsource_duizhang_wkf.xml',

#       'outsource_delivery_wkf.xml',
      

	   
       
     ],
    'demo_xml': [],
    'test': [],
    'css' : ["static/src/css/outsource_process.css"],

    'installable': True,
    'active': False,
    'certificate': '',
}


