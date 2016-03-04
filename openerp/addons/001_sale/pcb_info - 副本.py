# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from  openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
 
class blind_buried_via(osv.osv):
    _name='blind.buried.via'
    _columns={
        'name': fields.char(u'名称', size=16,  select=True,),
        'start':fields.integer(u'开始', ),
        'end':fields.integer(u'结束', ),
        'pcb_info_id':fields.many2one('pcb.info', u'用户单' , ondelete="cascade", invisible=True),        
    }
    #===========================================================================
    # _sql_constraints = [
    #    ('name', 'unique (name)', 'name  must unique!'),        
    # ]    
    #===========================================================================
blind_buried_via()

class pcb_info_mark(osv.osv):
    _name='pcb.info.mark'
    _columns={
        'name':fields.char('Mark name',size=64),
    }
pcb_info_mark()

class layer_cu_thickness(osv.osv):
    _name='layer.cu.thickness'
    _columns={
        'name': fields.char(u'名称', size=16,  select=True,),
        'cu_thickness':fields.integer(u'铜厚', ),
        'pcb_info_id':fields.many2one('pcb.info', u'用户单' , ondelete="cascade", invisible=True),        
        'impdance_info_ids':fields.one2many('impdance.info','layer_cu_thickness_id',u'阻抗信息'),#阻抗描述
    }       
layer_cu_thickness()  


#===============================================================================
# class layer_structure_line(osv.osv):
#    pass
#    _name='layer.structure.line'
#    _columns = {
#        'name': fields.char('name', size=16,  select=True,),
#        'type': fields.selection([('cu','CU'),('pp','PP'),('core','Core')],'Type', size=16, required=True, select=True,),
#        'cu_cu':fields.float( 'cu_cu',),
#        'core_top_cu':fields.float( 'core_top_cu',),
#        'core_bottom_cu':fields.float( 'core_bottom_cu',),
#        'core_thick':fields.float( 'core_base',),
#        'pp_thick':fields.float( 'pp_thick',),
#    }
#    _sql_constraints = [
#        ('name', 'unique (name)', 'name  must unique!'),        
#    ]    
# layer_structure_line()  
#===============================================================================
 
class  gold_finger (osv.osv):
    _name='gold.finger'
    _columns = {
        'name': fields.char(u'名称', size=16, required=True, select=True,),
        'finger_count':fields.integer( u'金手指数量',),
        'au_thick':fields.float(u'金厚',),
        'ni_thick':fields.float( u'镍厚',),       
        'finger_length':fields.float( u'金手指长',),
        'finger_width':fields.float( u'金手指宽',), 
        'bevel_edge'  :fields.selection([('30','30'),('45','45'),('60','60')], u'斜边度',),
        'note' :fields.char(u'备注',size=64,),
    }
    _sql_constraints = [
        ('name', 'unique (name)', 'name  must unique!'),        
    ]
gold_finger()  

#===============================================================================
# class  solder_mask (osv.osv):
#    _name="solder.mask"
#    
# solder_mask()
#===============================================================================
#===============================================================================
# class layer_structure(osv.osv):
#    _name='layer.structure'
#    _columns = {
#        'name': fields.char('name', size=16,  select=True,),
#    }
# layer_structure()
#===============================================================================

class select_selection(osv.osv):
    _inherit='select.selection'
    _columns={
        'route_type_id':  fields.many2one('pcb.info', u'外形加工',),
        'test_type_id':  fields.many2one('pcb.info', u'通断测试',),
        'accept_standard_id':  fields.many2one('pcb.info', u'验收标准',),
        'request_with_goods_id':fields.many2one('pcb.info', u'付货要求',),
        'packing_type_id':fields.many2one('pcb.info', u'包装方式',),
        'mark_request_id': fields.many2one('pcb.info', u'标记要求',),
        'special_process_id':fields.many2one('pcb.info', u'特殊工艺',),
        'board_material_id':fields.many2one('pcb.info',u'板材料'),
    }
select_selection()

