# -*- encoding: utf-8 -*-

from osv import osv,fields

from tools.translate import _
import datetime,time


class unconventional_review(osv.osv):
    _name='unconventional.review'
    _description='Unconventional review'
    _state_list=[('draft',u'草稿'),('w_eng',u'待工程'),('w_tech',u'待工艺'),('w_quality',u'待品质'),('w_material',u'待仓库'),('w_plan',u'待计划'),('w_ger_deparment',u'待总经办'),('w_order_center',u'待订单中心'),('done',u'完成'),('not_pass',u'未通过'),('refuse',u'作废')]
 #   _state_list=[(i,i.title()) for i in _state_list] 
    _columns={
        'name'  :         fields.char('非常規单号',size=128,required=False,readonly=True),#非常規編號
        'pcb_info_id':    fields.many2one('pcb.info','用户单号',select=True),#單據編號
        'create_date':    fields.datetime('创建日期',readonly=True),#單據時間
        'partner_id':     fields.related('pcb_info_id','partner_id',type='many2one',relation='res.partners',string='客户',readonly=True),#客戶代號
        'file_name':      fields.related('pcb_info_id','source_file_name',type='char',relation='pcb.info',string='文件名',readonly=True),#文件名
        'product_id':     fields.related('pcb_info_id','product_id',type='char',relation='pcb.info',string='档案号',readonly=True,select=True),#檔案號
        ##review_user:#經手人
        'order_qty':      fields.integer('订货数量'),#訂貨數量
        'delivery_time':  fields.datetime('交货日期'),#交貨日期
        'production_factory': fields.selection([('szmtl',u'深圳牧泰莱'),('csmtl',u'长沙牧泰莱')],u'投产工厂',readnoly=True),#投產工廠
        'unconventional_note':fields.text('系统非常规描述',required=True),#非常規描述
        'note':     fields.text('订单中心参数描述'),#参数描述
        'unconventional_review_ids':fields.one2many('unconventional.review.line','unconventional_review_id','Review info'),
        'state'        :   fields.selection(_state_list,'单据状态',readonly=True,size=64,select=True),
        'responsible_id':  fields.many2one('res.users','申请人'),#申请人
        
        'tech_review':      fields.boolean('工艺评审'), #工艺评审
        'quality_review':  fields.boolean('品质评审'),# 品质评审
        'material_review':fields.boolean('物控评审'),#物料评审
        'plan_review':      fields.boolean('计划评审'),# 计划评审
        'confirm_time':fields.datetime(u'审批时间',readonly=True),
    }
    _defaults={
        'name':lambda self,cr,uid,c: self.pool.get('ir.sequence').get(cr,uid,'unconventional.review'),
        'state' :lambda *a:'draft',
		'responsible_id':lambda  self,cr,uid,c: uid,
        #'create_time':lambda *a: time.strftime('%Y-%m-%d'),
    }

                       
    def wait(self,cr,uid,ids,context):
        
        print context,'context'
        nowstr = time.strftime("%Y-%m-%d %H:%M:%S")
        now=datetime.datetime.strptime(nowstr,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=8)
        employee_obj=self.pool.get('employee')
        user_obj=self.pool.get('res.users')
        line_obj=self.pool.get('unconventional.review.line')
        dpt_obj=self.pool.get('res.department')
        dpt_eng_ids=dpt_obj.search(cr,uid,[('name','=','工程部')])
        dpt_tech_ids=dpt_obj.search(cr,uid,[('name','=','工艺部')])
        dpt_quality_ids=dpt_obj.search(cr,uid,[('name','=','品质部')])
        
        dpt_material_ids=dpt_obj.search(cr,uid,[('name','=','物控部')])
        
        dpt_plan_ids=dpt_obj.search(cr,uid,[('name','=','计划部')])
        
        dpt_ger_ids=dpt_obj.search(cr,uid,[('name','=','总经办')])
        
        dpt_order_center_ids=dpt_obj.search(cr,uid,[('name','=','订单中心')])
        
        info=self.browse(cr,uid,ids[0])
        line_eng_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_eng_ids)])
        line_tech_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_tech_ids)])
        line_quality_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_quality_ids)])
        line_material_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_material_ids)])
        line_plan_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_plan_ids)])
        line_ger_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_ger_ids)])
        line_order_center_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_order_center_ids)])

        dict={}
        dict[dpt_eng_ids[0]]='w_eng'
        dict[dpt_tech_ids[0]]='w_tech'
        dict[dpt_quality_ids[0]]='w_quality'
        dict[dpt_material_ids[0]]='w_material'
        dict[dpt_plan_ids[0]]='w_plan'
        dict[dpt_ger_ids[0]]='w_ger_deparment'
        dict[dpt_order_center_ids[0]]='w_order_center'
        
        if info.state=='draft':
            
            user_info=user_obj.browse(cr,uid,uid)
            employee_ids=employee_obj.search(cr,uid,[('employeecode','=',user_info.login)])
            if not employee_ids:
                raise  osv.except_osv(_('Warning !'), _('评审人账号不匹配，请联系管理员！'))
            employee_info=employee_obj.browse(cr,uid,employee_ids[0])
            dpt_ids=dpt_obj.search(cr,uid,[('name','like',employee_info.department)])
            if  dpt_ids[0]!=dpt_order_center_ids[0]:   
                raise  osv.except_osv(_('Warning !'), _('需要订单中心审批,审批人不属于订单中心，请检查！'))
            
            if not line_eng_ids:
                line_eng_id=line_obj.create(cr,uid,{
                                        'unconventional_review_id':info.id,
                                         'department_id':dpt_eng_ids[0],
                                        })
            if info.confirm_time==False:
                self.write(cr,uid,ids[0],{
                                          'confirm_time':now,
                                          'state':'w_eng'
                                          })
            if info.confirm_time==True:
                self.write(cr,uid,ids[0],{
                                          
                                          'state':'w_eng'
                                          })
        else:    
            #找出此时反审批的部门id
            line_draft_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','draft')])
            line_draft_info=line_obj.browse(cr,uid,line_draft_ids[0])   
            ######找出评审部门所属的部门id
            user_info=user_obj.browse(cr,uid,uid)
            employee_ids=employee_obj.search(cr,uid,[('employeecode','=',user_info.login)])
                
            if not employee_ids:
                raise  osv.except_osv(_('Warning !'), _('评审人账号不匹配，请联系管理员！'))
                
            employee_info=employee_obj.browse(cr,uid,employee_ids[0])
            dpt_ids=dpt_obj.search(cr,uid,[('name','like',employee_info.department)])
    
            if dpt_ids[0]!=line_draft_info.department_id.id:
                   raise  osv.except_osv(_('Warning !'), _('评审人不属于'+line_draft_info.department_id.name+',请检查！'))
           
        if info.state=='w_eng':
           if info.tech_review==1 and not line_tech_ids:
               line_obj.create(cr,uid,{
                                      'unconventional_review_id':info.id,
                                      'department_id':dpt_tech_ids[0],
                                      })

           if info.quality_review==1 and not line_quality_ids:
             line_quality_id=line_obj.create(cr,uid,{
                                      'unconventional_review_id':info.id,
                                      'department_id':dpt_quality_ids[0],
                                      }) 
             
           if info.material_review==1 and not line_material_ids:
                line_obj.create(cr,uid,{
                                      'unconventional_review_id':info.id,
                                      'department_id':dpt_material_ids[0],
                                      })  
                
           if info.plan_review==1 and not line_plan_ids:
               line_obj.create(cr,uid,{
                                      'unconventional_review_id':info.id,
                                      'department_id':dpt_plan_ids[0],
                                      })  

           consume_time=round((now-datetime.datetime.strptime(info.confirm_time,'%Y-%m-%d %H:%M:%S')).seconds/3600.0,2)+(now-datetime.datetime.strptime(info.confirm_time,'%Y-%m-%d %H:%M:%S')).days*24
           se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_eng_ids)])[0]
           re=line_obj.browse(cr,uid,se).return_date
           if re==False:
               line_obj.write(cr,uid,line_eng_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      }) 
           else:
               total_time=consume_time+re
               line_obj.write(cr,uid,line_eng_ids[0],{'state':'done',
                                                      'review_users_id':uid,
                                                      'review_date':now,
                                                      'consume_time':total_time,
                                                      }) 
           
        if info.state not in['w_eng','draft']:
            line_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','done')])
            line_info=line_obj.browse(cr,uid,max(line_ids))
            consume_time=round((now-datetime.datetime.strptime(line_info.review_date,'%Y-%m-%d %H:%M:%S')).seconds/3600.0,2)+(now-datetime.datetime.strptime(line_info.review_date,'%Y-%m-%d %H:%M:%S')).days*24
        if info.state=='w_tech':
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_tech_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_tech_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })
            else:
                line_obj.write(cr,uid,line_tech_ids[0],{'state':'done',
                                                      'review_users_id':uid,
                                                    
                                                      })
        if info.state=='w_quality':
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_quality_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_quality_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })
            else:
                line_obj.write(cr,uid,line_quality_ids[0],{'state':'done',
                                                      'review_users_id':uid,})
        if info.state=='w_material':
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_material_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_material_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })    
            else:
                line_obj.write(cr,uid,line_material_ids[0],{'state':'done',
                                                      'review_users_id':uid,
                                                      })    

        if info.state=='w_plan':
           
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=', dpt_plan_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_plan_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })
            else:
                line_obj.write(cr,uid,line_plan_ids[0],{'state':'done',
                                                      'review_users_id':uid,
                                                     
                                                      })
        if info.state=='w_ger_deparment':
            
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=', dpt_ger_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_ger_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })
            else:
                line_obj.write(cr,uid,line_ger_ids[0],{'state':'done',
                                                    
                                                      'review_users_id':uid,
                                                     
                                                      })
            self.write(cr,uid,ids[0],{
                                      'state':'w_order_center'
                                      })
        if info.state=='w_order_center':
            
            se=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=', dpt_order_center_ids)])[0]
            re=line_obj.browse(cr,uid,se).review_date
            if re==False:
                line_obj.write(cr,uid,line_order_center_ids[0],{'state':'done',
                                                      'review_date':now,
                                                      'review_users_id':uid,
                                                      'consume_time':consume_time
                                                      })  
            else:
                line_obj.write(cr,uid,line_order_center_ids[0],{'state':'done',
                                                      'review_users_id':uid,
                                                      }) 
            if line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('ok_final_affirm','=', False)]):
                self.write(cr,uid,ids[0],{
                                      'state':'not_pass'
                                      })
            else:
                self.write(cr,uid,ids[0],{
                                          'state':'done'
                                          })
        
        if info.state!='w_order_center': 
            line_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','draft')])#######找出下一个要评审的部门
            if line_ids:
                   line_info=line_obj.browse(cr,uid,line_ids[0])
                   self.write(cr,uid,ids[0],{
                                          'state':dict[line_info.department_id.id]
                                          })
            else:    
                line_sure_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','done'),('ok_final_affirm','=',False)])
                if line_sure_ids and not line_ger_ids:  ###如果其中有部门评“否”,则就到总经办
                    line_obj.create(cr,uid,{
                                          'unconventional_review_id':info.id,
                                          'department_id':dpt_ger_ids[0],
                                          }) 
                    self.write(cr,uid,ids[0],{
                                      'state':'w_ger_deparment'
                                      })
                if not line_order_center_ids and not line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','draft')]):
                    line_obj.create(cr,uid,{
                                              'unconventional_review_id':info.id,
                                              'department_id':dpt_order_center_ids[0],
                                              })
                    self.write(cr,uid,ids[0],{
                                      'state':'w_order_center'
                                      })
        return True   
        
    def back(self,cr,uid,ids,context):
        
        print context,'context'
        nowstr = time.strftime("%Y-%m-%d %H:%M:%S")
        now=datetime.datetime.strptime(nowstr,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=8)

        print type(now),'type(now)'
        print now,'now'
        employee_obj=self.pool.get('employee')
        user_obj=self.pool.get('res.users')
        line_obj=self.pool.get('unconventional.review.line')
        dpt_obj=self.pool.get('res.department')
        dpt_eng_ids=dpt_obj.search(cr,uid,[('name','=','工程部')])
        dpt_tech_ids=dpt_obj.search(cr,uid,[('name','=','工艺部')])
        dpt_quality_ids=dpt_obj.search(cr,uid,[('name','=','品质部')])
        dpt_material_ids=dpt_obj.search(cr,uid,[('name','=','物控部')])
        
        dpt_plan_ids=dpt_obj.search(cr,uid,[('name','=','计划部')])
        
        dpt_ger_ids=dpt_obj.search(cr,uid,[('name','=','总经办')])
        
        dpt_order_center_ids=dpt_obj.search(cr,uid,[('name','=','订单中心')])
        
        info=self.browse(cr,uid,ids[0])
        line_eng_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_eng_ids)])
        line_tech_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_tech_ids)])
        line_quality_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_quality_ids)])
        line_material_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_material_ids)])
        line_plan_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_plan_ids)])
        line_ger_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_ger_ids)])
        line_order_center_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('department_id','=',dpt_order_center_ids)])

        dict={}
        dict[dpt_eng_ids[0]]='w_eng'
        dict[dpt_tech_ids[0]]='w_tech'
        dict[dpt_quality_ids[0]]='w_quality'
        dict[dpt_material_ids[0]]='w_material'
        dict[dpt_plan_ids[0]]='w_plan'
        dict[dpt_ger_ids[0]]='w_ger_deparment'
        dict[dpt_order_center_ids[0]]='w_order_center'
        
        

        
        if info.state  in['draft','done','cancel']: 
                raise osv.except_osv(_('Warning !'), _('此状态或完成状态下,不能反审批'))
        else:
            #找出此时反审批的部门id
            line_draft_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','draft')])
            line_draft_info=line_obj.browse(cr,uid,line_draft_ids[0])   
             ######找出评审部门所属的部门id
            user_info=user_obj.browse(cr,uid,uid)
            employee_ids=employee_obj.search(cr,uid,[('employeecode','=',user_info.login)])
            
            if not employee_ids:
                raise  osv.except_osv(_('Warning !'), _('评审人账号不匹配，请联系管理员！'))
            
            employee_info=employee_obj.browse(cr,uid,employee_ids[0])
            dpt_ids=dpt_obj.search(cr,uid,[('name','like',employee_info.department)])

            if dpt_ids[0]!=line_draft_info.department_id.id:
                   raise  osv.except_osv(_('Warning !'), _('反审人不属于'+line_draft_info.department_id.name+',请检查！'))
             
            if info.state=='w_eng':
                self.write(cr,uid,ids[0],{
                                          'state':'draft'
                                          })
                line_obj.write(cr,uid,line_eng_ids,{
                                                         'state':'draft'
                                                         })
            else:
                line_ids=line_obj.search(cr,uid,[('unconventional_review_id','=',info.id),('state','=','done')])

                line_obj.write(cr,uid,max(line_ids),{
                                                     'state':'draft',
                                                     'return_date':now,
                                                     })
                line_info=line_obj.browse(cr,uid,max(line_ids))
                self.write(cr,uid,ids[0],{
                                          'state':dict[line_info.department_id.id]
                                          })
            
            
            
            
            
            
        return True      
     
    def unlink(self, cr, uid, ids, context=None):
            my=self.browse(cr,uid,ids[0])
            if my.state!='draft':
                 raise osv.except_osv(_('Error!'),_(u'状态不是草稿状态时不能删除！'))
            return super(unconventional_review,self).unlink(cr,uid,ids)
 
