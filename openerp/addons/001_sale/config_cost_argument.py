#!usr/bin/python
# -*- coding -*-

from openerp.osv import osv,fields
import time

class config_cost_argument(osv.osv):
    _name='config.cost.argument'
    _inherit='pcb.cost.argument'
    _columns={}
config_cost_argument()