class pcb_info (osv.osv):
    _name='pcb.info'
    _description = "pcb.info"

    def _info_get(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        for id in ids:
            me=self.browse(cr, uid, id, context,)
            if me.state == 'draft':   #  if state is draft , function fields dont need computer
                res[id]=0
                continue
            
            elif field_name == 'pcs_area':
                res[id]=(me.pcs_length * me.pcs_width)
            elif field_name == 'delivery_type':
                res[id]=me.pcs_unit_count
            elif field_name == 'test_point_density' and me.pcs_area:
                res[id]=me.test_point_count/me.pcs_area
            elif field_name == 'drill_density' and me.pcs_area:
                res[id]=(me.pcs_drill_count + me.pcs_slot_count*20)/me.pcs_area
            elif field_name == 'standard_days':
                days=self._get_arg(cr,uid,[('layer_count','=',me.layer_count),('cost_type','=','standard_days')])
                cu_max=self.get_cu_thickness_max(cr,uid,me)
                days= cu_max>2 and days+cu_max-1 or days
                days= me.pad_via and days+2 or days
                if me.blind_buried_via_ids:
                    for line in me.blind_buried_via_ids:
                        days=abs(line.end-line.start)==1 and days+1 or days+2
                #if add days to
                res[id]=days
            #===================================================================
            # elif field_name == 'plot_count':
            #    dic_sm={'no':0,'double':2,'top_bo':1,'top_bf':2,'bot_to':1,'bot_tf':2,}
            #    dic_ss={'no':0,'double':2,'top':1,'bot':1,}
            #    res[id]=me.layer_count + dic_sm.get(me.solder_type,0) + dic_ss.get(me.silk_type ,0)
            #===================================================================
                
        return res   
    
    def _check_one2one(self,cr,uid,ids,context=None):
        for me in self.browse(cr, uid, ids, context,  ):
            if me.gold_finger_id  and  me.gold_finger_id.name != me.name:
                return False
        return True    
    def _check_state(self,cr,uid,ids,context=None):  
        '''
            when state is not draft, some argment is must > 0
        '''
        for me in self.browse(cr, uid, ids, context,  ): 
            if me.state != 'draft':       
                for k in ['layer_count','pcs_length','pcs_width','min_line_width','min_line_space','pcs_drill_count',]:
                    if getattr(me ,k,0.0)<=0.0 :
                        return False
        return True
    def _check_layer_count(self,cr,uid,ids,context=None):
        for me in self.browse(cr, uid, ids, context,  ):        
            if me.layer_count % 2:
                return False
        return True
    def check_draft2wait_order_supervisor(self,cr,uid,ids,context=None):
        info=''
        field_gt_zero=[
            'layer_count','finish_board_thickness','min_line_width',
            'min_line_space','pcs_drill_count','pcs_length','pcs_width','unit_length','unit_width',
            'basic_board_thickness','finish_tol_upper',
            
        ] ## 不能小于0的组的字段
        field_cant_none=[ 'silk_colour','solder_colour',
        ]#不能为空的字段
        trans_obj=self.pool.get('ir.translation')
        for key in field_gt_zero:
                trans=trans_obj._get_source(cr,uid,'','field','zh_CN',source=self._columns[key].string)
                if key=='layer_count':
                    if self.read(cr,uid,ids[0],[key])[key]<30:
                        continue
                    else:
                        info+=trans+'must be <30 \n'
                else:
                    if  self.read(cr,uid,ids[0],[key])[key]>0:
                        continue
                    else:
                        info+=trans+'must be >0 \n'
        for k in field_cant_none:
            if self.read(cr,uid,ids[0],[k])[k]==False:
                trans=trans_obj._get_source(cr,uid,'','field','zh_CN',source=self._columns[k].string)
                info+=trans+'can not be None! \n' 
        if info:
            raise osv.except_osv(_('input value Error'),info )
        return True
            
    def onchange_tol_upper(self,cr,uid,ids,finish_tol_upper,context=None):
        return{'value':{'finish_tol_lower':finish_tol_upper}}  
    _state_list=('draft','wait_order_supervisor','done','refuse')
    _state_list=[(i,i.title()) for i in _state_list] 
    
    _columns = {
        'product_id' :fields.many2one('product.product',u'档案号',  select=True),
        'name'       :fields.char(u'用户单号', size=64,readonly=False), 
        'state'      :fields.selection(_state_list,u'单据状态',size=64,readonly=True,select=True),
        'temp_state':fields.char('Temp state',size=64),
        'responsible_id': fields.many2one('res.users',u'负责人', size=16,  select=True,domain=[('context_department_id','=','订单中心')]),
        'create_time'  :fields.date(u"创建日期", readonly=True),
        'board_material'              :fields.one2many('select.selection','board_material_id',u'板材料',domain=[('type','=','board_material')],), #板材类型
        'mix_press'                   :fields.boolean(u'混压'),     #混压
        'partner_id'                  :fields.many2one( 'res.partners', u'客户', select=True, domain=[('customer','=',True)]),##
        'basic_board_thickness'       :fields.float( u'基板厚度',), #基础板厚
		'contract_id'                 :fields.char(u'合同号',size=32,),#合同号
        'layer_count'            :fields.integer(u'层数', change_default=True), #层数
        'finish_board_thickness' :fields.float( u'成品板厚度',),#成品板厚
        'finish_tol_upper'       :fields.float( u'成品公差正',),#成品公差
        'finish_tol_lower'       :fields.float( u'成品公差负',),#成品公差
        'surface_treatment'           :fields.many2one( 'select.selection', u'表面涂覆' ,domain=[('type','=','surface_treatment')]),#表面处理
        'surface_treatment_request'   :fields.char(  u'涂覆描述' ,size=64,),#表面处理要求
        'gold_finger_id'              :fields.many2one( 'gold.finger', u'金手指', domain="[('name','=',name)]"),#金手指
        'special_process' :fields.one2many('select.selection', 'special_process_id',u'特殊工艺',domain=[('type','=','special_process')]),#特殊工艺
        'special_process_note'             :fields.text( u'特殊工艺' ,),#特殊工艺说明   
        'solder_colour'      :fields.many2one('select.selection',u'阻焊颜色', domain=[('type','=','solder_colour')]),#阻焊颜色 
        'solder_variants'    :fields.many2one('select.selection',u'阻焊油墨',domain=[('type','=','ink_type')]), #阻焊油墨型号
        'solder_type'        :fields.many2one('select.selection', u'阻焊类型',domain=[('type','=','solder_type')]),#阻焊类型
        'solder_via'         :fields.many2one('select.selection', u'过孔阻焊',domain=[('type','=','solder_via')],),#过孔阻焊方式
        'silk_colour'             :fields.many2one('select.selection',u'字符颜色', domain=[('type','=','silk_colour')]),  #字符颜色
        'silk_variants'           :fields.many2one('select.selection',u'字符油墨',domain=[('type','=','ink_type')]), #字符油墨型号
        'silk_type'               :fields.many2one('select.selection', u'字符类型',domain=[('type','=','silk_type')]),#字符类型  
        'route_type'            :fields.one2many('select.selection','route_type_id',u'外形加工',domain=[('type','=','route_type')]) ,#外形方式
        'vcut_angle'            :fields.many2one('select.selection',u'VCUT度',domain=[('type','=','vcut_angle')]) ,#vcut角度
        'accept_standard'      :fields.one2many('select.selection','accept_standard_id',u'验收标准',domain=[('type','=','accept_standard')]) ,##验收标准
        'test_type'            :fields.one2many('select.selection','test_type_id',u'通断测试',domain=[('type','=','test_type')]) ,#测试类型
        'mark_request'         :fields.one2many('select.selection','mark_request_id',u'标记要求',  domain=[('type','=','mark_request')]  ), #标记要求
        'packing_request'      :fields.char(u'包装要求',  size=128  ), #包装要求
        'request_with_goods'   :fields.one2many('select.selection','request_with_goods_id',u'附货要求',domain=[('type','=','request_with_goods')]), #附货要求     
        'min_line_width'              :fields.float( u'最小线宽',),#最小线
        'min_line_space'              :fields.float( '最小间距',),#最先线距
        'min_line2pad'                :fields.float( u'最小线到pad',),  #线到pad
        'min_finish_hole'             :fields.float( u'最小成品孔径',),#最小成品孔径
        'min_hole2line'               :fields.float( u'最小孔到线',),  #最小孔到线
        'min_via_ring'                :fields.float( u'最小过孔焊环',),   #最小过孔焊环
        'min_pth_ring'                :fields.float( u'最小器孔焊环',),   #最小器件孔焊环
        'pcs_drill_count'            :fields.float( u'pcs钻孔数量',),#pcs钻孔数量
        'pcs_slot_count'             :fields.float( u'pcs槽孔数量',change_default=True,), #pcs槽孔数量
        'fill_core_count'   :fields.integer(u'填充芯板', ),  #填充芯板
        'fill_pp_count'     :fields.integer(u'填充PP', ),    #填充PP
        'source_file_name'      :fields.char( u'源文件名',  size=128 ), #源文件名
        'soft_info'             :fields.char( u'软件信息',  size=32),##软件信息
        'soft_version':       fields.many2one('select.selection',u'软件版本',domain=[('type','=','soft_version')]),
        'source_product_code'   :fields.char( u'零件号',  size=32),#零件号
        'outline_size_request'        :fields.selection([('according_file',u'通过文件'),('other',u'其他')],u'按外形尺寸要求') ,#外形尺寸要求
        'pcs_length'                  :fields.float( u'pcs长', change_default=True,),#长
        'pcs_width'                   :fields.float( u'pcs宽',  change_default=True,),#宽
        'panel_request'               :fields.char(u'拼版要求',  size=32,),#拼版要求
        'unit_length'                 :fields.float(u'unit长', change_default=True),#单元长
        'unit_width'                  :fields.float(u'unit宽',  change_default=True),#单元宽
        'delivery_type':           fields.function(_info_get,method=True,type='integer',string=u'交货类型'),
        'allow_scrap_count'  :fields.integer(u'允许报废数量', ),#允许报废数量
        'allow_scrap_percent':fields.integer(u'允许报废比例',),    #允许报废比例
        'special_indicate'           :fields.text(u'特殊指示',),#特殊指示
        'test_point_count'            :fields.float( u'测试点数量',change_default=True,),#测试点数量        
        'surface_area'                :fields.float( u'涂覆面积',change_default=True),##表面处理面积
        'order_recive_id'            :fields.many2one('order.recive',u'接单单号'),
        'custmer_goodscode'           :fields.related('order_recive_id','custmer_goodscode',type='char',string=u'零件号',store=True,relation='order.recive',size=64), ## 零件名    
        'custmer_handler'             :fields.char      ( 'Custmerhandler',  size=30    ), ## 选择一个客户联系
        'blind_buried_via_ids'         :fields.one2many('blind.buried.via','pcb_info_id',u'盲埋孔'),#盲埋孔
        'layer_cu_thickness_ids'       :fields.one2many('layer.cu.thickness','pcb_info_id',u'铜厚信息'),#铜厚信息
        'impedance_id'                 :fields.boolean( u'阻抗',),#阻抗
 ####客户对产品的通用要求字段
        'packing_type':                 fields.one2many('select.selection','packing_type_id',u'包装方式',domain=[('type','=','packing_type')]),
        'count_unit_package'        :fields.integer(u'int每包数量'), #int每包数量
        'add_delivery_chapter'      :fields.boolean(u'是否加发货章'), #bool 是否加发货章
        'provide_steel_net'         :fields.boolean(u'提供钢网'),  #bool
        'provide_gerber'            :fields.boolean(u'提供生产gerber'),  #bool
        'confirm_gerber'            :fields.boolean(u'确认gerber后生产'),  #bool
        'packing_note'              :fields.text(u'包装备注'),   #包装备注
        'delivery_order_request'    :fields.text(u'送货单要求'), # 送货单要求
        'partner_special_request'   :fields.text(u'客户特殊要求'),  #客户特殊要求
        ##########################
        'npth_tolerance'              :fields.float( u'非金属化孔公差',),#非金属化孔公差
        'pth_tolerance'               :fields.float( u'金属化孔公差',),#金属化孔公差
        'hoe_density'                 :fields.float( u'孔密度',),#孔密度
        'route_length'                :fields.float( u'锣程长度',),#锣程长度
        'half_pth'                    :fields.float( u'金属化半孔',),#金属化半孔
        'flexible_layer_count'        :fields.integer( u'柔板层数',),#柔板层数
        'pad_via'                     :fields.float( u'盘中孔',),#盘中孔
        'control_deep_hole'           :fields.float( u'孔深钻',),#孔深钻
        'step_hole'                   :fields.float( u'台阶孔',),#台阶孔
        'multi_panel'                 :fields.float( u'多拼版',),#多拼版
        'laminar_structure'           :fields.float( u'层压结构',),#层压结构，
        'pcs_unit_count'              :fields.integer(u'UNIT/PCS数 量',), #pcs 的unit数
        'plot_count':                   fields.integer(u'菲林张数'),#菲林张数
        'pcs_area'                    :fields.function(_info_get, method=True, type='float',  string=u"pcs面积",),#面积
        'drill_density'               :fields.function(_info_get, method=True, type='float',  string=u"孔密度",),#孔密度      
        'test_point_density'          :fields.function(_info_get, method=True, type='float',  string=u"测试点密度",),#测试点密度
        'standard_days'               :fields.function(_info_get, method=True, type='float',  string=u"标准周期",), #标准周期
        'cost_ready'                  :fields.float( u'准备费',digits_compute=dp.get_precision('Account'), readonly=True),  #工程准备费用
        'cost_plot'                   :fields.float( u'菲林费',digits_compute=dp.get_precision('Account'),readonly=True),   #菲林费
        'cost_test'                   :fields.float( u'测试费',digits_compute=dp.get_precision('Account'),readonly=True),   #测试费
        'cost_pack'                   :fields.float( u'工程打包费',digits_compute=dp.get_precision('Account'),readonly=True),   #工程打包费
        'cost_base'                   :fields.float( u'基板费',digits_compute=dp.get_precision('Account'),readonly=True),   #基础板费
        'cost_mould'                  :fields.float( u'磨具费',digits_compute=dp.get_precision('Account'),readonly=True),  #磨具费用
        'cost_change'                 :fields.float( u'变更费',digits_compute=dp.get_precision('Account'),readonly=True), #变更费用
        'cost_other'                  :fields.float( u'其他费',digits_compute=dp.get_precision('Account'),readonly=True),  #其他费用
        'cost_days'                   :fields.float( u'加急费',digits_compute=dp.get_precision('Account'),readonly=True),   #加急费用
        'cost_pcs'                    :fields.float( u'pcs单价',digits_compute=dp.get_precision('Account'),readonly=True),    #pcs单价
        'cost_sqcm'                   :fields.float( u'平方厘米价',digits=(12,5),readonly=True),
        'cost_all'                    :fields.float( u'费用汇总',digits_compute=dp.get_precision('Account'),readonly=True), #费用记总
        'matrial_use_ratio':     fields.float(u'材料利用率'),#材料利用率
        'eng_note':fields.text(u'工程要求'),
        'delivery_note':fields.text(u'出货要求(品质部)'),
        'normal_order_note':fields.text(u'标准用户单'),
        'per_quantity':fields.integer(u'每包数量'),
    }
    _defaults = {  
        'name': lambda obj, cr, uid, context:  obj.pool.get('ir.sequence').get(cr, uid, 'pcb.info'), 
        'create_time': lambda *a: time.strftime('%Y-%m-%d'),  
        'state'    :lambda *a: 'draft',
        'responsible_id': lambda  self,cr,uid,ids: uid,
        'pcs_unit_count':lambda *a: 1,
        
        'layer_count':0,
        'finish_board_thickness':0,
        'min_line_width':0,
        'min_line_space':0,
        'pcs_drill_count':0,
        'pcs_length':0,
        'pcs_width':0,
        'matrial_use_ratio':0,
    }
    
    _sql_constraints = [
        ('name', 'unique (name)', 'name  must unique!'),  
        ('product_id', 'unique (product_id)', 'product_id  must unique!'),  
        #('matrial_use_ratio','CHECK (0 < matrial_use_ratio and matrial_use_ratio <= 1)','matrial_use_ratio must be between 0 and 1 !'),
        #=======================================================================
        # ('pcs_length', 'CHECK(state != "draft" and pcs_length > 0 )', 'pcs_length must be greater than zero.'),   
        # ('pcs_width', 'CHECK( pcs_width > 0 )', 'pcs_width  must be greater than zero.'),
        # ('min_line_width', 'CHECK( min_line_width > 0 )', 'min_line_width  must be greater than zero.'),
        # ('finish_board_thickness', 'CHECK( finish_board_thickness > 0 )', 'finish_board_thickness  must be greater than zero.'),
        # ('min_line_space', 'CHECK( min_line_space > 0 )', 'min_line_space  must be greater than zero.'),
        # ('pcs_drill_count', 'CHECK( pcs_drill_count > 0 )', 'pcs_drill_count  must be greater than zero.'),
        # ('min_line_space', 'CHECK( min_line_space > 0 )', 'min_line_space  must be greater than zero.'),
        # ('layer_count', 'CHECK( layer_count > 0 )', 'layer_count  must be greater than zero.'),
        # ('pcs_drill_count', 'CHECK( pcs_drill_count > 0 )', 'pcs_drill_count  must be greater than zero.'),      
        #=======================================================================
     ]
    _constraints=[
        (_check_one2one, 'Error !gold_finger name must ==  pcb_info name', ['gold_finger_id']),
        (_check_layer_count,'Error! layer count cant be odd number 1,3,5...',['layer_count'] ),
        (_check_state,'Error! when draft approve , argments must > 0',['state'] ),
        
        ##(_check_product_id,'Error! product code must == name',['product_id'] ),
        
    ]    
    def copy(self, cr, uid, id, default=None, context=None):
        default=default or {}      
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'pcb.info'),
            'product_id':None,
        })
        return super(pcb_info, self).copy(cr, uid, id, default, context)
    
    def _get_arg (self,cr,uid, condition=None, field_name='v',   context=None ,):
        print condition
        obj=self.pool.get('pcb.cost.argument')
        ids=obj.search(cr,uid,condition)
        if not ids:
            raise osv.except_osv(_('Warning !'), _('not found argumnet %s' % condition) )
            
        me=ids and  obj.browse(cr,uid,ids[0])
        res= getattr(me, field_name,False)
        if res is False:
            pass 
        else:
            return res
        
    
    def default_layer_cu_thickness(self,cr,uid,ids,context=None):
        for id in ids:
            me=self.browse(cr,uid,id,context=context)
            for line in me.layer_cu_thickness_ids: 
                self.write(cr,uid,id,{'layer_cu_thickness_ids':[(2,line.id)]})
            for name in ['top']+['l'+str(l) for l in range(2, me.layer_count)]+['bot']:
                self.write(cr,uid,id,{'layer_cu_thickness_ids':[(0,0,{'name':name,'cu_thickness':1})]})
        return True



    def get_cu_thickness_max(self,cr,uid,me=None ,context=None):
        res=0
        for line in me.layer_cu_thickness_ids:
            res=  line.cu_thickness > res and line.cu_thickness or res
        return res
    def updata_state(self, cr, uid, ids, state=None, state_filter=None, **args):
        self.write(cr, uid, ids, {'state':state})
        
    def to_price_shhet(self,cr,uid, ids,context=None):  
        me=self.browse(cr,uid,ids[0],context,)
        if me.state == 'done':
            ps_id=self.pool.get('price.sheet').create(cr,uid,{'pcb_info_id':me.id,})
            return {
                'name':_("price sheet"),
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'price.sheet',
                'res_id': ps_id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'domain': '[]',
                'context': dict(context, active_ids=ids)
            }
        else:
            raise osv.except_osv(_('Warning !'), _('state must be done') )
    def onchange_silk_solder_colour(self,cr,uid,ids,field_name,res_id,context=None):
        sel_obj=self.pool.get('select.selection')
        if res_id:
            var_id=sel_obj.browse(cr,uid,res_id).variants_id.id or None
        return {'value':{field_name:var_id}}
    def onchange_layer_count(self,cr,uid,ids,field):
        if field:
            return{'value':{'plot_count': 2 * field}}
        else:
            return False
    #def check_is_need_unconventional(self,cr,uid,ids,context=None):
      #  rec=self.browse(cr,uid,ids[0])
        #return True
        
