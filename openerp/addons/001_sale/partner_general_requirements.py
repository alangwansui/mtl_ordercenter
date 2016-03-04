# -*- coding:utf-8 -*-
from osv import osv,fields
import time
import pymssql
from tools.translate import _
server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'

class  partner_general_requirements(osv.osv):
    _name='partner.general.requirements'
    _description='Partner general requirements'
    _inherit='pcb.info'
    _res_name='partner_id'
    _columns={ 
              
        'name':fields.char(u'通用信息名称',size=32),
        'partner_id':fields.many2one('res.partners',u'客户',readonly=True),
        'ref'                         :fields.related('partner_id','partner_code',type='char',relation='res.partners',string=u'客户代号'),                        
        'custmer_goodscode':fields.char(u'零件号',size=32),
        'partner_general_requirements_ids_one':fields.one2many('partner.general.requirements.line','requirements_line',u'选项'),
#        'state_time_ids':    fields.one2many('purchase.prlog','partner_general_requirements_id','Sate time'),#审批状态时间

    }
    _defaults={'name':None,}
    _sql_constraints=[('name','unique(name)','通用信息名称必须是唯一的!'),
                      ('partner_id','unique(partner_id)','客户通用信息必须是唯一的!'),
                      ]
    
    
    def import_data(self, cr, uid, ids, context):
        my=self.browse(cr,uid,ids[0])
        partner_obj = self.pool.get('res.partners')
        line_obj=self.pool.get('partner.general.requirements.line')
        server='192.168.10.2'
        user='sa'
        password='719799'
        database='mtlerp-running'
        
        b=[]
        conn = pymssql.connect(server=server , user=user, password=password,database=database)
        cur = conn.cursor()       
        
        sql=''' select CustmerCode,CustmerName,HandlerCode,Memo,
                CustmerTel,CustmerHandler,InvoiceMemo,BillMemo,
                IsDealECN,ViaFType,TagRequest,ReportRequest,PackingType,
                PackingMemo,PackingQty,FType,FColor,CColor,ResiLayer,BaseBoard,
                IsGerber,IsGangWang,IsSureGerber
                from VBProductionCust_OE  ''' 
        cur.execute(sql) 
        s=cur.fetchall()
        b=[]
        for row1 in s:
            a=[]
            print row1
            for i in range(len(row1)):
                type1=type(u'中文')
                
                if type(row1[i])==type1:
                    a.append((''.join(map(lambda x: "%c" % ord(x), list(row1[i]))).decode('gbk')))
                else:
                    a.append(row1[i])
            b.append(a)
        
        for row in b:  
                partner_ids=partner_obj.search(cr,uid,[('ds_code','=',row[0])])
                id=self.create(cr,uid,{
                                       'partner_id':partner_ids[0],
                                       'provide_gerber':row[20],
                                       'provide_steel_net':row[22],
                                       'confirm_gerber':row[21],
                                       'add_delivery_chapter':row[8],
                                       'solder_colour':row[16],
                                       'solder_type':row[15],
                                       'solder_via':row[9],
                                       'silk_colour':row[17],
                                       'per_quantity':row[14],
                                       'normal_order_note':row[7],
                                       'partner_special_request':row[3],
                                       'packing_note':row[13],
                                       'delivery_order_request':row[6],
                                       })
                line_obj.create(cr,uid,{
                                        'requirements_line':id,
                                        'mark_label':row[10],
                                        'goods_label':row[11],
                                        'packing_label':row[12],
                                        })
        conn.commit()
        cur.close()
        conn.close()
        return True
    
