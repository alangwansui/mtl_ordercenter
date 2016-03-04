#!usr/bin/env python
# -*- coding:utf-8 -*-

from osv import  fields,osv
import datetime

class sequence(osv.osv):
    _name='sequence'
    _description='sequence'
    _columns={
             'name':fields.char(u'序号',size=32),
             'types':fields.char(u'类型',size=32),
             }
sequence()

class vendor(osv.osv):
    _name='vendor'
    _description='vendor of imformation'
   
    def _get_code(self,cr,uid,ids,field_name,args,context):
        if not ids:
            return []
        sequence_obj=self.pool.get('sequence')
        
        info=self.browse(cr,uid,ids[0])
        
        types=info.type
        print types,'types'
        sequence_ids=sequence_obj.search(cr,uid,[('types','=',types)])
        
        if not sequence_ids:
            sequence=1
            
        else:
           sequence_info=sequence_obj.browse(cr,uid,sequence_ids[0])
           sequence_name=sequence_info.name
           print sequence_name,'sequence_name'
           sequence=int(sequence_name[1:])+1
           
        zero=''
        
        for i in range(3-len(str(sequence))):
            zero='0'+zero
        code=types.upper()+zero+str(sequence)
        
        
        if  not sequence_ids:
            sequence_obj.create(cr,uid,{
                                        'name':code,
                                        'types':types
                                        })
        else:
            sequence_obj.write(cr,uid,sequence_ids[0],{'name':code})
            
        res=[]
        res.append((ids[0],code))
        return dict(res)
    
   
   
    _columns={
              'name':fields.char(u'供应商名称',size=64,required=True),
              'vendor_code':fields.function(_get_code,method=True,string=u'供应商代码',type='char',store=True,readonly=True),
              'type':fields.selection([('a','A'),('b','B'),('c','C'),('w',u'外协'),('s',u'服务')],u'类型',required=True),
              'region':fields.char(u'地区',size=32),
              'bank_name':fields.char(u'开户银行',size=64),
              'bank_code':fields.char(u'银行账号',size=32),
              'sale_mam':fields.char(u'业务员',size=32),
              'link_man':fields.char(u'联系人',size=32),
              'link_phone':fields.char(u'联系电话',size=64),
              'address':fields.char(u'地址',size=64),
              'fax_code':fields.char(u'传真',size=64),
              'mail_code':fields.char(u'邮箱',size=64),
              'zip_code':fields.char(u'邮编',size=32),
              'delivery_type':fields.char(u'交货方式',size=32),
              'payment_type':fields.char(u'付款方式',size=64),
              'business_goods':fields.char(u'经营产品种类',size=64),
              'note':fields.text(u'备注'),
              #'company':fields.selection([('szmtl',u'深圳牧泰莱'),('csmtl',u'长沙牧泰莱')],u'所属公司',required=True),
              }
    _sql_constraints = [('name', 'unique (name)', u'此供应商已经存在!'),('vendor_code','unique (vendor_code)', u'此供应商编码已经存在!')]
     
vendor()


