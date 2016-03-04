# -*- encoding: utf-8 -*-
from osv import fields, osv
import time
from decimal_precision import decimal_precision as dp
from tools.translate import _
import pymssql
server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'

class price_calculate(object):
    def __init__(self,value=0,info=''):
        self.value=value
        self.info=info
     
    def add(self,add_value=0,domain=None):
        self.value+=add_value
        self.info+='vale+%s; domain=%s \n' % (add_value, str(domain),)
        


class price_sheet (osv.osv):

    _name='price.sheet'
    _order = "name desc"

    
    def _cost_fun(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        my=self.browse(cr, uid, ids[0], context)
        for sheet in self.browse(cr, uid, ids, context):
            if field_name=='cost_all_o':
                if sheet.discount:
                    res[sheet.id]=(sheet.cost_pcs_s * sheet.product_number  +  sheet.cost_ready_s + sheet.cost_plot_s  + sheet.cost_test_s + sheet.cost_days_s + sheet.cost_other_s+sheet.cost_gold_finger_s)* (1 - sheet.discount/100)
                else:
                    res[sheet.id]=(sheet.cost_pcs_s * sheet.product_number  +  sheet.cost_ready_s + sheet.cost_plot_s  + sheet.cost_test_s + sheet.cost_days_s + sheet.cost_other_s+sheet.cost_gold_finger_s)
            if field_name=='cost_price_s':
                res[sheet.id]= sheet.cost_all_o / sheet.product_number
            if field_name=='cost_once':
                res[sheet.id]=sheet.cost_ready_s + sheet.cost_plot_s  + sheet.cost_test_s + sheet.cost_days_s + sheet.cost_other_s
        return res
    
    def _info_get(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        for id in ids:
            my=self.browse(cr, uid, id, context,)
#            print  my.pcb_info_id.pcb_info_many,'id'
#            pcb_info=my.pcb_info_id
            pcb_info=my.pcb_info_id
            pcb_info_line=pcb_info.pcb_info_many
            if field_name == 'po_area':
                res[id]=pcb_info.pcs_area * my.product_number/10000

            if field_name == 'type':   #('normal_sample','normal_mass','hdi', 'rigid_flexible', 'special_matrial',)
#                names=[line.name for line in pcb_info.special_process]
                names=[line.special_process for line in pcb_info_line]
                print names,'names'
                if my.po_area > 1:
                    print my.po_area,'po_area'
                    res[id]='normal_mass'
                else:
                    res[id]='normal_sample'
                    
                #特殊板材    
                #material_text=' '.join( [line.name for line in pcb_info.board_material])
                #if 'ptfe' in material_text or 'al' in material_text or 'ro' in material_text:
                #    res[id]= 'special_matrial'
                print [line.is_specia_material for line in pcb_info_line]
                
                if True in [line.is_specia_material for line in pcb_info_line]:
                    res[id]= 'special_matrial'
                    
                if 'hdi' in names:
                    res[id]='hdi'
                
                if True in [line.is_rigid_flexible for line in pcb_info_line]:
                    res[id]='rigid_flexible'
            
            
                #===============================================================
                # res[id]=my.po_area > 1 and 'normal_mass' or 'normal_sample'
                # label_ls=[board.label for board in pcb_info.board_material]
                # #if pcb_info.board_material.name in ['al_base','ro4350','ro4003','ptfe']:
                # for name in label_ls:
                #    if name in ['al_base','ro4350','ro4003','ptfe']:
                #        res[id]='special'
                # ## 特殊工艺的价格计算 hdi  type 中是否包含hdi
                # 
                # if pcb_info.special_process:
                #    res[id]='hdi'
                # #if pcb_info.special_process.name=='hdi':
                # #    res[id]='hdi'
                #===============================================================
#===============================================================================
#            if field_name == 'standard_days':
#                
#                #特殊材料，参考材料种类，和层数
#                c_standard_days=[]
#                if my.type == 'special_matrial': 
#                    c_standard_days=[
#                        ('type','=',my.type),
#                        ('cost_type','=','standard_days'),
#                        ('layer_count','=',pcb_info.layer_count),
#                        ('material_category','=',pcb_info.board_material[0].id ),
#                    ]                    
#                #普通版，参考 层数
#                else:
#                    #批量，样板，都有面积,  hid与刚柔结合 参考 样板
#                    c_type= my.type in ['hdi', 'rigid_flexible'] and 'normal_sample' or my.type 
#                    c_standard_days=[
#                         ('type','=',c_type),
#                         ('layer_count','=',pcb_info.layer_count),
#                         ('cost_type','=','standard_days'),
#                         ('po_area_max','>',my.po_area),
#                         ('po_area_min','<',my.po_area),  
#                    ]
# 
#                standard_days=self._get_arg(cr,uid,ids,c_standard_days,'v',)
#                cu_max=self.pool.get('pcb.info').get_cu_thickness_max(cr,uid,pcb_info)
#                
#                #厚铜增加
#                if cu_max > 2:
#                    standard_days += cu_max - 1
#                # 盘中孔增加
#                if 'via_in_pad' in [line.name for line in pcb_info.special_process]:#
#                    standard_days +=2
#                    
#                # 盲埋孔增加
#                if pcb_info.blind_buried_via_ids:
#                    for line in pcb_info.blind_buried_via_ids:
#                        #双层盲 +1
#                        if abs(line.end -line.start)==1:
#                            standard_days+=1
#                        #多层盲+2
#                        else:
#                            standard_days+=2
#                            
#                            
#                res[id]= standard_days      
#===============================================================================

        return res
  
    
    _columns = {
        'name'          :fields.char(u'报价单号', size=64 , require=True,readonly=False,select=True), 
        'state'         :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('wait_sale_manager',u'待销售经理'),('wait_general_manager','待总经办'),('wait_customer_back',u'待客户回签'),('done',u'完成'),('cancel',u'作废'),('wait_change',u'待更改')],u'单据状态',select=True),
        'temp_state':fields.char('Temp state',size=64),
        'responsible_id':fields.many2one('res.users',u'负责人', size=16, required=True, select=True,domain=[('context_department_id','=','订单中心')]),
        'create_time'   :fields.date(u"创建日期", readonly=True),
#        'lead_id'       :fields.many2one('order.recive',u'接单'),
        'delivery_date':fields.date(u'交货日期'),
        'pcb_info_id'   :fields.many2one( 'pcb.info', u'用户单号', required=True ,domain=[('state','=','done')],readonly=True),
        'lead_id'       :fields.related('pcb_info_id','order_recive_id',type='many2one',relation='order.recive',string=u'接单单号',select=True,store=True),
        'partner_id'    :fields.related('pcb_info_id', 'partner_id', type='many2one',relation='res.partners', string=u'客户',readonly=True,select=True,store=True), 
        'product_id'    :fields.related('pcb_info_id', 'product_id', type='char',relation='pcb.info', string=u'档案号',readonly=True,select=True,store=True),
        'standard_days':fields.integer(u'标准天数'),
        'product_number':fields.integer( u'报价数量',required=True,),#报价数量
        'delivery_leadtime'           :fields.float( u'交货周期',required=True,),#交货周期 
        ##客户专用价格 
        'cost_ready'                  :fields.float( u'准备费', digits_compute=dp.get_precision('Account'), readonly=True), #工程准备费用
        'cost_plot'                   :fields.float( u'菲林费',  digits_compute=dp.get_precision('Account'),readonly=True),  #菲林费
        'cost_test'                   :fields.float( u'测试费',  digits_compute=dp.get_precision('Account'),readonly=True),  #测试费
        'cost_pack'                   :fields.float( u'打包费',  digits_compute=dp.get_precision('Account'),readonly=True),  #工程打包费
        'cost_base'                   :fields.float( u'基板费',  digits_compute=dp.get_precision('Account'),readonly=True),  #基础板费
        'cost_mould'                  :fields.float( u'磨具费', digits_compute=dp.get_precision('Account'),readonly=True),  #磨具费用
        'cost_change'                 :fields.float( u'变更费',digits_compute=dp.get_precision('Account'),readonly=True), #变更费用
        'cost_other'                  :fields.float( u'其他费', digits_compute=dp.get_precision('Account'),readonly=True),  #其他费用
        'cost_days'                   :fields.float( u'加急费',  digits_compute=dp.get_precision('Account'),readonly=True),  #加急费用
        'cost_gold_finger'         :fields.float( u'金手指费',  digits_compute=dp.get_precision('Account'),readonly=True),  #金手指费用
        'cost_pcs'                    :fields.float( u'pcs单价',   digits_compute=dp.get_precision('Account'),readonly=True),  #pcs单价
        'cost_sqcm'                   :fields.float( u'平方厘米价',  digits=(12,5),readonly=True),
        'cost_all'                    :fields.float( u'费用汇总',   digits_compute=dp.get_precision('Account'),readonly=True),  #费用记总
        'note'                        :fields.text(u'备注'),     
        ##实际价格   
        'cost_ready_s'                  :fields.float( u'准备费', digits_compute=dp.get_precision('Account'),change_default=True, readonly=False), #工程准备费用
        'cost_plot_s'                   :fields.float( u'菲林费',  digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #菲林费
        'cost_test_s'                   :fields.float( u'测试费',  digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #测试费
        'cost_pack_s'                   :fields.float( u'打包费',  digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #工程打包费
        'cost_base_s'                   :fields.float( u'基板费',  digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #基础板费
        'cost_mould_s'                  :fields.float( u'磨具费', digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #磨具费用
        'cost_change_s'                 :fields.float( u'变更费',digits_compute=dp.get_precision('Account'),change_default=True,readonly=False), #变更费用
        'cost_other_s'                  :fields.float( u'其他费', digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #其他费用
        'cost_days_s'                   :fields.float( u'加急费',  digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #加急费用
        'cost_gold_finger_s'         :fields.float( u'金手指费',  digits_compute=dp.get_precision('Account'),readonly=True),  #金手指费用
        'cost_pcs_s'                    :fields.float( u'pcs单价',   digits_compute=dp.get_precision('Account'),change_default=True,readonly=False),  #pcs单价
         ##折扣信息
        'discount':fields.float(u'折扣率(unit:%)'),#折扣率
        'mantissa':fields.float(u'去掉尾数'),#尾数
        'cost_all_o'                    :fields.function(_cost_fun,  method=True, type='float',  string=u"实际合同总额", readonly=True,store=True), #原合同总价
        'cost_all_s'                    :fields.float(u'标准合同总额',   digits_compute=dp.get_precision('Account'),change_default=True,readonly=False), #折扣合同总价
        'cost_price_s'                  :fields.function(_cost_fun,  method=True, type='float',  string=u"单价", readonly=True,store=True), #合同总价
        
        ##标准价格
        'cost_ready_b':             fields.float( u'准备费', digits_compute=dp.get_precision('Account'), readonly=True), #工程准备费用
        'cost_plot_b':                fields.float( u'菲林费',  digits_compute=dp.get_precision('Account'),readonly=True),  #菲林费
        'cost_test_b':                fields.float( u'测试费',  digits_compute=dp.get_precision('Account'),readonly=True),  #测试费
        'cost_other_b':              fields.float( u'其他费', digits_compute=dp.get_precision('Account'),readonly=True),  #其他费用
        'cost_pcs_b':                 fields.float( u'pcs单价',   igits_compute=dp.get_precision('Account'),readonly=True),  #pcs单价
        'cost_base_b':               fields.float( u'基板费',  digits_compute=dp.get_precision('Account'),readonly=True),  #基础板费
        'cost_pack_b':               fields.float( u'打包费',  digits_compute=dp.get_precision('Account'),readonly=True),  #工程打包费 
        'cost_mould_b':             fields.float( u'模具费', digits_compute=dp.get_precision('Account'),readonly=True),  #磨具费用 
        'cost_change_b':           fields.float( u'变更费',digits_compute=dp.get_precision('Account'),readonly=True), #变更费用
        'cost_days_b':               fields.float( u'加急费',  digits_compute=dp.get_precision('Account'),readonly=True),  #加急费用
        'cost_sqcm_b':              fields.float( u'平方厘米价',  digits=(12,5),readonly=True),
        'cost_gold_finger_b':     fields.float( u'金手指费',  digits_compute=dp.get_precision('Account'),readonly=True),  #金手指费用
        'cost_all_b':                   fields.float( u'费用汇总',   digits_compute=dp.get_precision('Account'),readonly=True),  #费用记总        
        'po_area' :fields.function(_info_get, method=True, type='float',  string=u"面积m2", digits=(4,4),store=True),#订单面积
        'type'    :fields.function(_info_get, method=True, type='char',   string=u"类型",store=True),#('normal_sample','normal_mass','hdi', 'rigid_flexible', 'special',)
        'price_calculate_info':fields.text(u'价格计算信息'),#价格计算信息
       'cost_pcs_discount':        fields.related('partner_id','pcs_discount',type='float',relation='res.partner',string=u'折扣信息',readonly=True,store=True),#折扣信息
       'cost_once':                     fields.function(_cost_fun,  method=True, type='float',  string=u"一次费用", readonly=True), #一次费用
       'new_price_unit':fields.float('new_price_unit',digits_compute= dp.get_precision('Account')),#
       'updata_time':fields.datetime('updata_time'),#
       'privilege_price':fields.float(u'优惠价格',digits=(4,4)),
       
       
       'bottom_price':fields.float(u'底价',readonly=True,digits=(4,4)),
       'per_PNL_price':fields.float(u'品质附加费',digits=(4,4)),
       'density_price':fields.float(u'孔密度',readonly=True,digits=(4,4)),
       'board_price':fields.float(u'板厚',readonly=True,digits=(4,4)),
       'min_hole_price':fields.float(u'最小孔径',readonly=True,digits=(4,4)),
       'upper_price':fields.float(u'压接孔',readonly=True,digits=(4,4)),
       'cu_price':fields.float(u'铜厚',readonly=True,digits=(4,4)),
       'ink_price':fields.float(u'油墨',readonly=True,digits=(4,4)),
       'buried_price':fields.float(u'盲埋孔',readonly=True,digits=(4,4)),
       'pad_price':fields.float(u'盘中孔',readonly=True,digits=(4,4)),
       'material_price':fields.float(u'叠成加材料费',readonly=True,digits=(4,4)),
       'unit_price':fields.float(u'小板加费',readonly=True,digits=(4,4)),
       'tg_price':fields.float(u'TG料',readonly=True,digits=(4,4)),
       'finger_price':fields.float(u'金手指费',readonly=True,digits=(4,4)),
       'half_price':fields.float(u'半孔',readonly=True,digits=(4,4)),
       'step_price':fields.float(u'台阶孔',readonly=True,digits=(4,4)),
       'surface_price':fields.float(u'表面工艺费',readonly=True,digits=(4,4)),
       'special_price':fields.float(u'特殊工艺',readonly=True,digits=(4,4)),
       'hole_line_price':fields.float(u'孔到线',readonly=True,digits=(4,4)),
       'min_line_price':fields.float(u'最小线',readonly=True,digits=(4,4)),
       'impdance_price':fields.float(u'阻抗费',readonly=True,digits=(4,4)),
       'test_price':fields.float(u'测试费',readonly=True,digits=(4,4)),
       'note':fields.text(u'备注'),
       'special_material_price':fields.float(u'原材料费'),
       'add_price':fields.float(u'附加费',digits=(4,4)),
       'recive_type':fields.selection([('new',u'新单'),('repeat',u'复投无更改'),('revise',u'复投有更改')],string=u'接单类型'),
       'is_quote':fields.boolean(u'引用'),
       
       
       
       
       
       
       
    }

    _defaults = {
        'name': lambda obj, cr, uid, context:  obj.pool.get('ir.sequence').get(cr, uid, 'price.sheet'), 
#        'name':lambda obj, cr, uid, context:'/',
        'product_number': lambda *a: 1,
        'state': lambda *a: 'draft',
        'create_time': lambda *a: time.strftime('%Y-%m-%d'), 
        'responsible_id': lambda  self,cr,uid,ids: uid, 
        'cost_all_s' :1,
        'is_quote':False,
    }
    _sql_constraints = [
        ('name', 'unique (name)', 'name  must unique!'), 
        ('product_number', 'CHECK (product_number >= 0)', 'product_number  must >= 0!'), 
       
        ]
    

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default['name']= self.pool.get('ir.sequence').get(cr, uid, 'price.sheet'), 
        return super(price_sheet, self).copy(cr, uid, id, default=default,context=context)
    
    def approve_type(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        res=self.pool.get('res.users')
        user_id=res.browse(cr,uid,uid).login
       
#        if my.responsible_id.employeecode!=user_id:
#             raise osv.except_osv(_('Error!'),_(u'资料审核员只能审批自己的！'))
#        else:
        return True
  
    def _check_delivery_date(self,cr,uid,ids,context=None):  
        my=self.browse(cr, uid, ids[0])
        if not my.delivery_date:       
            raise osv.except_osv(_('Error!'),_(u'交货日期不能为空!'))
        else:
            return True
        
    def button_approve(self,cr,uid,ids,context=None): 
        my=self.browse(cr, uid, ids[0])
        if my.state=='draft' and my.cost_all_b>0:
            self._check_delivery_date(cr,uid,ids,context=None)
            self.approve_type(cr,uid,ids,context=None)
            self.write(cr,uid,ids[0],{'state':'wait_order_supervisor'})
        
        if my.state=='wait_customer_back':
             self.write(cr,uid,ids[0],{'state':'done'})
             self.pool.get('order.recive').write(cr,uid,my.lead_id.id,{'state':'wait_sale'})
        return True
    
  
    ###检查金额是否大于公司的5%或者10%
    def check_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('res.partners')
        standard=my.partner_id.is_company_price
        print standard,'standard'
        so=my.cost_all_o ####实际合同
        co=my.cost_all_b ####公司标准价格
        mo=my.cost_all ###客户标准价格
        if my.state=='wait_order_supervisor' and my.recive_type=='new':
            if standard==True:
                ####abs()函数是绝对值
                if abs(so-co)/co<0.05 and so!=co:
                     self.write(cr,uid,ids[0],{'state':'wait_general_manager'})
                elif abs(so-co)/co>=0.05 and so!=co:
                     self.write(cr,uid,ids[0],{'state':'wait_sale_manager'})
                else:
                    self.write(cr,uid,ids[0],{'state':'wait_customer_back'})
            if standard==False:
                if abs(so-mo)/mo<0.05 and so!=mo:
                     self.write(cr,uid,ids[0],{'state':'wait_general_manager'})
                elif abs(so-mo)/mo>=0.05 and so!=mo:
                     self.write(cr,uid,ids[0],{'state':'wait_sale_manager'})
                else:
                    self.write(cr,uid,ids[0],{'state':'wait_customer_back'})
        if  my.state=='wait_order_supervisor' and my.recive_type!='new':
            self.write(cr,uid,ids[0],{'state':'wait_sale_manager'})
        return True
    
    
    def button_approve_one(self,cr,uid,ids,context=None): 
        my=self.browse(cr, uid, ids[0])
        so=my.cost_all_o
        co=my.cost_all_b
        if my.state=='wait_sale_manager':
            self.write(cr,uid,ids[0],{'state':'wait_general_manager'})

        return True    
    
    def button_general_manager(self,cr,uid,ids,context=None):
    
         self.write(cr,uid,ids[0],{'state':'wait_customer_back'})
         return True
    
    
    def button_cancel(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids[0],{'state':'cancel'})
        return True
        
        
    def function_standard_days(self, cr, uid, ids, default=None, context=None):
        
        sheet=self.browse(cr, uid, ids[0], context) 
        pi=sheet.pcb_info_id
        c_standard_days=[]
        pi_line=pi.pcb_info_many
        standard_days=0
        for i in pi_line:

            if i.board_material :
                if sheet.type == 'rigid_flexible' :
                    if pi.layer_count<2:
                        pi.layer_count=2
                   
                    c_standard_days=[
                             ('cost_type','=','standard_days'),
                            ('type','=','rigid_flexible'),
                            ('layer_count','=',pi.layer_count),
                            ('po_area_max','>=',sheet.po_area),
                            ('po_area_min','<=',sheet.po_area),  ]   
                  
                   
        #特殊材料，参考材料种类，和层数
                elif sheet.type == 'special_matrial':
               
                    if pi.layer_count<2:
                        pi.layer_count=2
                    
                    c_standard_days=[
                                         ('cost_type','=','standard_days'),
                                         ('type','=',sheet.type),
                                         ('layer_count','=',pi.layer_count),
                                         ('po_area_max','>=',sheet.po_area),
                                         ('po_area_min','<=',sheet.po_area),  
                                         ]   
                    
                    
        #普通版，参考 层数
                else :
            #批量，样板，都有面积,  hid与刚柔结合 参考 样板
                    if pi.layer_count<2:
                        pi.layer_count=2
                    print pi.layer_count,'pi.layer_count'
                    c_type= sheet.type in ['hdi', 'rigid_flexible'] and 'normal_sample' or sheet.type 
                    c_standard_days=[
                         ('cost_type','=','standard_days'),
                         ('type','=',c_type),
                         ('layer_count','=',pi.layer_count),
                         ('po_area_max','>=',sheet.po_area),
                         ('po_area_min','<=',sheet.po_area),  
                         ]
                    

                       
                    
        if self._get_arg(cr,uid,ids,c_standard_days,'v',context,'special'):
            standard_days=self._get_arg(cr,uid,ids,c_standard_days,'v',context,'special')
          
        else:
            standard_days=self._get_arg(cr,uid,ids,c_standard_days,'v',context,'standard')
        print standard_days,'standard_days'
        cu_max=self.pool.get('pcb.info').get_cu_thickness_max(cr,uid,pi)
        #厚铜增加
        if cu_max > 2:
            standard_days += cu_max - 2
        # 盘中孔增加
        if u'盘中孔' in [line.special_process for line in pi_line]:#
                standard_days +=3
                # 盲埋孔增加
        if pi.via_quantity:
                standard_days+=pi.via_quantity
        self.write(cr, uid, ids[0], {'standard_days':standard_days})   
        return True

    def function_cost(self,cr,uid,ids,context=None):
        
        for id in ids:
            
            #update standard days
            self.function_standard_days( cr, uid, [id],)
            sheet=self.browse(cr, uid, id, context,)
            pi=sheet.pcb_info_id
            min_line_price=0.0
            privilege_price=0.0
            add_price=0.0
            add_price=sheet.add_price
            privilege_price=sheet.privilege_price
            cost_sqcm,s_info=self._get_cost_sqcm(cr,uid,ids,context=context,cost_type='special')
            #print cost_sqcm,pi.pcs_area  ,cost_sqcm*pi.pcs_area
            cost_pcs =(cost_sqcm-privilege_price+add_price)*pi.pcs_area
            cost_base=cost_pcs*sheet.product_number
    
            cost_ready,r_info=self._get_cost_ready(cr,uid,ids ,context=context,cost_type='special')
            cost_plot ,p_info=self._get_cost_plot(cr,uid,ids,context=context,cost_type='special')
            cost_test ,t_info=self._get_cost_test(cr,uid,ids,context=context,cost_type='special')
            cost_other,o_info=self._get_cost_other(cr,uid,ids,context=context,cost_type='special')
            cost_pack,k_info=self._get_cost_pack(cr,uid,ids,context=context,cost_type='special')
            cost_gold_finger,f_info=self._get_cost_gold_finger(cr,uid,ids,context=context,cost_type='special')
            
            cost_days=self._get_cost_days(cr,uid,ids,cost_base=cost_base, cost_ready=cost_ready, cost_plot=cost_plot,
                                          cost_other=cost_other, cost_test=cost_test,cost_gold_finger=cost_gold_finger)
           
            
            cost_all=self._get_cost_all(cr,uid,ids,cost_base=cost_base, cost_ready=cost_ready, cost_plot=cost_plot,
                                        cost_other=cost_other, cost_test=cost_test,cost_days=cost_days,cost_gold_finger=cost_gold_finger)
            ##cost_base*sheet.product_number + cost_ready + cost_plot + cost_other
            #self.write(cr, uid, id, {'product_number_s' :self.browse(cr, uid, id,).product_number  }, context)
            
            self.write(cr, uid, id, {'cost_sqcm' :cost_sqcm  }, context)
            self.write(cr, uid, id, {'cost_pcs' :cost_pcs  }, context)
            self.write(cr, uid, id, {'cost_base' :cost_base  }, context)
            self.write(cr, uid, id, {'cost_ready':cost_ready }, context)
            self.write(cr, uid, id, {'cost_plot' :cost_plot  }, context)
            self.write(cr, uid, id, {'cost_other':cost_other }, context)
            self.write(cr, uid, id, {'cost_test':cost_test }, context)
            self.write(cr, uid, id, {'cost_pack':cost_pack }, context)
            self.write(cr, uid, id, {'cost_days':cost_days }, context)
            self.write(cr, uid, id, {'cost_gold_finger':cost_gold_finger},context)
            self.write(cr, uid, id, {'cost_all':cost_all }, context)
            
            
           #===========标准价格信息=====================================================
            cost_sqcm_b,sb_info=self._get_cost_sqcm(cr,uid,ids,context=context,cost_type='standard')
            #print cost_sqcm,pi.pcs_area  ,cost_sqcm*pi.pcs_area
            cost_pcs_b=cost_sqcm_b * pi.pcs_area
            cost_base_b=cost_pcs_b*sheet.product_number
            
            cost_ready_b,rb_info=self._get_cost_ready(cr,uid,ids ,context=context,cost_type='standard')
            cost_plot_b,pb_info=self._get_cost_plot_b(cr,uid,ids,context=context,cost_type='standard')
            cost_test_b,tb_info=self._get_cost_test(cr,uid,ids,context=context,cost_type='standard')
            cost_other_b,ob_info=self._get_cost_other(cr,uid,ids,context=context,cost_type='standard')
            cost_pack_b,kb_info=self._get_cost_pack(cr,uid,ids,context=context,cost_type='standard')
            cost_gold_finger_b,fb_info=self._get_cost_gold_finger(cr,uid,ids,context=context,cost_type='standard') 
            cost_days_b=self._get_cost_days(cr,uid,ids,cost_base=cost_base_b, cost_ready=cost_ready_b, cost_plot=cost_plot_b,
                                          cost_other=cost_other_b, cost_test=cost_test_b,cost_gold_finger=cost_gold_finger_b)
           
            
            cost_all_b=self._get_cost_all(cr,uid,ids,cost_base=cost_base_b, cost_ready=cost_ready_b, cost_plot=cost_plot_b,
                                        cost_other=cost_other_b, cost_test=cost_test_b,cost_days=cost_days_b,cost_gold_finger=cost_gold_finger_b)
            self.write(cr, uid, id, {
                    'cost_sqcm_b' :cost_sqcm_b ,
                    'cost_pcs_b':cost_pcs_b,
                    'cost_base_b':cost_base_b,
                    'cost_ready_b':cost_ready_b,
                    'cost_plot_b':cost_plot_b,
                    'cost_test_b':cost_test_b,
                    'cost_other_b':cost_other_b,
                    'cost_pack_b':cost_pack_b,
                    'cost_gold_finger_b':cost_gold_finger_b,
                    'cost_days_b':cost_days_b,
                    'cost_all_b':cost_all_b }, context)
            #==============================================================================
            text=p_info+t_info+k_info+s_info+o_info+r_info+f_info+'\n'+'=' *50+'\n' +\
                'standard price info: \n'+ pb_info+tb_info+kb_info+sb_info+ob_info+rb_info+fb_info
            
            cost_ready_s=sheet.lead_id.sale_type !='repeat' and cost_ready or 0.0
            cost_plot_s=sheet.lead_id.sale_type !='repeat' and cost_plot or 0.0
            print cost_plot_s,'cost_plot_s'
            cost_all=sheet.lead_id.sale_type !='repeat' and cost_all or (cost_all - cost_ready -cost_plot)

           
            if sheet.lead_id.sale_type =='repeat':
               
                if pi.layer_count==2 and cost_all< 300:
                    cost_all=300
                if pi.layer_count==4 and cost_all< 500:
                    cost_all=500
                if pi.layer_count==6 and cost_all< 700:
                    cost_all=700
                if pi.layer_count==8 and cost_all< 800:
                    cost_all=800
                if pi.layer_count>=10 and cost_all< 1000:
                    cost_all=1000
              
            self.write(cr, uid, id, {'cost_ready_s':cost_ready_s}, context)
            self.write(cr, uid, id, {'cost_plot_s' :cost_plot_s }, context)
            self.write(cr, uid, id, {'cost_pcs_s' :cost_pcs}, context)
            self.write(cr, uid, id, {'cost_other_s':cost_other}, context)
            self.write(cr, uid, id, {'cost_test_s':cost_test }, context)
            self.write(cr, uid, id, {'cost_days_s':cost_days }, context)
            self.write(cr, uid, id, {'cost_gold_finger_s':cost_gold_finger},context)
            self.write(cr,uid,id,{'cost_all_s':cost_all},context)
            self.write(cr, uid, id, {'price_calculate_info':text }, context)       
        return True
    
    def _get_arg (self,cr,uid,ids,condition=None, field_name='v',   context=None ,cost_type=None):
        arg_obj=self.pool.get('pcb.cost.argument')
        arg_ids=None
                
        if cost_type=='standard' or cost_type is None:
            arg_ids=arg_obj.search(cr,uid,[('res_partner_id','=',None)]+condition)
            print arg_ids,'arg_ids'
        elif cost_type=='special':
            partner_id=self.browse(cr,uid,ids[0]).partner_id.id
            arg_ids=arg_obj.search(cr,uid,[('res_partner_id','=',partner_id)]+condition) 
            # if not found special , search standard again
            if not arg_ids:
                arg_ids=arg_obj.search(cr,uid,[('res_partner_id','=',None)]+condition) 
                
        #搜索结果必须有且只有一条，否则会有歧义
        if not arg_ids:
            raise osv.except_osv(_('Warning not found record!'), _(condition) )
           
        if len(arg_ids) > 1:
            raise osv.except_osv(   _('Warning found mul record!'), _( str(condition)+str(arg_ids) )    )
            
        arg_instance=arg_obj.browse(cr,uid,arg_ids[0])
        print field_name,'field_name',arg_instance,'arg_instance'
        res= getattr(arg_instance, field_name,False)
        print res,'res001'
        if not res:
            raise osv.except_osv(_('Warning !'), _('arg id %s is False'  %  arg_instance.id ) )
        else:
            return res
        
        
    def _get_cost_all(self,cr,uid,ids,cost_base=0, cost_ready=0, cost_plot=0,cost_other=0, cost_test=0, cost_days=0,cost_gold_finger=0,context=None):
        res=cost_base + cost_ready + cost_plot + cost_other + cost_test + cost_days+cost_gold_finger
        return res
                     
    def _get_cost_days(self,cr,uid,ids,cost_base=0, cost_ready=0, cost_plot=0,cost_other=0, cost_test=0,cost_gold_finger=0,context=None):
        
        sheet=self.browse(cr, uid, ids[0], context,)
        pi=sheet.pcb_info_id
        
        res=cost_base + cost_ready + cost_plot + cost_other + cost_test+cost_gold_finger

    
        cost_days=sheet.standard_days - sheet.delivery_leadtime
        print cost_days,'cost_days'
        #print cost_days ,  sheet.delivery_leadtime
        if cost_days > 0:
            c_cost_days=pi.layer_count < 8 and [('layer_count','=',pi.layer_count),('cost_days','=',cost_days)] or [('layer_count','>',pi.layer_count),('cost_days','=',cost_days)] 
            print c_cost_days,'c_cost_days'
            ratio= self._get_arg(cr, uid, ids,c_cost_days, 'v',context,'standard' ) or False
            if not ratio:
                raise osv.except_osv(_('Warning !'), _('arg cost_days not found' ) )
            else:
                print res*ratio,'cost_days'
                return res*ratio
        else:
            return 0
    #####计算客户菲林费
    def _get_cost_plot(self,cr,uid,ids,context=None,cost_type=None):
        
        sheet=self.browse(cr, uid, ids[0],)
        pi=sheet.pcb_info_id
        #c_plot=[('cost_type','=','plot'),('layer_count','=',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
        res=price_calculate()
        arg_obj=self.pool.get('pcb.cost.argument')
        
        
        #=======================================================================
        # ##是否复投无更改，不计算菲林费
        # if sheet.lead_id.sale_type=='repeat':
        #    return res.value,res.info
        # 
        # ##新单 或则 复投有更改
        # elif sheet.lead_id.sale_type !='repeat':
        #=======================================================================
            
        #双面板0.12 300 ≤200cm2 300 元；≤400cm2 350 元；> 400cm2 增加部分1.0 元/cm2
        #if sheet.type=='normal_sample' and  pi.surface_treatment and pi.surface_treatment.name not in ['hasl','osp']:
        #    c_surface=[('cost_type','=','surface_treatment'),('surface_treatment','=',pi.surface_treatment.id)]
        #    #加价小于80的按80计算
        #    if  pi.surface_area/(pi.pcs_length * pi.pcs_width) <= 0.2:
        #        tmp=80
        #    else:
        #        tmp=80 * (pi.surface_area/(pi.pcs_length * pi.pcs_width))
        #    res.add( tmp, c_surface)
        
        if pi.layer_count<=2:
            c_plot=[('cost_type','=','plot'),('layer_count','=',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
            tmp=0
            if pi.pcs_area > 400:
                tmp=(self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type) + 1*(pi.pcs_area-400)) 
            else:
                tmp= self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type) 
                
            res.add( tmp, c_plot)
        #层数 > 2
        else:
            ##hdi板和rigid_flexible板菲林费计算
            if sheet.type in ['hdi','rigid_flexible']: 
                c_plot=[('cost_type','=','plot'),('type','=','hdi'),('layer_count','=',pi.layer_count)]
                hdi_cost_plot_min=self._get_arg(cr, uid,ids, c_plot, 'v',context,cost_type )  #hdi 菲林收费表
                res.add(hdi_cost_plot_min ,c_plot)
                
                ##单板面积大于200 平方厘米的时候菲林费按0.12 元/cm2 加收费用
                if pi.pcs_area > 200:
                    tmp=(pi.pcs_area - 200)*0.12*pi.plot_count
                    res.add(tmp, [('cost_type','=','plot'),('arear - 200  *  0.12/cm2')])
                    
            ##不是hdi和rigid_flexible板时，菲林费计算
            else:
                c_plot=[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
                


                price=self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type)
                tmp=0
                if pi.pcs_area > 400:
                    if arg_obj.search(cr,uid,[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area),('res_partner_id','=',sheet.partner_id.id)]):
                            tmp=price*(pi.pcs_area-400)*pi.plot_count
                    else:
                        tmp=price*pi.pcs_area*pi.plot_count
                elif pi.pcs_area <= 400:
                    print arg_obj.search(cr,uid,[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<=',pi.pcs_area),('res_partner_id','=',sheet.partner_id.id)]),'cooo'
                    if arg_obj.search(cr,uid,[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area),('res_partner_id','=',sheet.partner_id.id)]):
                            tmp=0
                    elif pi.pcs_area < 100:
                        res.add(12*pi.plot_count, [('cost_type','=','plot'),('plot_count',r'*',12)])
                    else:
                        print tmp,'tmp'
                        tmp=price*pi.pcs_area*pi.plot_count
                        print tmp,'tmp100'
                   
                res.add(tmp,c_plot)
        
        return res.value,res.info,
    
    
    
    ####计算菲林标准费
    def _get_cost_plot_b(self,cr,uid,ids,context=None,cost_type=None):
        
        sheet=self.browse(cr, uid, ids[0],)
        pi=sheet.pcb_info_id
        #c_plot=[('cost_type','=','plot'),('layer_count','=',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
        res=price_calculate()
        arg_obj=self.pool.get('pcb.cost.argument')
        
        
        #=======================================================================
        # ##是否复投无更改，不计算菲林费
        # if sheet.lead_id.sale_type=='repeat':
        #    return res.value,res.info
        # 
        # ##新单 或则 复投有更改
        # elif sheet.lead_id.sale_type !='repeat':
        #=======================================================================
            
        #双面板0.12 300 ≤200cm2 300 元；≤400cm2 350 元；> 400cm2 增加部分1.0 元/cm2
        #if sheet.type=='normal_sample' and  pi.surface_treatment and pi.surface_treatment.name not in ['hasl','osp']:
        #    c_surface=[('cost_type','=','surface_treatment'),('surface_treatment','=',pi.surface_treatment.id)]
        #    #加价小于80的按80计算
        #    if  pi.surface_area/(pi.pcs_length * pi.pcs_width) <= 0.2:
        #        tmp=80
        #    else:
        #        tmp=80 * (pi.surface_area/(pi.pcs_length * pi.pcs_width))
        #    res.add( tmp, c_surface)
        
        if pi.layer_count<=2:
            c_plot=[('cost_type','=','plot'),('layer_count','=',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
            tmp=0
            if pi.pcs_area > 400:
                tmp=(self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type) + 1*(pi.pcs_area-400)) 
            else:
                tmp= self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type) 
                
            res.add( tmp, c_plot)
        #层数 > 2
        else:
            ##hdi板和rigid_flexible板菲林费计算
            if sheet.type in ['hdi','rigid_flexible']: 
                c_plot=[('cost_type','=','plot'),('type','=','hdi'),('layer_count','=',pi.layer_count)]
                hdi_cost_plot_min=self._get_arg(cr, uid,ids, c_plot, 'v',context,cost_type )  #hdi 菲林收费表
                res.add(hdi_cost_plot_min ,c_plot)
                
                ##单板面积大于200 平方厘米的时候菲林费按0.12 元/cm2 加收费用
                if pi.pcs_area > 200:
                    tmp=(pi.pcs_area - 200)*0.12*pi.plot_count
                    res.add(tmp, [('cost_type','=','plot'),('arear - 200  *  0.12/cm2')])
                    
            ##不是hdi和rigid_flexible板时，菲林费计算
            else:
                c_plot=[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max' ,'>=',pi.pcs_area),('pcs_area_min' ,'<',pi.pcs_area), ]
                
                ##单板面积<100 cm²时，按每张12 元计算；
                if pi.pcs_area < 100:
                    res.add(12*pi.plot_count, [('cost_type','=','plot'),('plot_count',r'*',12)])
                ##大于100 cm²时，取价格参数表中值
                else:
                    price=self._get_arg(cr,uid,ids,c_plot,'v',context,cost_type)
                    print price,'price'
                    tmp=price*pi.pcs_area*pi.plot_count
                    res.add(tmp,c_plot)
        
        return res.value,res.info,
    
    def _get_cost_test(self,cr,uid,ids,context=None,cost_type=None):
        
        sheet=self.browse(cr, uid, ids[0],)
        pi=sheet.pcb_info_id
        pi_line=pi.pcb_info_many
        res=price_calculate()
        if sheet.type == 'rigid_flexible' and  sheet.po_area <= 1:
            c_rf_test=[('cost_type','=','test'),('type','=','rigid_flexible'),('layer_count','=',pi.layer_count)]
            tmp=self._get_arg(cr, uid,ids,c_rf_test , 'v',context,cost_type )
            print tmp,'test1'
            res.add(tmp,c_rf_test)
        if sheet.type =='special_matrial':
                #特种板测试费
            pcs_area=pi.pcs_length*pi.pcs_width
            for i in pi_line:
                if i.board_material and i.is_specia_material:
                    matrial=i.board_material
                    c_special_test=[
                            ('cost_type','=','test'),
                            ('type','=',sheet.type),
                            ('layer_count','=',pi.layer_count),
                            ('pcs_area_min','<=',pcs_area),
                            ('pcs_area_max','>=',pcs_area),
                            ]
                    tmp=self._get_arg(cr,uid,ids,c_special_test,'v',context,cost_type)
                    res.add( tmp,c_special_test)  
                    print res,'res'
        if sheet.type=='hdi' and sheet.po_area<=3:
                c_hdi_tes=[('cost_type','=','test'),('type','=','hdi'),('layer_count','=',pi.layer_count)]
                print c_hdi_tes,'c_hdi_tes'
                tmp=self._get_arg(cr, uid,ids,c_hdi_tes , 'v', context,cost_type)
                res.add(tmp, c_hdi_tes)
        if sheet.po_area > 1:
            for i in pi_line:
                if i.board_material !=False:
                    matrial=i.board_material
                pass

            ##是否需要测试
    #        if  len(i.test_type)==0:
            if 'false' in [i.test_type]:
                return res.value,res.info
            
  
                    
             
    		##飞针测试免费， 10点/cm2以上，（实际测试点密度-10 点/cm2）×0.004（元/ cm2）
    		
            if u'飞针测试' in [line.test_type for line in pi_line]:
    			fly_cost=0.0
    		   
    			# 3平米以上的飞针
    			if sheet.po_area >= 3:
    				fly_cost = 0.004 * sheet.product_number * pi.test_point_count
    				res.add(fly_cost,[('cost_type','=','fly'),('po_area','>=',3)])
    			
    			 
    		#通用测试费用
            if u'通用测试' in [line.test_type for line in pi_line]:
    			c_jig=[('cost_type','=','test_jig'),('test_point_max','>=',pi.test_point_count),('test_point_min','<',pi.test_point_count)]
    			jig=self._get_arg(cr,uid,ids, c_jig,'v',context,cost_type)
    			res.add(jig,c_jig)
    			
    			c_test=[('cost_type','=','test_pcs'),('test_point_max','>=',pi.test_point_count),('test_point_min','<',pi.test_point_count)]
    			test_pcs=self._get_arg(cr, uid,ids,c_test,'v',context,cost_type)*sheet.product_number
    			res.add(test_pcs, c_test)
    		#专用测试费用
            elif u'专用测试' in [line.test_type for line in pi_line]:
    			pass    
    		##hdi 测试 , 订单总孔数多于10 万以上的部分，按250 元/10K 孔加收
            if sheet.type=='hdi':
                c_hdi_tes=[('cost_type','=','test'),('type','=','hdi'),('layer_count','=',pi.layer_count)]
                print c_hdi_tes,'c_hdi_tes'
                hdi_cost_test_min=self._get_arg(cr, uid,ids,c_hdi_tes , 'v', context,cost_type)
                print hdi_cost_test_min,'hdi_cost_test_min'
                if  hdi_cost_test_min > res.value :
    				res.add(hdi_cost_test_min,c_hdi_tes )
    				
    			#订单总孔数多于10 万以上的部分，按250 元/10K 孔加收    
                drill_more_10w=pi.test_point_count * sheet.product_number - 100000
                if drill_more_10w > 0:
    				tmp=  drill_more_10w * (250/10000)
    				res.add(tmp,[('cost_type','=','test'),('type','=','hdi'),('drill_more_10w','=',drill_more_10w)])
    				
    			
    		##刚柔结合测试
            if sheet.type == 'rigid_flexible':
    			c_rf_test=[('cost_type','=','test'),('type','=','rigid_flexible'),('layer_count','=',pi.layer_count)]
    			tmp=self._get_arg(cr, uid,ids,c_rf_test , 'v',context,cost_type )
    			res.add(tmp,c_rf_test)
    			
        return res.value,res.info
       
    def _get_cost_pack(self,cr,uid,ids,context=None,cost_type=None):
        
        sheet=self.browse(cr, uid, ids[0],)
        pi=sheet.pcb_info_id
        res=price_calculate()
        
        if pi.pcs_area <= 600:
            c_pack=[('cost_type','=','pack'),('layer_count','=',pi.layer_count),('pcs_area_min','<',pi.pcs_area),('pcs_area_max','>=',pi.pcs_area)]
            res.add(self._get_arg(cr, uid,ids, c_pack, 'v',context,cost_type ),c_pack)
        elif pi.pcs_area > 600:
            c_pack=[('cost_type','=','pack'),('layer_count','=',pi.layer_count),('pcs_area_min','<',600),('pcs_area_max','>=',600)]
            c_pack_add=[('cost_type','=','pack'),('layer_count','=',pi.layer_count),('pcs_area_max','>=',600)]
            res.add(self._get_arg(cr, uid,ids, c_pack, 'v', context,cost_type) + (pi.pcs_area-600)*self._get_arg(cr, uid,ids,c_pack_add, 'v', context,cost_type),c_pack)
        return res.value,res.info
    
    def _get_cost_sqcm(self,cr,uid,ids,context=None,cost_type=None):
        
        # 计算板费用，每平方里面价格， 按类计算：   样板 、 批量、刚柔结合、HDI
        # 'normal_sample','normal_mass','hdi', 'rigid_flexible' ,
        
        sheet=self.browse(cr, uid, ids[0],)
        obj=self.pool.get('pcb.cost.argument')
        pi=sheet.pcb_info_id
        pi_line=pi.pcb_info_many
        base=0
        base_res=price_calculate() 
        for i in pi_line:
            if i.board_material != False:
                board_material=i.board_material
                
            if i.special_process:
            #####特殊工艺加价半槽、半孔各加5分钱
            #####金手指：       批量加3分钱
            ###沉边、沉孔：各加2分
            ###金属包边加5分钱
            ###树脂加1.2角钱
            ###铜浆加1.5角钱
            ####蓝胶、碳油各加1分
            ####锥型孔加2分钱
            ###压接孔加3分钱
            ###背钻：如果2组以下加2分钱，2组以上加单价的30%
            
                special_process=i.special_process
                print special_process,'special_process'
                if u'半槽' in special_process or u'半孔' in special_process or u'金属化包边' in special_process:
                    tmp=0.05
                    base_res.add(tmp,[('cost_type','=','base'),('half_pth','=', pi.half_pth)])
                    self.write(cr,uid,ids[0],{'half_price':tmp})
                if u'长短金手指' in special_process and sheet.po_area>1 or u'间断金手指' in special_process and sheet.po_area>1:
                    tmp=0.03
                    base_res.add(tmp,[('cost_type','=','base'),('jinshouzhi')])
                    self.write(cr,uid,ids[0],{'half_price':tmp})
                if u'树脂' in special_process:
                    tmp=0.12
                    base_res.add(tmp,[('cost_type','=','base'),('shuzhi')])
                    self.write(cr,uid,ids[0],{'pad_price':tmp})
                if u'铜浆' in special_process:
                    tmp=0.15
                    base_res.add(tmp,[('cost_type','=','base'),('tongjiang')])
                    self.write(cr,uid,ids[0],{'pad_price':tmp})
                if u'沉边' in special_process or u'沉孔' in special_process or u'锥型孔' in special_process:
                    tmp=0.02
                    print tmp,'tmp001'
                    base_res.add(tmp,[('cost_type','=','base'),('chenbian','chenkong','zhuixingkong')])
                    self.write(cr,uid,ids[0],{'step_price':tmp})
                if u'压接孔' in special_process:
                    tmp=0.03
                    base_res.add(tmp,[('cost_type','=','base'),('yajiekong')])
                    self.write(cr,uid,ids[0],{'upper_price':tmp})
                if u'蓝胶' in special_process and sheet.po_area>1 or u'碳油' in special_process and sheet.po_area>1:
                    tmp=0.01
                    base_res.add(tmp,[('cost_type','=','base')])
                    self.write(cr,uid,ids[0],{'special_price':tmp})
                    
                if u'背钻' in special_process and pi.back_drill:
                    if pi.back_drill<=2:
                        tmp=0.02
                        base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('back_drill','=','back_drill')])
                       
                    elif pi.back_drill>2:
                        if sheet.type=='special_matrial':
                            cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),('material_category','=',board_material)]
                            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                            tmp=base*0.3
                            base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('back_drill','=','back_drill')])
                           
                        else:
                            cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count)]
                            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                            tmp=base*0.3
                            base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('back_drill','=','back_drill')])
                           
                        
                if u'盘中孔' in special_process:
                    if sheet.po_area<=1:
                        tmp=0.15
                        base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('pad','=','panzhongkong')])
                        print base_res,'base_res19'
                
                    elif sheet.po_area>1:
                        tmp=0.12
                        base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('pad','=', 'panzhongkong')])
                    self.write(cr,uid,ids[0],{'pad_price':tmp})
                if u'控深钻' in special_process or u'台阶孔' in special_process:
                    tmp=0.02
                    base_res.add(tmp,[('cost_type','=','base'),('type','=',sheet.type),('deep_hole', 'step_hole')])
                    self.write(cr,uid,ids[0],{'step_price':tmp})
                if  u'无卤素板' in special_process:
                    if sheet.type=='special_matrial':
                        cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),('material_category','=',board_material)]
                        base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                        tmp=base*0.3
                        
                    else:
                        cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count)]
                        base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                        tmp=base*0.3
                    base_res.add(tmp,[('wulusuban')])
                    self.write(cr,uid,ids[0],{'add_price':tmp})
                if u'阻抗测试' in special_process:
                    if sheet.type=='special_matrial':
                        cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),('material_category','=',board_material)]
                        base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                        tmp=base*0.1
                        print tmp,'000'
                    else:
                        cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),('po_area_min','<=',sheet.po_area),('po_area_max','>=',sheet.po_area)]
                        base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) 
                        tmp=base*0.1
                    base_res.add(tmp,[('zukangceshi')])
                    self.write(cr,uid,ids[0],{'impdance_price':tmp})
            pass
          ##基数累加值存放结果
        #=======================================================================
        # cost_base=[('type','=',sheet.type),('layer_count','=',pi.layer_count),('cost_type','=','base'),('po_area_max','>=',sheet.po_area),('po_area_min','<',sheet.po_area)]
        # if sheet.type=='hdi':
        #    cost_base=[('type','=',sheet.type),('layer_count','=',pi.layer_count),('cost_type','=','base')]
        #=======================================================================
        
         #################计算基板费   
        if sheet.type=='normal_sample':
            print sheet.type,'sheet.type'
            cost_base=[
                ('cost_type','=','base'),
                ('type','=',sheet.type),
                ('layer_count','=',pi.layer_count),
            ]
            print cost_base,'cost_base0'
            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type)  ##基数价格
            base_res.add(base,cost_base)
            self.write(cr,uid,ids[0],{'bottom_price':base})
            
        elif sheet.type=='normal_mass':
            cost_base=[
                ('cost_type','=','base'),
                ('type','=',sheet.type),
                ('layer_count','=',pi.layer_count),
                ('po_area_max','>=',sheet.po_area),
                ('po_area_min','<',sheet.po_area)
            ]
            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type)  ##基数价格
            base_res.add(base,cost_base)
            self.write(cr,uid,ids[0],{'bottom_price':base})
        elif sheet.type == 'special_matrial' and not u'聚酰亚胺' in i.board_material:
            print sheet.type,'sheet.types'
            ###
            for i in pi_line:
                if i.board_material and i.is_specia_material:
                    
                    if u'ptfe' in i.board_material or u'铝基板' in i.board_material:
                        for r in pi.layer_cu_thickness_ids:
                                    a=r.cu_thickness
                                    b=[]
                                    b.append(a)
                        cu=max(b)
                        print cu,'cucu'
                        print i.board_material,'i.board_material'
                        cost_base=[
                            ('cost_type','=','base'),
                            ('type','=',sheet.type),
                         
                            ('material_category','=',i.board_material),
                            ('cu_thickness','=',cu)
                            ]
                        print cost_base,'cost_base'
                    else:
                         cost_base=[
                            ('cost_type','=','base'),
                            ('type','=',sheet.type),
                            ('layer_count','=',pi.layer_count),
                            ('material_category','=',i.board_material),
                            
                            ]
            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type)  ##基数价格
            base_res.add(base,cost_base)
           
            print base,'base_res0'
            
        elif sheet.type=='hdi':
            cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),]
            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type)  ##基数价格
            base_res.add(base,cost_base)
            self.write(cr,uid,ids[0],{'bottom_price':base})
        elif sheet.type=='rigid_flexible':
            
            cost_base=[('cost_type','=','base'),('type','=',sheet.type),('layer_count','=',pi.layer_count),]
            cost_flexible=[('cost_type','=','flexible'),('type','=',sheet.type),('layer_count','=',pi.layer_count),('flexible_count','=',pi.flexible_layer_count),]
                
                ##基数价格  ，=钢板+柔板
            base=self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type) +  self._get_arg(cr,uid,ids,cost_flexible,'v',context,cost_type)
            tmp=0
            if pi.sepecial_board_size:
                board_size=pi.sepecial_board_size
                print board_size,'board_size'
                special=[('cost_type','=','special_matrial'),('type','=','special_matrial'),('board_size','=',board_size),('po_area_min','<=',sheet.po_area),('po_area_max','>=',sheet.po_area)]
                print special,'special' 
                c_v=self._get_arg(cr,uid,ids,special,'v',context,cost_type)
                print c_v,'c_v'
                obj_id=obj.search(cr,uid,special)
                my=obj.browse(cr,uid,obj_id)[0]
                use_ratio=my.use_ratio
                print use_ratio,'use_ratio'
                if board_size=='500*500':
                    se=sheet.special_material_price/(50*50)/pi.matrial_use_ratio/(1-0.1) #材料费
                    print se,'se'
                    co=se * my.append_amount  #报废率
                    print co,'co'
                    tmp=se+co
                    print tmp,'tmp00'
                    base_res.add(tmp,special)
                    print base_res,'res10'
                if board_size=='500*600':
                    se=sheet.special_material_price/(50*60)/pi.matrial_use_ratio/(1-0.1)
                    co=se * my.append_amount
                    tmp=se+co
                    base_res.add(tmp,special)
                    print base_res,'res'
                if board_size=='18*24':
                    se=sheet.special_material_price/(45.72*60.96)/pi.matrial_use_ratio/(1-0.1)
                    co=se * my.append_amount
                    tmp=se + co
                    base_res.add(tmp,special)
                    print base_res,'res'
                if board_size=='36*48':
                    se=sheet.special_material_price / (91.44*121.92)/pi.matrial_use_ratio/(1-0.1)
                    co=se*my.append_amount
                    tmp=se+co
                    base_res.add(tmp,special)
                    print base_res,'res'
                if board_size=='24*36':
                    se=sheet.special_material_price / (60.96*91.44)/pi.matrial_use_ratio/(1-0.1)
                    co=se*my.append_amount
                    tmp=se+co
            total=tmp+self._get_arg(cr,uid,ids,cost_base,'v',context,cost_type)
            if pi.sepecial_board_size:
                base_res.add(total,cost_base+cost_flexible)
                self.write(cr,uid,ids[0],{'bottom_price':total})
            else:
                base_res.add(base,cost_base+cost_flexible)
                self.write(cr,uid,ids[0],{'bottom_price':base})
        else:
            pass
            
        

        
        if pi.layer_count <= 2:   ##双面板厚度加价
            if 1.6< pi.finish_board_thickness  <= 3 and pi.layer_count <= 2:
                cost_bd_thick=[('cost_type','=','base_bd_thick'),('layer_count','=',pi.layer_count),
                                 ('bd_thick_max','>=',pi.finish_board_thickness),('bd_thick_min','<',pi.finish_board_thickness)]
                print cost_bd_thick,'cost_bd_thick'
                tmp=self._get_arg(cr,uid,ids,cost_bd_thick,'v',context,cost_type) or 0.0 
                print tmp,'tmp'
                base_res.add(tmp, cost_bd_thick)
                print base_res,'base_res1'
                self.write(cr,uid,ids[0],{'board_price':tmp})
            else:  
                pass #板厚大于3 按照多层板计算  <?  无具体要求>
            

        elif pi.layer_count > 2:  ##多层板厚度加价  ：厚度超过基准值时，每增加0.25mm 厚度，单价增加0.025 元/ cm2； 10 层板以上厚度超过4.0mm 时具体特殊报价
            # bd_thick_max  存放加价的起始厚度
            c_limit_thick=[('cost_type','=','base_bd_thick'),('layer_count','=',pi.layer_count),]
            print c_limit_thick,'c_limit_thick'
            limit_thick=self._get_arg(cr,uid,ids,c_limit_thick,'bd_thick_max',context,cost_type)
            print limit_thick,'limit_thick'
            if pi.finish_board_thickness > limit_thick:
                tmp=(pi.finish_board_thickness - limit_thick)/0.25*0.025  # <? 0.025表格化>
                print tmp,'tmpp'
                base_res.add(tmp,c_limit_thick+[('finish_board_thickness','>',limit_thick)])
                print base,'base_res2'
                self.write(cr,uid,ids[0],{'board_price':tmp})
            if pi.layer_count > 10 and pi.finish_board_thickness > 4:
                #需要特殊报价 <?>
                pass
            
        #是否需要铜厚加价 <? 0.02 0.2 表格化>
        if self.is_need_cost_cu(cr,uid,ids,context=context):  
            #所有层铜厚一样
            if self.is_cu_thickness_same(cr,uid,ids,context=context):
                #铜厚大于1oz小于2oz
                
                #全部2oz
                if pi.layer_cu_thickness_ids[0].cu_thickness == 2:
                    tmp= base*0.2
                    base_res.add( tmp,[('cost_type','=','base'),('cu','=','2oz')])
                    self.write(cr,uid,ids[0],{'cu_price':tmp})
                    print base,'base_res3'
                #全部 大于2oz
                if pi.layer_cu_thickness_ids[0].cu_thickness >  2:
                    for r in pi.layer_cu_thickness_ids:
                        a=r.cu_thickness
                        b=[]
                        b.append(a)
                    s=max(b)
                    print s,'sss'
                    tmp= (s -1)*pi.layer_count*0.02
                    base_res.add( tmp, [('cost_type','=','base'),('cu','>','2oz')] )
                    self.write(cr,uid,ids[0],{'cu_price':tmp})
                    print base,'base_res4'
                
            #内层和外层铜厚不一样
            else:
                thick_count_hash=self.get_cu_thickness_hash(cr,uid,ids,context=context)
                #print thick_count_hash
                s=0.0
                s1=0.0
                for thick,count in  thick_count_hash.items():
                    #厚度为2oz的
                    if thick==2:  #铜厚为2的有几组， 就乘一个  2层板基数的 0.2乘以组数
                        print count,'count1'
                        c_domain=[('cost_type','=','base'),('type','=','normal_sample'),('layer_count','=',2),]
                        tmp= self._get_arg(cr,uid,ids,c_domain,'v',context,cost_type)*0.2*count/2
                        base_res.add(tmp,c_domain+[('cu','=','2oz')], )
                        print base,'base_res5'
                        s=tmp
                    if thick > 2:
                        print count,'count2'
                        tmp= (thick-1)*count*0.02
                        base_res.add(tmp,[('cost_type','=','base'),('cu', '>', '2oz'),])
                        print base_res,'base_res6'
                        s1=tmp
                so=s+s1
                self.write(cr,uid,ids[0],{'cu_price':so})
            
            
            
        # htg 板材费用 : htg 且层数 小于10的，tg板材费用
        if   True in [line.is_htg for line in pi_line] and pi.layer_count < 10:
