#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
from decimal_precision import decimal_precision as dp
import xmlrpclib
import pymssql
from tools.translate import _





class res_partners (osv.osv):
    _name='res.partners'
    _description='Res Partners'
    _order='create_date desc'
   
    
    def _lang_get(self, cr, uid, context=None):
        lang_pool = self.pool.get('res.lang')
        ids = lang_pool.search(cr, uid, [], context=context)
        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res]
    
    def _currency_get(self,cr,uid,context=None):
       obj=self.pool.get('select.selection')
       ids=obj.search(cr,uid,[('type','=','currency')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]

    def _get_saleman(self,cr,uid,context=None):
        obj=self.pool.get('employee')
        ids=obj.search(cr,uid,[('is_saleman','=',False)],context=context)
        res=obj.read(cr,uid,ids,['employeename','employeename'],context)
        return [(r['employeename'],r['employeename'])for r in res]
   
   
   
   
        
    _columns={
              
        'name':fields.char(u'客户名称',size=128),
        'partner_code':fields.char(u'客户代号',size=32),
        'customer':fields.boolean(u'客户'),
        'supplier':fields.boolean(u'供应商'),
        'state':fields.selection([('draft',u'非正式'),('nomal',u'合格'),('done',u'正式'),('cancel',u'作废')],u'客户状态'),
        'lang': fields.selection(_lang_get, u'语言',
            help="If the selected language is loaded in the system, all documents related to this contact will be printed in this language. If not, it will be English."),
        'date': fields.date(u'创建日期', select=1),
        'responsible_name':fields.many2one('res.users', u'负责人'),
        'dept_id':fields.many2one('res.department',u'部门'),
#        'user_id': fields.many2one('employee', u'业务员'),
        'user_id':fields.selection(_get_saleman,u'业务员'),
        'street': fields.char(u'注册地址', size=128),
        'street2': fields.char(u'送货地址', size=128),
        'city': fields.char(u'城市', size=128),
        'email': fields.char(u'电子邮箱', size=240),
        'phone': fields.char(u'电话号码', size=64),
        'fax': fields.char(u'传真', size=64),
        'mobile': fields.char(u'手机号码', size=64),
        'pur_contact':fields.char(u'默认送货联系人',size=64),
        'pur_phone':fields.char(u'默认送货联系人电话',size=64),
        'eng_contact':fields.char(u'默认技术联系人',size=64),
        'eng_phone':fields.char(u'默认技术联系人电话',size=64),
        'payment':fields.many2one('account.payment.term',u'付款方式',),
        'settle':fields.many2one('payment.mode',u'结算方式'),
        'credit_limit':fields.float(u'信用额度'),
        'credit':fields.float(u'欠款期限/月'),
        'tax':fields.many2one('account.tax',u'发票类型'),
        'currency':fields.selection(_currency_get,u'币种'),
        'sale_company':fields.selection([('shenzhen_company',u'深圳公司'),('changsha_company',u'长沙公司')],u'销售公司'),
        'res_partner_contact_ids':fields.one2many('res.partner.contact','res_partner_contact_id',u'联系人'),
        'ds_code':fields.char(u'东烁系统代号id',size=32),
        
        'english_customer':fields.char(u'英文名称',size=128),
        'customer_type':fields.selection([('normal',u'普通'),('vip',u'VIP'),('important',u'重要')],string=u'客户级别'),
        'postcode':fields.char(u'邮编',size=32),
        'source_business':fields.selection([('telecom',u'电信'),('electronic',u'电子'),('communication','通讯'),('other','其他行业')],string=u'来源行业'),
        'manage_type':fields.selection([('keep',u'保守'),('unnormal',u'不定'),('active',u'积极'),('steady',u'踏实'),('opportunity',u'投机')],string=u'经营方式'),
        'credit_class':fields.char(u'信誉等级',size=128),
        'redemption_name':fields.char(u'放赎期',size=128),
        'publicity':fields.char(u'行业声望',size=128),
        'redemption_money':fields.float(u'放赎金额'),
        'register_money':fields.float(u'注册资金万'),
        'sale_money':fields.float(u'预计年订单额'),
        'enterprise_type':fields.selection([('state-run',u'国营'),(' public-run',u'民营')],string=u'企业性质'),
        'sale_dpt':fields.many2one('res.department',u'业务部门'),
        'sale_state':fields.selection([('grow',u'成长'),('low',u'衰退'),('danger',u'危险'),('normal',u'稳定'),('good',u'兴旺')],string=u'业务状况'),
        'product_type':fields.char(u'经营产品类型',size=128),
        'first_time':fields.date(u'首次拜访日期'),
        'finance_state':fields.char(u'财务现状',size=128),
        'market_power':fields.char(u'市场潜力',size=128),
        'carriage':fields.selection([('customer',u'买方负担'),('mtl',u'卖方负担'),('first_party',u'甲方负担'),('second_party',u'乙方负担')],string=u'运费负担'),
        'sale_company':fields.selection([('szmtl',u'深圳牧泰莱'),('csmtl',u'长沙牧泰莱'),('mtl',u'牧泰莱投资')],string=u'销售公司'),
        'production_company':fields.selection([('szmtl',u'深圳牧泰莱'),('csmtl',u'长沙牧泰莱'),('mtl',u'牧泰莱投资')],string=u'投产地'),
        'enterprise_eare':fields.char(u'营业面积',size=64),
        'employee_quantity':fields.char(u'员工数量',size=64),
        'saleman_note':fields.text(u'业务员评价'),
        'note':fields.text(u'附加信息'),
        'special_note':fields.text(u'特别注意'),
        'user_note':fields.text(u'用户注意'),
#################################################################################################
        'other_discount':      fields.float('other_discount',digits=(2,3)),
        'ready_discount':      fields.float('ready_discount',digits=(2,3)),
        'plot_discount':       fields.float('plot_discount',digits=(2,3)),
        'test_discount':       fields.float('test_discount',digits=(2,3)),
        'base_discount':       fields.float('base_discount',digits=(2,3)),
        'pcs_discount':        fields.float('pcs_discount',digits=(2,3)),#折扣信息
###########################################################################################       
        
    }
    _defaults = {
                 
                 'responsible_name':lambda obj, cr, uid, context: uid,
                 'state':lambda *a:'draft',
                 'date': fields.date.context_today,
                 
                 'other_discount': lambda  *a:1.0,
                 'ready_discount': lambda  *a:1.0,
                 'plot_discount':  lambda  *a:1.0,
                 'test_discount':  lambda  *a:1.0,
                 'base_discount':  lambda  *a:1.0,
                 'pcs_discount':   lambda  *a:1.0,#折扣信息
    }
    
    
#    _sql_constraints = [('partner_code', 'unique (partner_code)', u'客户代号不能有相同，只能是唯一的!'),    ]
    

######更新客户状态为作废！#########################
    def button_refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'}, context=context)


#################导入东烁客户资料##############
    def import_data(self, cr, uid, ids, context):
        my=self.browse(cr,uid,ids[0])
        obj = self.pool.get('res.partners')
        obj_line=self.pool.get('res.partner.contact')
        res_partner_contact_ids=my.res_partner_contact_ids
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        b=[]
        conn = pymssql.connect(server=server , user=user, password=passward,database=database)
        cur = conn.cursor()       
        print cur
        cur.execute('''select isnull(custmerTname,''),isnull(custmercode1,''),isnull(registaddr,''),isnull(deladdr,''),isnull(b.RegionName,'') as RegionName,isnull(LinkTel,''),isnull(EMailCode,''),isnull(FaxCode,''),a.CustmerCode, from VBcustmer a left join TBRegion b on a.Regioncode=b.regioncode where isnull(a.custmercode1,'')<>''  ''' ) 
        s=cur.fetchall()
        
        for row in s:
            #此行是作为一个变量i去把Unicode的打印出来的如u'\02343'里的把u删除掉！然后再去解码为gbk
            b.append([(''.join(map(lambda x: "%c" % ord(x), list(row[i]))).decode('gbk')) for i in range(len(row))])
        
        for row in b:  
                
                info_id=obj.create(cr,uid,{                                                                                                                 
                'name':row[0],
                'partner_code':row[1],
                'street':row[2],
                'street2':row[3],
                'city':row[4],
                'phone':row[5],
                'email':row[6],
                'fax':row[7],
                'ds_code':row[8],
                'customer':True,   
                
                    })
                print row[0],'name'
                
                cur.execute(''' select isnull(LinkmanName,'') as LinkmanName,isnull(Sex,'') as Sex,isnull(CustmerTName,'') as CustmerTName ,isnull(LinkTel,'') as LinkTel ,isnull(Faxcode,'') as Faxcode ,isnull(SendAddr,'') as SendAddr,case when isnull(IsDefault,0)=1 then '1' else '' end as IsDefault,CustmerCode from TCCustmerLinkman where CustmerCode='%s'  '''%row[8] ) 
                s1=cur.fetchall()
                c=[]
                for row1 in s1:
                    
                    c.append([(''.join(map(lambda x: "%c" % ord(x), list(row1[r]))).decode('gbk')) for r in range(len(row1))])
                for row1 in c:
                    print row1[0],'contact'
                    
                    obj_line.create(cr,uid,{
                            'res_partner_contact_id':info_id,
                             'contact':row1[0],
                             'gender':row1[1],
                             'company_name':row1[2],
                             'mobile':row1[3],
                             'fax':row1[4],
                             'street3':row1[5],
                             'defualt_connact':row1[6],
                             })
                    
        conn.commit()
        cur.close()
        conn.close()
        return True
        
        
#        通过搜索名称或代号查找客户
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
            if not args:
                args = []
            args = args[:]
            ids = []
            if name:
                ids = self.search(cr, user, [('partner_code', 'ilike', name)]+args, limit=limit, context=context)
                print ids,'ids'
                if not ids:
                    ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
                    print ids,'ids1'
            else:
                ids = self.search(cr, user, args, limit=limit, context=context)
            return self.name_get(cr, user, ids, context=context)
            
        
 
     
     
####################################################
################ 导入客户通用信息 ##########################
    def import_partner_general_data(self,cr, uid, ids, context):
        my=self.browse(cr,uid,ids[0])
        print my.partner_general_id.id,'id'
        obj=self.pool.get('partner.general.requirements')
        obj_line=self.pool.get('partner.general.requirements.line')
        partner_id=my.partner_general_id.id
        se=obj.browse(cr,uid,partner_id)
        print se,'se'
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        conn = pymssql.connect(server=server , user=user, password=passward,database=database)
        print conn,'conn'
        cur = conn.cursor()       
        print cur,'cur'
        sql='''select  Custmercode,case when isnull(IsGerber,0)=1 then '1' else ''end ,case when isnull(IsGangWang,0)=1 then '1' else ''end,
            case when isnull(IsSureGerber,0)=1 then '1' else ''end,case when isnull(IsDealECN,0)=1 then '1' else ''end,
            isnull(FColor,''),isnull(FType,''),isnull(ViaFType,''),isnull(CColor,''),isnull(PackingQty,0),isnull(BillMemo,''),isnull(Memo,''),isnull(Packingmemo,''),isnull(InvoiceMemo,''),isnull(ReportRequest,''),isnull(TagRequest,''),isnull(PackingType,'') 
                from TBProductionCust where billstate<>50 and isnull(custmercode,'') in(select custmercode from VBcustmer where isnull(custmercode1,'')<>'') '''

        cur.execute(sql)
        s=cur.fetchall()
        d=[]
        for row1 in s:
            #此行是作为一个变量i去把Unicode的打印出来的如u'\02343'里的把u删除掉！然后再去解码为gbk
            a=[]
            for i in range(len(row1)):
                type1=type(row1[1])
                print row1[1]
                if type(row1[i])==type1:
                    a.append((''.join(map(lambda x: "%c" % ord(x), list(row1[i]))).decode('gbk')))
                else:
                    a.append(row1[i])
            d.append(a)
        for row in d:
            code= self.search(cr,uid,[('ds_code','=',row[0])])[0]
            print code,'code',
            print row[5],'solder_colour'
              
            info_id=obj.create(cr,uid,{
                               'partner_id':code,
                               'provide_gerber':row[1],
                               'provide_steel_net':row[2],
                               'confirm_gerber':row[3],
                               'add_delivery_chapter':row[4],
                               'solder_colour':row[5],
                               'solder_variants':row[6],
                               'solder_via':row[7],
                               'silk_colour':row[8],
                               'per_quantity':row[9],
                               'normal_order_note':row[10],
                               'partner_special_request':row[11],
                               'packing_note':row[12],
                               'delivery_order_request':row[13],
                               })
            goods_label=len(row[14])
            mark_label=len(row[15])
            packing_label=len(row[16])
            obj_line.create(cr,uid,{
                                    'requirements_line':info_id,
                                    'goods_label':row[14],
                                    'mark_label':row[15],
                                    'packing_label':row[16],
                                    
                                    })
        
        return True
                                                   
    
         
     
     
     
     
     
     
     
     
     
     
     
     
     
res_partners()

class res_partner_contact(osv.osv):
    _name='res.partner.contact'
    _description='Res Partner Contact'
    
    _order = 'res_partner_contact_id'

    


    _columns={
              'res_partner_contact_id':fields.many2one('res.partners',u'客户',ondelete='cascade',select=True),
             
              'contact':fields.char(u'联系人',size=64,select=True),
              'email': fields.char(u'电子邮箱', size=240),
              'mobile': fields.char(u'电话', size=64),
              'fax':fields.char(u'传真',size=64),
              'sequence':fields.integer(u'序号'),
              'street3':fields.char(u'送货地址',size=128),
              'company_name':fields.char(u'客户全称',size=128,select=True),
              'type':fields.selection([('saler', u'业务员'), ('invoice', u'发票'),
                                   ('delivery', u'配送'), ('engineering', u'工程'),
                                   ('other', u'其他')],u'联系人类型'),
#              'gender':fields.selection([('male',u'男'),('female',u'女')],u'性别'),
              'gender':fields.selection([(u'男',u'男'),(u'女',u'女')],u'性别'),
              'defualt_connact':fields.boolean(u'默认联系人'),
              
              
              
              
              }
            
    
    _defaults={
               
            
             
              }
    
    def create(self,cr,uid,vals,context=None):
       super(res_partner_contact,self).create(cr,uid,vals,context=context)
       res_partner_contact_id=vals['res_partner_contact_id']
       print res_partner_contact_id
       line_id=self.search(cr,uid,[('res_partner_contact_id','=',res_partner_contact_id)])
       print line_id,'line_id'
       i=1
       for id in line_id:
           self.write(cr,uid,id,{'sequence':i})
           i=i+1
       
     
    def unlink(self,cr,uid,ids,context=None): 
       for id in ids:
           object=self.browse(cr,uid,id)
       res_partner_contact_id=object.res_partner_contact_id.id
       print res_partner_contact_id,'res_partner_contact_id'
       line_id=self.search(cr,uid,[('res_partner_contact_id','=',res_partner_contact_id),('id','!=',ids[0])])
       i=1
       for id in line_id:
           self.write(cr,uid,id,{'sequence':i})
           i=i+1
       return super(res_partner_contact,self).unlink(cr,uid,ids,context=context) 
    
    
res_partner_contact()