#-------------同步数据到东烁中--------------     
    def insert_to_ds(self,cr,uid,id,vals,context=None):  
        column=[]
        info=self.browse(cr,uid,id) 
        partners_obj=self.pool.get('res.partners')
        line_obj=self.pool.get('partner.general.requirements.line')
        line_ids=line_obj.search(cr,uid,[('requirements_line','=',info.id)])
        partner_info=partners_obj.browse(cr,uid,info.partner_id.id)
        info_mark=''
        info_goods=''
        info_packing=''
        for line_id in line_ids:
          line_info=line_obj.browse(cr,uid,line_id)
          if line_info.mark_label:
              info_mark=info_mark+line_info.mark_label+';'
          if line_info.goods_label:
              info_goods=info_goods+line_info.goods_label+';'
          if line_info.packing_label:
              info_packing=info_packing+line_info.packing_label+';'

        column.append('') 
        column.append(info.partner_special_request)  
        column.append(partner_info.name)
        column.append(partner_info.phone)                                 
        column.append(partner_info.pur_contact)
        column.append(partner_info.user_id)
        column.append(info_mark)
        column.append(info_goods)
        column.append(info_packing)
        column.append(info.packing_note)
        column.append(info.per_quantity)
        column.append(info.normal_order_note)
        column.append(info.add_delivery_chapter)
        column.append(info.delivery_order_request)
        column.append(info.solder_via)
        column.append(info.silk_colour)
        column.append('')
        column.append(info.solder_type)
        column.append(0)
        column.append(info.solder_colour)
        column.append(info.provide_gerber)
        column.append(info.confirm_gerber)
        column.append(info.provide_steel_net)
        column.append(partner_info.partner_code)
        column.append('create')
        row=[]
        se=partner_info.partner_code
        if not se:
                 raise osv.except_osv(_('Error!'),_(u'客户代码不存在，请检查！'))
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
            
            sql='''exec pp_TBProductionCust_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                               '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                               '%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk')
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'同步失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return id
    
    def create(self,cr,uid,vals,context=None):
       print 'partner.general.requirements','create'
       id=super(partner_general_requirements,self).create(cr,uid,vals,context=context)
       return self.insert_to_ds(cr,uid,id,vals,context=context)    
      
      
    def update_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
           info=self.browse(cr,uid,ids[0])
        else:
           info=self.browse(cr,uid,ids)
        print info.id
        partners_obj=self.pool.get('res.partners')
        line_obj=self.pool.get('partner.general.requirements.line')
        line_ids=line_obj.search(cr,uid,[('requirements_line','=',info.id)])
        
        partner_info=partners_obj.browse(cr,uid,info.partner_id.id)
        info_mark=''
        info_goods=''
        info_packing=''
        for line_id in line_ids:
          line_info=line_obj.browse(cr,uid,line_id)
          if line_info.mark_label:
              info_mark=info_mark+line_info.mark_label+';'
          if line_info.goods_label:
              info_goods=info_goods+line_info.goods_label+';'
          if line_info.packing_label:
              info_packing=info_packing+line_info.packing_label+';'

        column.append('') 
        column.append(info.partner_special_request)  
        column.append(partner_info.name)
        column.append(partner_info.phone)                                 
        column.append(partner_info.pur_contact)
        column.append(partner_info.user_id)
        column.append(info_mark)
        column.append(info_goods)
        column.append(info_packing)
        column.append(info.packing_note)
        column.append(info.per_quantity)
        column.append(info.normal_order_note)
        column.append(info.add_delivery_chapter)
        column.append(info.delivery_order_request)
        column.append(info.solder_via)
        column.append(info.silk_colour)
        column.append('')
        column.append(info.solder_type)
        column.append(0)
        column.append(info.solder_colour)
        column.append(info.provide_gerber)
        column.append(info.confirm_gerber)
        column.append(info.provide_steel_net)
        column.append(partner_info.partner_code)
        column.append('write')
        if not partner_info.partner_code:
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
            
            sql='''exec pp_TBProductionCust_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                               '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s', 
                                               '%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk')
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'同步失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return True
    
    def write(self,cr,uid,ids,vals,context=None):
        print 'partner_general_requirements','write'
        super(partner_general_requirements,self).write(cr,uid,ids,vals,context=None)
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
        partners_obj=self.pool.get('res.partners')
        line_obj=self.pool.get('partner.general.requirements.line')
        line_ids=line_obj.search(cr,uid,[('requirements_line','=',info.id)])
        partner_info=partners_obj.browse(cr,uid,info.partner_id.id)
        info_mark=''
        info_goods=''
        info_packing=''
        for line_id in line_ids:
          line_info=line_obj.browse(cr,uid,line_id)
          if line_info.mark_label:
              info_mark=info_mark+line_info.mark_label+';'
          if line_info.goods_label:
              info_goods=info_goods+line_info.goods_label+';'
          if line_info.packing_label:
              info_packing=info_packing+line_info.packing_label+';'

        column.append('') 
        column.append(info.partner_special_request)  
        column.append(partner_info.name)
        column.append(partner_info.phone)                                 
        column.append(partner_info.pur_contact)
        column.append(partner_info.user_id)
        column.append(info_mark)
        column.append(info_goods)
        column.append(info_packing)
        column.append(info.packing_note)
        column.append(info.per_quantity)
        column.append(info.normal_order_note)
        column.append(info.add_delivery_chapter)
        column.append(info.delivery_order_request)
        column.append(info.solder_via)
        column.append(info.silk_colour)
        column.append('')
        column.append(info.solder_type)
        column.append(0)
        column.append(info.solder_colour)
        column.append(info.provide_gerber)
        column.append(info.confirm_gerber)
        column.append(info.provide_steel_net)
        column.append(partner_info.partner_code)
        column.append('unlink')
        if not partner_info.partner_code:
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
            
            sql='''exec pp_TBProductionCust_OE '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                               '%d','%s','%s','%s','%s','%s','%s','%s','%s','%s', 
                                               '%s','%s','%s','%s','%s','' ''' %row
            print sql.encode('gbk')
            cur.execute(sql) 
        except:
           raise osv.except_osv(_('Error!'),_(u'同步失败，请检查数据是否正确！'))
        else:
            
            conn.commit()
            conn.close() 
            print u'更新成功'
        return True   
    
    def unlink(self,cr,uid,ids,context=None):
           print 'partner.general.requirements','unlink'
           self.delete_to_ds(cr,uid,ids,context=None)
           return super(partner_general_requirements,self).unlink(cr,uid,ids)   
    

                                                
    