#            for r in pi_line:
#                if r.is_htg != False:
#                    is_htg=r.is_htg
#                    print is_htg,'is_htg'
#            c_htg=[('cost_type','=','base_bd_thick'),
#                   ('material_category','=',board_material),
#                   ('is_gtg','=',is_htg),
#                   ('bd_thick_max','>=',pi.finish_board_thickness),('bd_thick_min','<=',pi.finish_board_thickness)
#                   ]
            if pi.layer_count<10:
                if pi.finish_board_thickness<=1:
                    tmp=0.01
                    base_res.add(tmp)
                    print base_res,'base_res7'
                    self.write(cr,uid,ids[0],{'tg_price':tmp})
                if pi.finish_board_thickness>1 and pi.finish_board_thickness<=1.6:
                    tmp=0.02
                    base_res.add(tmp)
                    self.write(cr,uid,ids[0],{'tg_price':tmp})
                if pi.finish_board_thickness>1.6 :
                    tmp=((pi.finish_board_thickness-1.6)/0.5)*0.01+0.02
                    base_res.add(tmp)
                    self.write(cr,uid,ids[0],{'tg_price':tmp})
          
            
            
        # 盲埋孔费用    <?是否需要在盲埋孔信息中增加盲埋孔的 价格计算参数>    
        if  pi.blind_buried_via_ids and sheet.type!='hdi':
            co=0
            for bb in  pi.blind_buried_via_ids:
                bb_layer_count=abs(bb.end-bb.start)+1
                print bb_layer_count,'bb_layer_count'
                bb_layer_count = bb_layer_count % 2 and  bb_layer_count+1 or bb_layer_count
                c_domain=[('cost_type','=','base'),('type','=','normal_sample'),('layer_count','=',bb_layer_count),]
                tmp=self._get_arg(cr,uid,ids,c_domain,'v',context,cost_type)*0.45
                base_res.add(tmp, c_domain,)
                print base_res,'base_res8'
                co+=tmp
                
                self.write(cr,uid,ids[0],{'buried_price':co})
           
                
        # 阻抗要求，价格提高10%  <? 0.1表格化>
        if pi.impedance_id:
            if sheet.type=='special_matrial':
                board_size=pi.sepecial_board_size
                special=[('cost_type','=','special_matrial'),('type','=','special_matrial'),('board_size','=',board_size),('po_area_min','<=',sheet.po_area),('po_area_max','>=',sheet.po_area)]
                c_v=self._get_arg(cr,uid,ids,special,'v',context,cost_type)
                obj_id=obj.search(cr,uid,special)
                my=obj.browse(cr,uid,obj_id)[0]
                use_ratio=my.use_ratio
                if board_size=='500*500':
                    se=sheet.special_material_price/(50*50)/pi.matrial_use_ratio/(1-0.1) #材料费
                    co=se * my.append_amount  #报废率
                    tmp=(se+co+base)*0.1
                    
                if board_size=='500*600':
                    se=sheet.special_material_price/(50*60)/pi.matrial_use_ratio/(1-0.1)
                    co=se * my.append_amount
                    tmp=(se+co+base)*0.1
                   
                if board_size=='18*24':
                    se=sheet.special_material_price/(45.72*60.96)/pi.matrial_use_ratio/(1-0.1)
                    co=se * my.append_amount
                    tmp=(se+co+base)*0.1
                if board_size=='36*48':
                    se=sheet.special_material_price / (91.44*121.92)/pi.matrial_use_ratio/(1-0.1)
                    co=se*my.append_amount
                    tmp=(se+co+base)*0.1
                if board_size=='24*36':
                    se=sheet.special_material_price / (60.96*91.44)/pi.matrial_use_ratio/(1-0.1)
                    co=se*my.append_amount
                    tmp=(se+co+base)*0.1
                    
                    
            else:
                tmp= base*0.1
            base_res.add(tmp,[('impedance','=','yes')])
            print base_res,'base_res9'
            self.write(cr,uid,ids[0],{'impdance_price':tmp})
        #非osp表面处理费用, 涂层增加费用少于80 元时，每批最少加收80 元当有效沉金面积大于20%时，按比例加价，
        #如有效面积为25%时则沉金（镀金）单价为0.015X25%/20%=0.01875 元/cm2
        if sheet.po_area>=1 and  pi.surface_treatment and pi.surface_treatment not in [u'OSP',u'有铅喷锡']:
            c_surface=[('cost_type','=','surface_treatment'),('surface_treatment','=',pi.surface_treatment)]
            print c_surface,'c_surface'
            c_v=self._get_arg(cr,uid,ids,c_surface,'v',context,cost_type)
            if pi.au_area<20 and not pi.au_thickness:
                tmp=c_v
                
            else:
                if not pi.au_thickness:
                    tmp=c_v*pi.au_area/100/0.2
            base_res.add(tmp,c_surface)
            self.write(cr,uid,ids[0],{'surface_price':tmp})
            ##沉金或镀金  的有效面积大于25%  <?>
        ###如果有沉金厚度的大于1平方
        if pi.au_thickness and sheet.po_area>=1:
     
            print pi.au_thickness,'au_thickness'
            au_thick=[('cost_type','=','au_amount'),('type','=','normal_mass'),('au_thickness','=',pi.au_thickness)] 
            tmp=self._get_arg(cr,uid,ids,au_thick,'v',context,cost_type)
            print tmp,'tmtm'
            if pi.au_area<20:
                base_res.add(tmp,au_thick)
                self.write(cr,uid,ids[0],{'surface_price':tmp})
            if pi.au_area>=20:
                tmp=tmp*pi.au_area/100/0.2
                base_res.add(tmp,au_thick)
                self.write(cr,uid,ids[0],{'surface_price':tmp})
  
            
        #####特殊材料计算价格 材料来源是自供
        if sheet.type=='special_matrial' and pi.product_material=='come_company':
            board_size=pi.sepecial_board_size
            print board_size,'board_size'
            special=[('cost_type','=','special_matrial'),('type','=','special_matrial'),('board_size','=',board_size),('po_area_min','<=',sheet.po_area),('po_area_max','>=',sheet.po_area)]
            print special,'special' 
            c_v=self._get_arg(cr,uid,ids,special,'v',context,cost_type)
            print c_v,'c_v'
            obj_id=obj.search(cr,uid,special)
            my=obj.browse(cr,uid,obj_id)[0]
            use_ratio=my.use_ratio
            print use_ratio,'use_ratio'
            if board_size=='500*500':
                se=sheet.special_material_price/(50*50)/pi.matrial_use_ratio/(1-0.1) #材料费
                print se,'se'
                co=se * my.append_amount  #报废率
                print co,'co'
                tmp=se+co
                print tmp,'tmp00'
                base_res.add(tmp,special)
                print base_res,'res10'
            if board_size=='500*600':
                se=sheet.special_material_price/(50*60)/pi.matrial_use_ratio/(1-0.1)
                co=se * my.append_amount
                tmp=se+co
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='18*24':
                se=sheet.special_material_price/(45.72*60.96)/pi.matrial_use_ratio/(1-0.1)
                co=se * my.append_amount
                tmp=se + co
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='36*48':
                se=sheet.special_material_price / (91.44*121.92)/pi.matrial_use_ratio/(1-0.1)
                co=se*my.append_amount
                tmp=se+co
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='24*36':
                se=sheet.special_material_price / (60.96*91.44)/pi.matrial_use_ratio/(1-0.1)
                co=se*my.append_amount
                tmp=se+co
            total=tmp+base
            self.write(cr,uid,ids[0],{'bottom_price':total})
            
            
            
         #####特殊材料计算价格 材料来源是客供
        if sheet.type=='special_matrial' and pi.product_material=='come_customer':
            board_size=pi.sepecial_board_size
            print board_size,'board_size'
            special=[('cost_type','=','special_matrial'),('type','=','special_matrial'),('board_size','=',board_size),('po_area_min','<=',sheet.po_area),('po_area_max','>=',sheet.po_area)]
            print special,'special' 
            c_v=self._get_arg(cr,uid,ids,special,'v',context,cost_type)
            print c_v,'c_v'
            obj_id=obj.search(cr,uid,special)
            my=obj.browse(cr,uid,obj_id)[0]
            use_ratio=my.use_ratio
            print use_ratio,'use_ratio'
            if board_size=='500*500':
                se=sheet.special_material_price/(50*50)/pi.matrial_use_ratio/(1-0.1) #材料费
                print se,'se'
                tmp=se * my.append_amount  #报废率
              
                print tmp,'tmp00'
                base_res.add(tmp,special)
                print base_res,'res10'
            if board_size=='500*600':
                se=sheet.special_material_price/(50*60)/pi.matrial_use_ratio/(1-0.1)
                tmp=se * my.append_amount
              
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='18*24':
                se=sheet.special_material_price/(45.72*60.96)/pi.matrial_use_ratio/(1-0.1)
                tmp=se * my.append_amount
               
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='36*48':
                se=sheet.special_material_price / (91.44*121.92)/pi.matrial_use_ratio/(1-0.1)
                tmp=se*my.append_amount
               
                base_res.add(tmp,special)
                print base_res,'res'
            if board_size=='24*36':
                    se=sheet.special_material_price / (60.96*91.44)/pi.matrial_use_ratio/(1-0.1)
                    tmp=se*my.append_amount
            total=tmp+base
            self.write(cr,uid,ids[0],{'bottom_price':total})
        ##最小线宽加价
        if pi.min_line_width < 4 and pi.min_line_width !=0 or pi.min_line_space < 4 and pi.min_line_space !=0:
            min=pi.min_line_width < pi.min_line_space and  pi.min_line_width or pi.min_line_space
            print min,'min'
            print base,'base'
            tmp= base*(4-min)/0.1 * 0.03
            print tmp,'tmp'
            base_res.add(tmp,[('cost_type','=','base'),('min_line_width','=',pi.min_line_width),('min_line_space','=',pi.min_line_space)])
            print base_res,'base11'
            self.write(cr,uid,ids[0],{'min_line_price':tmp})
        #最小成品孔径加价
        if pi.min_finish_hole <= 0.20 and pi.min_finish_hole != 0.0:
            tmp=0.02
            base_res.add(tmp, [('cost_type','=','base'),('min_finish_hole','=', pi.min_finish_hole)])
            print base_res,'base_res12'
            self.write(cr,uid,ids[0],{'min_hole_price':tmp})
        #最小孔到线
        if pi.min_hole2line < 8 and pi.min_hole2line != 0.0:
            tmp= base * (8-pi.min_hole2line)/0.5 * 0.05
            base_res.add(tmp,[('cost_type','=','base'),('min_hole2line','=',pi.min_hole2line)])
            print base_res,'base_res13'
            self.write(cr,uid,ids[0],{'hole_line_price':tmp})

           
        #过孔最小ring
        #器件孔最小ring
        #pad2line
            
        # 非金属化孔公差
        if pi.npth_tolerance < 0.05 and pi.npth_tolerance != 0.0:
            tmp=0.02
            base_res.add(tmp,[('cost_type','=','base'),('npth_tolerance','=', pi.npth_tolerance)])
            print base_res,'base_res14'
        #金属化孔公差
        if pi.pth_tolerance < 0.08 and pi.pth_tolerance != 0.0:
            tmp=0.03
            base_res.add(tmp,[('cost_type','=','base'),('pth_tolerance','=',pi.pth_tolerance)])
            print base_res,'base_res15'
        # 孔密度
        if pi.drill_density > 10:
            tmp=  round(pi.drill_density-10)*0.003
            base_res.add(tmp,[('cost_type','=','base'),('drill_density','=', pi.drill_density)])
            print base_res,'base_res16'
            self.write(cr,uid,ids[0],{'density_price':tmp})
        #锣长
        if pi.route_length/pi.pcs_area > 0.9:
            tmp=  (pi.route_length/pi.pcs_area - 0.9)/0.1*0.002
            base_res.add(tmp,[('cost_type','=','base'),('pi.route_length/pi.pcs_area > 0.9')])
            print base_res,'base_res17'
        #金属半孔
        if pi.half_pth :
            tmp=0.05
            base_res.add(tmp,[('cost_type','=','base'),('half_pth','=', pi.half_pth)])
            self.write(cr,uid,ids[0],{'half_price':tmp})
            print base_res,'base_res18'

        # 台阶孔 或者 控深钻
        if pi.step_hole or pi.control_deep_hole:
            tmp=0.02
            base_res.add(tmp,[('cost_type','=','base'),('npth_tolerance','=',pi.npth_tolerance)])
            print base_res,'base_res20'
            self.write(cr,uid,ids[0],{'step_price':tmp})
            
            
            
            
            
        #材料利用率
