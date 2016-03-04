# -*- coding:utf-8 -*-

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
    "name" : "001_qingjia ",
    "version" : "0.1",
    "author" : "Wulf Chow",
    "category" : "Generic Modules/001_qingjia module",
    "website" : "http://www.openerp.com",
    "description": """  update view 
""",
    "depends" : ['base','hr','hr_holidays','mrp'],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    'qingjia_record_view.xml',
#                    'qingjia_record_wkf.xml',
                    'qingjia_calendar_view.xml',
                    'reward_punish_view.xml',
                    'reward_lines_wkf.xml',
                    'punish_lines_wkf.xml',
#                    'punish_lines_info_wkf.xml',
#                    'hr_employee_mtl_view.xml',
#                    'wizard/employee_job_view.xml',
#					'wizard/employee_info_search_view.xml',
#                    'wizard/punish_lines_filter_view.xml',
    ],
    "active": True,
    "test":[],
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

