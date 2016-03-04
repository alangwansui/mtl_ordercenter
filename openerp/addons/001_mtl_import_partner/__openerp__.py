# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': '牧泰莱数据导入客户',
    'version': '1.0.1',
    'category': 'Generic Modules/Others',
    'description': """牧泰莱数据导入模块:
""",
    'author': 'MTL R&D',
    'website': 'http://www.mtlpcb.com/',
    'depends': ['base','product','hr'],
    'init_xml': [],
    'update_xml': [
        'import_partner_view.xml',
        'import_partner_data.xml',
        'import_partner_workflow.xml',
        'security/import_partner_security.xml',
        'security/ir.model.access.csv',
        'import_data_view.xml',
     ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': True,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