#        if pi.matrial_use_ratio:
#            if pi.layer_count == 2 and pi.matrial_use_ratio < 65:
#                tmp=base * (65 - pi.matrial_use_ratio) * 0.008
#                base_res.add(tmp,[('cost_type','=','base'),('matrial_use_ratio','=', pi.matrial_use_ratio)])
#            elif pi.layer_count > 2 and pi.matrial_use_ratio < 60:
#                tmp=base * (60 - pi.matrial_use_ratio) * 0.008
#                base_res.add(tmp,[('cost_type','=','base'),('matrial_use_ratio','=', pi.matrial_use_ratio)])
#            else:
#                pass
        # 小板尺寸加价
        if pi.unit_length >0 and pi.unit_width >0 and pi.unit_length*pi.unit_width<20:
            
            tmp=(20-pi.unit_length * pi.unit_width)*0.002
            
            base_res.add(tmp,[('type','=',sheet.type)])
            self.write(cr,uid,ids[0],{'unit_price':tmp})
        if pi.pcs_length >0 and pi.pcs_width >0 and pi.pcs_length*pi.pcs_width<20:
            
            tmp=(20-pi.pcs_length * pi.pcs_width)*0.002
            
            base_res.add(tmp,[('type','=',sheet.type)])
            self.write(cr,uid,ids[0],{'unit_price':tmp})
        
        if pi.pcs_length < 50 or pi.pcs_width < 50 or pi.pcs_length > 600 or pi.pcs_width > 600:
            pass
        
        #打叉板子费用
        if pi.multi_panel:
            pass #look cost_ready
        if pi.solder_colour:
            if u'太阳' in pi.solder_colour:
                tmp=0.01
                base_res.add(tmp,[('cost_type','=','solder_colour')])
                self.write(cr,uid,ids[0],{'ink_price':tmp})
        #####测试费计算价格
        if sheet.po_area <= 1 :
            if 'false' in [i.test_type]:
                return base_res.value,base_res.info
          
                   
            ##飞针测试免费， 12点/cm2以上，（实际测试点密度-12 点/cm2）×0.004（元/ cm2）
            print pi.test_point_density,'ok'
            if u'飞针测试' in [line.test_type for line in pi_line]:
                fly_cost=0.0
                if pi.test_point_density > 12 and sheet.po_area <= 1:
                    tmp = (pi.test_point_density - 12) * 0.004 
                 
                    base_res.add(tmp,[('cost_type','=','fly'),('test_point_density','>',10),('po_area','<',3)])
                    self.write(cr,uid,ids[0],{'test_price':tmp})
            #专用测试费用
            elif u'专用测试' in [line.test_type for line in pi_line]:
                pass    
            
            ##hdi 测试 , 订单总孔数多于10 万以上的部分，按250 元/10K 孔加收 
