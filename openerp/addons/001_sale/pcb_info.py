# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, osv
from  openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import psycopg2
import pymssql
server='192.168.10.2'
user='sa'
password='719799'
database='mtlerp-running'
 
class blind_buried_via(osv.osv):
    _name='blind.buried.via'
    _columns={
        'name': fields.char(u'名称', size=16,select=True,),
        'start':fields.integer(u'开始', ),
        'end':fields.integer(u'结束', ),
        'pcb_info_id':fields.many2one('pcb.info', u'用户单' , ondelete="cascade", invisible=True),     
        'state'      :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('done',u'完成'),('refuse',u'作废'),('wait_change',u'待更改')],u'单据状态',readonly=True,select=True),         
    }
    
    _defualts={
               'state':lambda *a:'draft',}
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
        'cu_thickness':fields.float(u'铜厚', ),
        'pcb_info_id':fields.many2one('pcb.info', u'用户单' , ondelete="cascade", invisible=True),        
        'impdance_info_ids':fields.one2many('impdance.info','layer_cu_thickness_id',u'阻抗信息'),#阻抗描述
        'state'      :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('done',u'完成'),('refuse',u'作废'),('wait_change',u'待更改')],u'单据状态',readonly=True,select=True),
    }       
    _defualts={
               'state':lambda *a:'draft',}
    
layer_cu_thickness()  



 
class  gold_finger (osv.osv):
    _name='gold.finger'
    _columns = {
        'name': fields.char(u'名称', size=16, select=True,),
        'finger_count':fields.integer( u'金手指数量(PCS支数)',),
        'au_thick':fields.float(u'金厚u"',),
        'ni_thick':fields.float( u'镍厚u"',),       
        'finger_length':fields.float( u'金手指长mm',),
        'finger_width':fields.float( u'金手指宽mm',), 
        'bevel_edge'  :fields.selection([('30','30'),('45','45'),('60','60')], u'斜边度',),
        'note' :fields.char(u'备注',size=64,),
     'state'      :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('done',u'完成'),('refuse',u'作废'),('wait_change',u'待更改')],u'单据状态',readonly=True,select=True),
    }       
    _defualts={
               'state':lambda *a:'draft',}
    _sql_constraints = [
        ('name', 'unique (name)', 'name  must unique!'),        
    ]