unconventional_review()    
  
class unconventional_review_line(osv.osv):
    _name='unconventional.review.line'
    _description='review line'
    _columns={
        'state':                          fields.selection([('draft','草稿'),('done','完成')],'单据状态', size=32,readonly=True),
        'unconventional_review_id':       fields.many2one('unconventional.review','Review id'),
        'department_id':                  fields.many2one('res.department','评审部门',readonly=True,required=True),#評審部門
        'review_date':                    fields.datetime('评审时间',readonly=True),#評審時間
        'return_date':                    fields.datetime('反审时间',readonly=True),
        'review_users_id':                fields.many2one('res.users','评审人',readonly=True),#評審人
        'review_note':                    fields.text('评审意见'),
        'is_limit_example':               fields.boolean('限于样品加工'),#是否限于樣品加工
        'ok_create_project':              fields.boolean('需要申请研发立项'),#是否需要申請研發立項
        'ok_final_affirm':                fields.boolean('可以做'),#是否最終確認
        'consume_time':                   fields.float(u'耗时',digits=(9,2)),
        'cost_opinion':                   fields.text('成本意见'),
       # 'next_dept_id':                   fields.many2one('res.department','下一评审部门'),#評審部門
    }
  
    _defaults={
        'department_id': lambda self,cr,uid,context,: context.get('department_id'),
        'state': lambda *a: 'draft',
    }
    def write_done(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'done','review_date':time.strftime('%Y-%m-%d %H:%M:%S')})
        
    def unlink(self, cr, uid, ids, context=None):
            my=self.browse(cr,uid,ids[0])
            if my.state!='draft':
                 raise osv.except_osv(_('Error!'),_(u'状态完成时不能删除！'))
           # else:
                #return True
            return super(unconventional_review_line,self).unlink(cr,uid,ids)
        
unconventional_review_line()