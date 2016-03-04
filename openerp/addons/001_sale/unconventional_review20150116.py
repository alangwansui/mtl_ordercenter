# -*- encoding: utf-8 -*-

from osv import osv,fields
import time
from tools.translate import _



class unconventional_review(osv.osv):
    _name='unconventional.review'
    _description='Unconventional review'
    _state_list=[('draft',u'草稿'),('w_eng',u'待工程'),('w_tech',u'待工艺'),('w_quality',u'待品质'),('w_material',u'待仓库'),('w_plan',u'待计划'),('w_ger_deparment',u'待总经办'),('w_order_center',u'待订单中心'),('done',u'完成'),('refuse',u'作废')]
 #   _state_list=[(i,i.title()) for i in _state_list] 
    _columns={
        'name'  :         fields.char('非常規单号',size=128,required=False),#非常規編號
        'pcb_info_id':    fields.many2one('pcb.info','用户单号',select=True),#單據編號
        'create_time':    fields.datetime('创建日期',readonly=True),#單據時間
        'partner_id':     fields.related('pcb_info_id','partner_id',type='many2one',relation='res.partners',string='客户',readonly=True),#客戶代號
        'file_name':      fields.char('文件名',size=128,required=False),#文件名
        'product_id':     fields.related('pcb_info_id','product_id',type='many2one',relation='product.product',string='档案号',readonly=True,select=True),#檔案號
        ##review_user:#經手人
        'order_qty':      fields.integer('订货数量'),#訂貨數量
        'delivery_time':  fields.datetime('交货日期'),#交貨日期
        'production_factory': fields.many2one('res.company','投产工厂'),#投產工廠
        'unconventional_note':fields.text('非常规描述'),#非常規描述
        'parameter_note':     fields.text('参数描述'),#参数描述
        'unconventional_review_ids':fields.one2many('unconventional.review.line','unconventional_review_id','Review info'),
        'state'        :   fields.selection(_state_list,'单据状态',readonly=True,size=64,select=True),
        'responsible_id':  fields.many2one('res.users','申请人'),#申请人
        
        'tech_review':      fields.boolean('工艺评审'), #工艺评审
        'quality_review':  fields.boolean('品质评审'),# 品质评审
        'material_review':fields.boolean('物料评审'),#物料评审
        'plan_review':      fields.boolean('计划评审'),# 计划评审
      
    }
    _defaults={
        'name':lambda self,cr,uid,c: self.pool.get('ir.sequence').get(cr,uid,'unconventional.review'),
        'state' :lambda *a:'draft',
		'responsible_id':lambda  self,cr,uid,c: uid,
        'create_time':lambda *a: time.strftime('%Y-%m-%d'),
    }
    def review_condition(self,cr,uid,ids,trans_list=None,context=None):
        return True
    def next_dpt_is(self,cr,uid,ids,dpt_name=None,context=None):
        my=self.browse(cr, uid, ids[0])
        review_line_obj=self.pool.get('unconventional.review.line')
        
        next_line_search=review_line_obj.search(cr,uid,[('unconventional_review_id','=',my.id),('state','!=','done')],order='id')
        next_line_id=next_line_search and next_line_search[0] or False
        
        if next_line_id:
            next_dpt_name=review_line_obj.browse(cr,uid,next_line_id,).department_id.name
            if next_dpt_name == dpt_name:
                return True
        return False
    
    def review_dpt_is(self,cr,uid,ids, list_tqmp=None,context=None):
        
        """  True is need ,False is not need, NOne is not matter   list_tqmp=[True, False, None, None]
        """
        
        if list_tqmp is None: return False
        
        my = self.browse(cr, uid, ids[0],)
        
        my_tqmp =[ my.tech_review , my.quality_review, my.material_review, my.plan_review ]
        
        res=True
        
        for i in range(4):
            if list_tqmp[i] is None:
                pass
            else:
                if list_tqmp[i] != my_tqmp[i]:
                    res=False
                    
        return res
            

                
                
            
        
        
        
    
 
unconventional_review()    
  
class unconventional_review_line(osv.osv):
    _name='unconventional.review.line'
    _description='review line'
    _columns={
        'state':                          fields.selection([('draft','草稿'),('done','完成')],'单据状态', size=32,),
        'unconventional_review_id':       fields.many2one('unconventional.review','Review id'),
        'department_id':                  fields.many2one('hr.department','评审部门'),#評審部門
        'department_requirement':         fields.many2many('hr.department','department_info_ids','unconventional_review_id','department_id','Department requirement'),
        'review_date':                    fields.datetime('评审时间'),#評審時間
        'review_users_id':                fields.many2one('res.users','评审人'),#評審人
        'review_note':                    fields.text('评审记录'),
        'ok_desgin_requirement':          fields.boolean('是否滿足合同特殊設計'),#是否滿足合同特殊設計/工藝要求
        'is_need_other_dpt':              fields.boolean('是否需要其他部門評審'),#是否需要其他部門評審
        'is_limit_example':               fields.boolean('是否限于樣品加工'),#是否限于樣品加工
        'ok_create_project':              fields.boolean('是否需要申請研發立項'),#是否需要申請研發立項
        'ok_meet_quality':                fields.boolean('是否滿足特殊品質要求'),#是否滿足特殊品質要求
        'ok_meet_material':               fields.boolean('是否滿足特殊物料要求'),#是否滿足特殊物料要求
        'ok_delivery_time':               fields.boolean('是否滿足特殊交貨期'),#是否滿足特殊交貨期
        'ok_final_affirm':                fields.boolean('是否最終確認'),#是否最終確認
    }
  
    _defaults={
        'department_id': lambda self,cr,uid,context,: context.get('department_id'),
        'state': lambda *a: 'draft',
    }
    def write_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done','review_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        

        
unconventional_review_line()