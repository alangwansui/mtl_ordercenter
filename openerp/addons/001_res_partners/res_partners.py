#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
from decimal_precision import decimal_precision as dp
import xmlrpclib
import pymssql
from tools.translate import _
server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'
class sale_parameter(osv.osv):                
    _name="sale.parameter"
    _description="sale related of information"
   
    _type_list=[('manage_type',u'经营方式'),('enterprise_type',u'企业性质'),('customer_type',u'客户级别'),('source_business',u'来源行业'),('sale_state',u'业务状况'),('carriage',u'运费负担'),
                ('payment',u'付款方式'),('tax',u'发票类型'),('settle',u'结算方式'),('currency',u'币种'),('region',u'地点'),('delivery_way',u'交货方式')]
    

       
    _columns={
            'name':fields.char(u"名称",size=32),
            'type':fields.selection(_type_list,string=u'类型'),
              }
    _order='type'
    def sale_parameter_import(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('sale.parameter')
        server='192.168.10.2'
        user='sa'
        passward='719799'
        database='mtlerp-running'
        conn=pymssql.connect(server=server,user=user, password=passward,database=database)
        cur=conn.cursor()
        sql=''' select BasicDetailName as name, 'manage_type' as type  from TBBasicDetail where TypeCode = '64' union
                select BasicDetailName as name, 'enterprise_type' as type  from TBBasicDetail where TypeCode = '67'union
                select BasicDetailName as name, 'customer_type' as type  from TBBasicDetail where TypeCode = '63' union
                select BasicDetailName as name, 'source_business' as type  from TBBasicDetail where TypeCode = '59' union
                select BasicDetailName as name, 'sale_state' as type  from TBBasicDetail where TypeCode = '66' union
                select BasicDetailName as name, 'carriage' as type  from TBBasicDetail where TypeCode = '50'union
                select BasicDetailName as name, 'payment' as type  from TBBasicDetail where TypeCode = '48' union
                select BasicDetailName as name, 'tax' as type  from TBBasicDetail where TypeCode = '29' and ISDisplay = 1 union
                select BasicDetailName as name, 'settle' as type  from TBBasicDetail where TypeCode = '47'union
                select '人民币' as name,'currency' as type union
                select '美元' as name,'currency' as type union
                select '港币' as name,'currency' as type union
                select '英镑' as name,'currency' as type union
                select BasicDetailName as name, 'delivery_way' as type  from TBBasicDetail where TypeCode = '04' union
                select BasicDetailName as name, 'region' as type  from TBBasicDetail where TypeCode = '52'
                 ''' 
        cur.execute(sql)
        s=cur.fetchall()
        b=[]
        for row in s:
            b.append([(''.join(map(lambda x: "%c" % ord(x), list(row[i]))).decode('gbk')) for i in range(len(row))])
        for row in b:  
                info_id=obj.create(cr,uid,{                                                                                                                 
                'name':row[0],
                'type':row[1],
                    })

        conn.close()
                
        return True

sale_parameter()




class res_partners (osv.osv):
    _name='res.partners'
    _description='Res Partners'
    _order='create_date desc'
   
    
    def _lang_get(self, cr, uid, context=None):
        lang_pool = self.pool.get('res.lang')
        ids = lang_pool.search(cr, uid, [], context=context)
        res = lang_pool.read(cr, uid, ids, ['code', 'name'], context)
        return [(r['code'], r['name']) for r in res]
    
    def _manage_type_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','manage_type')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]

    def _enterprise_type_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','enterprise_type')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]
   
    def _customer_type_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','customer_type')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]
   
    def _source_business_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','source_business')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]  
   
    def _sale_state_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','sale_state')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]    

    def _carriage_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','carriage')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]  
   
    def _payment_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','payment')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]    
   
   
    def _tax_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','tax')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]
   
    def _settle_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','settle')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]   
   
   
    def _currency_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','currency')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]
    
    def _city_get(self,cr,uid,context=None):
       obj=self.pool.get('sale.parameter')
       ids=obj.search(cr,uid,[('type','=','city')],context=context)
       res=obj.read(cr,uid,ids,['name','name'],context)
       return [(r['name'],r['name'])for r in res]    
   
   
    def _get_saleman(self,cr,uid,context=None):
        obj=self.pool.get('employee')
        ids=obj.search(cr,uid,[('is_saleman','=',True)],context=context)
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
        'user_id':fields.selection(_get_saleman,u'业务员'),
        'street': fields.char(u'注册地址', size=128),
        'street2': fields.char(u'送货地址', size=128),
        'city': fields.char(u'城市', size=128),
        'email': fields.char(u'电子邮箱', size=240),
        'phone': fields.char(u'电话号码', size=64),
        'fax': fields.char(u'传真', size=64),
        'mobile': fields.char(u'手机号码', size=64),
        'pur_contact':fields.char(u'默认送货联系人',size=64),
        'pur_phone':fields.char(u'默认收货联系人电话',size=64),
        'eng_contact':fields.char(u'默认技术联系人',size=64),
        'eng_phone':fields.char(u'默认技术联系人电话',size=64),
        #'payment':fields.many2one('account.payment.term',u'付款方式',),_payment_get
        'payment':fields.selection(_payment_get,u'付款方式',),
        #'settle':fields.many2one('payment.mode',u'结算方式'),_settle_get
        'settle':fields.selection(_settle_get,u'结算方式'),
        'credit_limit':fields.float(u'信用额度'),
        'credit':fields.float(u'欠款期限/月'),
        #'tax':fields.many2one('account.tax',u'发票类型'),_tax_get
        'tax':fields.selection(_tax_get,u'发票类型'),
        'currency':fields.selection(_currency_get,u'币种'),
        'res_partner_contact_ids':fields.one2many('res.partner.contact','res_partner_contact_id',u'联系人'),
        'ds_code':fields.char(u'东烁系统代号id',size=32),
        
        'english_customer':fields.char(u'英文名称',size=128),
        'customer_type':fields.selection(_customer_type_get,string=u'客户级别'),
        'postcode':fields.char(u'邮编',size=32),
        'source_business':fields.selection(_source_business_get,string=u'来源行业'),
        'manage_type':fields.selection(_manage_type_get,string=u'经营方式'),
        'credit_class':fields.char(u'信誉等级',size=128),
        'redemption_name':fields.char(u'放赎期',size=128),
        'publicity':fields.char(u'行业声望',size=128),
        'redemption_money':fields.float(u'放赎金额'),
        'register_money':fields.float(u'注册资金万'),
        'sale_money':fields.float(u'预计年订单额'),
        'enterprise_type':fields.selection(_enterprise_type_get,string=u'企业性质'),
        'sale_dpt':fields.many2one('res.department',u'业务部门'),
        'sale_state':fields.selection(_sale_state_get,string=u'业务状况'),
        'product_type':fields.char(u'经营产品类型',size=128),
        'first_time':fields.date(u'首次拜访日期'),
        'finance_state':fields.char(u'财务现状',size=128),
        'market_power':fields.char(u'市场潜力',size=128),
        'carriage':fields.selection(_carriage_get,string=u'运费负担'),
        'sale_company':fields.selection([('SZMTL',u'深圳牧泰莱'),('CSMTL',u'长沙牧泰莱'),('MTL',u'牧泰莱投资')],string=u'销售公司'),
        'production_company':fields.selection([('SZMTL',u'深圳牧泰莱'),('CSMTL',u'长沙牧泰莱'),('MTL',u'牧泰莱投资')],string=u'投产地'),
        'enterprise_eare':fields.char(u'营业面积',size=64),
        'employee_quantity':fields.char(u'员工数量',size=64),
        'saleman_note':fields.text(u'业务员评价'),
        'note':fields.text(u'附加信息'),
        'special_note':fields.text(u'特别注意'),
        'user_note':fields.text(u'用户注意'),
        'is_company_price':fields.boolean(u'按公司标准价格计算溢价'),
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
        res_department_obj=self.pool.get('res.department')
        res_partner_contact_ids=my.res_partner_contact_ids
        server='192.168.10.2'
        user='sa'
        password='719799'
        database='mtlerp-running'
        
        b=[]
        conn = pymssql.connect(server=server , user=user, password=password,database=database)
        cur = conn.cursor()       
        print cur
        sql=''' select custmercode,CustmerTName,RegionName,LinkMan,LinkTel,handlername,FaxCode,WebCode,
                    EMailCode,ZipCode,DelAddr,WorkGoods,Memo,OtherInfo,RegistAddr,OperationState,
                    EmployeeQty,Area,IndustryCode,FromType,CustmerLevel,RegisterFund,RansomMoney,
                    RansomDay,VisitDay,FirstVisitDay,ManagementType,TradeCredit,MarketPotential,
                    GenerallyPayDate,FinanceState,ForecastOrder,CompanyKind,InvoiceType,OtherPayType,
                    CreditType,CreditAMT,PayCode,CustmerEName,OrderPayType,CustmerCode1,departmentname,PhaseFactory,
                    CustmerPhaseFactory from VBCustmerManage_OE  ''' 
        cur.execute(sql) 
        s=cur.fetchall()
        b=[]
        for row1 in s:
            a=[]
            for i in range(len(row1)):
                type1=type(u'中文')
                if type(row1[i])==type1 and row1:
                    a.append((''.join(map(lambda x: "%c" % ord(x), list(row1[i]))).decode('gbk')))
                else:
                    a.append(row1[i])
            b.append(a)
        
        for row in b:  
                print res_department_obj,'res_department_obj'
                res_department_ids=res_department_obj.search(cr,uid,[('name','like',row[41])])
                if res_department_ids:
                    res_department_id=res_department_ids[0]
                else:
                    res_department_id=53     #### id=53 的部门名称为空
                info_id=obj.create(cr,uid,{                                                                                                                 
                'ds_code':row[0],'name':row[1],'city':row[2],'pur_contact':row[3],
                'pur_phone':row[4],'user_id':row[5],'fax':row[6],'email':row[8],'postcode':row[9],'street2':row[10],
                'product_type':row[11],'saleman_note':row[12],'note':row[13],'street':row[14],'sale_state':row[15],
                'employee_quantity':row[16],'enterprise_eare':row[17],'source_business':row[18],'customer_type':row[20],
                'register_money':row[21],'redemption_money':row[22],'redemption_name':row[23],'first_time':row[25],
                'manage_type':row[26],'publicity':row[27],'market_power':row[28],'finance_state':row[30],'sale_money':row[31],
                'enterprise_type':row[32],'tax':row[33],'carriage':row[34],'credit_class':row[35],'credit_limit':row[36],
                'settle':row[37],'english_customer':row[38],'payment':row[39],'partner_code':row[40],'sale_dpt':res_department_id,
                'sale_company':row[42],'production_company':row[43],'customer':True,  
                    })
                print row[0],'name'
                
                cur.execute(''' select isnull(LinkmanName,'') as LinkmanName,isnull(Sex,'') as Sex,isnull(CustmerTName,'') as CustmerTName ,isnull(LinkTel,'') as LinkTel ,isnull(Faxcode,'') as Faxcode ,isnull(SendAddr,'') as SendAddr,case when isnull(IsDefault,0)=1 then '1' else '' end as IsDefault,CustmerCode from TCCustmerLinkman where CustmerCode='%s'  '''%row[0] ) 
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
                                                   
    
         
     
 
     
     
#----------------------数据写入东烁---------------------------------      
    def insert_to_ds(self,cr,uid,id,vals,context=None):  
        column=[]
        customer_type=''
        department_obj=self.pool.get('res.department')
        info=self.browse(cr,uid,id)
        if info.customer==True:
            customer_type='2001' 
        if info.supplier==True:
            customer_type='2002'  
        
        print info.sale_dpt.name,'info.sale_dpt.name'        
        column.append(info.name)
        column.append(info.name)
        column.append(info.city)
        column.append(info.pur_contact)
        column.append(info.phone)
        column.append(info.user_id)
        column.append(info.fax)
        column.append('')
        column.append(info.email)
        column.append(info.postcode)
        column.append(info.street2)
        column.append('')
        column.append(info.saleman_note)
        column.append(info.note)
        column.append(info.street)
        column.append(info.sale_state)
        column.append(info.employee_quantity)
        column.append(info.enterprise_eare)
        column.append(info.source_business)
        column.append('')
        column.append(info.customer_type)
        column.append(info.register_money)
        column.append(info.redemption_money)
        column.append(info.redemption_name)
        column.append(0)
        column.append(info.first_time)
        column.append(info.manage_type)
        column.append(info.publicity)
        column.append(info.market_power)
        column.append('')
        column.append(info.finance_state)
        column.append(info.sale_money)
        column.append(info.enterprise_type)
        column.append(info.tax)
        column.append(info.carriage)
        column.append(info.credit_class)
        column.append('')
        column.append('')
        column.append(info.settle)
        column.append(info.english_customer)
        column.append(customer_type)
        column.append(info.payment)
        column.append(info.partner_code)
        column.append(info.sale_dpt.name)
        column.append(info.sale_company)
        column.append(info.production_company)
        column.append('create')
        if not info.partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            sql='''exec PP_TBcustmer_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,%f,'%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,'%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)
            
            
        except:
           raise osv.except_osv(_('Error!'),_(u'同步数据失败,请检查！'))
        else:
            conn.commit()
            conn.close() 
            print u'同步成功'.encode('gbk')
        
        return id
    
    def create(self,cr,uid,vals,context=None):
       print 'res.partners','create'
       id=super(res_partners,self).create(cr,uid,vals,context=context)
       return self.insert_to_ds(cr,uid,id,vals,context=context) 
        
        
    def update_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
           info=self.browse(cr,uid,ids[0])
        else:
          info=self.browse(cr,uid,ids)
        if info.customer==True:
            customer_type='2001' 
        if info.supplier==True:
            customer_type='2002'        
        column.append(info.name)
        column.append(info.name)
        column.append(info.city)
        column.append(info.pur_contact)
        column.append(info.phone)
        column.append(info.user_id)
        column.append(info.fax)
        column.append('')
        column.append(info.email)
        column.append(info.postcode)
        column.append(info.street2)
        column.append('')
        column.append(info.saleman_note)
        column.append(info.note)
        column.append(info.street)
        column.append(info.sale_state)
        column.append(info.employee_quantity)
        column.append(info.enterprise_eare)
        column.append(info.source_business)
        column.append('')
        column.append(info.customer_type)
        column.append(info.register_money)
        column.append(info.redemption_money)
        column.append(info.redemption_name)
        column.append(0)
        column.append(info.first_time)
        column.append(info.manage_type)
        column.append(info.publicity)
        column.append(info.market_power)
        column.append('')
        column.append(info.finance_state)
        column.append(info.sale_money)
        column.append(info.enterprise_type)
        column.append(info.tax)
        column.append(info.carriage)
        column.append(info.credit_class)
        column.append('')
        column.append('')
        column.append(info.settle)
        column.append(info.english_customer)
        column.append(customer_type)
        column.append(info.payment)
        column.append(info.partner_code)
        column.append(info.sale_dpt.name)
        column.append(info.sale_company)
        column.append(info.production_company)
        column.append('write')
        if not info.partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            sql='''exec PP_TBcustmer_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,%f,'%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,'%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)
            
            
        except:
           raise osv.except_osv(_('Error!'),_(u'同步数据失败,请检查！'))
        else:
            conn.commit()
            conn.close() 
            print u'同步成功'.encode('gbk')
        return True  
          
          
    def write(self,cr,uid,ids,vals,context=None):
        print 'res.partners','write'
        super(res_partners,self).write(cr,uid,ids,vals,context=None)
        #self.update_to_ds(cr,uid,ids,context=None)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True   
    
    
    def delete_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
           info=self.browse(cr,uid,ids[0])
        else:
          info=self.browse(cr,uid,ids)
        if info.customer==True:
            customer_type='2001' 
        if info.supplier==True:
            customer_type='2002'        
        column.append(info.name)
        column.append(info.name)
        column.append(info.city)
        column.append(info.pur_contact)
        column.append(info.phone)
        column.append(info.user_id)
        column.append(info.fax)
        column.append('')
        column.append(info.email)
        column.append(info.postcode)
        column.append(info.street2)
        column.append('')
        column.append(info.saleman_note)
        column.append(info.note)
        column.append(info.street)
        column.append(info.sale_state)
        column.append(info.employee_quantity)
        column.append(info.enterprise_eare)
        column.append(info.source_business)
        column.append('')
        column.append(info.customer_type)
        column.append(info.register_money)
        column.append(info.redemption_money)
        column.append(info.redemption_name)
        column.append(0)
        column.append(info.first_time)
        column.append(info.manage_type)
        column.append(info.publicity)
        column.append(info.market_power)
        column.append('')
        column.append(info.finance_state)
        column.append(info.sale_money)
        column.append(info.enterprise_type)
        column.append(info.tax)
        column.append(info.carriage)
        column.append(info.credit_class)
        column.append('')
        column.append('')
        column.append(info.settle)
        column.append(info.english_customer)
        column.append(customer_type)
        column.append(info.payment)
        column.append(info.partner_code)
        column.append(info.sale_dpt.name)
        column.append(info.sale_company)
        column.append(info.production_company)
        column.append('unlink')
        if not info.partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)
        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            sql='''exec PP_TBcustmer_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,%f,'%s','%s','%s','%s','%s','%s','%s',
                                             '%s',%f,'%s','%s','%s','%s','%s','%s','%s','%s',
                                             '%s','%s','%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk'),'sql'
            cur.execute(sql)
            
            
        except:
           raise osv.except_osv(_('Error!'),_(u'删除数据失败,请检查！'))
        else:
            conn.commit()
            conn.close() 
            print u'同步成功'.encode('gbk')
        return True
      
    def unlink(self,cr,uid,ids,context=None):
           print 'res.partners','unlink'
           self.delete_to_ds(cr,uid,ids,context=None)
           return super(res_partners,self).unlink(cr,uid,ids)     
     
     
     
     
     
     
res_partners()

class res_partner_contact(osv.osv):
    _name='res.partner.contact'
    _description='Res Partner Contact'
    
    _order = 'res_partner_contact_id'

    _rec_name="contact"


    _columns={
              'res_partner_contact_id':fields.many2one('res.partners',u'客户',ondelete='cascade',select=True),
              'ref':fields.related('res_partner_contact_id','partner_code',relation='res.partners',string='客户代码',type='char',store=True,readonly=True),
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
    

       
       
#        通过搜索名称或代号查找联系人
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
            if not args:
                args = []
            args = args[:]
            ids = []
            if name:
                ids = self.search(cr, user, [('ref', operator, name)]+args, limit=limit, context=context)
                print ids,'ids'
                if not ids:
                    ids = self.search(cr, user, [('contact', operator, name)]+ args, limit=limit, context=context)
                    print ids,'ids1'
            else:
                ids = self.search(cr, user, args, limit=limit, context=context)
            return self.name_get(cr, user, ids, context=context)
     
     
   # def unlink(self,cr,uid,ids,context=None): 
   #    for id in ids:
   #        object=self.browse(cr,uid,id)
   #    res_partner_contact_id=object.res_partner_contact_id.id
   #    print res_partner_contact_id,'res_partner_contact_id'
   #    line_id=self.search(cr,uid,[('res_partner_contact_id','=',res_partner_contact_id),('id','!=',ids[0])])
   #    i=1
   #    for id in line_id:
    #       self.write(cr,uid,id,{'sequence':i})
   #        i=i+1
   #    return super(res_partner_contact,self).unlink(cr,uid,ids,context=context) 

    def insert_to_ds(self,cr,uid,id,vals,context=None):
        column=[]
        info=self.browse(cr,uid,id)
        partner_obj=self.pool.get('res.partners')
        partner_info=partner_obj.browse(cr,uid,info.res_partner_contact_id.id)
        partner_code=partner_info.partner_code
        column=[]
        column.append(partner_code)
        column.append(info.contact)
        column.append(info.gender)
        column.append(info.company_name)
        column.append(info.mobile)
        column.append(info.email)
        column.append(info.street3)
        column.append(info.defualt_connact)
        column.append('create')
        if not partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        print column
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)

        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            
            sql='''exec pp_TCCustmerLinkman_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','' ''' %row
            sql=sql.decode('utf-8')
            print sql
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return id
    
    def create(self,cr,uid,vals,context=None):
       print 'res_partner_contact','create'
       id=super(res_partner_contact,self).create(cr,uid,vals,context=context)
       res_partner_contact_id=vals['res_partner_contact_id']
       print res_partner_contact_id
       line_id=self.search(cr,uid,[('res_partner_contact_id','=',res_partner_contact_id)])
       print line_id,'line_id'
       i=1
       #self.insert_to_ds(cr,uid,id,vals,context=None)
       for id in line_id:
           self.write(cr,uid,id,{'sequence':i})
           i=i+1
       return self.insert_to_ds(cr,uid,id,vals,context=None)
       

    def update_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
           info=self.browse(cr,uid,ids[0])
        else:
          info=self.browse(cr,uid,ids)
        partner_obj=self.pool.get('res.partners')
        partner_info=partner_obj.browse(cr,uid,info.res_partner_contact_id.id)
        partner_code=partner_info.partner_code
        column=[]
        column.append(partner_code)
        column.append(info.contact)
        column.append(info.gender)
        column.append(info.company_name)
        column.append(info.mobile)
        column.append(info.email)
        column.append(info.street3)
        column.append(info.defualt_connact)
        column.append('write')
        if not partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        print column
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)

        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            
            sql='''exec pp_TCCustmerLinkman_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','' ''' %row
            sql=sql.decode('utf-8')
            print sql
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return True
    def write(self,cr,uid,ids,vals,context=None):
        print 'res.partners','write'
        super(res_partner_contact,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True
        
    def delete_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
           info=self.browse(cr,uid,ids[0])
        else:
          info=self.browse(cr,uid,ids)
        partner_obj=self.pool.get('res.partners')
        partner_info=partner_obj.browse(cr,uid,info.res_partner_contact_id.id)
        partner_code=partner_info.partner_code
        column=[]
        column.append(partner_code)
        column.append(info.contact)
        column.append(info.gender)
        column.append(info.company_name)
        column.append(info.mobile)
        column.append(info.email)
        column.append(info.street3)
        column.append(info.defualt_connact)
        column.append('unlink')
        print column
        if not partner_code:
            raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
        row=[]
        for i in range(len(column)):
            if type(column[i])==type(u'中文'):
                print column[i]
                row.append((column[i]).encode('utf-8'))
            else:
                row.append(column[i])    
        row=tuple(row)

        try:
            conn=pymssql.connect(server=server,user=user,password=password,database=database)
            cur=conn.cursor()
            
            sql='''exec pp_TCCustmerLinkman_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','' ''' %row
            sql=sql.decode('utf-8')
            print sql
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return True
          
    def unlink(self,cr,uid,ids,context=None):
           print 'res.partners','unlink'
           self.delete_to_ds(cr,uid,ids,context=None)
           return super(res_partner_contact,self).unlink(cr,uid,ids)

    
res_partner_contact()



