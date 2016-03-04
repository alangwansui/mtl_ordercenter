# -*- coding: utf-8 -*-
import time
from osv import fields, osv
from decimal_precision import decimal_precision as dp
from tools.translate import _
##外协商报价参数表对象
class outsource_cost_argument(osv.osv):
    ''' type:镀金手指;镀金 ;
       type_code:gold_finger_process'''
    
    ''' type:化学镍金 ;沉银 ; 沉锡 ;
       type_code:chemical_process
    '''
    ''' type:钻孔; 外形; V-Cut; 飞针测试 ;
       type_code: machine_process:
    '''
    ''' type:热风整平(无铅、有铅) ; OSP(抗氧化); 刷镀板;
       type_code: handmade_process:
    '''
    _name='outsource.cost.argument'
    _type_list=[(i,i) for i in ('machine_process','gold_finger_process','chemical_process','chemical_process_a','chemical_process_b','chemical_process_c','chemical_process_d','handmade_process','laminate_process')]
    _process_list=[(i,i) for i in ('sink_gold','sink_silver','sink_Sn','gd_finger_plated','plasma_process',
                                   'gold_plated','OSP','hot_equate_hpb','br_plated_board','laser_drill','wire_drawing','bf_laminate_pre',
                                   'hot_equate_npb','drill_outsource','flying_probe','shape_gong_side','shape_VCUT','VCUT+ gong_side','other','cutting','repair_gold','laminate','aoi','sliver_plating')]
    ##double_gt_15:双面板>=1.5 m2 ;multilayer_gt_15:多层板 >=1.5 m2
    _sub_list=[(i,i) for  i in ('nomal_sample','double_gt_15','multilayer_gt_15','bdthick_lt_04','FPC_sample','length_gt_610','length_gt_900','low_resistance','pcb_remove','above_15')]
    _bd_type=[(i,i) for i  in ('general_board','aluminum_board','double_board','much_layer_board','cu_board')]
    _bd_mal=[(i,i) for i in ('pp1078-1080','pp1080-2116')]
    _sh_list=[(i,i) for i in ('shape_gong_side','shape_VCUT','VCUT+ gong_side')]
    _cut_list=[(i,i) for i in ('cvl','fpc','fpc_3m','soft_hard_fpc','double_fpc','fpc_3m_double','3m_cut','laser_cut')]
    _columns={
        'outsource_partner_id'   :fields.many2one("res.partner", 'Outsource Supplier', size=16, select=True,domain=[('supplier','=',True)]),
        #'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id'),
        'process_type':fields.selection(_process_list,'process_type',size=32,select=True),
        'shape_type':fields.selection(_sh_list,'shape_type',size=32,),
        'sink_sn_type':fields.selection([('spray_Sn have pb','spray_Sn have pb'),('spray_Sn nhav pb','spray_Sn nhav pb')],'sink_sn_type',size=64,select=True),
        'sub_process_type':fields.selection(_sub_list,'sub_process_type'),
        'process_category':fields.selection(_type_list,'process_category',select=True),
        'workcenter_id':fields.char('workcenter_id',size=32),#工艺
        'layer_count':fields.integer('layer_count',select=True),
        'board_thickness':fields.float('board_thickness'),
        'board_type':fields.selection(_bd_type,'board_type'),
        'board_material':fields.selection(_bd_mal,'board_material'),#材质
       
        'min_board_thickness':fields.float('min_board_thickness'),
        'max_board_thickness':fields.float('max_board_thickness'),
        'cu_thickness':fields.char('cu_thickness',size=16),
        'price_units':fields.float('price_units',digits=(5,5),select=True),#
        'account_tax_id':fields.many2one('account.tax','account_tax'),#税率
        'if_have_tax':fields.boolean('if_have_tax'),
        'if_without_tax':fields.boolean('if_without_tax'),
        'default_lowest_cost':fields.float('default_lowest_cost', digits_compute=dp.get_precision('Account'),),#最低费用
        'price_add_rate':fields.float('price_add_rate'),#总价加价比例
        'nickel_thickness_add':fields.float('nickel_thickness_add'),#镍厚增加值
        'nickel_thickness_base':fields.float('nickel_thickness_base'),#加价基本镍厚
         'note':fields.text('note'),#备注
         ##化学镍金
        'nickel_thickness':fields.float("nickel_thickness(u')"),#外协商镍厚
        'gold_thickness':fields.float("gold_thickness(u')"),#外协商金厚
        
        'nickel_thickness_m':fields.float("nickel_thickness(u')"),#本厂默认镍厚
        'gold_thickness_m':fields.float("gold_thickness(u')"),#本厂默认金厚
        'top_area':fields.float('top_area'),
        'bottom_area':fields.float('bottom_area'),
     
        ##钻孔
        'min_hole_dia':fields.float('min_hole_dia(mm)'),#最小孔径
        'hole_count':fields.integer('hole_count'),#总孔数
        'min_hole_value':fields.float('min_hole_value'),
        'max_hole_value':fields.float('max_hole_value'),
        'min_larse_hole':fields.float('min_larse_hole(mil)'),#最小激光钻孔孔径
        'max_larse_hole':fields.float('max_larse_hole(mil)'),#最大激光钻孔孔径
        'drills_type':fields.selection([('drill_hole','drill_hole'),('slot_hole','slot_hole'),('join_hole','join_hole'),('special_hole','special_hole')],'drills_type',),
        ##金手指
        'au_thick_min'    :fields.float( 'au_thick_min',),             #金厚下限
        'au_thick_max'    :fields.float( 'au_thick_max',),             #最大上限
        'finger_count_min':fields.float( 'finger_count_min',),         #手指数下限
        'finger_count_max':fields.float( 'finger_count_max',),         #手指数上限
        'finger_length':fields.float( 'finger_length',),
        'finger_width':fields.float( 'finger_width',), 
        'bevel_edge'  :fields.selection([('30','30'),('45','45'),('60','60')], 'bevel_edge',),
        'finger_count':fields.integer( 'finger_count',),
        'pcs_unit_count':fields.integer('pcs_unit_count'),#排版unit数
        'default_width_reduce':fields.float('default_width_reduce(mm)'),
        'default_length_reduce':fields.float('default_length_reduce(mm)'),
        'red_tape_price':fields.float('red_tape_price(/inch)'),#贴红胶纸单价
        ##飞针测试:flying_probe
        'side_length_max':fields.float('side_length_max'),
        'basic_cost':fields.float('basic_cost'),
        'if_retest_free':fields.boolean('if_retest_free'),#是否复测免收
        ##外形VCUT
        'price_cutter':fields.float('price_cut',digits=(5,5)),#刀具单价
        
        ##外形锣边
        'min_cutter_size':fields.float('min_cutter_size(inch)'),#最小锣刀尺寸
        'max_cutter_size':fields.float('max_cutter_size(inch)'),#最大锣刀尺寸
        'gong_price_units':fields.float('gong_price_units(/inch)',digits=(5,5)),#锣程单价
        'v_price_units':fields.float('v_price_units(/m)',digits=(5,5)),#v程单价
        'vmin_bd_thickness':fields.float('vmin_bd_thickness'),
        'vmax_bd_thickness':fields.float('vmax_bd_thickness'),
        'slot_price':fields.float('slot_price',digits=(5,5)),#锣槽单价
        ##喷锡
        'sn_board_type':fields.selection([('multilayer_board','multilayer_board'),('single_board','single_board')],'sink_sn_board_type'),
        ##拉丝，层压前表面处理
        'norms_mark':fields.char('norms_mark',size=256),#规格号
        'film_thickness':fields.float('film_thickness'),#膜厚
        'min_film_thickness':fields.float('min_film_thickness'),#最小膜厚
        'max_film_thickness':fields.float('max_film_thickness'),#最大膜厚
        'price_dm2':fields.float('price_dm2(dm2)',digits=(5,5)),#每平方分米单价
        'price_uom':fields.many2one('product.uom','price_uom'),#单价单位
        ##沉银
        'min_silver_thick':fields.float('min_silver_thick'),
        'max_silver_thick':fields.float('min_silver_thick'),
        'board_type_new':fields.selection([('big_board','big_board'),('small_board','small_board')],'board_type_new'),#
        'min_sn_thick':fields.float('min_sn_thick'),#
        'max_sn_thick':fields.float('max_sn_thick'),#
        'price_min':fields.float('price_min'),#
        'sink_sliver_type':fields.selection([('normal_board','normal_board'),('special_board','special_board')],'sink_sliver_type'),#沉银板类型
        'wire_draw_type':fields.selection([('sand_blast','sand_blast'),('wire_draw','wire_draw'),('oxide_anodes','oxide_anodes'),('sand_oxide','sand_oxide'),('wire_oxide','wire_oxide')],'wire_draw_type'),
        'fly_board_type':fields.selection([('double_board','double_board'),('four_board','four_board'),('six_most_board',('six_most_board'))],'fly_board_type'),
        'cutting_type':fields.selection(_cut_list,'cutting_type'),#切割类型
        'repair_type':fields.selection([('brush_finger','brush_finger'),('repair_line','repair_line'),('brush_gold','brush_gold')],'repair_type'),#修金板类型
        'osp_type':fields.selection([('normal','normal'),('special','special')],'osp_type'),#osp类型
        'pd_thickness':fields.float('pd_thickness'),#钯厚 
        'laminate_type':fields.selection([('normal_board','normal_board'),('special_board','special_board'),('high_tg','high_tg'),('middle_tg','middle_tg')],'laminate_type'),#层压板类型
        'aoi_type':fields.selection([('test','test')],'aoi_type'),#AOI检测类型
        ###电镀银类型
        'nickel_thickness_min':fields.float('nickel_thickness_min'),#最小镍厚
        'nickel_thickness_max':fields.float('nickel_thickness_max'),#最大镍厚
        'area_min':fields.float('area_min'),#最小有效面积
        'area_max':fields.float('area_max'),#最大有效面积
        
        
    }
        

outsource_cost_argument()