partner_general_requirements()

#################################################################
#客户通用信息多选的项目是通过三个one2many的方法做框架，然后用selection方法去得到值！

class partner_general_requirements_line(osv.osv):
    _name='partner.general.requirements.line'
    ####搜索标记要求的类
    def _get_mark(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','mark_request')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    def _get_goods(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','request_with_goods')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]

    def _get_packing(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','packing_type')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    _columns={
              'requirements_line':fields.many2one('partner.general.requirements','requirements_line'),
           
              'mark_label':fields.selection(_get_mark,u'标记要求',),
              'goods_label':fields.selection(_get_goods,u'附货要求',),
              'packing_label':fields.selection(_get_packing,u'包装方式',),
              }
    
    
    
    
    
    
   
    
    
    
    
    
    
    
    
    
    
    
    
partner_general_requirements_line()





########################################################################################################

class select_selection(osv.osv):
    _inherit='select.selection'
    _columns={

        'request_with_goods_general_id':fields.many2one('partner.general.requirements', 'request_with_goods_general_id',readonly=True),
        'packing_type_general_id':fields.many2one('partner.general.requirements', 'packing_type_general_id',readonly=True),
        'mark_request_general_id': fields.many2one('partner.general.requirements', 'mark_request_general_id',readonly=True),

    }
select_selection()


class res_partners(osv.osv):
    _inherit='res.partners'
    _columns={
               'partner_general_id':fields.many2one('partner.general.requirements',u'客户通用信息',readonly=True),
              
              
              
              }
                  


    