pcb_info()


class pcb_cost_argument(osv.osv):
    _name='pcb.cost.argument'
    _material_category=('fr4','htg')
    _material_category=[(i,i.title()) for i in _material_category]  
    _cost_type=(
        'none',       #无
        'ready',      #准备费
        'plot',       #菲林费
        'test',       #测试费
        'test_jig',   #夹具费
        'test_pcs',   #测试pcs费
        'pack',       #工程打包费用  
        'base',       #基板费
        'mould',      #模具费
        'change',     #更改费
        'other',      #其他费用
        'base_bd_thick',  #
        'standard_days', #标准天数
        'cost_days',     #加急费
        'finger',        #金手指费
        #'rf_rigid',      #刚性板费  钢板费用就是基板费用
        'flexible',   #柔性板费
        'surface_treatment',  # 表面处理费用
        
    )
    #最小线+阻抗费+孔到线+测试费+盲埋孔+TG料+最小孔径+孔密度+压接孔+盘中孔+半孔+台阶孔+铜孔+板厚+叠压加材料费+油墨+小板+表面工艺费
    _cost_type_2=(
        'none'    #无
        ''
    )
    
    
    
    
    
    _cost_type=[(i,i.title()) for i in _cost_type]
    
    _columns = {                   
        'name'            :fields.char(u'名称', size=64 , require=True,select=True,), 
        'type'            :fields.selection([('normal_sample',u'样板'),('normal_mass',u'批量生产'),('hdi','Hdi'),('rigid_flexible',u'刚柔结合板'),('special_matrial',u'特殊材料'),('none',u'无')],u'类型', size=32,  select=True,),   #报价类型
        'cost_type'       :fields.selection([('none',u'无'),('ready',u'准备费'),('plot',u'菲林费'),('test',u'测试费'),('test_jig',u'测试jig费'),('test_pcs',u'测试pcs费'),
                                             ('pack',u'打包费'),('base',u'基板费'),('mould',u'模具费'),('change',u'变更费'),('other',u'其他费'),('base_bd_thick',u'基板厚度'),
                                             ('standard_days',u'标准天数'),('cost_days',u'加急费'),('finger',u'金手指'),('flexible',u'刚柔结合板'),('surface_treatment',u'表面涂覆'),
                                             ],u'费用类型', size=32,  select=True,), # 费用类型
        'v'               :fields.float( u'值',digits=(6,3)),  #值
        'layer_count'     :fields.integer(u'层数', select=True,),  #层数
        'au_thick_min'    :fields.float( u'最小金厚',),             #金厚下限
        'au_thick_max'    :fields.float( u'最大金厚',),             #最大上限
        'finger_count_min':fields.float( u'最小金手指数',),         #手指数下限
        'finger_count_max':fields.float( u'最大金手指数',),         #手指数上限
        'test_point_min'  :fields.float( u'最小测试点',),           #测试点密度
        'test_point_max'  :fields.float( u'最大测试点',),
        'cost_days'       :fields.float( u'加急费',),                #加急费用 
        'po_area_max'     :fields.float( u'最大订单面积',),              #订单面积上限
        'po_area_min'     :fields.float( u'最小订单面积',),              #
        'pcs_area_max'    :fields.float( u'pcs最大面积',),             #pcs面积上限
        'pcs_area_min'    :fields.float( u'pcs最小面积',),
        'bd_thick_max'    :fields.float( u'最大板厚',),             #板厚上限
        'bd_thick_min'    :fields.float(u'最小板厚',),             #
        'layer_count_min' :fields.float( u'最小层数',),          #
        'layer_count_max' :fields.float( u'最大层数',),          #层数上限
        #'material_category'      :fields.selection(_material_category,'material_category', size=32,select=True),  #材料分类
        'material_category'      :fields.many2one('select.selection',u'材料分类',domain=[('type','=','board_material')],select=True),  #材料分类
        
        'material_addition'      :fields.float( u'材料附加费',select=True),   #材料附加费
        'cu_thickness'           :fields.float( u'铜厚',select=True),           
        #'test_point_count_max'   :fields.float( 'test_point_count_max',), #测试点数量,已经定义，重复
        #'test_point_count_min'   :fields.float( 'test_point_count_min',),  
        'flexible_count'         :fields.float( u'柔性层数',),  #柔性层数
        'surface_treatment' :fields.many2one( 'select.selection', u'表面涂覆' ,domain=[('type','=','surface_treatment')],select=True),
        'res_partner_id':       fields.many2one('res.partner',u'客户'),
    }
    _defaults = {  
        'type'   : lambda *a:  'none',
        'cost_type':lambda *a: 'none',
        'po_area_max':0.0,
        'po_area_min':0.0,
        #'material_category':lambda *a:'fr4',
    }
    