gold_finger()  



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
    _order = "name desc"
    def _info_get(self,cr,uid,ids,field_name,arg,context=None):
        res={}
        for id in ids:
            me=self.browse(cr, uid, id, context,)
            pi=me.pcb_info_many
            
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
                days= cu_max>2 and days+cu_max-2 or days
                days= me.pad_via and days+3 or days
             
                if me.blind_buried_via_ids:
                    for line in me.blind_buried_via_ids:
                        days=abs(line.end-line.start)==1 and days+1 or days+2
                #if add days to
                res[id]=days
            elif field_name=='pcs_unit_count':
                res[id]=me.panel_x * me.panel_y
                
            elif field_name=='plot_count':
                res[id]=me.layer_count
                if me.silk_type:
                    if me.silk_type==u'双面字符':
                        res[id]+=2
                    if  me.silk_type==u'单面字符':
                        res[id]+=1
                if me.solder_type:
                    if  me.solder_type==u'双面阻焊':
                        res[id]+=2
                    if  me.solder_type==u'底层阻焊顶层整版开窗':
                        res[id]+=1
                    if  me.solder_type==u'顶层阻焊底层整版开窗':
                        res[id]+=1
                    if  me.solder_type==u'底层阻焊顶层覆盖':
                        res[id]+=2
                        
                    if me.solder_type==u'单面阻焊':
                        res[id]+=1
                        
                        
                        
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
                for k in ['layer_count','pcs_length','pcs_width','min_line_width','pcs_drill_count',]:
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
        
        
        
        
    #单据状态
    _state_list=('draft','wait_order_supervisor','done','refuse','wait_change')
    _state_list=[(i,i.title()) for i in _state_list] 
    
    #得到阻焊颜色
    def _get_solder_colour(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','solder_colour')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    #得到阻焊油墨
    def _get_solder_variants(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','ink_type')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    #得到字符颜色
    def _get_silk_colour(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','silk_colour')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    #得到字符油墨
    def _get_silk_variants(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','silk_variants')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    #得到阻抗类型
    def _get_solder_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','solder_type')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_solder_via(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','solder_via')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_silk_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','silk_type')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_surface_treatment(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','surface_treatment')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_vcut_angle(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','vcut_angle')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_cu(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','cu_thickness')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]
    
    def _get_version(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','soft_version')],context=context)
        res=obj.read(cr,uid,ids,['name','name'],context)
        return [(r['name'],r['name'])for r in res]



    _columns = {
#        'product_id' :fields.many2one('product.product',u'档案号',  select=True),
        'name'       :fields.char(u'用户单号', size=64,readonly=True), 
        'product_id':fields.char(u'档案号',size=64),
        'state'      :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('done',u'完成'),('refuse',u'作废'),('wait_change',u'待更改')],u'单据状态',readonly=True,select=True),
        'temp_state':fields.char('Temp state',size=64),
        'responsible_id': fields.many2one('employee',u'资料审核员',domain=[('is_sale_approve','=',True)]),
        'create_date'  :fields.datetime(u"创建日期", readonly=True),
        'mix_press'                   :fields.boolean(u'混压'),     #混压
        'partner_id'                  :fields.many2one( 'res.partners', u'客户', select=True, required=True, domain=[('customer','=',True)],readonly=True),##
        'ref'                         :fields.related('partner_id','partner_code',type='char',relation='res.partners',string=u'客户代号'),                        
        'basic_board_thickness'       :fields.float( u'基板厚度',), #基础板厚
		'contract_id'                 :fields.char(u'合同号',size=32,),#合同号
        'layer_count'            :fields.integer(u'层数', change_default=True,required=True), #层数
        'finish_board_thickness' :fields.float( u'成品板厚度',),#成品板厚
        'finish_tol_upper'       :fields.float( u'成品公差正',),#成品公差
        'finish_tol_lower'       :fields.float( u'成品公差负',),#成品公差  
        'surface_treatment_request':fields.char(  u'涂覆描述' ,size=64,),#表面处理要求
        'gold_finger_id'           :fields.many2one( 'gold.finger', u'金手指', domain="[('name','=',name)]"),#金手指    
        'special_process_note'     :fields.text( u'特殊说明' ,),#特殊工艺说明  
        'buried_name'           :fields.char(u'盲埋孔描述',size=128),   
        'buried_quantity'       :fields.float(u'盲埋孔数量'),
        'solder_colour'      :fields.selection(_get_solder_colour,u'阻焊颜色', ),#阻焊颜色
        'solder_variants'    :fields.selection(_get_solder_variants,u'阻焊型号'), #阻焊油墨型号
        'solder_type'        :fields.selection(_get_solder_type,u'阻焊类型'),
        'solder_via'         :fields.selection(_get_solder_via,u'过孔阻焊'),
        'silk_colour'        :fields.selection(_get_silk_colour,u'字符颜色'),
        'silk_variants'      :fields.selection(_get_silk_variants,u'字符型号'),
        'silk_type'          :fields.selection(_get_silk_type,u'字符类型'),
        'surface_treatment'  :fields.selection(_get_surface_treatment,u'表面涂覆'),
        'vcut_angle'         :fields.selection(_get_vcut_angle,u'VCUT度'),
        'inner_cu'           :fields.selection(_get_cu,u'内层铜厚'),
        'out_cu'             :fields.selection(_get_cu,u'外层铜厚'),
        'finish_inner_cu'    :fields.selection(_get_cu,u'成品内层铜厚'),
        'finish_out_cu'      :fields.selection(_get_cu,u'成品外层铜厚'),
        'soft_version':       fields.selection(_get_version,u'软件版本'),
        'pcb_info_many'        :fields.one2many('pcb.info.line','pcb_info_many_line',u'选择项'),
         
        'packing_request'      :fields.char(u'包装要求',  size=128  ), #包装要求    
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
        'source_file_name':fields.char(u'文件名',size=64),
 #       'source_file_name'      :fields.related('order_recive_id','fname',type='char',relation='order.recive',string=u'文件名',readonly=True,store=True ), #源文件名
        'soft_info'             :fields.char( u'软件信息',  size=32),##软件信息
      
      #  'source_product_code'   :fields.char( u'零件号',  size=32),#零件号
        'outline_size_request'        :fields.selection([('according_file',u'通过文件'),('other',u'其他')],u'按外形尺寸要求') ,#外形尺寸要求
        'pcs_length'                  :fields.float( u'pcs长cm', change_default=True,),#长
        'pcs_width'                   :fields.float( u'pcs宽cm',  change_default=True,),#宽
        'panel_request'               :fields.char(u'拼版要求',  size=32,),#拼版要求
        'unit_length'                 :fields.float(u'unit长cm', change_default=True),#单元长
        'unit_width'                  :fields.float(u'unit宽cm',  change_default=True),#单元宽
        'delivery_type':           fields.function(_info_get,method=True,type='integer',string=u'交货方式',store=True),
        'allow_scrap_count'  :fields.integer(u'允许报废数量', ),#允许报废数量
        'allow_scrap_percent':fields.integer(u'允许报废比例',),    #允许报废比例
        'special_indicate'           :fields.text(u'特殊指示',),#特殊指示
        'test_point_count'            :fields.float( u'测试点数量',change_default=True,),#测试点数量        
        
        'order_recive_id'            :fields.many2one('order.recive',u'接单单号'),
        'custmer_goodscode'           :fields.related('order_recive_id','custmer_goodscode',type='char',string=u'零件号',store=True,relation='order.recive',size=64), ## 零件名    
        'custmer_handler'             :fields.char      ( 'Custmerhandler',  size=30    ), ## 选择一个客户联系
        'blind_buried_via_ids'         :fields.one2many('blind.buried.via','pcb_info_id',u'盲埋孔'),#盲埋孔
        'layer_cu_thickness_ids'       :fields.one2many('layer.cu.thickness','pcb_info_id',u'铜厚信息'),#铜厚信息
        'impedance_id'                 :fields.boolean( u'阻抗',),#阻抗
        'next_note'                 :fields.text(u'特别提醒'),
        'except_note'               :fields.text(u'异常订单情况'),
        'fname':fields.related('order_recive_id','fname',type='char',relation='order.recive',string=u'附件名',store=True),
 ####客户对产品的通用要求字段
 
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
        
        'back_drill'                  :fields.integer( u'背钻',),            
        'panel_x'                     :fields.integer('拼版X',reqiured=True),
        'panel_y'                     :fields.integer('拼版Y',reqiured=True),              
            
        'pcs_unit_count'              :fields.function(_info_get, method=True, type='integer',string=u'UNIT/PCS数 量',store=True), #pcs 的unit数

        
        'plot_count':                   fields.function(_info_get, method=True, type='integer',  string=u"菲林张数",store=True),#面积
        'pcs_area'                    :fields.function(_info_get, method=True, type='float',  string=u"pcs面积",store=True),#面积
        'drill_density'               :fields.function(_info_get, method=True, type='float',  string=u"孔密度",store=True),#孔密度      
        'test_point_density'          :fields.function(_info_get, method=True, type='float',  string=u"测试点密度",store=True),#测试点密度
        'standard_days'               :fields.char(u'标准天数',size=64),
 #       'standard_days'               :fields.function(_info_get, method=True, type='float',  string=u"标准周期",store=True), #标准周期
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
        'price_sheet_id':fields.many2one('price.sheet',u'报价单'),
        'au_area':fields.integer(u'沉金面积%'),
        'szmtl_company':fields.boolean(u'预计投产深圳工厂'),
        'csmtl_company':fields.boolean(u'预计投产长沙工厂'),
        'product_material':fields.selection([('come_customer',u'客供'),('come_company',u'自供')],u'材料来源'),
#        'contact':fields.related('partner_id','eng_contact',type='char',relation='res.partners',string=u'联系人',readonly=True,store=True),
        'contact':fields.many2one('res.partner.contact',u'联系人',domain="[('res_partner_contact_id','=',partner_id)]"),
        'phone':fields.related('contact','mobile',type='char',relation='res.partner.contact',string=u'客户电话',readonly=True,store=True),
        'email':fields.related('contact','email',type='char',relation='res.partner.contact',string=u'电子邮件',readonly=True,store=True,reqiured=True),
        'sepecial_board_size':         fields.selection([('500*500','500*500'),('500*600','500*600'),('18*24','18*24'),('36*48','36*48'),('24*36','24*36')],u'材料尺寸'),
        'au_thickness':fields.float(u'沉金厚度'),
        
        'receive_type':               fields.selection([('high',u'紧急'),('low',u'一般')],u'紧急状况',size=32),#紧急
        'via_quantity':fields.integer(u'盲埋孔加急天'),
        
    }
    _defaults = {  
        'name': lambda obj, cr, uid, context:  obj.pool.get('ir.sequence').get(cr, uid, 'pcb.info'), 
 #       'name':lambda obj, cr, uid, context:'/',
        'state'    :lambda *a: 'draft',
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
 #       ('product_id', 'unique (product_id)', 'product_id  must unique!'),  
        #('matrial_use_ratio','CHECK (0 < matrial_use_ratio and matrial_use_ratio <= 1)','matrial_use_ratio must be between 0 and 1 !'),
        #=======================================================================
        # ('pcs_length', 'CHECK(state != "draft" and pcs_length > 0 )', 'pcs_length must be greater than zero.'),   
        # ('pcs_width', 'CHECK( pcs_width > 0 )', 'pcs_width  must be greater than zero.'),
        # ('min_line_width', 'CHECK( min_line_width > 0 )', 'min_line_width  must be greater than zero.'),
        # ('finish_board_thickness', 'CHECK( finish_board_thickness > 0 )', 'finish_board_thickness  must be greater than zero.'),
        # ('min_line_space', 'CHECK( min_line_space > 0 )', 'min_line_space  must be greater than zero.'),
        # ('pcs_drill_count', 'CHECK( pcs_drill_count > 0 )', 'pcs_drill_count  must be greater than zero.'),
        # ('min_line_space', 'CHECK( min_line_space > 0 )', 'min_line_space  must be greater than zero.'),
        # ('pcs_drill_count', 'CHECK( pcs_drill_count > 0 )', 'pcs_drill_count  must be greater than zero.'),      
        #=======================================================================
     ]
    _constraints=[
        (_check_one2one, '金手指名称必须是用户单单号!', ['gold_finger_id']),
#        (_check_layer_count,'Error! layer count cant be odd number 1,3,5...',['layer_count'] ),
        (_check_state,'层数,pcs长,pcs宽,最小线宽,最小间距,pcs钻孔数量,必须大于0 !',['state'] ),
        
        ##(_check_product_id,'Error! product code must == name',['product_id'] ),
        
    ]    
    ######状态为待更改时，审批用户单。
    def button_approves(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state=='wait_change':
              
              obj=self.pool.get('price.sheet')
              se=obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','!=','cancel')])
              print se,'se'
              self.pool.get('order.recive').write(cr,uid,my.order_recive_id.id,{'state':'wait_price'})

              if not se:
                      res_id=self.pool.get('price.sheet').create(cr,uid,{
                                                               'pcb_info_id':my.id,
                                                               'product_number':1,
                                                               'delivery_leadtime':1,
                                                               'responsible_id':uid,
                                                               'recive_type':my.order_recive_id.sale_type,
                                                               })
                
              self.write(cr,uid,ids[0],{'state':'done'})
        return True
    
    
    def button_refuse(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids[0],{'state':'refuse'})
        return True
####create 调用系统自带的新增一条数据时，更新金手指的名称为用户单号
    def create(self,cr,uid,vals,context=None):
        id=super(pcb_info,self).create(cr,uid,vals,context=context)
        return self.insert_golder_finger_name(cr,uid,id,vals,context=None)
    
####当用户单状态等于完成状态时更新其他表明细为完成
    def other_done(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        cu=self.pool.get('layer.cu.thickness')
        via=self.pool.get('blind.buried.via')
        line=self.pool.get('pcb.info.line')
        if my.blind_buried_via_ids:
            for r in my.blind_buried_via_ids:
                via.write(cr,uid,r.id,{'state':'done'})
        if my.layer_cu_thickness_ids:
            for n in my.layer_cu_thickness_ids:
                cu.write(cr,uid,n.id,{'state':'done'})
        if my.pcb_info_many:
            for b in my.pcb_info_many:
                line.write(cr,uid,b.id,{'state':'done'})
        return True
    
    
    def insert_golder_finger_name(self,cr,uid,id,vals,context=None):
        my=self.browse(cr,uid,id)
        obj=self.pool.get('order.recive')
        gold_finger=self.pool.get('gold.finger')
        order_recive_id=my.order_recive_id.id
        se=obj.browse(cr,uid,order_recive_id).re_pcb_info_id.gold_finger_id
        if se:
            gold_id=gold_finger.create(cr,uid,{
                                        'name':my.name,
                                        'finger_count':se.finger_count,
                                        'au_thick':se.au_thick,
                                        'ni_thick':se.ni_thick,
                                        'finger_length':se.finger_length,
                                        'finger_width':se.finger_width,
                                        'bevel_edge':se.bevel_edge,
                                        'note':se.note,
                                       })
            
            self.write(cr,uid,id,{'gold_finger_id':gold_id})
            
        return id
    
#########################################################################   
    
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
            if not args:
                args = []
            args = args[:]
            ids = []
            if name:
                ids = self.search(cr, user, [('product_id', 'ilike', name)]+args, limit=limit, context=context)
                
                if not ids:
                    ids = self.search(cr, user, [('name', operator, name)]+ args, limit=limit, context=context)
                   
            else:
                ids = self.search(cr, user, args, limit=limit, context=context)
            return self.name_get(cr, user, ids, context=context)   
    
    def sure(self,cr,uid,ids,context=None):
        info=self.browse(cr,uid,ids[0])
        name=info.name
        if name[0:2]!='JD':
            raise osv.except_osv(_('Warning !'), _('不是导入的用户单信息,不能确认' ))
        return self.write(cr,uid,ids[0],{
                                         'state':'done'
                                         })
######资料审核员只能审批自己的单
    def approve_type(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        res=self.pool.get('res.users')
        user_id=res.browse(cr,uid,uid).login
        print user_id,'user_id'
        print my.responsible_id.employeecode,'my.responsible_id'
        if my.responsible_id.employeecode!=user_id and uid!=1:
             raise osv.except_osv(_('Error!'),_(u'资料审核员只能审批自己的！'))
        else:
            return True




    def copy(self, cr, uid, id, default=None, context=None):
        default=default or {}      
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'pcb.info'),
            'product_id':None,
        })
        return super(pcb_info, self).copy(cr, uid, id, default, context)
    
    
    def unlink(self, cr, uid, ids, context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state!='draft':
                raise osv.except_osv(_('Error!'),_(u'状态完成时不能删除！'))
        else:
            return True
    
    
    
    
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
        
    #当用户单完成时，自动创建一张报价单   
    def to_price_sheet(self,cr,uid, ids,context=None): 
        self.write(cr,uid,ids[0],{'state':'done'}) 
        my=self.browse(cr,uid,ids[0])
        obj=self.pool.get('price.sheet')
       
        self.pool.get('order.recive').write(cr,uid,my.order_recive_id.id,{'state':'wait_price'})
        if my.state == 'done':
            print my.order_recive_id.sale_type,'id'
            print my.id,'id'
            #判断报价单是否已经存在
            price_sheet_ids=obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','!=','cancel')])
            if not price_sheet_ids:
                res_id=self.pool.get('price.sheet').create(cr,uid,{
                                                                   'pcb_info_id':my.id,
                                                                   'product_number':1,
                                                                   'delivery_leadtime':1,
                                                                   'responsible_id':uid,
                                                                   'recive_type':my.order_recive_id.sale_type,
                                                                   })
                return True
               
        else:
            raise osv.except_osv(_('Warning !'), _('单据状态必须是完成！') )
#    def onchange_silk_solder_colour(self,cr,uid,ids,field_name,res_id,context=None):
#        sel_obj=self.pool.get('select.selection')
#        if res_id:
#            print sel_obj.browse(cr,uid,res_id).label,'id'
#            var_id=sel_obj.browse(cr,uid,res_id).variants_id.id or None
#        return {'value':{field_name:var_id}}
    
    def onchange_silk_solder_colour(self,cr,uid,ids,res_id,context=None):
        sel_obj=self.pool.get('select.selection')
        if res_id:
            ids=sel_obj.search(cr,uid,[('name','=',res_id),('type','=','solder_colour')],context=context)[0]
            se=sel_obj.browse(cr,uid,ids).variants_id.name or None
        
        return {'value':{'solder_variants':se}}
    
    def onchange_silk_colour(self,cr,uid,ids,res_id,context=None):
        sel_obj=self.pool.get('select.selection')
        if res_id:
            ids=sel_obj.search(cr,uid,[('name','=',res_id),('type','=','silk_colour')],context=context)[0]
            se=sel_obj.browse(cr,uid,ids).variants_id.name or None
        
        return {'value':{'silk_variants':se}}
    
    
    
    
    
    
    def onchange_layer_count(self,cr,uid,ids,field):
        if field:
            return{'value':{'plot_count': 2 * field}}
        else:
            return False
        
        
 #####复投有更改时，检查合同更改的状态是否已经到订单中心       
    def check_sale_change(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        sale_type=my.order_recive_id.sale_type
        obj=self.pool.get('sale.order.change')
        if sale_type=='revise':
            if obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','not in',('done','cancel','wait_order_center','wait_order_manager'))]):
                raise osv.except_osv(_('Warning !'), _('检查合同更改的状态是否已经到订单中心！'))
            else:
                 return True
        else:
            return True
        
        
        
        
###检查有非常规的如果没审批完非常规则提示信息！
    def check_unconventional(self,cr,uid,ids,context=None):
         cs_info=''
         sz_info=''
         my=self.browse(cr,uid,ids[0])
         obj=self.pool.get('unconventional.review')
         dpt_obj=self.pool.get('res.department')
         obj_line=self.pool.get('unconventional.review.line')
         if obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','!=','refuse')]):
             cs_info=0
             sz_info=0
             if not obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','=','done')]):   
                 raise osv.except_osv(_('Warning !'), _('非常规没审批完成不能生成报价单！'))
             else:
                 se=obj.search(cr,uid,[('pcb_info_id','=',my.id)])
                 dpt_ger_ids=dpt_obj.search(cr,uid,[('name','=','总经办')])
                 cs_ids=obj.search(cr,uid,[('pcb_info_id','=',my.id),('production_factory','=','csmtl'),('state','=','done')])
                 print cs_ids,'cs_ids'
                 if cs_ids:
                     cs_line_ids=obj_line.search(cr,uid,[('unconventional_review_id','=',cs_ids[0]),('ok_final_affirm','=',False)])
                     if not cs_line_ids:
                         cs_info=1
                     else:
                         cs_line_g_ids=obj_line.search(cr,uid,[('unconventional_review_id','=',cs_ids[0]),('ok_final_affirm','=',True),('department_id','=',dpt_ger_ids)])
                         if cs_line_g_ids:
                             cs_info=1
        
                 sz_ids=obj.search(cr,uid,[('pcb_info_id','=',my.id),('production_factory','=','szmtl'),('state','=','done')])
                 if sz_ids:
                     sz_line_ids=obj_line.search(cr,uid,[('unconventional_review_id','=',sz_ids[0]),('ok_final_affirm','=',False)])
                     print sz_line_ids,'sz_line_ids'
                     if not sz_line_ids:
                         sz_info=1
                     else:
                         sz_line_g_ids=obj_line.search(cr,uid,[('unconventional_review_id','=',sz_ids[0]),('ok_final_affirm','=',True),('department_id','=',dpt_ger_ids)])
                         if sz_line_g_ids:
                             sz_info=1
                         else:
                             sz_info=0
         print sz_info,cs_info,'cs_info'
         if cs_info==0 and sz_info==0:
            raise osv.except_osv(_('Warning !'), _('非常规没有通过请确认！'))   
                        
         return True

         
         
    ######非常规评审
    def to_unconventional(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        line=my.pcb_info_many
        obj=self.pool.get('unconventional.review')
        config=self.pool.get('technology.capabilities.parameter')
        info=''
        type_string=u'中文'
        name=my.name
        if name[0:2]=='JD':
            raise osv.except_osv(_('Warning !'), _('导入的用户单信息不能审批！'))

        if not my.csmtl_company and not my.szmtl_company:
            raise osv.except_osv(_('Warning !'), _('预投工厂必须勾选一个'))
        
        if my.csmtl_company==True:   ###长沙 
    #---------板材-----------------------       
            board_type=[]
            board_ids=config.search(cr,uid,[('item','=','board_type'),('res_company','=','csmtl')])
            if board_ids:
                records=config.read(cr,uid,board_ids,['board_material'])        
                for record in records:
                    board_type.append(record['board_material'])
               
                for i in line:
                    if i.board_material and i.board_material not in board_type:
                        if type('i.board_material')!=type(type_string):  
                            info=info+'板材:'+ str(i.board_material)+';'
                        else:
                            info=info+'板材:'+i.board_material+';'
            
    #---------------成品板厚------------     
            height_ids=config.search(cr,uid,[('item','=','board_thickness'),('res_company','=','csmtl'),('layer','=',my.layer_count)])
            if height_ids:
                records=config.read(cr,uid,height_ids,['min','max']) 
                if records:
                    min=records[0]['min']
                    max=records[0]['max']
                    if my.layer_count:
                        if my.finish_board_thickness < min or my.finish_board_thickness >max:
                            if type('my.finish_board_thinckness')!=type(type_string):  
                                info=info+'成品板厚:'+ str(my.finish_board_thickness)+' mm;'
                            else:
                                info=info+'成品板厚:'+my.finish_board_thinckess+' mm;'
                        
             
    #----------公差----------------
            if my.finish_board_thickness>1.6:
                 if my.finish_tol_upper < my.finish_board_thickness*0.08:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,正公差为:'+str( my.finish_tol_upper)+'mm;'
                 if  my.finish_tol_lower < my.finish_board_thickness*0.08:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,负公差为:'+str( my.finish_tol_lower)+'mm;'
                 
            else: 
                tolerance_ids=config.search(cr,uid,[('item','=','tolerance'),('res_company','=','csmtl'),('min','<=',my.finish_board_thickness),('max','>=',my.finish_board_thickness)])
                if tolerance_ids:
                    records=config.read(cr,uid,tolerance_ids,['tol_lower','tol_upper']) 
                    tol_lower=records[0]['tol_lower']
                    tol_upper=records[0]['tol_upper']
                    print tol_upper,'tol_upper',tol_lower,'tol_lower',my.finish_tol_upper,'finish_tol_upper'
                    if my.finish_tol_upper < tol_upper:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,正公差为:'+str( my.finish_tol_upper)+'mm;'
                    if  my.finish_tol_lower < tol_lower:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,负公差为:'+str( my.finish_tol_lower)+'mm;'
    
    
    #----------孔到线---------------
            
            min_hole_line_ids=config.search(cr,uid,[('item','=','min_hole_line'),('res_company','=','csmtl'),('layer','=',my.layer_count)])
            if min_hole_line_ids:
                 records=config.read(cr,uid,min_hole_line_ids,['v'])
                 min_hole_line=records[0]['v']
                 print my.min_hole2line,'my.min_hole2line'
                 print min_hole_line,'min_hole_line'
                 if my.min_hole2line < float(min_hole_line):
                      info=info+'最小孔到线:'+str( my.min_hole2line)+'mil;'
            else:
                if my.layer_count>14 and  my.min_hole2line<8:
                    info=info+'最小孔到线:'+str( my.min_hole2line)+'mil;'
                    
    #--------成品孔径--------------
            hole_ids=config.search(cr,uid,[('item','=','hole_dia')])
            if hole_ids:
                records=config.read(cr,uid,hole_ids,['min','max']) 
                if records:
                    min=records[0]['min']
                    max=records[0]['max']
                    if my.min_finish_hole:
                        if my.min_finish_hole < min or my.min_finish_hole >max:
                                info=info+'孔径:'+ str(my.min_finish_hole)+' mm;'   
    #----------内层最小线宽------------
            min_line_width_ids=config.search(cr,uid,[('item','=','min_line_width'),('res_company','=','csmtl'),('inorout','=','in'),('cu_thickness','like',my.finish_inner_cu)])
            print my.finish_inner_cu,'inner_cu'
            if min_line_width_ids:
                print 'min_line_width_ids'
                records=config.read(cr,uid,min_line_width_ids,['v'])
                min_line_width=records[0]['v']
                if my.min_line_width<float(min_line_width):
                        info=info+'内层铜厚:'+str(my.finish_inner_cu)+'OZ,'+'最小线宽:'+str(my.min_line_width)+'mil;'
                  
    #--------内层最小线距--------------              
            min_line_space_ids=config.search(cr,uid,[('item','=','min_line_space'),('res_company','=','csmtl'),('inorout','=','in'),('cu_thickness','like',my.finish_inner_cu)])
            print my.finish_inner_cu,'inner_cu'
            if min_line_space_ids:
                print 'min_line_space_ids'
                records=config.read(cr,uid,min_line_space_ids,['v'])
                min_line_space=records[0]['v']
                if my.min_line_space<float(min_line_space):
                        info=info+'内层铜厚:'+str(my.finish_inner_cu)+'OZ,'+'最小线距:'+str(my.min_line_space)+'mil;'     
    
    
    #----------外层最小线宽------------
            min_line_width_ids=config.search(cr,uid,[('item','=','min_line_width'),('res_company','=','csmtl'),('inorout','=','out'),('cu_thickness','like',my.finish_out_cu)])
            print my.finish_out_cu,'out_cu'
            if min_line_width_ids:
                print 'min_line_width_ids'
                records=config.read(cr,uid,min_line_width_ids,['v'])
                min_line_width=records[0]['v']
                if my.min_line_width<float(min_line_width):
                        info=info+'外层铜厚:'+str(my.finish_out_cu)+'OZ,'+'最小线宽:'+str(my.min_line_width)+'mil;'
                  
    #--------外层最小线距--------------              
            min_line_space_ids=config.search(cr,uid,[('item','=','min_line_space'),('res_company','=','csmtl'),('inorout','=','out'),('cu_thickness','like',my.finish_out_cu)])
            print my.finish_out_cu,'out_cu'
            if min_line_space_ids:
                print 'min_line_space_ids'
                records=config.read(cr,uid,min_line_space_ids,['v'])
                min_line_space=records[0]['v']
                if my.min_line_space<float(min_line_space):
                        info=info+'外层铜厚:'+str(my.finish_out_cu)+'OZ,'+'最小线距:'+str(my.min_line_space)+'mil;'
    
    #--------拼板尺寸--------------
    #------最大尺寸----------------
            if my.layer_count<=2:
                layer='2'
            else:
                layer='3'
            max_panel_size_ids=config.search(cr,uid,[('item','=','panel_size'),('v','=','max'),('res_company','=','csmtl'),('layer','=',layer)])
            if max_panel_size_ids:
               records=config.read(cr,uid,max_panel_size_ids,['min','max'])
               
               max=records[0]['max']
               min=records[0]['min']

               
               if my.pcs_length>=my.pcs_width:
                   if my.pcs_length*10>max or my.pcs_width*10>min:
                       info=info+'拼板尺寸:'+str(my.pcs_length*10)+'*'+str(my.pcs_width*10)+'cm;'
                     
               else:
                   if  my.pcs_width*10>max or my.pcs_length*10>min:
                       info=info+'拼板尺寸:'+str(my.pcs_length*10)+'*'+str(my.pcs_width*10)+'cm;'
                       
     #------最小尺寸----------------                  
            min_panel_size_ids=config.search(cr,uid,[('item','=','panel_size'),('v','=','min'),('res_company','=','csmtl')])
            if min_panel_size_ids:
               records=config.read(cr,uid,min_panel_size_ids,['min','max'])
               min=records[0]['min']
               max=records[0]['max']
               
               if my.pcs_length<my.pcs_width:
                   if my.pcs_length*10<min or my.pcs_width*10<max:
                       info=info+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                     
               else:
                   if  my.pcs_width*10<min or my.pcs_length*10<max:
                       info=info+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                      
            
    #-----------表面涂覆板厚------------------
            surface_height_ids=config.search(cr,uid,[('item','=','board_thickness'),('res_company','=','csmtl'),('surface_treatment','=',my.surface_treatment)]) 
            if surface_height_ids:
                records=config.read(cr,uid,surface_height_ids,['min','max'])
                min=records[0]['min']
                max=records[0]['max']
                if my.finish_board_thickness < min or my.finish_board_thickness>max:
                    info=info+'表面涂覆:'+str(my.surface_treatment)+',板厚:'+str(my.finish_board_thickness)+'mm;'
    #---------表面涂覆尺寸------------------      
     
            surface_size_ids=config.search(cr,uid,[('item','=','panel_size'),('res_company','=','csmtl'),('surface_treatment','=',my.surface_treatment)])
            print surface_size_ids,'surface_size_ids'
            print my.surface_treatment,' my.surface_treatment'
            if surface_size_ids:
                records=config.read(cr,uid,surface_size_ids,['min','max'])
                max=records[0]['max']
                min=records[0]['min']
                if my.pcs_length<my.pcs_width:
                       if my.pcs_length*10>max or my.pcs_width*10>min:
                           info=info+'表面涂覆:'+str(my.surface_treatment)+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                else:
                       if  my.pcs_width*10>max or my.pcs_length*10>min:
                           info=info+'表面涂覆:'+str(my.surface_treatment)+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                       
 #------厚径比----------------
            td_rate=my.finish_board_thickness*1.0/my.min_finish_hole
            if  td_rate>12:
                 info=info+'厚径比为:'+str(td_rate)
        
#------层数-----------------
            
            if my.layer_count>24:
                info=info+'层数:'+str(my.layer_count)                   
                         
            print info,'info123'
            unconventional_review_ids=obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','!=','refuse'),('production_factory','=','csmtl')])
            if info !='' and not unconventional_review_ids:
        
                obj.create(cr,uid,{
                               'pcb_info_id':my.id,
                               'partner_id':my.partner_id,
                               'unconventional_note':info,
                               'production_factory':'csmtl',
                             }) 
            
                
            
            #raise osv.except_osv(_('Warning !'), _('CS:'+info))                    
            #print info.encode('gbk') 
            
               
        if my.szmtl_company==True:
            info=''    
    #---------板材-----------------------       
            board_type=[]
            board_ids=config.search(cr,uid,[('item','=','board_type'),('res_company','=','szmtl')])
            if board_ids:
                records=config.read(cr,uid,board_ids,['board_material'])        
                for record in records:
                    board_type.append(record['board_material'])
               
                for i in line:
                    if i.board_material and i.board_material not in board_type:
                        if type('i.board_material')!=type(type_string):  
                            info=info+'板材:'+ str(i.board_material)+';'
                        else:
                            info=info+'板材:'+i.board_material+';'
            
    #---------------成品板厚------------     
            height_ids=config.search(cr,uid,[('item','=','board_thickness'),('res_company','=','szmtl'),('layer','=',my.layer_count)])
            if height_ids:
                records=config.read(cr,uid,height_ids,['min','max']) 
                if records:
                    min=records[0]['min']
                    max=records[0]['max']
                    if my.layer_count:
                        if my.finish_board_thickness < min or my.finish_board_thickness >max:
                            if type('my.finish_board_thinckness')!=type(type_string):  
                                info=info+'成品板厚:'+ str(my.finish_board_thickness)+' mm;'
                            else:
                                info=info+'成品板厚:'+my.finish_board_thinckess+' mm;'
                        
             
    #----------公差----------------
            if my.finish_board_thickness>3.2:
                 if my.finish_tol_upper < my.finish_board_thickness*0.08:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,正公差为:'+str( my.finish_tol_upper)+'mm;'
                 if  my.finish_tol_lower < my.finish_board_thickness*0.08:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,负公差为:'+str( my.finish_tol_lower)+'mm;'
                 
            else: 
                tolerance_ids=config.search(cr,uid,[('item','=','tolerance'),('res_company','=','szmtl'),('min','<=',my.finish_board_thickness),('max','>=',my.finish_board_thickness)])
                if tolerance_ids:
                    records=config.read(cr,uid,tolerance_ids,['tol_lower','tol_upper']) 
                    tol_lower=records[0]['tol_lower']
                    tol_upper=records[0]['tol_upper']
                    if my.finish_tol_upper < tol_upper:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,正公差为:'+str( my.finish_tol_upper)+'mm;'
                    if  my.finish_tol_lower < tol_lower:
                        info=info+'成品板厚:'+str(my.finish_board_thickness)+' mm,负公差为:'+str( my.finish_tol_lower)+'mm;'
    
           
    #----------孔到线---------------
            
            min_hole_line_ids=config.search(cr,uid,[('item','=','min_hole_line'),('res_company','=','szmtl'),('layer','=',my.layer_count)])
            if min_hole_line_ids:
                 records=config.read(cr,uid,min_hole_line_ids,['v'])
                 min_hole_line=records[0]['v']
                 print my.min_hole2line,'my.min_hole2line'
                 print min_hole_line,'min_hole_line'
                 if my.min_hole2line < float(min_hole_line):
                      info=info+'最小孔到线:'+str( my.min_hole2line)+'mil;'
            else:
                if my.layer_count>14 and  my.min_hole2line<8:
                    info=info+'最小孔到线:'+str( my.min_hole2line)+'mil;'
                    
    #--------成品孔径--------------
            hole_ids=config.search(cr,uid,[('item','=','hole_dia')])
            if hole_ids:
                records=config.read(cr,uid,hole_ids,['min','max']) 
                if records:
                    min=records[0]['min']
                    max=records[0]['max']
                    if my.min_finish_hole:
                        if my.min_finish_hole < min or my.min_finish_hole >max:
                                info=info+'孔径:'+ str(my.min_finish_hole)+' mm;'   
    #----------内层最小线宽------------
            min_line_width_ids=config.search(cr,uid,[('item','=','min_line_width'),('res_company','=','szmtl'),('inorout','=','in'),('cu_thickness','like',my.finish_inner_cu)])
            print my.finish_inner_cu,'inner_cu'
            if min_line_width_ids:
                print 'min_line_width_ids'
                records=config.read(cr,uid,min_line_width_ids,['v'])
                min_line_width=records[0]['v']
                if my.min_line_width<float(min_line_width):
                        info=info+'内层铜厚:'+str(my.finish_inner_cu)+'OZ,'+'最小线宽:'+str(my.min_line_width)+'mil;'
                  
    #--------内层最小线距--------------              
            min_line_space_ids=config.search(cr,uid,[('item','=','min_line_space'),('res_company','=','szmtl'),('inorout','=','in'),('cu_thickness','like',my.finish_inner_cu)])
            print my.finish_inner_cu,'inner_cu'
            if min_line_space_ids:
                print 'min_line_space_ids'
                records=config.read(cr,uid,min_line_space_ids,['v'])
                min_line_space=records[0]['v']
                if my.min_line_space<float(min_line_space):
                        info=info+'内层铜厚:'+str(my.finish_inner_cu)+'OZ,'+'最小线距:'+str(my.min_line_space)+'mil;'     
    
    
    #----------外层最小线宽------------
            min_line_width_ids=config.search(cr,uid,[('item','=','min_line_width'),('res_company','=','szmtl'),('inorout','=','out'),('cu_thickness','like',my.finish_out_cu)])
            print my.finish_out_cu,'out_cu'
            if min_line_width_ids:
                print 'min_line_width_ids'
                records=config.read(cr,uid,min_line_width_ids,['v'])
                min_line_width=records[0]['v']
                if my.min_line_width<float(min_line_width):
                        info=info+'外层铜厚:'+str(my.finish_out_cu)+'OZ,'+'最小线宽:'+str(my.min_line_width)+'mil;'
                  
    #--------外层最小线距--------------              
            min_line_space_ids=config.search(cr,uid,[('item','=','min_line_space'),('res_company','=','szmtl'),('inorout','=','out'),('cu_thickness','like',my.finish_out_cu)])
            print my.finish_out_cu,'out_cu'
            if min_line_space_ids:
                print 'min_line_space_ids'
                records=config.read(cr,uid,min_line_space_ids,['v'])
                min_line_space=records[0]['v']
                if my.min_line_space<float(min_line_space):
                        info=info+'外层铜厚:'+str(my.finish_out_cu)+'OZ,'+'最小线距:'+str(my.min_line_space)+'mil;'
    
    #--------拼板尺寸--------------
    #------最大尺寸----------------
            if my.layer_count<=2:
                layer='2'
            else:
                layer='3'
            max_panel_size_ids=config.search(cr,uid,[('item','=','panel_size'),('v','=','max'),('res_company','=','szmtl'),('layer','=',layer)])
            if max_panel_size_ids:
               records=config.read(cr,uid,max_panel_size_ids,['min','max'])
               
               max=records[0]['max']
               min=records[0]['min']

               
               if my.pcs_length>=my.pcs_width:
                   if my.pcs_length*10>max or my.pcs_width*10>min:
                       info=info+'拼板尺寸:'+str(my.pcs_length*10)+'*'+str(my.pcs_width*10)+'cm;'
               else:
                   if  my.pcs_width*10>max or my.pcs_length*10>min:
                       info=info+'拼板尺寸:'+str(my.pcs_length*10)+'*'+str(my.pcs_width*10)+'cm;'
     #------最小尺寸----------------                  
            min_panel_size_ids=config.search(cr,uid,[('item','=','panel_size'),('v','=','min'),('res_company','=','szmtl')])
            if min_panel_size_ids:
               records=config.read(cr,uid,min_panel_size_ids,['min','max'])
               min=records[0]['min']
               max=records[0]['max']
               
               if my.pcs_length<my.pcs_width:
                   if my.pcs_length*10<min or my.pcs_width*10<max:
                       info=info+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
               else:
                   if  my.pcs_width*10<min or my.pcs_length*10<max:
                       info=info+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
            
    #-----------表面涂覆板厚------------------
            surface_height_ids=config.search(cr,uid,[('item','=','board_thickness'),('res_company','=','szmtl'),('surface_treatment','=',my.surface_treatment)]) 
            if surface_height_ids:
                records=config.read(cr,uid,surface_height_ids,['min','max'])
                min=records[0]['min']
                max=records[0]['max']
                if my.finish_board_thickness < min or my.finish_board_thickness>max:
                    info=info+'表面涂覆:'+str(my.surface_treatment)+',板厚:'+str(my.finish_board_thickness)+'mm;'
    #---------表面涂覆尺寸------------------      
     
            surface_size_ids=config.search(cr,uid,[('item','=','panel_size'),('res_company','=','szmtl'),('surface_treatment','=',my.surface_treatment)])
            print surface_size_ids,'surface_size_ids'
            print my.surface_treatment,' my.surface_treatment'
            if surface_size_ids:
                records=config.read(cr,uid,surface_size_ids,['min','max'])
                max=records[0]['max']
                min=records[0]['min']
                if my.pcs_length<my.pcs_width:
                       if my.pcs_length*10>max or my.pcs_width*10>min:
                           info=info+'表面涂覆:'+str(my.surface_treatment)+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                else:
                       if  my.pcs_width*10>max or my.pcs_length*10>min:
                           info=info+'表面涂覆:'+str(my.surface_treatment)+'拼板尺寸:'+str(my.pcs_length)+'*'+str(my.pcs_width)+'cm;'
                       
 #------厚径比----------------
            td_rate=my.finish_board_thickness*1.0/my.min_finish_hole
            if  td_rate>12:
                 info=info+'厚径比为:'+str(td_rate)
        
#------层数-----------------
            if my.layer_count>24:
                info=info+'层数:'+str(my.layer_count)            
            #raise osv.except_osv(_('Warning !'), _('SZ:'+info))                    
            #print info.encode('gbk')
            unconventional_review_ids=obj.search(cr,uid,[('pcb_info_id','=',my.id),('state','!=','refuse'),('production_factory','=','szmtl')])
            if info !='' and not unconventional_review_ids:
                obj.create(cr,uid,{
                               'pcb_info_id':my.id,
                               'partner_id':my.partner_id,
                               'unconventional_note':info,
                               'production_factory':'szmtl',
                             })
        return True 
        
#-----------------同步数据到东烁中----------------
    def insert_to_ds(self,cr,uid,id,vals,context=None):  
        column=[]
        info=self.browse(cr,uid,id)
        pcb_line_obj=self.pool.get('pcb.info.line')
        line_ids=pcb_line_obj.search(cr,uid,[('pcb_info_many_line','=',info.id)])
        info_board_material=''
        info_special_process=''
        info_route_type=''
        info_test_type=''
        info_accept_standard=''
        info_mark_request=''
        info_packing_type=''
        info_request_with_goods=''
        mark_request=[]
        special_process=[]
        for line_id in line_ids:
            line_info=pcb_line_obj.browse(cr,uid,line_id)
            if line_info.board_material:
                info_board_material=info_board_material+line_info.board_material+' '
            if line_info.special_process:
                info_special_process=info_special_process+line_info.special_process+';'
                special_process.append(line_info.special_process)
            if line_info.route_type:
                info_route_type=info_route_type+line_info.route_type+';'
            if line_info.test_type:
                info_test_type=info_test_type+line_info.test_type+';'
            if line_info.accept_standard:
                info_accept_standard=info_accept_standard+line_info.accept_standard+';'
            if line_info.mark_request:
                info_mark_request=info_mark_request+line_info.mark_request+';'
                mark_request.append(line_info.mark_request)
            if line_info.packing_type:
               info_packing_type=info_packing_type+line_info.packing_type+';'
            if line_info.request_with_goods:
               info_request_with_goods=info_request_with_goods+line_info.request_with_goods+';'

        
        
        #---单据编号---
        billcode=info.order_recive_id.name
        
        #---客户代号---
        partner_code=info.partner_id.partner_code
        #------公差--------
        
        if info.finish_tol_upper==info.finish_tol_lower:
            tolerance='±'+str(info.finish_tol_lower)
        else:
            tolerance='+'+str(info.finish_tol_upper)+'-'+str(info.finish_tol_lower)
        #----金手指--------
        if info.gold_finger_id:
            finger_count=info.gold_finger_id.finger_count
            bevel_edge=info.gold_finger_id.bevel_edge
            gold_finger_note=info.gold_finger_id.note
        else:
            finger_count=0
            bevel_edge=0
            gold_finger_note=''
        #---盲埋孔-------
        blind_buried_via_obj=self.pool.get('blind.buried.via')
        blind_buried_via_ids=blind_buried_via_obj.search(cr,uid,[('pcb_info_id','=',info.id)])
        blind_buried_via_note=''
        blind_buried_via_count=0
        if blind_buried_via_ids:
           for blind_buried_via_id in blind_buried_via_ids:
               blind_info=blind_buried_via_obj.browse(cr,uid,blind_buried_via_id)
               blind_buried_via_note=blind_buried_via_note+str(blind_info.start)+'-'+str(blind_info.end)+u'盲孔;'
               blind_buried_via_count=blind_buried_via_count+1
        #----软件半杯-----
        print info.soft_version,'info.soft_version111'
        if info.soft_version:
             soft_version_name=info.soft_version
        else:
            soft_version_name=''
        #-----特殊说明----------
        submemo=''
        if info.special_process_note:
            submemo=submemo+info.special_process_note
        if info.packing_note:
            submemo=submemo+info.packing_note
        if info.delivery_order_request:
             submemo=submemo+info.delivery_order_request
        if info.partner_special_request:
             submemo=submemo+info.partner_special_request
        #----ET章------------   
        if u'盖ET' in mark_request:
            et='True'
        else:
            et='False'
        #----混压------------
        if u'混压' in special_process:
            blend='True'
        else:
            blend='False'
        #-------v-cut-------------
        contact=''
        if info.contact:
            contact=info.contact.contact
        if  info.vcut_angle:
            vcut_angle=float(info.vcut_angle)
        else:
            vcut_angle=0
        column.append(info.partner_id.name)
        column.append(info.source_file_name)
        column.append(info_board_material)
        column.append(info.layer_count)
        column.append(info.out_cu)
        column.append(info.inner_cu)
        column.append(info.finish_board_thickness)
        column.append(tolerance)
        column.append(info.surface_treatment)
        column.append(finger_count)
        
        column.append(bevel_edge)
        column.append(info.surface_treatment_request)
        column.append(info_special_process)
        column.append(blind_buried_via_note)
        column.append('')
        column.append(info.solder_colour)
        column.append(info.solder_type)
        column.append(info.solder_via)
        column.append('')
        column.append(info.silk_colour)
        
        column.append(info.silk_type)
        column.append('')
        column.append(info_route_type)
        column.append(info_test_type)
        column.append(info_accept_standard)
        column.append(info_mark_request)
        column.append(info_packing_type)
        column.append(info_request_with_goods)
        column.append(info.delivery_type)
        column.append(info.allow_scrap_count)
        
        column.append(info.custmer_goodscode)
        column.append(soft_version_name)
        column.append('')
        column.append(info.unit_length)
        column.append(blind_buried_via_count)
        column.append(info.unit_width)
        column.append('')
        column.append(info.pcs_length)
        column.append(info.pcs_width)
        column.append(info.email)
        
        column.append(contact)
        column.append(info.phone)
        column.append(vcut_angle)
        column.append(info.product_id)
        column.append(submemo)
        column.append('')
        column.append(info.silk_variants)
        column.append(info.solder_variants)
        column.append(info.basic_board_thickness)
        column.append(info.finish_out_cu)
        
        column.append(info.finish_inner_cu)
        column.append(info.panel_x)
        column.append(info.panel_y)
        column.append(et)
        column.append(str(info.allow_scrap_percent))
        column.append(blend)
        column.append(info.min_line_width)
        column.append(info.min_line_space)
        column.append(info.min_hole2line)
        column.append(info.min_finish_hole)
        
        column.append('')
        column.append(0)
        column.append('')
        column.append(0)
        column.append(info.next_note)
        column.append(info.product_material)   
        column.append(info.provide_steel_net)
        column.append(info.provide_gerber)
        column.append(info.confirm_gerber)
        column.append(gold_finger_note)
        
        column.append(info.test_point_count)
        column.append(info.fill_core_count)
        column.append(info.pcs_drill_count)
        column.append(info.pcs_slot_count)
        column.append(0)
        
        
        column.append(billcode)
        column.append(partner_code)
        column.append('create')
        column.append('')
        if not billcode:
                 raise osv.except_osv(_('Error!'),_(u'接单号不存在，请检查！'))
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
                
           sql='''exec pp_TBproduction_OE '%s','%s','%s','%s','%s','%s','%f','%s','%s','%d',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%d','%d',
                                          '%s','%s','%s','%f','%d','%f','%s','%s','%s','%s',
                                          '%s','%s','%f','%s','%s','%s','%s','%s','%f','%s',
                                          '%s','%d','%d','%s','%s','%s','%f','%f','%f','%f',
                                          '%s','%f','%s','%d','%s','%s','%s','%s','%s','%s',
                                           '%f','%f','%f','%f','%f','%s','%s','%s','%s' ''' %row
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
          print 'pcb.info','create'
       
          id=super(pcb_info,self).create(cr,uid,vals,context=context)
          return self.insert_to_ds(cr,uid,id,vals,context=context)   
        
        
    def update_to_ds(self,cr,uid,ids,context=None):
        column=[]
        if type(ids)==type(column):
            info=self.browse(cr,uid,ids[0])
        else:
            info=self.browse(cr,uid,ids)
        pcb_line_obj=self.pool.get('pcb.info.line')
        line_ids=pcb_line_obj.search(cr,uid,[('pcb_info_many_line','=',info.id)])
        info_board_material=''
        info_special_process=''
        info_route_type=''
        info_test_type=''
        info_accept_standard=''
        info_mark_request=''
        info_packing_type=''
        info_request_with_goods=''
        mark_request=[]
        special_process=[]
        for line_id in line_ids:
            line_info=pcb_line_obj.browse(cr,uid,line_id)
            if line_info.board_material:
                info_board_material=info_board_material+line_info.board_material+' '
            if line_info.special_process:
                info_special_process=info_special_process+line_info.special_process+';'
                special_process.append(line_info.special_process)
            if line_info.route_type:
                info_route_type=info_route_type+line_info.route_type+';'
            if line_info.test_type:
                info_test_type=info_test_type+line_info.test_type+';'
            if line_info.accept_standard:
                info_accept_standard=info_accept_standard+line_info.accept_standard+';'
            if line_info.mark_request:
                info_mark_request=info_mark_request+line_info.mark_request+';'
                mark_request.append(line_info.mark_request)
            if line_info.packing_type:
               info_packing_type=info_packing_type+line_info.packing_type+';'
            if line_info.request_with_goods:
               info_request_with_goods=info_request_with_goods+line_info.request_with_goods+';'
       # if u'测试' not in info_test_type:
       #     raise osv.except_osv(_('Error!'),_(u'通断测试类型不能为空，请检查！'))
        #---单据编号---
        billcode=info.order_recive_id.name
        
        #---客户代号---
        partner_code=info.partner_id.partner_code
        #------公差--------
        
        if info.finish_tol_upper==info.finish_tol_lower:
            tolerance='±'+str(info.finish_tol_lower)
        else:
            tolerance='+'+str(info.finish_tol_upper)+'/'+'-'+str(info.finish_tol_lower)
        #----金手指--------
        if info.gold_finger_id:
            finger_count=info.gold_finger_id.finger_count
            bevel_edge=info.gold_finger_id.bevel_edge
            gold_finger_note=info.gold_finger_id.note

        else:
            finger_count=0
            bevel_edge=0
            gold_finger_note=''
        #---盲埋孔-------
        blind_buried_via_obj=self.pool.get('blind.buried.via')
        blind_buried_via_ids=blind_buried_via_obj.search(cr,uid,[('pcb_info_id','=',info.id)])
        blind_buried_via_note=''
        blind_buried_via_count=0
        if blind_buried_via_ids:
           for blind_buried_via_id in blind_buried_via_ids:
               blind_info=blind_buried_via_obj.browse(cr,uid,blind_buried_via_id)
               blind_buried_via_note=blind_buried_via_note+str(blind_info.start)+'-'+str(blind_info.end)+u'盲孔;'
               blind_buried_via_count=blind_buried_via_count+1
        #----软件半杯-----
        
        if info.soft_version:
             soft_version_name=info.soft_version
        else:
            soft_version_name=''
        #-----特殊说明----------
        submemo=''
        if info.special_process_note:
            submemo=submemo+info.special_process_note
        if info.packing_note:
            submemo=submemo+info.packing_note
        if info.delivery_order_request:
             submemo=submemo+info.delivery_order_request
        if info.partner_special_request:
             submemo=submemo+info.partner_special_request
        #----ET章------------   
        if u'盖ET' in mark_request:
            et='True'
        else:
            et='False'
        #----混压------------
        if u'混压' in special_process:
            blend='True'
        else:
            blend='False'
        #-------v-cut-------------
        contact=''
        if info.contact:
            contact=info.contact.contact
        if  info.vcut_angle:
            vcut_angle=float(info.vcut_angle)
        else:
            vcut_angle=0
        column.append(info.partner_id.name)
        column.append(info.source_file_name)
        column.append(info_board_material)
        column.append(info.layer_count)
        column.append(info.out_cu)
        column.append(info.inner_cu)
        column.append(info.finish_board_thickness)
        column.append(tolerance)
        column.append(info.surface_treatment)
        column.append(finger_count)
        
        column.append(bevel_edge)
        column.append(info.surface_treatment_request)
        column.append(info_special_process)
        column.append(blind_buried_via_note)
        column.append('')
        column.append(info.solder_colour)
        column.append(info.solder_type)
        column.append(info.solder_via)
        column.append('')
        column.append(info.silk_colour)
        
        column.append(info.silk_type)
        column.append('')
        column.append(info_route_type)
        column.append(info_test_type)
        column.append(info_accept_standard)
        column.append(info_mark_request)
        column.append(info_packing_type)
        column.append(info_request_with_goods)
        column.append(info.delivery_type)
        column.append(info.allow_scrap_count)
        
        column.append(info.custmer_goodscode)
        column.append(soft_version_name)
        column.append('')
        column.append(info.unit_length)
        column.append(blind_buried_via_count)
        column.append(info.unit_width)
        column.append('')
        column.append(info.pcs_length)
        column.append(info.pcs_width)
        column.append(info.email)
        
        column.append(contact)
        column.append(info.phone)
        column.append(vcut_angle)
        column.append(info.product_id)
        column.append(submemo)
        column.append('')
        column.append(info.silk_variants)
        column.append(info.solder_variants)
        column.append(info.basic_board_thickness)
        column.append(info.finish_out_cu)
        
        column.append(info.finish_inner_cu)
        column.append(info.panel_x)
        column.append(info.panel_y)
        column.append(et)
        column.append(str(info.allow_scrap_percent))
        column.append(blend)
        column.append(info.min_line_width)
        column.append(info.min_line_space)
        column.append(info.min_hole2line)
        column.append(info.min_finish_hole)
        
        column.append('')
        column.append(0)
        column.append('')
        column.append(0)
        column.append(info.next_note)
        column.append(info.product_material)   
        column.append(info.provide_steel_net)
        column.append(info.provide_gerber)
        column.append(info.confirm_gerber)
        column.append(gold_finger_note)
        
        column.append(info.test_point_count)
        column.append(info.fill_core_count)
        column.append(info.pcs_drill_count)
        column.append(info.pcs_slot_count)
        column.append(0)
        
        
        column.append(billcode)
        column.append(partner_code)
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
           
           sql='''exec pp_TBproduction_OE '%s','%s','%s','%s','%s','%s','%f','%s','%s','%d',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                          '%s','%s','%s','%s','%s','%s','%s','%s','%d','%d',
                                          '%s','%s','%s','%f','%d','%f','%s','%s','%s','%s',
                                          '%s','%s','%f','%s','%s','%s','%s','%s','%f','%s',
                                          '%s','%d','%d','%s','%s','%s','%f','%f','%f','%f',
                                          '%s','%f','%s','%d','%s','%s','%s','%s','%s','%s',
                                          '%f','%f','%f','%f','%f','%s','%s','%s','%s' ''' %row
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
        print 'pcb.info','write'
        super(pcb_info,self).write(cr,uid,ids,vals,context=context)
        if ids:
            return self.update_to_ds(cr,uid,ids,context=None)
        else:
            return True         

        
        

        
pcb_info()


class pcb_info_line(osv.osv):
    _name='pcb.info.line'
    _description='Pcb info line'
    
    def _get_packing_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','packing_type')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_request_with_goods(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','request_with_goods')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
        

    def _get_mark_request(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','mark_request')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_test_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','test_type')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    
    def _get_accept_standard(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','accept_standard')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_route_type(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','route_type')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    def _get_special_process(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','special_process')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _get_board_material(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','board_material')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    def _info_get(self,cr,uid,ids,field_name,args,context=None):
        res={}
        my=self.browse(cr,uid,ids[0])
        board_material=my.board_material
        print board_material,'board_material'
        obj=self.pool.get('select.selection')
        id=obj.search(cr,uid,[('label','=',board_material)],context=context)
        print id,'id'
        if id :
            if field_name=='is_specia_material':
                re=obj.browse(cr,uid,id[0]).is_specia_material
                print re,'re'
                for id in ids:
                    res[id]=re
            elif field_name=='is_htg':
                re=obj.browse(cr,uid,id[0]).is_htg
                print re,'res'
                for id in ids:
                    res[id]=re
            elif field_name=='is_rigid_flexible':
                re=obj.browse(cr,uid,id[0]).is_rigid_flexible
                for id in ids:
                    res[id]=re
            return res
        else:
            return res
    
    _columns={
              
        'pcb_info_many_line'   :fields.many2one('pcb.info',u'用户单明细',ondelete='cascade'),
        'board_material'       :fields.selection(_get_board_material,u'板材料'), #板材类型
        'special_process'      :fields.selection(_get_special_process,u'特殊工艺'),#特殊工艺
        'route_type'           :fields.selection(_get_route_type,u'外形加工') ,#外形方式   
        'accept_standard'      :fields.selection(_get_accept_standard,u'验收标准') ,##验收标准
        'test_type'            :fields.selection(_get_test_type,u'通断测试') ,#测试类型
        'mark_request'         :fields.selection(_get_mark_request,u'标记要求'), #标记要求
        'request_with_goods'   :fields.selection(_get_request_with_goods,u'附货要求'), #附货要求
        'packing_type'         :fields.selection(_get_packing_type,u'包装方式'),
        'is_specia_material'   :fields.function(_info_get,method=True,type='boolean',string=u'是否特殊材料',store=True,readonly=True),
        'is_htg'               :fields.function(_info_get,method=True,type='boolean',string=u'是否高TG',store=True,readonly=True),
        'is_rigid_flexible'    :fields.function(_info_get,method=True,type='boolean',string=u'是否刚柔结合',store=True,readonly=True),
        
        'state'      :fields.selection([('draft',u'草稿'),('wait_order_supervisor',u'待部门主管'),('done',u'完成'),('refuse',u'作废'),('wait_change',u'待更改')],u'单据状态',readonly=True,select=True),
    }       


    _defualts={
               'is_specia_material':False,
               'is_htg':False,
               'state':lambda *a:'draft',
               }

pcb_info_line()

class pcb_list(osv.osv):
    _name='pcb.list'

    _description='Pcb list'

    _columns={
              
        'name'   :fields.char(u'档案号',size=64,readonly=True),
        'pcb_info_id'    :fields.many2one('pcb.info',u'用户单号',readonly=True),
        'partner_id':fields.many2one('res.partners',u'客户名称',readonly=True),
        'ref':fields.char('客户代号',size=128,readonly=True),
        
    }
    def unlink(self, cr, uid, ids, context=None):
        my=self.browse(cr,uid,ids[0])
        if my.name or my.partner_id:
                raise osv.except_osv(_('Error!'),_(u'档案号清单不能删除！'))
        else:
            return super(pcb_info,self).unlink(cr,uid,ids)
    
pcb_list()

class pcb_cost_argument(osv.osv):
    _name='pcb.cost.argument'
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
    
    
    def _material_category(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','board_material')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    
    def _surface_treatment(self,cr,uid,context=None):
        obj=self.pool.get('select.selection')
        ids=obj.search(cr,uid,[('type','=','surface_treatment')],context=context)
        res=obj.read(cr,uid,ids,['label','label'],context)
        return [(r['label'],r['label'])for r in res]
    
    _columns = {                   
        'name'            :fields.char(u'名称', size=64 , require=True,select=True,), 
        'type'            :fields.selection([('normal_sample',u'样板'),('normal_mass',u'批量生产'),('hdi','Hdi'),('rigid_flexible',u'刚柔结合板'),('special_matrial',u'特殊材料'),('none',u'无')],u'类型', size=32,  select=True,),   #报价类型
        'cost_type'       :fields.selection([('none',u'无'),('ready',u'准备费'),('plot',u'菲林费'),('test',u'测试费'),('test_jig',u'测试jig费'),('test_pcs',u'测试pcs费'),
                                             ('pack',u'打包费'),('base',u'基板费'),('mould',u'模具费'),('change',u'变更费'),('other',u'其他费'),('base_bd_thick',u'基板厚度'),
                                             ('standard_days',u'标准天数'),('cost_days',u'加急费'),('finger',u'金手指'),('flexible',u'刚柔结合板'),('surface_treatment',u'表面涂覆'),('special_matrial',u'特殊材料'),
                                             ('au_amount',u'沉金厚度费')],u'费用类型', size=32,  select=True,), # 费用类型
        'v'               :fields.float( u'值',digits=(6,3)),  #值
        'layer_count'     :fields.integer(u'层数', select=True,),  #层数
        'au_thick_min'    :fields.float( u'最小金厚',),             #金厚下限
        'au_thick_max'    :fields.float( u'最大金厚',),             #最大上限
        'finger_count_min':fields.float( u'最小金手指数',),         #手指数下限
        'finger_count_max':fields.float( u'最大金手指数',),         #手指数上限
        'test_point_min'  :fields.float( u'最小测试点',),           #测试点密度
        'test_point_max'  :fields.float( u'最大测试点',),
        'cost_days'       :fields.float( u'加急天',),                #加急费用 
        'po_area_max'     :fields.float( u'最大订单面积',),              #订单面积上限
        'po_area_min'     :fields.float( u'最小订单面积',),              #
        'pcs_area_max'    :fields.float( u'pcs最大面积',),             #pcs面积上限
        'pcs_area_min'    :fields.float( u'pcs最小面积',),
        'bd_thick_max'    :fields.float( u'最大板厚',),             #板厚上限
        'bd_thick_min'    :fields.float(u'最小板厚',),             #
        'layer_count_min' :fields.float( u'最小层数',),          #
        'layer_count_max' :fields.float( u'最大层数',),          #层数上限
        'material_category'      :fields.selection(_material_category,u'材料分类', size=32,select=True),  #材料分类
        'surface_treatment'      :fields.selection(_surface_treatment,u'表面涂覆',size=32,select=True),
#        'material_category'      :fields.many2one('select.selection',u'材料分类',domain=[('type','=','board_material')],select=True),  #材料分类
        
        'material_addition'      :fields.float( u'材料附加费',select=True),   #材料附加费
        'cu_thickness'           :fields.float( u'铜厚',select=True),           
        #'test_point_count_max'   :fields.float( 'test_point_count_max',), #测试点数量,已经定义，重复
        #'test_point_count_min'   :fields.float( 'test_point_count_min',),  
        'flexible_count'         :fields.float( u'柔性层数',),  #柔性层数
#        'surface_treatment' :fields.many2one( 'select.selection', u'表面涂覆' ,domain=[('type','=','surface_treatment')],select=True),
        'res_partner_id':       fields.many2one('res.partners',u'客户'),
        'board_size':         fields.selection([('500*500','500*500'),('500*600','500*600'),('18*24','18*24'),('36*48','36*48'),('24*36','24*36')],u'材料尺寸'),
#        'board_width':          fields.float(u'材料宽'),
        'use_ratio':            fields.float(u'利用率'),
        'append_amount':        fields.float(u'附加费'),
        'is_gtg':fields.boolean(u'是否高TG'),
        'au_thickness':fields.float( u'沉金厚度',),
        'state':fields.selection([('draft',u'草稿'),('done',u'完成')],string=u'状态',readonly=True),
    }
    _defaults = {  
        'type'   : lambda *a:  'none',
        'cost_type':lambda *a: 'none',
        'po_area_max':0.0,
        'po_area_min':0.0,
        'state':lambda *a:'draft',
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
    
    
    



