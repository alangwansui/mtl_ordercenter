#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv


class res_users(osv.osv):
    _inherit = 'res.users'
    _columns={
        'code':fields.char('code',size=256),
    }
res_users()