pcb_cost_argument()



    
class product_product (osv.osv):
    _inherit = "product.product"
    def _check_pcb_info(self, cr, uid, ids, context=None):
        for id in ids:
            me=self.browse(cr, uid, id)
            print me.pcb_info_id,  me.default_code
            #if  me.pcb_info_id  and  me.pcb_info_id.name != me.default_code:
            #    return False
        return True
    _columns = {
        'pcb_info_id':fields.float( 'pcb_info_id',),            
    }
    _constraints=[
        (_check_pcb_info, 'Error !pcb name must ==  product default_code', ['pcb_info_id'])
    ]       
product_product()






'''
    #_surface_treatment=('hasl','lfhasl','imm_tin','imm_au','imm_ag','plate_au','osp',)
    #_surface_treatment=[(i,i.title()) for i in _surface_treatment] 
    
    #_board_material=('fr-4','htg','al_base','ro4350','ro4003','ptfe') 
    #_board_material=[(i,i.title()) for i in _board_material] 
    
    
    
    def function_cost(self,cr,uid,ids,context=None):
        
        arg_obj=self.pool.get('pcb.cost.argument')
        for id in ids:
            me=self.browse(cr, uid, id, context,)
            
            cost_sqcm=self._get_cost_sqcm(cr,uid,me=me,)
            print cost_sqcm,me.pcs_area  ,cost_sqcm*me.pcs_area
            cost_pcs =cost_sqcm*me.pcs_area
            cost_base=cost_pcs*me.delivery_count
            
            cost_ready=self._get_cost_ready(cr,uid,me=me,)
            cost_plot =self._get_cost_plot(cr,uid,me=me,)
            cost_test =self._get_cost_test(cr,uid,me=me,)
            cost_other=self._get_cost_other(cr,uid,me=me,)
            cost_pack=self._get_cost_pack(cr,uid,me=me,)
            cost_days=self._get_cost_days(cr,uid,me=me,cost_base=cost_base, cost_ready=cost_ready, cost_plot=cost_plot,
                                          cost_other=cost_other, cost_test=cost_test,)
            
            cost_all=self._get_cost_all(cr,uid,me=me,cost_base=cost_base, cost_ready=cost_ready, cost_plot=cost_plot,
                                        cost_other=cost_other, cost_test=cost_test,cost_days=cost_days)
            ##cost_base*me.delivery_count + cost_ready + cost_plot + cost_other
            
            self.write(cr, uid, id, {'cost_sqcm' :cost_sqcm  }, context)
            self.write(cr, uid, id, {'cost_pcs' :cost_pcs  }, context)
            self.write(cr, uid, id, {'cost_base' :cost_base  }, context)
            self.write(cr, uid, id, {'cost_ready':cost_ready }, context)
            self.write(cr, uid, id, {'cost_plot' :cost_plot  }, context)
            self.write(cr, uid, id, {'cost_other':cost_other }, context)
            self.write(cr, uid, id, {'cost_test':cost_test }, context)
            self.write(cr, uid, id, {'cost_pack':cost_pack }, context)
            self.write(cr, uid, id, {'cost_days':cost_days }, context)
            self.write(cr, uid, id, {'cost_all':cost_all }, context)
            
        return True    
    
    
    
    
    
    
    
    
    def _get_cost_all(self,cr,uid,me=None,cost_base=0, cost_ready=0, cost_plot=0,cost_other=0, cost_test=0, cost_days=0,context=None):
        res=cost_base + cost_ready + cost_plot + cost_other + cost_test + cost_days

        #=======================================================================
        # print cost_days ,  me.delivery_leadtime
        # if cost_days > 0:
        #    c_cost_days=me.layer_count < 8 and [('layer_count','=',me.layer_count),('cost_days','=',cost_days)] or [('layer_count','>',me.layer_count),('cost_days','=','cost_days')] 
        #    ratio= self._get_arg(cr, uid, c_cost_days, 'v', ) or 0
        #    print ratio, 'ratio'
        #    res+=res*ratio
        #=======================================================================
        return res
                     
    def _get_cost_days(self,cr,uid,me=None,cost_base=0, cost_ready=0, cost_plot=0,cost_other=0, cost_test=0,context=None):
        res=cost_base + cost_ready + cost_plot + cost_other + cost_test
        
        cost_days=me.standard_days-me.delivery_leadtime
        print cost_days ,  me.delivery_leadtime
        if cost_days > 0:
            c_cost_days=me.layer_count < 8 and [('layer_count','=',me.layer_count),('cost_days','=',cost_days)] or [('layer_count','>',me.layer_count),('cost_days','=','cost_days')] 
            ratio= self._get_arg(cr, uid, c_cost_days, 'v', ) or 0
            print ratio, 'ratio'
            return res*ratio
        else:
            return 0
          
    def _get_cost_plot(self,cr,uid,me=None,context=None):
        c_plot=[]
        res=0.0
        if me.layer_count<=2:
           c_plot=[('cost_type','=','plot'),('layer_count','=',2),('pcs_area_max' ,'>=',me.pcs_area),('pcs_area_min' ,'<',me.pcs_area), ]
           res= me.pcs_area > 400 and  self._get_arg(cr,uid,c_plot,'v') + 1*(me.pcs_area-400) or self._get_arg(cr,uid,c_plot,'v')
           
        else:
            c_plot=[('cost_type','=','plot'),('layer_count','>',2),('pcs_area_max','>=',me.pcs_area),('pcs_area_min' ,'<',me.pcs_area), ]
            if me.pcs_area < 100:
                res= 12*me.plot_count
            else:
                res=self._get_arg(cr,uid,c_plot,'v')*me.pcs_area
        
        if me.type=='hdi':
            hdi_cost_plot_min=self._get_arg(cr, uid, [('type','=','hdi'),('cost_type','=','plot'),('layer_count','=',me.layer_count)], 'v', )
            res = hdi_cost_plot_min > res and hdi_cost_plot_min or res
            
        
        return res
    
    def _get_cost_test(self,cr,uid,me=None,context=None):
        res=0.0
        if me.test_type=='common':
            jig=self._get_arg(cr, uid, [('cost_type','=','test_jig'),('test_point_max','>=',me.test_point_count),('test_point_min','<',me.test_point_count)],  )
            test_pcs=self._get_arg(cr, uid, [('cost_type','=','test_pcs'),('test_point_max','>=',me.test_point_count),('test_point_min','<',me.test_point_count)],  )
            res= jig + test_pcs*me.delivery_count
        elif me.test_type=='dedicated':
            pass    
        
        if me.type=='hdi':
            hdi_cost_test_min=self._get_arg(cr, uid, [('type','=','hdi'),('cost_type','=','test'),('layer_count','=',me.layer_count)], 'v', )
            res = hdi_cost_test_min > res and hdi_cost_test_min or res
            
        return res
        ##'),(' 
    def _get_cost_pack(self,cr,uid,me=None,context=None):
        res=0.0
        if me.pcs_area <= 600:
            c_pack=[('cost_type','=','pack'),('layer_count','=',me.layer_count),('pcs_area_min','<',me.pcs_area),('pcs_area_max','>=',me.pcs_area)]
            res=self._get_arg(cr, uid, c_pack, 'v', )
        elif me.pcs_area > 600:
            c_pack=[('cost_type','=','pack'),('layer_count','=',me.layer_count),('pcs_area_min','<',600),('pcs_area_max','>=',600)]
            c_pack_add=[('cost_type','=','pack'),('layer_count','=',me.layer_count),('pcs_area_min','>=',600)]
            
            res=self._get_arg(cr, uid, c_pack, 'v', ) + (me.pcs_area-600)*self._get_arg(cr, uid, c_pack_add, 'v', )
            
        return res
    
    def _get_cost_sqcm(self,cr,uid,me=None,context=None):
        res=0.0
        
        c_base=[('type','=',me.type),('layer_count','=',me.layer_count),('cost_type','=','base'),('po_area_max','>=',me.po_area),('po_area_min','<',me.po_area)]
        if me.type=='hdi':
            c_base=[('type','=',me.type),('layer_count','=',me.layer_count),('cost_type','=','base')]
            

        base=self._get_arg(cr,uid,c_base,'v')  ##基数价格
        base_add=base                                   ##基数累加值



        
        if me.layer_count<=2:   ##厚度加价
            if me.basic_board_thickness  <= 3:
                c_base_bd_thick=[('layer_count','=',me.layer_count),('cost_type','=','base_bd_thick'),
                                 ('bd_thick_max','>=',me.finish_board_thickness),('bd_thick_min','<',me.finish_board_thickness)]
                base_add += self._get_arg(cr,uid,c_base_bd_thick,'v')  
            else:  
                pass #板厚大于3 按照多层板就散



            
        elif me.layer_count > 2:
            limit_thick=self._get_arg(cr,uid,[('layer_count','=',me.layer_count),('cost_type','=','base_bd_thick')],'bd_thick_max')
            if me.finish_board_thickness > limit_thick:
                base_add+=(me.finish_board_thickness - limit_thick)/0.025
                
        if self.is_need_cost_cu(cr,uid,me,context):
            print 'need cost cu'
            if self.is_cu_thickness_same(cr,uid,me,context):
                print 'sanme'
                if me.layer_cu_thickness_ids[0].cu_thickness == 2:
                    base_add+= base*0.2
                if me.layer_cu_thickness_ids[0].cu_thickness >  2:
                    base_add+= (me.layer_cu_thickness_ids[0].cu_thickness -1)*me.layer_count*0.02
            else:
                print 'not same'
                thick_count_hash=self.get_cu_thickness_hash(cr,uid,me,context)
                print thick_count_hash
                for thick,count in  thick_count_hash.items():
                    if thick==2:
                        base_add+= self._get_arg(cr,uid,[('layer_count','=',count),('cost_type','=','base')],'v')
                    if thick > 2:
                        base_add+= (thick-1)*count*0.02
              
                        
        if me.board_material == 'htg' and me.layer_count < 10:
            c_htg=[('material_category','=','htg'),('cost_type','=','base'),
                   ('bd_thick_max','>=',me.finish_board_thickness),('bd_thick_min','<',me.finish_board_thickness)]
            base_add+=self._get_arg(cr,uid,c_htg,'v')  
            
        if  me.blind_buried_via_ids:
            
            for bb in  me.blind_buried_via_ids:
                print base_add
                bb_layer_count=abs(bb.end-bb.start)+1
                bb_layer_count = bb_layer_count % 2 and  bb_layer_count+1 or bb_layer_count
                base_add+=  self._get_arg(cr,uid,[('layer_count','=',bb_layer_count),('cost_type','=','base')],'v')*0.45
            
        if me.impedance_id:
            base_add+= base*0.1

        if me.surface_treatment != 'hasl' and me.type== 'normal_sample':
            if me.surface_treatment == 'imm_tin':
                base_add+=0.01
            if me.surface_treatment == 'imm_ag':
                base_add+=0.01
            if me.surface_treatment == 'lfhasl':
                base_add+=0.005
            if me.surface_treatment == 'imm_au':
                base_add+=0.015
            if me.surface_treatment == 'plate_au':
                base_add+=0.015                
            ##look in cost_ready  ('hasl','lfhasl','imm_tin','imm_au','imm_ag','plate_au','osp',)
        
        if me.min_line_width < 4 or me.min_line_space < 4:
            min=me.min_line_width < me.min_line_space and  me.min_line_width or me.min_line_space
            base_add+= base*(4-min)/0.1 * 0.03
            
        if me.min_finish_hole <= 2:
            base_add+= 0.02

        if me.min_hole2line < 8:
            base_add += base * (8-me.min_hole2line)/0.5 * 0.05
            
        if me.npth_tolerance < 0.05:
            base_add+=0.02
 
        if me.pth_tolerance < 0.08:
            base_add+=0.03
            
        if me.drill_density > 10:
            base_add+=  (me.drill_density-10)*0.004
            
        if me.route_length/me.pcs_area > 0.9:
            base_add +=  (me.route_length/me.pcs_area - 0.9)/0.1*0.002
            
        if me.half_pth :
            base_add+=0.05
        if me.pad_via:
            if me.type=='normal_sample':
                base_add+=0.15
            elif me.type=='normal_mass':
                base_add+=0.12
            
        if me.step_hole or me.control_deep_hole:
            base_add+=0.02
            
        if me.pcs_length < 50 or me.pcs_width < 50 or me.pcs_length > 600 or me.pcs_width > 600:
            pass
        
        if me.multi_panel:
            pass #look cost_ready
        
        if me.fill_pp_count or me.fill_core_count:
            base_add+= me.fill_pp_count*0.004 + me.fill_core_count*0.03
            
        
        return base_add

    
    def _get_cost_ready(self,cr,uid,me=None,context=None):
        c_ready=[('type','=',me.type),('layer_count','=',me.layer_count), ('cost_type','=','ready'),]
        res= self._get_arg(cr,uid,c_ready,'v')
        if me.blind_buried_via_ids:
            res=res*(1+0.25)
            
        if me.multi_panel:
            res=res*( 1 +  0.5*(me.multi_panel-1)  )
        return res
    def _get_cost_other(self,cr,uid,me=None,context=None):
        res=0.0
        if me.surface_treatment != 'hasl':
            res=80
            if me.surface_area/me.pcs_area > 0.2:
                res= 80 * (me.surface_area/me.pcs_area)/0.2
                
        if me.type=='hdi' and  me.pcs_drill_count*me.delivery_count > 100000:
            res+=  (me.pcs_drill_count*me.delivery_count-100000)/10000*250
            
        if me.gold_finger_id:
            finger=me.gold_finger_id
            f_base=self._get_arg(cr, uid, [('cost_type','=','finger',),
                                           ('au_thick_min','<', finger.au_thick),
                                           ('au_thick_max','>=', finger.au_thick),
                                           ('finger_count_min','<=', finger.finger_count),
                                           ('finger_count_max','>=', finger.finger_count),
                                           ], 'v', )
            #print 'f_base' , f_base
            res+=f_base*me.delivery_count
        return res  
    
    
     def is_need_cost_cu(self,cr,uid,me=None ,context=None):
        for line in me.layer_cu_thickness_ids:
            if line.cu_thickness > 1:
                return True
        return False   
    
    def is_cu_thickness_same(self,cr,uid,me=None ,context=None):
        if len( set( [line.cu_thickness for line in me.layer_cu_thickness_ids] ) ) == 1:
            return True
        else:
            return False    
            
    def get_cu_thickness_hash(self,cr,uid,me=None ,context=None):
        res={}
        for line in me.layer_cu_thickness_ids:
            res[line.cu_thickness] = res.get(line.cu_thickness) and res[line.cu_thickness]+1 or 1
        return res
        
        
         fields=['packing_type','count_unit_package','add_delivery_chapter',
                'provide_steel_net','provide_gerber','confirm_gerber','silk_colour','solder_via',
                'solder_type','solder_colour','basic_board_thickness','solder_variants','packing_request',
                'mark_request','request_with_goods','packing_note','delivery_order_request','partner_special_request', 
        ]       
    
'''
    
    
    



