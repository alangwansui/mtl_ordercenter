#!/usr/bin/python
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

from osv import fields, osv
from tools.translate import _
import time
import _mssql

#先导入 l10n_cn中文基础模块，确保省市都导进去后，再来开始导，才能成功
#对象改了字段名，可能影响数据库运行，如果那样则应该删除数据表
#加上以下内容，否则在centos下中文运行有问题
import sys
reload(sys)
sys.setdefaultencoding('utf8')
#centos

#报表中文乱码问题的解决方案
#http://openerp-china.org/blog/space.php?uid=169&do=blog&id=174
#http://shine-it.net/index.php?topic=2314.0


class hr_department(osv.osv):
    _description = "Department"
    _inherit = 'hr.department'
    _columns = {       
     'dpt_code': fields.char('dpt_code', size=256),     
     'ref2': fields.char('ref2', size=256),  
  } 

hr_department()


#===============================================================================
#      
# class product_product(osv.osv):  
#    _name = 'product.product'  
#    _inherit = 'hr.department'  
#    _description = 'Product'  
#    _columns = {  
#        'pic':fields.binary('Pic'),   
#    }  
#    
# product_product()
#===============================================================================

    
class import_partner(osv.osv):
    _name = "import.partner"
    _description = "客户导入"


    #def _auto_init(self, cursor, context=None):
    #    return
    
        
    _columns = {
        'server': fields.char('服务器', size=64, required=True, select=True),
        'user': fields.char('用户名', size=256, required=True, select=True),
        'password': fields.char('密码', size=256, required=True, select=True),
        'database': fields.char('数据库', size=256, required=True, select=True),
        'sqlrequery': fields.text('查询语句'),
        'type': fields.selection([('customer','客户'),('supplier','供应商'),('department','部门'),\
                                  ('employee','职员'),('group','用户组'),\
                                  ('user','用户'),('production','产品')], '导入类型'),
        'result':  fields.text('查询结果语句')
    }
    _defaults = {
        'server': lambda *a:'192.168.0.2',
        'user': lambda *a: 'sa',
        'password': lambda *a: '719799',
        'database': lambda *a:'mtltest',
        'sqlrequery': lambda *a:'SELECT top 10 * FROM tblog order by id desc'
    }
     
    def gb2312ToUtf8(self,strtemp):
          if strtemp is None:
              return ''
          strtemp = strtemp.decode('gb2312')
          strtemp = strtemp.encode('utf-8')
          strtemp = strtemp.strip();  
          return strtemp       
  
    def get_city(self, cr, uid, ids, context, strtemp):
        obj_country_state= self.pool.get('res.country.state')
        strleftaddr = strtemp
        strprovince = ""
        strcity = ""
        #默认一个省，不能是空，否则报错
        state_id = self.pool.get('res.country.state').search(cr, uid, [("name",'=','广东省')],context=context)[0]
        #company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳市牧泰莱电路%')],context=context)[0]
        #isfind = False
        if(strleftaddr.decode('utf-8').find('深圳') > -1):
            strprovince = '广东省'
            strcity = '深圳市'
            #state_id = 67
            return (strprovince,strcity,state_id)
        state_ids =  obj_country_state.search(cr, uid, [("country_id",'=',46)],context=context)
        states = obj_country_state.browse(cr, uid, state_ids, context=context)
        for state in states:           
            pos=strleftaddr.decode('utf-8').find(state.name)
            if(pos>-1):
                state_id = state.id
                pos+=len(state.name)
                strprovince = state.name
                #strleftaddr=straddress[pos:len(strleftaddr)]
                if(state.name.decode('utf-8').find('市') > -1):
                    strcity = strprovince
                    return (strprovince,strcity,state_id)
                strleftaddr=strleftaddr.decode('utf-8')[pos:len(strleftaddr)].encode('utf-8')
                break
                #isfind = True   
        pos=strleftaddr.decode('utf-8').find('市')
        if(pos>-1):
            pos+=1
            strcity = strleftaddr.decode('utf-8')[0:pos].encode('utf-8')
            #strleftaddr=strleftaddr.decode('utf-8')[pos:len(strleftaddr)].encode('utf-8') 
        print strprovince,strcity           
        return (strprovince,strcity,state_id)

  
      
    def import_customer(self, cr, uid, ids, context,t):
        obj_partener = self.pool.get('res.partner')
        obj_partener_contact = self.pool.get('res.partner.contact')
        obj_partener_address = self.pool.get('res.partner.address')
        obj_partener_job = self.pool.get('res.partner.job')    
        obj_country_state= self.pool.get('res.country.state')  
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],\
                              database=t['database'])            
        #conn.execute_query(t['sqlreqery'])     
        #conn = _mssql.connect(server='192.168.0.2', user='sa', password='719799',\
        #          database='mtltest')
          #=================================================================
          # SELECT  TOP (10) id, BillCode, CustmerCode, CustmerCode1, CustmerName, CustmerTName, CustmerEName, CustmerClass, CustmerType, CurrencyCode, 
          # PayCode, FiscalType, RegionCode, HandlerCode, CreditType, CreditAMT, TaxKind, TaxCode, TaxType, TaxRate, BankName, BankCode, BossName, 
          # LinkMan, LinkTel, LinkMobil, FaxCode, ZipCode, EMailCode, RegistAddr, DelAddr, WebCode, PassWord, StateCode, OrganizationCode, Memo, 
          # HandleDeptCode, OtherInfo, GoodsCheckDay, OrderPayDay, PCustmerCode, IsCreditControl, PaymentType, EmployeeQty, Area, IndustryCode, 
          # FromType, CustmerLevel, RegisterFund, RansomMoney, RansomDay, VisitDay, FirstVisitDay, ManagementType, OperationState, TradeCredit, 
          # MarketPotential, GenerallyPayDate, FinanceState, ForecastOrder, CompanyKind, CreateDate, PassDate, ShipType, WorkGoods, OtherPayType, 
          # InvoiceType, OrderPayType, FastQuery, IsLocked
          # FROM         TBCustmer
          #=================================================================
        #conn.execute_query('SELECT top 5 * FROM tbcustmer where len(CustmerCode1)>0 order by id desc')     
        #conn.execute_query('SELECT  *\
        #               FROM TBCustmer\
        #               WHERE  (CustmerClass = ''2001'') AND (cast(CustmerCode1 as int) > 0)\
        #                AND (cast(CustmerCode1 as int) < 100) ORDER BY CAST(CustmerCode1 AS int)')  
        conn.execute_query('SELECT top 1 * FROM tbcustmer where CustmerCode1=''008''')
        #conn.execute_query('SELECT  top 10 *\
        #                FROM TBCustmer\
        #                WHERE  (CustmerClass = ''2001'') AND (cast(CustmerCode1 as int) > 0)\
        #                ORDER BY CAST(CustmerCode1 AS int)')
        for row in conn:
            print "ID=%d" % (row['id'])
            mstrtemp = import_partner.gb2312ToUtf8(self,row['CustmerName'])
            mstrtemp1 = import_partner.gb2312ToUtf8(self,row['CustmerTName'])
            mstrtemp2 = import_partner.gb2312ToUtf8(self,row['CustmerCode'])
            mstrtemp3 = import_partner.gb2312ToUtf8(self,row['CustmerCode1'])
            mstrtemp4 = import_partner.gb2312ToUtf8(self,row['ZipCode'])
            mstrtemp5 = import_partner.gb2312ToUtf8(self,row['RegistAddr'])
            mstrtemp6 = import_partner.gb2312ToUtf8(self,row['DelAddr'])
            mstrtemp7 = import_partner.gb2312ToUtf8(self,row['LinkMan'])
            mstrtemp8 = import_partner.gb2312ToUtf8(self,row['LinkTel'])
            mstrtemp9 = import_partner.gb2312ToUtf8(self,row['LinkMobil'])
            mstrtemp10 = import_partner.gb2312ToUtf8(self,row['FaxCode'])
            mstrtemp11 = import_partner.gb2312ToUtf8(self,row['EMailCode'])
            mstrtemp12 = import_partner.gb2312ToUtf8(self,row['WebCode'])
            mstrtemp13 = import_partner.gb2312ToUtf8(self,row['HandlerCode']) #业务员
            #print strlogcontent
            print "ID=%d, Name=%s" % (row['id'], mstrtemp)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp1)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp2)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp3)
            partner_id = obj_partener.create(cr, uid, {
                'name': mstrtemp,
                'ref': mstrtemp3,
                'user_id': uid,
                'ean13': mstrtemp2, #此字段暂存系统客户代号
                'website': mstrtemp12, 
                'customer':True,   
                'supplier':False,
                'comment': mstrtemp1,
             })
            if(len(mstrtemp6)>0):#添加默认发货地址
                 strprovince,strcity,stateid=import_partner.get_city(self, cr, uid, ids, context,mstrtemp5)
                 address_id = obj_partener_address.create(cr, uid, {
                                'partner_id': partner_id,
                                'name': mstrtemp7,
                                'phone': mstrtemp8,
                                'mobile': mstrtemp9,                        
                                'email': mstrtemp11,
                                'fax': mstrtemp10,
                                'title': '',
                                'type': 'delivery', #default,contact，invoice，delivery，other
                                'street': mstrtemp6,
                                'street2': mstrtemp5, 
                                'zip': mstrtemp4,
                                'city': strcity,
                                'state_id':stateid, 
                                'country_id': '46'
                            })  
            #===============================================================
            # SELECT  TOP (10) id, CustmerCode, CustmerName, CustmerTName, LinkmanCode, LinkmanName, Sex, DepartmentName, IDCardCode, WorkerType, EmailCode, 
            #      LinkTel, FaxCode, LinkMobil, OICQ, Ethnic, HomeAddr, Age, LastLinkDate, Birthday, IsDefault, iid, CreateDate, Memo, SendAddr
            # FROM         TCCustmerLinkman
            #===============================================================
            conn1 = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],\
                              database=t['database'])     
            conn1.execute_query('SELECT * FROM TCCustmerLinkman WHERE CustmerCode=%s order by isdefault  desc', mstrtemp2)
            #conn.execute_query('SELECT * FROM  TCCustmerLinkman WHERE CustmerCode = \'%s\'',strtemp2) 
            #self.cr.execute('SELECT period_id, journal_id FROM account_journal_period WHERE id IN %s', (tuple(new_ids),))
            default_address_id=-1;
            for row1 in conn1:
                #===========================================================
                # contact_id = contact_obj.create(cr, uid, {
                #        'partner_id': partner_id,
                #        'name': lead.contact_name,
                #        'phone': lead.phone,
                #        'mobile': lead.mobile,
                #        'email': lead.email_from,
                #        'fax': lead.fax,
                #        'title': lead.title and lead.title.id or False,
                #        'function': lead.function,
                #        'street': lead.street,
                #        'street2': lead.street2,
                #        'zip': lead.zip,
                #        'city': lead.city,
                #        'country_id': lead.country_id and lead.country_id.id or False,
                #        'state_id': lead.state_id and lead.state_id.id or False,
                #    })
                #===========================================================
                #print "ID=%d, Name=%s" % (row['id'], row['LogContent'])    
                strtemp1 = import_partner.gb2312ToUtf8(self,row1['LinkmanName'])
                strtemp2 = import_partner.gb2312ToUtf8(self,row1['LinkMobil'])
                strtemp3 = import_partner.gb2312ToUtf8(self,row1['LinkTel'])
                strtemp4 = import_partner.gb2312ToUtf8(self,row1['SendAddr'])
                strtemp5 = import_partner.gb2312ToUtf8(self,row1['EmailCode'])
                strtemp6 = row1['FaxCode']
                strtemp7 = import_partner.gb2312ToUtf8(self,row1['Sex'])
                strtemp8 = row1['Birthday']
                strtemp9 = row1['IsDefault']   
                strtemp10 = import_partner.gb2312ToUtf8(self,row1['DepartmentName'])
                strtemp11 = import_partner.gb2312ToUtf8(self,row1['Memo'])
                strfunction = '采购员'
                if(len(strtemp10)>0):
                    strfunction = strtemp10
                strsex = 5         
                if(strtemp7.find('女')>=0):
                     strsex = 3   
                if(strtemp1.find('先生')>=0):
                     strsex = 5   
                if(strtemp1.find('女士')>=0):
                     strsex = 3 
                if(strtemp1.find('小姐')>=0):
                     strsex = 4   
                contact_id = obj_partener_contact.create(cr, uid, {
                        'partner_id': partner_id,
                        'name': strtemp1,
                        'phone': strtemp3,
                        'birthdate': strtemp8,
                        'title': strsex,     #5先生 3女士  
                        'comment': strtemp11,
                        'website': mstrtemp12,                       
                        'mobile': strtemp2
                    })
                strdefault='other'
                if(strtemp9): #如果是默认地址,地址必须存在
                    strdefault='default'
                    if(len(strtemp4) == 0):# < 2): #为空时度为1
                        strtemp4=mstrtemp5
                #elif(len(strtemp4) == 0):#如果不是默认地址，且送货地址为空
                #    strtemp4=mstrtemp6
                #    strdefault='delivery'
                if(len(strtemp4) > 0): #如果地址为空，则不添加地址
                    strprovince=''
                    strcity=''
                    strprovince,strcity,stateid=import_partner.get_city(self, cr, uid, ids, context,strtemp4)
                    #product_price_type_ids = product_price_type_obj.search(cr, uid, [('field','=','standard_price')], context=context)
                    #pricetype = product_price_type_obj.browse(cr, uid, product_price_type_ids, context=context)[0]
                    #ids = self.search(cr, user, [('code', '=like', name+"%")]+args, limit=limit)
                    #state_ids =  obj_country_state.search(cr, uid, [("name",'=like',strprovince+"%")],context=context)   
                    #stateid=obj_country_state.
                    address_id = obj_partener_address.create(cr, uid, {
                            'partner_id': partner_id,
                            'name': strtemp1,
                            'phone': strtemp3,
                            'mobile': strtemp2,                        
                            'email': strtemp5,
                            'fax': strtemp6,
                            'title': '',
                            'type': strdefault, #default,contact，invoice，delivery，other
                            'city': strcity,
                            'street': strtemp4,
                            'street2': mstrtemp6, #第二地址全选为送货地址
                            'zip': '',
                            'city': strcity,
                            'state_id':stateid, 
                            'country_id': '46'
                        })  
                if(strtemp9):
                    default_address_id=address_id;   
                #所有联系人默认都往默认地址中增加   
                if(default_address_id>=0):
                    job_id = obj_partener_job.create(cr, uid, {
                            'address_id': default_address_id,
                            'contact_id': contact_id,
                            'email': strtemp5,
                            'function': strfunction,
                            'phone': strtemp3,   
                            'other': strtemp11,                         
                            'state': 'current'
                        })            
                print "ID=%d, Name=%s" % (row1['id'], strtemp1)
                print "ID=%d, Name=%s" % (row1['id'], strtemp2)
                print "ID=%d, Name=%s" % (row1['id'], strtemp3) 
            conn1.close()          
            default_address_id=-1;
        conn.close()   
            
    def import_supplier(self, cr, uid, ids, context,t):
        pass
        obj_partener = self.pool.get('res.partner')
        obj_partener_contact = self.pool.get('res.partner.contact')
        obj_partener_address = self.pool.get('res.partner.address')
        obj_partener_job = self.pool.get('res.partner.job')    
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],\
                              database=t['database'])            
        #conn.execute_query(t['sqlreqery'])     
        #conn = _mssql.connect(server='192.168.0.2', user='sa', password='719799',\
        #          database='mtltest')
          #=================================================================
          # SELECT  TOP (10) id, BillCode, CustmerCode, CustmerCode1, CustmerName, CustmerTName, CustmerEName, CustmerClass, CustmerType, CurrencyCode, 
          # PayCode, FiscalType, RegionCode, HandlerCode, CreditType, CreditAMT, TaxKind, TaxCode, TaxType, TaxRate, BankName, BankCode, BossName, 
          # LinkMan, LinkTel, LinkMobil, FaxCode, ZipCode, EMailCode, RegistAddr, DelAddr, WebCode, PassWord, StateCode, OrganizationCode, Memo, 
          # HandleDeptCode, OtherInfo, GoodsCheckDay, OrderPayDay, PCustmerCode, IsCreditControl, PaymentType, EmployeeQty, Area, IndustryCode, 
          # FromType, CustmerLevel, RegisterFund, RansomMoney, RansomDay, VisitDay, FirstVisitDay, ManagementType, OperationState, TradeCredit, 
          # MarketPotential, GenerallyPayDate, FinanceState, ForecastOrder, CompanyKind, CreateDate, PassDate, ShipType, WorkGoods, OtherPayType, 
          # InvoiceType, OrderPayType, FastQuery, IsLocked
          # FROM         TBCustmer
          #=================================================================
        #conn.execute_query('SELECT top 5 * FROM tbcustmer where len(CustmerCode1)>0 order by id desc')
        conn.execute_query('SELECT  * FROM TBCustmer\
               WHERE  (CustmerClass = ''2002'') AND (CustmerCode >= \'G001\')\
                AND (CustmerCode < \'G021\')')  
                       
        #conn.execute_query('SELECT top 1 * FROM tbcustmer where CustmerCode=\'G004\'')
        #conn.execute_query('SELECT  top 10 *\
        #                FROM TBCustmer\
        #                WHERE  (CustmerClass = ''2002'') AND (cast(CustmerCode1 as int) > 0)\
        #                ORDER BY CAST(CustmerCode1 AS int)')
        for row in conn:
            print "ID=%d" % (row['id'])
            mstrtemp = import_partner.gb2312ToUtf8(self,row['CustmerName'])
            mstrtemp1 = import_partner.gb2312ToUtf8(self,row['CustmerTName'])
            mstrtemp2 = import_partner.gb2312ToUtf8(self,row['CustmerCode'])
            mstrtemp3 = import_partner.gb2312ToUtf8(self,row['CustmerCode1'])
            mstrtemp4 = import_partner.gb2312ToUtf8(self,row['ZipCode'])
            mstrtemp5 = import_partner.gb2312ToUtf8(self,row['RegistAddr'])
            mstrtemp6 = import_partner.gb2312ToUtf8(self,row['DelAddr'])
            mstrtemp7 = import_partner.gb2312ToUtf8(self,row['LinkMan'])
            mstrtemp8 = import_partner.gb2312ToUtf8(self,row['LinkTel'])
            mstrtemp9 = import_partner.gb2312ToUtf8(self,row['LinkMobil'])
            mstrtemp10 = import_partner.gb2312ToUtf8(self,row['FaxCode'])
            mstrtemp11 = import_partner.gb2312ToUtf8(self,row['EMailCode'])
            mstrtemp12 = import_partner.gb2312ToUtf8(self,row['WebCode'])
            mstrtemp13 = import_partner.gb2312ToUtf8(self,row['HandlerCode']) #业务员
            #print strlogcontent
            print "ID=%d, Name=%s" % (row['id'], mstrtemp)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp1)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp2)
            print "ID=%d, Name=%s" % (row['id'], mstrtemp3)
            partner_id = obj_partener.create(cr, uid, {
                'name': mstrtemp,
                'ref': mstrtemp2,#此字段暂存系统客户代号
                'user_id': uid,
                'customer':False,   
                'supplier':True,
                'ean13': mstrtemp3, 
                'website': mstrtemp12,    
                'comment': mstrtemp1,
             })
            strprovince,strcity,stateid=import_partner.get_city(self, cr, uid, ids, context,mstrtemp5)
            address_id = obj_partener_address.create(cr, uid, {
                                'partner_id': partner_id,
                                'name': mstrtemp7,
                                'phone': mstrtemp8,
                                'mobile': mstrtemp9,                        
                                'email': mstrtemp11,
                                'fax': mstrtemp10,
                                'title': '',
                                'type': 'default', #default,contact，invoice，delivery，other
                                'street': mstrtemp5,
                                'street2': mstrtemp6, 
                                'zip': mstrtemp4,
                                'city': strcity,
                                'state_id':stateid, 
                                'country_id': '46'
                            })  
            strfunction = '业务员'
            strsex = 5         
            if(mstrtemp7.find('女')>=0):
                 strsex = 3   
            if(mstrtemp7.find('先生')>=0):
                 strsex = 5   
            if(mstrtemp7.find('女士')>=0):
                 strsex = 3 
            if(mstrtemp7.find('小姐')>=0):
                 strsex = 4   
            contact_id = obj_partener_contact.create(cr, uid, {
                    'partner_id': partner_id,
                    'name': mstrtemp7,
                    'phone': mstrtemp8,
                    'title': strsex,     #5先生 3女士  
                    #'comment': strtemp11,
                    'website': mstrtemp12,                       
                    'mobile': mstrtemp9
                })
            strdefault='other'
            job_id = obj_partener_job.create(cr, uid, {
                          'address_id': address_id,
                          'contact_id': contact_id,
                          'email': mstrtemp11,
                          'function': strfunction,
                          'phone': mstrtemp8,   
                          #'other': strtemp11,                         
                          'state': 'current'
                      })                   
        conn.close()      

    def import_department(self, cr, uid, ids, context,t,departid,parentid,companyid):
        
        obj_dept = self.pool.get('hr.department')
        
        #obj_user = self.pool.get('res.users')
                        
        #SELECT     id, DepartmentCode, DepartmentName, IdLevel, ParentId, DepartmentType, DepartmentManager, DefaultFetcherCode, Telephone, Address, StateCode, 
        #              OrganizationCode, Memo, ParentCode
       # FROM         dbo.TBDepartment
        #company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳市牧泰莱电路%')],context=context)[0]   
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],\
                              database=t['database'])            
        conn.execute_query('SELECT  * FROM TBDepartment where ParentId = \'%d\'',departid)
        departids_dict = {}
        
        if (departid==-1):
            mstrtemp1=''
       
   
        
        for row in conn:
            print "ID=%d" % (row['id'])
            mstrtemp1 = import_partner.gb2312ToUtf8(self,row['DepartmentCode'])
            mstrtemp2 = import_partner.gb2312ToUtf8(self,row['DepartmentName'])
            mstrtemp3 = row['IdLevel']
            mstrtemp4 = row['ParentId']
            mstrtemp5 = import_partner.gb2312ToUtf8(self,row['DepartmentType'])
            mstrtemp6 = import_partner.gb2312ToUtf8(self,row['DepartmentManager'])
            mstrtemp7 = import_partner.gb2312ToUtf8(self,row['Telephone'])
            mstrtemp8 = import_partner.gb2312ToUtf8(self,row['Address'])
            mstrtemp9 = import_partner.gb2312ToUtf8(self,row['Memo'])
            
            #print strlogcontent
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp1)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp2)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp3)
            
            print parentid
            print mstrtemp2
            print mstrtemp4
            #company_id = -1
            departmentid = obj_dept.create(cr, uid, {
                'name': mstrtemp2,
                'note': mstrtemp8,#此字段暂存部门代号
                'parent_id':parentid,
                'company_id':companyid, 
                'dpt_code':mstrtemp1,     
                'manager_id':False
             })            
            import_partner.import_department(self, cr, uid, ids, context,t,row['id'],departmentid,companyid)
        conn.close()      
              
         
    def import_employee(self, cr, uid, ids, context,t,companyid=1):   
        obj_partener = self.pool.get('res.partner')
        obj_partener_address = self.pool.get('res.partner.address')     
        obj_dept = self.pool.get('hr.department')        
        obj_empl = self.pool.get('hr.employee')
        #职员的姓名存放位置
        obj_resource = self.pool.get('resource.resource')
        #职员的岗位存放位置
        obj_job = self.pool.get('hr.job')
        #职员的地址存放位置
        obj_address = self.pool.get('res.partner.address')
        #obj_user = self.pool.get('res.users')
                        
        #SELECT  TOP (1) id, EmployeeCode, EmployeeName, EmployeeEName, Sex, IDCardCode, Birthday, BirthPlace, MarriageState, Diploma, TechnicalTitle, Ethnic,
                      # Politic, HealthyState, RegionCode, DepartmentCode, WorkerType, EmployeeType, WorkStartDate, EMailCode, DwellingPlace, StateCode, IsExport,
                      # Memo, BasicSalary, Telephone, HomeTel, MobileTelephone, CodeName, Specialty, WorkEndDate, ERPPassWord, DimissionType, ImageContent,
                      # ContractDate, ContractOverDate, IsOldInsurance, IsSocialCard, BillCode, EmpCompany
        #           FROM  TBEmployee
        company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳市牧泰莱电路%')],context=context)[0]   
        conn = _mssql.connect(server=t['server'] , user=t['user'], password=t['password'],\
                              database=t['database'])            
        conn.execute_query('SELECT TOP (1)  * FROM TBEmployee' )
        ##conn.execute_query('SELECT TOP (1)  * FROM TBEmployee where DepartmentCode = \'%s\'',dptcode)
        departids_dict = {}
        for row in conn:
            print "ID=%d" % (row['id'])
            mstrtemp1 = import_partner.gb2312ToUtf8(self,row['EmployeeCode'])
            print mstrtemp1
            mstrtemp2 = import_partner.gb2312ToUtf8(self,row['EmployeeName'])
            print mstrtemp2
            #mstrtemp3 = row['IdLevel']
            #mstrtemp4 = row['ParentId']
            mstrtemp5 = import_partner.gb2312ToUtf8(self,row['Sex'])
            mstrtemp6 = import_partner.gb2312ToUtf8(self,row['IDCardCode'])
            #mstrtemp7 = import_partner.gb2312ToUtf8(self,row['Telephone'])
            #mstrtemp8 = import_partner.gb2312ToUtf8(self,row['Address'])
            #mstrtemp9 = import_partner.gb2312ToUtf8(self,row['Memo'])
            mstrtemp10 = row['Birthday']
            mstrtemp11 = import_partner.gb2312ToUtf8(self,row['MarriageState'])
            mstrtemp12 = import_partner.gb2312ToUtf8(self,row['Diploma'])
            print mstrtemp12
            mstrtemp13 = import_partner.gb2312ToUtf8(self,row['TechnicalTitle'])
            mstrtemp14 = import_partner.gb2312ToUtf8(self,row['Ethnic'])
            mstrtemp15 = import_partner.gb2312ToUtf8(self,row['Politic'])
            mstrtemp16 = import_partner.gb2312ToUtf8(self,row['HealthyState'])
            mstrtemp17 = import_partner.gb2312ToUtf8(self,row['Politic'])        
            mstrtemp18 = import_partner.gb2312ToUtf8(self,row['HealthyState'])   
            mstrtemp19 = import_partner.gb2312ToUtf8(self,row['RegionCode'])
            mstrtemp20 = import_partner.gb2312ToUtf8(self,row['DepartmentCode'])
            mstrtemp21 = import_partner.gb2312ToUtf8(self,row['WorkerType'])
            print mstrtemp21
            mstrtemp22 = import_partner.gb2312ToUtf8(self,row['EmployeeType'])
            print mstrtemp22
            mstrtemp23 = row['WorkStartDate']
            mstrtemp24 = import_partner.gb2312ToUtf8(self,row['EMailCode'])
            mstrtemp25 = import_partner.gb2312ToUtf8(self,row['DwellingPlace'])
            mstrtemp26 = import_partner.gb2312ToUtf8(self,row['StateCode'])
            mstrtemp27 = row['IsExport']
            mstrtemp28 = row['ContractDate']
            mstrtemp29 = import_partner.gb2312ToUtf8(self,row['Memo'])
            mstrtemp30 = row['BasicSalary']
            mstrtemp31 = import_partner.gb2312ToUtf8(self,row['Telephone'])
            mstrtemp32 = import_partner.gb2312ToUtf8(self,row['HomeTel'])
            #mstrtemp33 = import_partner.gb2312ToUtf8(self,row['Politic'])        
            mstrtemp34 = import_partner.gb2312ToUtf8(self,row['HomeTel'])   
            mstrtemp35 = import_partner.gb2312ToUtf8(self,row['CodeName'])
            mstrtemp36 = import_partner.gb2312ToUtf8(self,row['Specialty'])
            mstrtemp37 = row['WorkEndDate']
            mstrtemp38 = row['ERPPassWord']
            mstrtemp39 = import_partner.gb2312ToUtf8(self,row['DimissionType'])
            mstrtemp40 = row['ContractOverDate']
            mstrtemp41 = row['IsOldInsurance']
            mstrtemp42 = row['IsSocialCard']
            mstrtemp43 = import_partner.gb2312ToUtf8(self,row['BillCode'])        
            mstrtemp44 = row['EmpCompany']
            #print strlogcontent
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp1)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp2)
            #print "ID=%d, Name=%s" % (row['id'], mstrtemp3)
            
            parent_id = departids_dict.get(mstrtemp4,False)
            print parent_id
            print mstrtemp2
            print mstrtemp4
            #company_id = -1
            empl_resource_id = obj_resource.create(cr, uid, {
                'name': mstrtemp2,
                'resource_type':'user',
                'time_efficiency':1,
                'company_id':companyid,
                'active':True,
             }) 
            manager_id = False
            empl_id = obj_empl.create(cr, uid, {
                'name': mstrtemp2,
                'note': mstrtemp8,#此字段暂存部门代号
                'parent_id':parent_id,
                'company_id':companyid,  
                'place_of_birth':'user', 
                'resource_id':empl_resource_id, 
                'manager_id':manager_id
             }) 
            import_partner.import_department_sub(self, cr, uid, ids, context,t,row['id'],department_id,company_id)              
            #departids_dict[row['id']] = department_id
            #print departids_dict[row['id']]
        conn.close()   
          
    def action_draft(self, cr, uid, ids, context=None):
       if context is None:
            context = {}
       company_id = self.pool.get('res.company').search(cr, uid, [("name",'like','%深圳市牧泰莱电路%')],context=context)[0] 
       qjds = self.read(cr, uid, ids,['server','user','password','database','type','sqlreqery'], context=context)   
       unlink_ids = []
       for t in qjds:       
            if(t['type'] == 'customer'):
                import_partner.import_customer(self, cr, uid, ids,context,t)
            elif(t['type'] == 'supplier'):
                import_partner.import_supplier(self, cr, uid, ids,context,t)
            elif(t['type'] == 'department'):
                import_partner.import_department(self, cr, uid, ids, context,t,-1,False,company_id)               
            elif(t['type'] == 'employee'):
                import_partner.import_employee(self, cr, uid, ids,context,t,companyid=1)
            elif(t['type'] == 'group'):
                import_partner.import_supplier(self, cr, uid, ids,context,t)
            elif(t['type'] == 'user'):
                import_partner.import_supplier(self, cr, uid, ids,context,t)
            elif(t['type'] == 'production'):
                import_partner.import_supplier(self, cr, uid, ids,context,t)                       
       return True  
   
  
   
    
import_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