#            if sheet.type=='hdi' and sheet.po_area<=1:
#                c_hdi_tes=[('cost_type','=','test'),('type','=','hdi'),('layer_count','=',pi.layer_count)]
#                hdi_cost_test_min=self._get_arg(cr, uid,ids,c_hdi_tes , 'v', context,cost_type)
#                if  hdi_cost_test_min > base_res.value :
#                    base_res.add(hdi_cost_test_min,c_hdi_tes )
#                    
#                #订单总孔数多于10 万以上的部分，按250 元/10K 孔加收    
##                drill_more_10w=pi.test_point_count * sheet.product_number - 100000
#                if drill_more_10w > 0:
#                    tmp=  drill_more_10w * (250/10000)
#                    base_res.add(tmp,[('cost_type','=','test'),('type','=','hdi'),('drill_more_10w','=',drill_more_10w)])
#                self.write(cr,uid,ids[0],{'test_price':tmp})
            ##刚柔结合测试
#            if sheet.type == 'rigid_flexible' and sheet.po_area<=1:
#                c_rf_test=[('cost_type','=','test'),('type','=','rigid_flexible'),('layer_count','=',pi.layer_count)]
#                tmp=self._get_arg(cr, uid,ids,c_rf_test , 'v',context,cost_type )
#                base_res.add(tmp,c_rf_test)
#                self.write(cr,uid,ids[0],{'test_price':tmp})
            
            
                
        #填充pp 芯板
        if pi.fill_pp_count or pi.fill_core_count:
            tmp= pi.fill_pp_count*0.004 + pi.fill_core_count*0.03
            base_res.add(tmp,[('cost_type','=','base'),('fill_pp_count','=', pi.fill_pp_count),('fill_core_count','=', pi.fill_core_count)])
            print base_res,'base_res21'
            self.write(cr,uid,ids[0],{'material_price':tmp})
            


            
        return base_res.value,base_res.info,




    
    def _get_cost_ready(self,cr,uid, ids, context=None,cost_type=None):
        #('normal_sample','normal_mass','hdi', 'rigid_flexible', 'special_matrial', 'none',)
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        pi_line=pi.pcb_info_many
       
        res=price_calculate()
        ##<? 判断是否要收工程费，新单，复投有更改，....>
        ##
        
        c_ready=[('type','=',sheet.type),('layer_count','=',pi.layer_count), ('cost_type','=','ready')]
        
        #特殊板材
        if sheet.type=='special_matrial':
            #计算材料类型
            for i in pi_line:
                if i.board_material and i.is_specia_material:
                    board_material_name=i.board_material
                    
                pass
            print board_material_name,'board_material_id'
            c_ready=( [('type','=',sheet.type),('cost_type','=','ready'),('material_category','=',board_material_name )] )
            #类型是ptfe al ，考虑铜厚
          
            if  u'ptfe' in board_material_name or u'铝基板' in board_material_name:
                cu_thick= max( [line.cu_thickness for line in  pi.layer_cu_thickness_ids] )
                
               # c_ready.extend( [('cu_thickness','=', cu_thick )] )
                
        res_base=  self._get_arg(cr,uid,ids,c_ready,'v',context,cost_type)      
        res.add(res_base,str(c_ready)) 
        
        #有盲埋孔的 提高25%
        if pi.blind_buried_via_ids and sheet.type!='hdi':
            res.add(res_base*+0.25,[('盲埋孔费用')])
        
        #多拼版，每个拼版增加50%
        if pi.multi_panel:
            res.add(res_base* 0.5 * pi.multi_panel,[('多拼版费用')])
        return res.value,res.info
    
        #更改费用
    
    def _get_cost_other(self,cr,uid,ids,context=None,cost_type=None):
        res=price_calculate()
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        pi_line=pi.pcb_info_many
        for i in pi_line:
            if i.special_process:
                special_process=i.special_process
                if  u'蓝胶' in special_process and sheet.type=='normal_sample' or u'碳油' in special_process and sheet.type=='normal_sample':
                    tmp=100
                    res.add( tmp)
                
            pass
#        if sheet.type=='normal_sample' and  pi.surface_treatment and pi.surface_treatment.name not in ['hasl','osp']:
        if sheet.po_area<1 and  pi.surface_treatment and pi.surface_treatment not in [u'有铅喷锡','osp']:    
            c_surface=[('cost_type','=','surface_treatment'),('surface_treatment','=',pi.surface_treatment)]
            #加价小于80的按80计算
            if  pi.au_area<= 20 and not pi.au_thickness:
                tmp=80
                res.add( tmp, c_surface)
            else:
                if not pi.au_thickness:
                    tmp=80 * pi.au_area/100 /0.2
                    res.add( tmp, c_surface)
        if pi.au_thickness:
            if sheet.po_area<1 :
                au_thick=[('cost_type','=','au_amount'),('type','=','normal_sample'),('au_thickness','=',pi.au_thickness)] 
                tmp=self._get_arg(cr,uid,ids,au_thick,'v',context,cost_type)
                print tmp,'au_thickness'
                if pi.au_area<=20:
                    res.add(tmp,au_thick)
                if pi.au_area>20:
                    tmp=tmp * pi.au_area/100 /0.2
                    res.add(tmp,au_thick)
                    
                    
        if sheet.type=='hdi' and  pi.pcs_drill_count*sheet.product_number > 100000:
            res_value=res.value+ (pi.pcs_drill_count*sheet.product_number-100000)/10000*250
            res.add(res_value,[('cost_type','=','other'),('type','=','hdi'),])
       
        return res.value,res.info
    
    def _get_cost_gold_finger(self,cr,uid,ids,context=None,cost_type=None):
        res=price_calculate()
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        
        if pi.gold_finger_id:
            finger=pi.gold_finger_id
            finger_count=finger.finger_count*finger.finger_width*finger.finger_length/7
            print finger_count,'finger_count'
            f_base=self._get_arg(cr, uid, ids,[('cost_type','=','finger',),
                                           ('au_thick_min','<', finger.au_thick),
                                           ('au_thick_max','>=', finger.au_thick),
                                           ('finger_count_min','<=', finger_count),
                                           ('finger_count_max','>=', finger_count),
                                           ], 'v',context,cost_type )
            print f_base,'f_base'
#            res_value=res.value+f_base*sheet.product_number
            res_value=f_base*sheet.product_number*1.3
            if sheet.po_area<1:
                if pi.gold_finger_id.au_thick < 20 :
                    if res_value<200:
                        res_value=200
                if pi.gold_finger_id.au_thick >=20 :
                    if res_value<300:
                        res_value=300
                    
            res.add(res_value, [('cost_type','=','finger',),
                                           ('au_thick_min','<', finger.au_thick),
                                           ('au_thick_max','>=', finger.au_thick),
                                           ('finger_count_min','<=', finger_count),
                                           ('finger_count_max','>=', finger_count),
                                           ])
            self.write(cr,uid,ids[0],{'finger_price':f_base})
        return res.value,res.info
        
    
    def default_layer_cu_thickness(self,cr,uid,ids,context=None):
        for id in ids:
            pi=self.browse(cr,uid,id,context=context)
            for line in pi.layer_cu_thickness_ids: 
                self.write(cr,uid,id,{'layer_cu_thickness_ids':[(2,line.id)]})
            for name in ['top']+['l'+str(l) for l in range(2, pi.layer_count)]+['bot']:
                self.write(cr,uid,id,{'layer_cu_thickness_ids':[(0,0,{'name':name,'cu_thickness':1})]})
        return True
    def is_need_cost_cu(self,cr,uid,ids,context=None):
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        
        for line in pi.layer_cu_thickness_ids:
            if line.cu_thickness > 1:
                return True
        return False
    def is_cu_thickness_same(self,cr,uid,ids,context=None):
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        
        if len( set( [line.cu_thickness for line in pi.layer_cu_thickness_ids] ) ) == 1:
            return True
        else:
            return False
    def get_cu_thickness_hash(self,cr,uid,ids ,context=None):
        sheet=self.browse(cr, uid, ids[0], )
        pi=sheet.pcb_info_id
        
        res={}
        for line in pi.layer_cu_thickness_ids:
            res[line.cu_thickness] = res.get(line.cu_thickness) and res[line.cu_thickness]+1 or 1
        return res

    def updata_state(self, cr, uid, ids, state=None, state_filter=None, **args):
        return self.write(cr, uid, ids, {'state':state})
    
    #生成销售订单
    def to_sale_order(self,cr,uid,ids,context=None):
        sol_obj=self.pool.get('sale.order.new.line')
        so_obj=self.pool.get('sale.order.new')
        
        partner_obj=self.pool.get('res.partners')
        
        price_sheet=self.browse(cr, uid, ids[0],)
        partner=price_sheet.partner_id
        self.write(cr,uid,price_sheet.id,{'state':'done'})
        self.pool.get('order.recive').write(cr,uid,price_sheet.lead_id.id,{'state':'wait_sale'})
        if not partner.partner_code and partner.customer:
            ref=self.pool.get('ir.sequence').get(cr,uid,'res.partners')
            partner_obj.write(cr,uid,partner.id,{'partner_code':ref})

        print partner.street,'addr'

        print partner['street2'],'partner.id',partner['street'],partner.id
        if partner['street']:
            so_id=so_obj.create(cr,uid,{
                                        'partner_id':partner.id,
                                        'street': partner['street'],
                                        'street1': partner['street2'],
                                                      })
            print so_id,'so_id'
            print sol_obj,'sol_obj'
            if so_id:
                sol_id=sol_obj.create(cr,uid,{
                    'sale_order_new_id'  :so_id,
                    'price_sheet_id'       :price_sheet.id,  
                    'wait_production_count':price_sheet.product_number,
                    'price_unit':price_sheet.cost_pcs_s,
                    'product_qty':price_sheet.product_number,
               

                })
                print sol_id,'sol_id'
                return {'name':_("Convent sale order"),
                            'view_mode': 'form',
                            'view_id': False,
                            'view_type': 'form',
                            'res_model': 'sale.order.new',
                            'res_id': so_id,
                            'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'domain': [],
                  }
        else:
            raise osv.except_osv(_('Error'),_('没有客户地址信息,请检查!'))
        
        
    def create_product_code(self,cr,uid,ids,line_id=None,context=None):
        my=self.browse(cr,uid,ids[0])
        default_code=self.browse(cr,uid,ids[0]).product_id
        line_obj=self.pool.get('sale.order.new.line')
        product_id=False
        if default_code:
            product_id=default_code
            #raise osv.except_osv(_('Error Product exists!'),_('product is exists '))
        else:
            
            type=[]
            code=self.pool.get('ir.sequence').get(cr,uid,'product.code')
            layer_count=self.browse(cr,uid,ids[0]).pcb_info_id.layer_count
            obj=self.pool.get('pcb.sequence.code')
            if layer_count==1:
                type='S'
            if layer_count==2:
                type='D'
            if layer_count>2:
                type='M'
            id=obj.search(cr,uid,[('type','=',type)])[0]
            obj_name=obj.browse(cr,uid,id).name
            b=obj_name[1:]
            length=len(b)-int(b)
            print length,'l'
            default_code=str(int(b)+1)
            print default_code,'code'
            d=default_code.zfill(len(b))
            print d,'d'
            if layer_count==1:
                default_code='S'+d
                
            elif layer_count==2:
                default_code='D'+d
                
            elif layer_count>2:
                default_code='M'+d
               
            print default_code,'default_code'
   #         product_id=self.pool.get('product.product').create(cr,uid,{
   #           'name':default_code,
   #           'default_code': default_code,
                                         
    #        })
            obj.write(cr,uid,id,{'name':default_code,'type':type})
            print my.partner_id.id,'my.partner_id',my.pcb_info_id
            ###创建档案号时同时创建一张档案号清单
            self.pool.get('pcb.list').create(cr,uid,{'name':default_code,
                                                     'pcb_info_id':my.pcb_info_id.id,
                                                     'partner_id':my.partner_id.id,
                                                     })
        if line_id:
            line_obj.write(cr,uid,line_id,{'product_id':default_code})
              
        self.write(cr,uid,ids[0],{'product_id':default_code,})
        return True
   
#-----------同步数据到东烁--------------
    def insert_to_ds(self,cr,uid,id,vals,context=None):  
        column=[]
        info=self.browse(cr,uid,id)
        
        currencyname=info.partner_id.currency
        addr=info.partner_id.street
        billcode=info.lead_id.name
        cost_other_s=info.cost_all_o-(info.cost_ready_s+info.cost_plot_s+info.cost_test_s+info.cost_pcs_s*info.product_number)
        
        column.append('')
        column.append('')
        column.append('')
        column.append(0.0)
        column.append(0)
        column.append('')
        column.append('')
        column.append(0)
        column.append('')
        column.append('')
        
        column.append(0.0)
        column.append(info.product_number)
        column.append(info.cost_pcs_s)
        column.append(info.cost_plot_s)
        column.append(currencyname)
        column.append(info.cost_ready_s)
        column.append(info.cost_test_s)
        column.append(0.0)
        column.append(cost_other_s)
        column.append(info.note)
        
        column.append(0.0)
        column.append(0.0)
        column.append('')
        column.append(str(info.delivery_leadtime))
        column.append('')
        column.append('')
        column.append(0)
        column.append('')
        column.append('')
        column.append(0)
        
        column.append('')
        column.append('')
        column.append('')
        column.append('')
        column.append(addr)
        
        column.append(billcode)
        column.append('create')
        column.append('')
        print column
		#if not billcode:
         #   raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
        row=[]
        for i in range(len(column)):
           if type(column[i])==type(u'中文'):
                 row.append((column[i]).encode('utf-8'))
           else:
                 row.append(column[i])    
        row=tuple(row)
    
        try:
           conn=pymssql.connect(server=server,user=user,password=password,database=database)
           cur=conn.cursor()
           print len(row),'len(row)'
           sql='''exec pp_TBprduction_BJ_OE '%s','%s','%s','%f','%d','%s','%s','%d','%s','%s',
                                            '%f','%d','%f','%f','%s','%f','%f','%f','%f','%s',
                                            '%f','%f','%s','%s','%s','%s','%d','%s','%s','%d',
                                            '%s','%s','%s','%s','%s','%s','%s','%s' ''' %row
           print sql.encode('gbk')   
           cur.execute(sql) 
        except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
                
                conn.commit()
                conn.close() 
                print u'更新成功'
        return id     
    def create(self,cr,uid,vals,context=None):
          print 'price.sheet','create'
        
          id=super(price_sheet,self).create(cr,uid,vals,context=context)
          return self.insert_to_ds(cr,uid,id,vals,context=context)
    
    def update_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
        else:
            info=self.browse(cr,uid,ids)
        currencyname=info.partner_id.currency
        addr=info.partner_id.street
        billcode=info.lead_id.name
        cost_other_s=info.cost_all_o-(info.cost_ready_s+info.cost_plot_s+info.cost_test_s+info.cost_pcs_s*info.product_number)
        print cost_other_s,'cost_other_s'
        column.append('')
        column.append('')
        column.append('')
        column.append(0.0)
        column.append(0)
        column.append('')
        column.append('')
        column.append(0)
        column.append('')
        column.append('')
        
        column.append(0.0)
        column.append(info.product_number)
        column.append(info.cost_pcs_s)
        column.append(info.cost_plot_s)
        column.append(currencyname)
        column.append(info.cost_ready_s)
        column.append(info.cost_test_s)
        column.append(0.0)
        column.append(cost_other_s)
        column.append(info.note)
        
        column.append(0.0)
        column.append(0.0)
        column.append('')
        column.append(str(info.delivery_leadtime))
        column.append('')
        column.append('')
        column.append(0)
        column.append('')
        column.append('')
        column.append(0)
        
        column.append('')
        column.append('')
        column.append('')
        column.append('')
        column.append(addr)
        
        column.append(billcode)
        column.append('write')
        column.append('')
        if not billcode:
            raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
        print column
        row=[]
        for i in range(len(column)):
           if type(column[i])==type(u'中文'):
                 row.append((column[i]).encode('utf-8'))
           else:
                 row.append(column[i])    
        row=tuple(row)
    
        try:
           conn=pymssql.connect(server=server,user=user,password=password,database=database)
           cur=conn.cursor()
           print len(row),'len(row)'
           sql='''exec pp_TBprduction_BJ_OE '%s','%s','%s','%f','%d','%s','%s','%d','%s','%s',
                                            '%f','%d','%f','%f','%s','%f','%f','%f','%f','%s',
                                            '%f','%f','%s','%s','%s','%s','%d','%s','%s','%d',
                                            '%s','%s','%s','%s','%s','%s','%s','%s' ''' %row
           print sql.encode('gbk')   
           cur.execute(sql) 
        except:
               raise osv.except_osv(_('Error!'),_(u'更新失败，请检查数据是否正确！'))
        else:
                
                conn.commit()
                conn.close() 
                print u'更新成功'
        return True
    def write(self,cr,uid,ids,vals,context=None):
        print 'price.sheet','write'
        super(price_sheet,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True   
    
price_sheet()

class product_product (osv.osv):
    _inherit = "product.product"
    _columns = {
        'price_sheet_id':fields.many2one('price.sheet', 'price_sheet_id',  readonly=False),       
        
            
    }
    #===========================================================================
    # _constraints=[
    # ]       
    #===========================================================================
product_product()



