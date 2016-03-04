#!/usr/bin/python
# -*- coding: utf-8 -*-

from osv import fields, osv
import time
from datetime import datetime
from decimal_precision import decimal_precision as dp
from datetime import datetime
import netsvc


class reward_punish(osv.osv):
    
    _name='reward.punish'
    _sql_info='''select he.id,he.department_id,he.job_id,
                                        hd.id, hd.name,hj.id,hj.name,resc.id,resc.name 
                                      from hr_employee he,hr_department hd,hr_job hj,res_company resc
                                      where  he.department_id=hd.id and hd.name='%s' \
                                      and he.job_id=hj.id and hj.name='经理' and  resc.name='%s' ''' 
   
    _columns={
              #'name':   fields.many2one('hr.employee','name',select=True,required=True),#姓名
              'dpt_id':  fields.related('name','department_id',type='many2one',relation='hr.department',readonly=True,string='dpt_id'),#部门
              #'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id',select=True),#工序
              'job_id':fields.related('name','job_id',type='many2one',relation='hr.job',readonly=True,string='job_id'),#职务
              'in_factory':fields.related('name','in_factory',type='date',string='in_factory_date',readonly=True),#入厂时间
              'create_date':fields.datetime('create_date', readonly=True,),
              'event_time':fields.datetime('event_time'),#事件发生时间
              'event_site':fields.char('event_site',size=128),#事件发生地点
              'event_note':fields.text('event_note'),#事件描述
              'type':fields.selection([('reward','reward'),('punish','punish')],'type',size=32),#类型
              'product_description':fields.char('product_description',size=128,select=True),
              'responsible_idea':fields.text('responsible_note'),
              'responsible_sel':fields.selection([('agree','agree'),('disagree','disagree'),('not_have','not_have')],'responsible_sel',select=True,),
              'responsible_amount':fields.float('responsible_amount',digits_compute=dp.get_precision('Account')),
          
              'dpt_director_idea':fields.text('dpt_director_idea'),
              'dpt_sel':fields.selection([('agree','agree'),('disagree','disagree')],'dpt_sel',),
              'dpt_amount':fields.float('dpt_amount',digits_compute=dp.get_precision('Account')),
             
              'director_idea':fields.text('director_idea'),
              'director_sel':fields.selection([('agree','agree'),('disagree','disagree')],'director_sel',),
              'director_amount':fields.float('director_amount',digits_compute=dp.get_precision('Account')),
            
              'quality_manager_idea':fields.text('quality_manager_idea'),
              'quality_sel':fields.selection([('agree','agree'),('disagree','disagree')],'quality_sel',),
              'quality_amount':fields.float('quality_amount',digits_compute=dp.get_precision('Account')),
            
              'responsible_director_idea':fields.text('responsible_director_idea'),
              'responsible_dpt_sel':fields.selection([('agree','agree'),('disagree','disagree')],'responsible_dpt_sel',),
              'responsible_dpt_amount':fields.float('responsible_dpt_amount',digits_compute=dp.get_precision('Account')),
             
              'personnel_idea':fields.text('personnel_idea'),
              'personnel_sel':fields.selection([('agree','agree'),('disagree','disagree')],'personnel_sel',),
              'personnel_amount':fields.float('personnel_amount',digits_compute=dp.get_precision('Account')),
           
              'gmanager_idea':fields.text('gmanager_idea'),
              'gmanager_sel':fields.selection([('agree','agree'),('disagree','disagree')],'gmanager_sel',),
              'gmanager_amount':fields.float('gmanager_amount',digits_compute=dp.get_precision('Account')),
           
              'top_responsible_idea':fields.text('process_idea'),#工序负责人意见
              'top_responsible_sel':fields.selection([('agree','agree'),('disagree','disagree'),('not_have','not_have')],'top_responsible_sel',),
              'top_responsible_amount':fields.float('top_responsible_amount',digits_compute=dp.get_precision('Account')),
              
              'create_time':fields.datetime('create_time'),
              'finish_date':fields.date('finish_date'),
            
              'approver_name':fields.many2one('res.users','approver_name'),
              'approver_time':fields.datetime('approver_time'),
              'approver_sel':fields.selection([('agree','agree'),('disagree','disagree')],'approver_sel',),
              'approver_note':fields.text('approver_note'), 
              'reality_amount':fields.float('reality_amount',digits_compute=dp.get_precision('Account')),
              'if_wapprover':fields.boolean('if_approver'),
              'if_alter_amount':fields.boolean('if_alter_amount'),
              'alter_note':fields.text('alter_amount_note'),
              'approver_note':fields.text('approver_note'),
    }
    
    
    def check_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
      
        if my._table_name == 'reward.lines':
            rew_lines=my.reward_lines_info_ids
            flg=False
            if not my.reward_clause_amount:
                for line in rew_lines:
                    if line.reward_amount >=50.0:
                        flg=True
                return flg
                    
            elif my.reward_clause_amount >=50.0:
                return True
            else:
                self.check_eng_question(cr,uid,ids)
                return False
        elif my._table_name == 'punish.lines':
            if not my.punish_clause_amount:
                if my.total_amount  >= 50.0:
                    return True
                else:
                    return False
            elif my.punish_clause_amount >=50.0:
                return True
            else:
                return False
     
    def check_approver_sel(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        app_obj=None
        state_dic={}
        app_lines=None
        
        state_dic={
                            'w_director':'director_idea',
                            'w_personnel':'personnel_idea',
                            'w_gmanager':'gmanager_idea'}
        
        if self._name=='reward.lines':
            app_obj=self.pool.get('reward.approver.lines')
            app_lines=my.reward_approver_lines_ids
            state_dic.update(
                             {'w_dpt_director':'top_responsible_idea',
                            'w_quality_manager':'quality_manager_idea',}
                             )
        elif self._name=='punish.lines':
            app_obj=self.pool.get('punish.approver.lines')
            app_lines=my.punish_approver_lines_ids
            state_dic.update(
                             {'top_responsible':'top_responsible_idea',
                            'w_dpt_manager':'responsible_director_idea',}
                             )
        for line in app_lines:
            if line.if_wapprover:
                if line.approver_sel =='disagree':
                    f_idea=app_obj.read(cr,uid,line.id,['approver_note'])['approver_note']
                    #f_idea=app_obj.read(cr,uid,line.id,[state_dic[my.state]])[state_dic[my.state]]
                    if not f_idea:
                        raise osv.except_osv(('Disagree idea not found error!'),('please input disagree idea!'))
                    else:
                        return True
                    
                           
    def parent_dpt_search(self,cr,uid,ids,dpt_id=None,dpt_list=None,ser_type=None,context=None):
        dep_obj=self.pool.get('hr.department')
        if not dpt_list:
            dpt_list=[]
        if dpt_id:
            dpt_list.append(dpt_id)
            if ser_type=='sub':
                sub_dpt=dep_obj.search(cr,uid,[('parent_id','=',dpt_id)])
                if sub_dpt:
                    for sub in sub_dpt:
                        dpt_list.append(sub)
                    
            else: 
                def ser_parent(cr,uid,dpt_id=None):
                    parent_dpt=dep_obj.browse(cr,uid,dpt_id).parent_id
                    if parent_dpt:
                        dpt_list.append(parent_dpt.id)
             
                        ser_parent(cr,uid,dpt_id=parent_dpt.id)
                    return True
                ser_parent(cr,uid,dpt_id=dpt_id)
           
        return dpt_list
    
    def _repu_info_get(self,cr,uid,ids,fields_name,args,context=None):
        gp_obj=self.pool.get('res.groups')
        fliter_obj=self.pool.get('ir.filters')
        mod_obj=self.pool.get('ir.model')
        user_obj=self.pool.get('res.users')
        res={}
        s_state=['draft']
        pu_state=['draft']
        u_dptid=context.get('department_id',False)
        u_rec=user_obj.browse(cr,uid,uid)
        gp_map={'director_jl':'w_dpt_director','supervisor_jl':'w_director',
                        'Quality/Manager':'w_quality_manager','Human Resources / Manager':'w_personnel',
                        }
        pugp_map={'user_cf':['w_responsible'],'director_cf':['w_dpt_confirm','top_responsible'],
                                'supervisor_cf':['w_director'],'manager_cf':['w_dpt_manager']}
        cr.execute('''select gid from res_groups_users_rel where uid=%s''' % uid)
        gp_all=cr.fetchall()
        
        fliter_ser=fliter_obj.search(cr,uid,[('model_id','=',self._name),('user_id','=',uid)])        
        
        for gp_tup in gp_all:
            gp_name=gp_obj.browse(cr,uid,gp_tup[0]).name
            if gp_name in gp_map:
                s_state.append(gp_map[gp_name])
            if gp_name in pugp_map:
                for pugp in pugp_map[gp_name]:
                    pu_state.append(pugp)

        re_dpt=self.parent_dpt_search(cr,uid,ids,dpt_id=u_dptid,ser_type='sub')
        u_domain=[]
        if uid !=1 and re_dpt:
            new_state=None
            
            if self._name =='reward.lines':
                new_state=s_state
            elif self._name =='punish.lines':
                new_state=pu_state
            sd_ser=self.search(cr,uid,[('state','in',new_state),('dpt_id','in',re_dpt)])
            as_ser=self.search(cr,uid,[('applicant_id.id','=',uid),('state','=','draft')])
           
            all_ser=sd_ser+as_ser
            new_ids=list(set(all_ser))
            u_domain=[('id','in',new_ids)]
      
        if fliter_ser:
            f_domain=fliter_obj.browse(cr,uid,fliter_ser[0]).domain
            if f_domain != u_domain:
                fliter_obj.write(cr,uid,fliter_ser[0],{'domain':u_domain})
        else:
            fliter_obj.create(cr,uid,{
                                        'name':str(u_rec.login),
                                        'model_id':self._name,
                                        'domain':str(u_domain),
                                        'user_id':uid,     
                                        'context':'{}'  , })
        for id in ids:
            my=self.browse(cr,uid,id)
            
            if fields_name=='is_wapprover':
                
                if my.state in s_state and u_dptid in re_dpt or uid==my.applicant_id.id:
                    res[id]=True
                else:
                    res[id]=False
          
        return res
    
    def onchange_reward_punish_clause(self,cr,uid,ids,res_id,context=None):
        if res_id:   
            cf_obj=self.pool.get('reward.punish.config')
            descrp=cf_obj.browse(cr,uid,res_id).description
            amount=cf_obj.browse(cr,uid,res_id).amount
            if self._name=='reward.lines':
                return {'value':{'reward_clause':descrp,}}
            elif self._name=='punish.lines':
                return {'value':{'punish_clause':descrp,}}
    
    def onchange_reward_punish_amount(self,cr,uid,ids,amount,context=None):
        if amount:
    
            if self._name=='reward.lines.info':
                return {'value':{'reality_reward_amount':amount}}
            elif self._name=='punish.lines.info':
                return {'value':{'reality_punish_amount':amount}}  
            
reward_punish()

class reward_punish_category(osv.osv):
    _name='reward.punish.category'
    _columns={
                'name':fields.char('name',size=32,required=True),
                'config_ids':fields.one2many('reward.punish.config','category_id','config_ids'),
                'create_date':fields.datetime('create_date',readonly=True),
                }
reward_punish_category()
         
class reward_punish_config(osv.osv):
    _name='reward.punish.config'
    _columns={
                'description':fields.text('description'),
                'name':fields.char('file_name',size=256,select=True,required=True),
                'type':fields.selection([('reward','reward'),('punish','punish')],'type',required=True),

                'amount':fields.float(' config amount',digits_compute=dp.get_precision('Account')),
                'category_id':fields.many2one('reward.punish.category','category_id',),
                'create_date':fields.datetime('create_date',readonly=True),
                #'clause_number':fields.char('clause_number',size=128),
                #'parent_clause_name':fields.char('parent_clause_name',size=64),
              }
reward_punish_config()

class reward_lines(osv.osv):
    _inherit='reward.punish'
    _name='reward.lines'
    _order='create_date desc'
    _rec_name='reward_number'
    re_list=('m_delivery','m_scrap_replenish','m_energy_standard','f_order_question','f_eng_question','fn_go_erp','personnel_reward','project_reward','other')
    _re_type=[(i,i.title()) for i in re_list]
    reward_state=('draft','w_director','w_dpt_director','w_quality_manager','w_personnel','w_gmanager','w_reward','done','cancel')
    _state_list=[(i,i.title()) for i in reward_state]
  
    def _rew_info_get(self,cr,uid,ids,fields_name,args,context=None):
        return self._repu_info_get(cr, uid, ids, fields_name, args, context)
   
    def check_reward_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_ids=my.reward_lines_info_ids 
        
        lines_amount=0.0
        if lines_ids:
        
            for line in lines_ids:
                lines_amount+=line.reality_reward_amount 
            if not my.reward_clause_amount:
                if lines_amount <= my.reward_amount:
                    return True
                else:
                    return False
                
            elif lines_amount <= my.reward_clause_amount:
            #if lines_amount <= my.total_amount:
                return True
            else:
                return False
        return True
    
    def _info_get(self,cr,uid,ids,field_name,args,context=None):
       
        line_obj=self.pool.get('reward.lines.info')
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            lines_rec=my.reward_lines_info_ids
            lines_number=[]
            lines_name=[]
            lines_info=False
            l_names=False
            
            if lines_rec:
                for line in lines_rec:
                    if line.name:
                        lines_number.append(line.name.job_number)
                        lines_name.append(line.name.name)
                   
                if lines_number and lines_name:
                    lines_info=','.join(lines_number)+':'+','.join(lines_name)
                    l_names=','.join(lines_name)
            
            if field_name=='reward_info':
                res[id]=lines_info
            elif field_name=='reward_name':
                res[id]=l_names  
        return res
     
    def _rew_search(self,cr,uid,ids,field_name,args,context=None):
      
        res_ids=[]
        resp_ser=self.search(cr,uid,[])
        s=args[0][2]
        
        for resp_id in resp_ser:
            my=self.browse(cr,uid,resp_id)
            lines_number=None
            lines_name=None
            if my.reward_info:
                lines_number,lines_name=my.reward_info.split(':')
                numbers=lines_number.split(',')
                names=lines_name.split(',')
             
                if s in numbers or s in names:
                    res_ids.append(resp_id)
      
        return [('id','in',res_ids)]
    def check_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.reward_amount<=30:
            
            return True 
        else:
            return False     
    
    #===========================================================================
    # def get_reward_name(self,cr,uid,context):
    #    dpt_obj=self.pool.get('hr.department')
    #    user_obj=self.pool.get('res.users')
    #    dpt_list=[]
    #    if uid ==1:
    #        dpt_ser=dpt_obj.search(cr,uid,[])
    #        for dpt in dpt_ser:
    #            dpt_name=dpt_obj.browse(cr,uid,dpt).name
    #            dpt_name=dpt_name.split('/')[-1]
    #            dpt_list.append((dpt,dpt_name))
    #                
    #    else:
    #        dpt_id=user_obj.browse(cr,uid,uid).context_department_id.id
    #        
    #        dpt_ser=self.parent_dpt_search(cr,uid,[uid],dpt_id=dpt_id,ser_type='sub')
    #        for dpt in dpt_ser:
    #            dpt_name=dpt_obj.browse(cr,uid,dpt).name
    #            dpt_name=dpt_name.split('/')[-1]
    #            dpt_list.append((dpt,dpt_name))
    #    return dpt_list
    #===========================================================================

    _columns={
              'reward_number':fields.char('reward_number',size=32,required=True,select=True),#奖励单号
              'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id',select=True,required=False),#工序
              'applicant_id':fields.many2one('res.users','applicant_id',required=True),#申请人
              'name':   fields.many2one('hr.employee','reward name',),#被奖励人姓名
              
              'dpt_id':fields.many2one('hr.department','dpt_id',select=True,required=True),
              'reward_type':fields.selection(_re_type,'reward_type',select=True,required=True),
              'directly':fields.boolean('directly'),#
              'not_dieectly':fields.boolean('not_directly'),#
              'direct_description':fields.char('direct_description',size=128),
              'if_material_reward':fields.boolean('if_material_reward'),
              'reward_amount':fields.float('reward_amount',digits_compute=dp.get_precision('Account')),
              'reward_description':fields.char('reward_description',size=128),
              'reward_config':fields.many2one('reward.punish.config','reward_clause',domain=[('type','=','reward')]),
              'reward_clause':fields.related('reward_config','description',type='text',string='reward_clause',readonly=True),    
              'reward_clause_amount':fields.related('reward_config','amount',type='float',string='reward_clause_amount'),
              
              'reality_reward_amount':fields.float('reality_reward_amount',digits_compute=dp.get_precision('Account'),readonly=True),
              'state':fields.selection(_state_list,'state',readonly=True,select=True),
              'reward_state':fields.selection([('have_reward','have_reward'),('not_have_reward','not_have_reward')],'reward_state',select=True,readonly=True),
              'is_wapprover':fields.function(_rew_info_get,method=True,type='boolean',string='is_wapprover',select=True),
              'if_wapprover':fields.boolean('if_wapprover'),
              'reward_lines_info_ids':fields.one2many('reward.lines.info','reward_lines_id','reward_lines_info_ids'),
              'reward_approver_lines_ids':fields.one2many('reward.approver.lines','reward_lines_id','reward_approver_lines_ids'),
               'reward_category_id':fields.many2one('reward.punish.category','reward_type',change_default=True),
               'create_time':fields.datetime('create_time'),
               'org_reward_number':fields.char('org_reward_number',size=64),
               'reward_name':fields.function(_info_get,method=True,type='char',size=256,string='reward'),
               'reward_info':fields.function(_info_get,fnct_search=_rew_search,method=True,type='char',size=256,string='reward'),
               'punish_lines_id':fields.many2one('punish.lines','punish_lines_id'),
    }
    
    _defaults={
               'reward_number':lambda self,cr,uid,context:self.pool.get('ir.sequence').get(cr,uid,'reward.lines'),
               'applicant_id':lambda self,cr,uid,context:uid,
               'type': lambda *a:'reward',
               #'reward_state':lambda *a:'not_have_reward',
               'state':lambda *a:'draft',
               #'create_time':lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
             
    }

    _constraints=[(check_amount,'amount error: reward amount is not more than thirty !',['reward_amount'])]
                  
    
    
    def check_reward_config(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.reward_config:
            if my.reward_config.category_id:
                if my.reward_config.category_id.id != my.reward_category_id.id:
                    return False
                else:
                    return True
            else:
                return False
    
    #_constraints=[(check_reward_amount,'Amount error: all reward line amount must be <= reward clause amount or total amount,please check!',['reward_lines_info_ids']),]
                              #(check_reward_config,'Clause error: reward clause not found in reward category',['reward_config'],)  ]
    
    def onchange_reward_disagree(self,cr,uid,ids,field_value,field_amount,context=None):
       
        if field_value == 'disagree':
            return {'value':{field_amount:0.0,}}
    
   
    def reward_button_cancel(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.state == 'w_dpt_director':
            amount='responsible_amount'
            field_agree='responsible_sel'
        elif my.state == 'w_director':
            amount='dpt_amount'
            field_agree='responsible_sel'
        elif my.state == 'w_quality_manager':
            amount='quality_amount'
            field_agree='responsible_sel'
        elif my.state == 'w_gmanager':
            amount='gmanager_amount'
            field_agree='responsible_sel'
        self.write(cr,uid,ids,{'state':'cancel',amount:0.0,field_agree:'disagree'})
        return True
    
    def updata_state(self,cr,uid,ids,state=None,button_type=None,context=None):
        my=self.browse(cr,uid,ids[0])
        org_state=my.state
        self.check_approver_sel(cr,uid,ids)
        self.write(cr,uid,ids,{'state':state})
        self.action_updata_state(cr,uid,ids,state=state,org_state=org_state,button_type=button_type,context=context)
        return True
    
    def action_updata_state(self,cr,uid,ids,state=None,org_state=None,button_type=None,context=None):
        my=self.browse(cr,uid,ids[0])
        user_obj=self.pool.get('res.users')
      
     
        dpt_rec=user_obj.browse(cr,uid,uid).context_department_id
        dpt_name=uid==1 and 'admin' or dpt_rec.name
        ap_time=time.strftime('%Y-%m-%d %H:%M:%S')
     
        ap_info=[uid,ap_time]
        lines_info=my.reward_lines_info_ids
        approver_lines=my.reward_approver_lines_ids
        
        wkf_ser=netsvc.LocalService('workflow')
        reapprover_obj=self.pool.get('reward.approver.lines')
        dpt_obj=self.pool.get('hr.department')
      
        human_ser=dpt_obj.search(cr,uid,[('dpt_code','=','A')])[0]
        gmg_ser=dpt_obj.search(cr,uid,[('dpt_code','=','G')])[0]
        qua_ser=dpt_obj.search(cr,uid,[('dpt_code','=','Q')])[0]
        rew_dpt=my.dpt_id.id
       
        state_dpt={'w_dpt_director':rew_dpt,'w_director':rew_dpt,'w_quality_manager':qua_ser,
                            'w_personnel':human_ser,'w_gmanager':gmg_ser,'done':''}
        
        state_list=['draft','w_dpt_director','w_director','w_quality_manager','w_personnel','w_gmanager','done']
        
        state_idea={'w_dpt_director':[['responsible_idea'],['responsible_idea']],
                    'w_director':[['responsible_idea',],['dpt_director_idea']],
                    'w_quality_manager':[['responsible_idea','dpt_director_idea'],['quality_manager_idea']],
                    'w_personnel':[['responsible_idea','dpt_director_idea','quality_manager_idea'],['personnel_idea']],
                    'w_gmanager':[['responsible_idea','dpt_director_idea','quality_manager_idea','personnel_idea'],['gmanager_idea']],
                   }
        
        if state in ['w_dpt_director','w_director']:
            if not my.reward_lines_info_ids:
                raise osv.except_osv(('reward lines not found error!'),('please create reward lines info!'))
        if state =='done':
            self.write(cr,uid,ids,{'finish_date':time.strftime('%Y-%m-%d')})
        if state in state_dpt:
            if lines_info:
                for line in lines_info:
                    if not line.name:
                        raise osv.except_osv(('lines name error:'),('reward lines name must be not null!please check '))
            if not approver_lines:
                reapprover_obj.create(cr,uid,{
                                                                        'approver_dpt':state_dpt[state],
                                                                        'reward_lines_id':ids[0],
                                                                        'approver_state':state,
                                                                    
                                                                       'approver_sel':'agree',
                                                                       
                                                                })
               
                
            else:
                lines_state=[line.approver_state for line in approver_lines]
                lines_state=lines_state+['done']
                amount=None
                idea=None
                line_dic={}
                if state in state_dpt:
                
                    if state not in lines_state:
                        for line in approver_lines:
                            if line.approver_state == org_state:
                                suggest_note=''
                                if line.if_alter_amount:
                                    for  line_info in line.reward_lines_id.reward_lines_info_ids:
                                        if line_info.name:
                                            suggest_note+="reward people name:%s ; suggest reward amount: %s ;\n"%(line_info.name.name,line_info.reality_reward_amount)
                                if suggest_note:
                                    suggest_note+='  approver_name:%s ;approver_time: %s \n'%(user_obj.browse(cr,uid,uid).name,ap_time)
                                if line.alter_note:
                                    suggest_note=line.alter_note+suggest_note
                        
                                reapprover_obj.write(cr,uid,line.id,{'approver_name':ap_info[0],'approver_time':ap_info[1],'alter_note':suggest_note,})   
                                
                                reapprover_obj.copy(cr,uid,line.id,{
                                                    'approver_dpt':state_dpt[state],
                                                    'approver_name':False,
                                                    'approver_time':False,
                                                    'approver_state':state, 
                                                    'approver_sel':'agree',
                                                    'if_alter_amount':False,
                                                    'approver_note':False,
                                                })
                                
                    else:
                        if  state_list.index(state) < state_list.index(org_state):
                            if org_state not in lines_state:
                                for line in approver_lines:
                                    if line.approver_state == org_state:
                                        reapprover_obj.copy(cr,uid,line.id,{
                                                                        'approver_dpt':state_dpt[state],
                                                                        'approver_name':False,
                                                                        'approver_time':False,
                                                                        'approver_state':state, 
                                                                        'approver_sel':'agree',
                                                                        'if_alter_amount':False,
                                                                         'approver_note':False,
                                                                })
                        elif state_list.index(state) > state_list.index(org_state):
                            up_id=None
                            org_id=None
                            org_note=''
                            for line in approver_lines:
                              
                                if line.approver_state == org_state:
                                    org_id=line.id
                                elif line.approver_state == state:
                                    up_id=line.id
                           
                            if org_id:
                                org_rec=reapprover_obj.browse(cr,uid,org_id)
                                if org_rec.if_alter_amount:
                                    for  org_line in org_rec.reward_lines_id.reward_lines_info_ids:
                                        if org_line.name and org_line.if_alter_amount:
                                            org_note+="reward people name:%s ; suggest reward amount: %s ;\n"%(org_line.name.name,org_line.reality_reward_amount)
                                if org_note:
                                    org_note+='  approver_name:%s ; approver_time:%s; \n'%(user_obj.browse(cr,uid,uid).name,ap_time)
                                if org_rec.alter_note:
                                    org_note=org_rec.alter_note+org_note
                                reapprover_obj.write(cr,uid,org_id,{'approver_name':ap_info[0],'approver_time':ap_info[1],'alter_note':org_note})   
                                
                                rem_idea=[idea[1][0] for idea in state_idea.values() if idea[1][0] != state_idea[org_state][1][0] ]
                              
                                rem_list=rem_idea+['approver_dpt','approver_name',
                                                    'approver_time','approver_sel',
                                                    'reward_lines_id','approver_state', 'approver_note',
                                                    'reward_state','if_alter_amount','if_wapprover']
                                rec=reapprover_obj.read(cr,uid,org_id,)
                                for key in rem_list:
                                    del rec[key]
                                line_dic=rec
                           
                            reapprover_obj.write(cr,uid,up_id,line_dic)                      
        return True
    
    def check_eng_question(self,cr,uid,ids,cre_pun=None,context=None):
        my=self.browse(cr,uid,ids[0])
        hr_obj=self.pool.get('hr.employee')
        reward_dic={'f_order_question':'订单中心','f_eng_question':'品质部'}
        rew_id=self.pool.get('punish.lines').search(cr,uid,[('reward_lines_id','=',ids[0])])
      
        if my.reward_type =='f_eng_question':
            if cre_pun:
                if not rew_id:
                    cr.execute(self._sql_info% (reward_dic[my.reward_type],my.dpt_id.company_id.name))
                    #manage_search=cr.fetchall()
                    manage_s=cr.fetchone()
                  
                    manage_id=manage_s and manage_s[0]
                    dpt_ser=self.pool.get('hr.department').search(cr,uid,[('dpt_code','=','E')])
                    
                    dpt_id=dpt_ser and dpt_ser[0]  
              
                    if manage_id:
                   
                        name=hr_obj.browse(cr,uid,manage_id).name
                        res_search=self.pool.get('res.users').search(cr,uid,[('name','=',name)])
                        punish_id=self.pool.get('punish.lines').create(cr,uid,{'applicant_id':res_search[0],'punish_type':'f_eng_question',
                                                                     'reward_lines_id':ids[0],'event_time':my.event_time,
                                                                     'event_site':my.event_site,
                                                                     'result_description':my.event_note,'product_description':my.product_description,
                                                                     'dpt_id':dpt_id})
                        if punish_id:
                            self.write(cr,uid,ids,{'punish_lines_id':punish_id})
                            self.pool.get('punish.lines').write(cr,uid,punish_id,{'state':'w_dpt_confirm'})
            return True
        else: 
            if my.reward_type=='f_order_question':
                if not rew_id:
                    order_dpt_ser=self.pool.get('hr.department').search(cr,uid,[('dpt_code','=','S03')])
                    #cr.execute(self._sql_info% (reward_dic[my.reward_type],my.name.company_id.name))
                    #manage_search=cr.fetchall()
                    #manage_s=cr.fetchone()
                    #manage_id=manage_s and manage_s[0]
                    #if manage_id:
                        #name=hr_obj.browse(cr,uid,manage_id).name
                        #res_search=self.pool.get('res.users').search(cr,uid,[('name','=',name)])
                    punish_ids=self.pool.get('punish.lines').create(cr,uid,{'applicant_id':my.applicant_id.id,'punish_type':'f_order_question',
                                                                                        'reward_lines_id':ids[0],'dpt_id':order_dpt_ser[0],
                                                                                        'event_time':my.event_time,
                                                                                        'event_site':my.event_site,
                                                                                        'result_description':my.event_note,'product_description':my.product_description,})
                    if punish_ids:
                            self.write(cr,uid,ids,{'punish_lines_id':punish_ids})

            return False
    
    def re_exist_position(self, cr, uid, ids,list_gp=None,b_type=None,context=None):
        my=self.browse(cr,uid,ids[0])
        dep_obj=self.pool.get('hr.department')
        user_obj=self.pool.get('res.users')
        gp_dic={}
        dpt_dic={}
        
        for key in ['user_jl','director_jl','supervisor_jl']:
            gp_dic[key]=[]
            if key == 'user_jl':
                res_id=my.applicant_id.id
                res_dptid = user_obj.browse(cr,uid,res_id).context_department_id.id
                print res_dptid,'res_dptid'        
                dpt_dic['user_jl']=[res_dptid]
            else:
                res_dptid =my.dpt_id.id 
                dpt_dic[key]=self.parent_dpt_search(cr,uid,ids,dpt_id=res_dptid)
            group_ids=self.pool.get('res.groups').search(cr,uid,[('name', '=', key)])
            if (group_ids):
              
                dpt_post_list=user_obj.search(cr,uid, [
                                    ('groups_id','=',group_ids[0]),
                                    ('context_department_id','=',res_dptid),                    
                ])
               
                dpt_temp=dpt_dic[key][:]
                dpt_temp.remove(res_dptid)
                
                if not dpt_post_list:
                    
                    for dptid in dpt_temp:
                        dpt_parent_list=user_obj.search(cr,uid, [
                                    ('groups_id','=',group_ids[0]),
                                    ('context_department_id','=',dptid),])
                        if dpt_parent_list:
                            gp_dic[key]=gp_dic[key]+dpt_parent_list
                       
                gp_dic[key]=gp_dic[key]+dpt_post_list
                
        gp_list=[gp_dic['user_jl'],gp_dic['director_jl'],gp_dic['supervisor_jl'],]
        dpt_list=dpt_dic['user_jl'] + dpt_dic['director_jl'] + dpt_dic['supervisor_jl']
        
        dpt_rec=self.pool.get('res.users').browse(cr,uid,uid).context_department_id
     
        u_dpt = self.pool.get('res.users').browse(cr,uid,uid).context_department_id.id
        dpt_code=self.pool.get('res.users').browse(cr,uid,uid).context_department_id.dpt_code
        rew_dpt=my.dpt_id.id 
        #rew_dpt=my.name.department_id.id 
        rewdpt_all=self.parent_dpt_search(cr,uid,ids,dpt_id=rew_dpt)
        
        print 'user dpt==>',u_dpt,'user all dpt ==>',dpt_list
        print 'user id ==>',uid,'user all id ==>',gp_list
        if list_gp[0]:
            if uid !=1:
                if u_dpt not in dpt_list:
                    raise osv.except_osv(('user department checking error!'),('please checking user department!'))
                if not gp_list[0]:
                    raise osv.except_osv(('user not in user_ji error!'),('please checking user_ji!'))
           
        self.check_reward_dpt(cr,uid,ids)
        
        flg=True
        for i in range(3):
            
            if list_gp[i] is None:
                pass
            else:
                if i==0:
                    if uid !=1:
                        if list_gp[0]:
                            if uid not in gp_list[0]:
                              
                                flg=False
                        else:
                            if uid in gp_list[0]:
                                flg=False
                else:
                    
                    if list_gp[i]:
                        if not dpt_list:
                           
                            flg=False 
                        else:
                            if uid==1 or list_gp[0]:
                                if not gp_list[i]:
                                   
                                    flg=False
                            else:
                                if not list_gp[0]:
                                    if dpt_rec.dpt_code not in ['A','E']:
                                        if u_dpt in rewdpt_all and dpt_code !='pwx':
                                            if not gp_list[i]:
                                                flg=False
                                        else:
                                            dpt_flg=dpt_code not in ['Q'] 
                                            if not gp_list[i] or uid not in gp_list[i] and dpt_flg:
                                                #raise osv.except_osv(('user department or reward approver groups error!'),('please checking user department or reward approver groups!'))
                                                flg=False
                                   
                    else:
                        if not dpt_list:
                            flg=False
                        else:
                            if uid==1 or list_gp[0]:
                                if gp_list[i]:
                                    flg=False
                            else:
                                if not list_gp[0]:
                                    if gp_list[i] and uid in gp_list[i]:
                                        flg=False
        print flg,'reward flg'
        return flg
    
    #===========================================================================
    # def re_exist_position(self, cr, uid, ids,list_gp=None,b_type=None,context=None):
    #    my=self.browse(cr,uid,ids[0])
    #    dep_obj=self.pool.get('hr.department')
    #    user_obj=self.pool.get('res.users')
    #    gp_dic={}
    #    dpt_dic={}
    #    
    #    
    #    for key in ['user_jl','director_jl','supervisor_jl']:
    #        gp_dic[key]=[]
    #        if key == 'user_jl':
    #            res_id=my.applicant_id.id
    #            res_dptid = user_obj.browse(cr,uid,res_id).context_department_id.id        
    #            dpt_dic['user_jl']=[res_dptid]
    #        else:
    #            res_dptid =my.dpt_id.id 
    #            #res_dptid =my.name.department_id.id 
    #            dpt_dic[key]=self.parent_dpt_search(cr,uid,ids,dpt_id=res_dptid)
    #        group_ids=self.pool.get('res.groups').search(cr,uid,[('name', '=', key)])
    #        if (group_ids):
    #          
    #            dpt_post_list=user_obj.search(cr,uid, [
    #                                ('groups_id','=',group_ids[0]),
    #                                ('context_department_id','=',res_dptid),                    
    #            ])
    #           
    #            dpt_temp=dpt_dic[key][:]
    #            dpt_temp.remove(res_dptid)
    #            
    #            if not dpt_post_list:
    #                
    #                for dptid in dpt_temp:
    #                    dpt_parent_list=user_obj.search(cr,uid, [
    #                                ('groups_id','=',group_ids[0]),
    #                                ('context_department_id','=',dptid),])
    #                    if dpt_parent_list:
    #                        gp_dic[key]=gp_dic[key]+dpt_parent_list
    #                   
    #            gp_dic[key]=gp_dic[key]+dpt_post_list
    #            
    #    gp_list=[gp_dic['user_jl'],gp_dic['director_jl'],gp_dic['supervisor_jl'],]
    #    dpt_list=dpt_dic['user_jl'] + dpt_dic['director_jl'] + dpt_dic['supervisor_jl']
    #    
    #    u_dpt = self.pool.get('res.users').browse(cr,uid,uid).context_department_id.id
    #    print 'user dpt==>',u_dpt,'user all dpt ==>',dpt_list
    #    print 'user id ==>',uid,'user all id ==>',gp_list
    #    if list_gp[0]:
    #        if uid !=1:
    #            if u_dpt not in dpt_list:
    #                raise osv.except_osv(('user department checking error!'),('please checking user department!'))
    #            if not gp_list[0]:
    #                raise osv.except_osv(('user not in user_ji error!'),('please checking user_ji!'))
    #       
    #    self.check_reward_dpt(cr,uid,ids)
    #    
    #    flg=True
    #    for i in range(3):
    #        
    #        if list_gp[i] is None:
    #            pass
    #        else:
    #            if i==0:
    #                if uid !=1:
    #                    if list_gp[0]:
    #                        if uid not in gp_list[0]:
    #                          
    #                            flg=False
    #                    else:
    #                        if uid in gp_list[0]:
    #                            flg=False
    #            else:
    #                
    #                if list_gp[i]:
    #                    if not dpt_list:
    #                       
    #                        flg=False 
    #                    else:
    #                        if uid==1 or list_gp[0]:
    #                            if not gp_list[i]:
    #                               
    #                                flg=False
    #                        else:
    #                            if not list_gp[0]:
    #                                if not gp_list[i] or uid not in gp_list[i]:
    #                                #raise osv.except_osv(('user department or reward approver groups error!'),('please checking user department or reward approver groups!'))
    #                                    flg=False
    #                               
    #                else:
    #                    if not dpt_list:
    #                        flg=False
    #                    else:
    #                        if uid==1 or list_gp[0]:
    #                            if gp_list[i]:
    #                                flg=False
    #                        else:
    #                            if not list_gp[0]:
    #                                if gp_list[i] and uid in gp_list[i]:
    #                                    flg=False
    #   
    #    return flg
    # 
    #===========================================================================
    def check_reward_dpt(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        user_obj=self.pool.get('res.users')
        redpt_id=my.dpt_id.id
        #redpt_id=my.name.department_id.id
        reward_dpt=self.parent_dpt_search(cr,uid,ids,dpt_id=redpt_id)
        key=['director_jl','supervisor_jl']
        gp_dic={}
        for  k in key:
            group_ids=self.pool.get('res.groups').search(cr,uid,[('name','=',k)])
            gp_dic[k]=group_ids
        flg=False
        for dptid in reward_dpt:
            for k in key:
               
                user_ser=user_obj.search(cr,uid, [
                                    ('groups_id','=',gp_dic[k][0]),
                                    ('context_department_id','=',dptid),])
                if user_ser:
                    flg=True
        if not flg:
            raise osv.except_osv(('reward department not found director or supervisor !'),('please checking reward department of groups!'))
        else:
            return flg
        
    def action_update_lines(self,cr,uid,context=None):
        app_obj=self.pool.get('reward.approver.lines')
        state_idea={'w_dpt_director':'responsible_idea',
                    'w_director':'dpt_director_idea',
                    'w_quality_manager':'quality_manager_idea',
                    'w_personnel':'personnel_idea',
                    'w_gmanager':'gmanager_idea',
                   }
        re_ids=self.search(cr,uid,[])
        for re_id in re_ids:
            my=self.browse(cr,uid,re_id)
            
            app_lines=my.reward_approver_lines_ids
            if app_lines:
                for line in app_lines:
                    if line.approver_state in state_idea.keys():
                        f_idea=state_idea[line.approver_state]
                        app_idea=app_obj.read(cr,uid,line.id,[f_idea])[f_idea]
                        app_obj.write(cr,uid,line.id,{'approver_note':app_idea})
        return True
reward_lines()

class punish_lines(osv.osv):
    _inherit='reward.punish'
    _name='punish.lines'
    _order='create_date desc'
    _rec_name='punish_number'
    pu_list=('replenish','scrap_residual','delivery_delay','customer_complain','inspect_violation','f_eng_question','f_order_question','tech_energy_question','personnel_inspect','other')
    _pu_type=[(i,i.title()) for i in pu_list]
    punish_state=('draft','w_dpt_confirm','w_responsible','top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','w_punish','done','cancel')
    _state_list=[(i,i.title()) for i in punish_state]
    _app_list=[(i,i) for i in ('agree','disagree')]
    
    def get_responsible_id(self,cr,uid,ids=False,context=None):
        wkf_server=netsvc.LocalService('workflow')
        he_obj=self.pool.get('hr.employee')
        punish_dic={'f_order_question':'','f_eng_question':''}
        if not context:
            context={}
        act_ids=self.search(cr,uid,[('state','=','w_dpt_confirm')])
 
        for  act_id in act_ids:
            my=self.browse(cr,uid,act_id)
            cur_time=datetime.now()
            
            name=not my.applicant_id and '' or my.applicant_id.company_id.name#
            #cr.execute(self._sql_info% (punish_dic[my.punish_type],name))
            #emp_s=cr.fetchone()
            if my.dpt_id:
                dpt_parent_one=my.dpt_id.parent_id and my.dpt_id.parent_id.id
                dpt_parent_two=my.dpt_id.parent_id.parent_id and my.dpt_id.parent_id.parent_id.id
                group_ser=self.pool.get('res.groups').search(cr,uid,[('name','=','director_cf')])
                group_sup=self.pool.get('res.groups').search(cr,uid,[('name','=','supervisor_cf')])
                gp_id=False
                if group_ser:
                    gp_id=group_ser[0]
                elif group_sup:
                    gp_id=group_sup[0]
                    
                user_ser_cur=self.pool.get('res.users').search(cr,uid, [
                                ('groups_id','=',gp_id),
                                ('context_department_id','=',my.dpt_id.id,)])
                
                user_ser_one=self.pool.get('res.users').search(cr,uid, [
                                ('groups_id','=',gp_id),
                                ('context_department_id','=',dpt_parent_one,)])
                
                user_ser_two=self.pool.get('res.users').search(cr,uid, [
                                ('groups_id','=',gp_id),
                                ('context_department_id','=',dpt_parent_two,)])
                for user_ser in [user_ser_cur,user_ser_one,user_ser_two]:
                    if user_ser:
                        emp_s=he_obj.search(cr,uid,[('user_id','=',user_ser[0])])
                        emp_id=emp_s and emp_s[0]
                        return_date=None
                        cre_date=None
                        if emp_id:
                            dpt_name=he_obj.browse(cr,uid,emp_id).department_id.name
                            he_rec=he_obj.browse(cr,uid,emp_id)
                            if he_rec.job_number == '2003':
                                emp_sea=he_obj.search(cr,uid,[('job_number','=','16')])
                                emp_id=emp_sea and emp_sea[0]
                                
                            name=he_obj.browse(cr,uid,emp_id).name
                            print ' dpt responsible_id info:department:%s  name:%s' %(dpt_name,name)
                        if my.return_time:
                            return_date=datetime.strptime(my.return_time,'%Y-%m-%d %H:%M:%S')
                        if my.create_date:
                            create_date=datetime.strptime(my.create_date,'%Y-%m-%d %H:%M:%S')
                            
                            #create_date=datetime.strptime('2013-04-18 00:00:00','%Y-%m-%d %H:%M:%S')
                            if return_date:
                                cre_date=return_date
                            else:
                                cre_date=create_date
                            if cur_time > cre_date:
                                if (cur_time - cre_date).days > 3:
                                    data=[(5,),(0,0,{'name':emp_id})]
                                    self.write(cr,uid,act_id,{'punish_lines_info_ids':data})
                                    wkf_server.trg_validate(uid,'punish.lines',act_id,'button_approver',cr)
            
        return True
    
    #===========================================================================
    # def check_punish_amount(self,cr,uid,ids,context=None):
    #    my=self.browse(cr,uid,ids[0])
    #    lines_ids=my.punish_lines_info_ids 
    # 
    #    lines_amount=0.0
    #    if lines_ids:
    #       
    #        for line in lines_ids:
    #            lines_amount+=line.compensate_amount 
    #        
    #        if lines_amount <= my.total_amount or my.dpt_id.dpt_code=='E':
    #            return True
    #        else:
    #            return False
    #    return True
    #===========================================================================
    
    def check_punish_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_ids=my.punish_lines_info_ids 
        
        lines_amount=0.0
        if lines_ids:
        
            for line in lines_ids:
                lines_amount+=line.reality_punish_amount 
            if not my.punish_clause_amount:
                if lines_amount <= my.total_amount  or my.dpt_id.dpt_code=='E':
                    return True
                else:
                    return False
                
            elif lines_amount <= my.punish_clause_amount or my.dpt_id.dpt_code=='E':
         
                return True
            else:
                return False
        return True
    
   
    
    def check_punish_lines(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_ids=my.punish_lines_info_ids
        if my.state =='w_responsible':
            if lines_ids:
                return True
            else:
                return False
        else:
            return True
        

            
    
    
    
    
    
    def check_punish_config(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        if my.punish_config:
            if my.punish_config.category_id:
                if my.punish_config.category_id.id != my.punish_category_id.id:
                    return False
                else:
                    return True
            else:
                return False
            
    def check_director_sel(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        app_lines=my.punish_approver_lines_ids
        director_sel=None
        if app_lines:
            for line in app_lines:
                if line.approver_state == 'w_director':
                    director_sel=line.approver_sel
        if director_sel =='agree':
            return True
        else:
            return False 
        
#     若品质经理不同意，则行政部反审批直接反到部门主管！         
    def check_quality_manager_sel(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        app_lines=my.punish_approver_lines_ids
        director_sel=None
        if app_lines:
            for line in app_lines:
                if line.approver_state == 'w_dpt_manager':
                    director_sel=line.approver_sel
        if director_sel =='agree':
            return True
        else:
            return False 
     
     
        
        
        
    def _info_get(self,cr,uid,ids,field_name,args,context=None):
       
        line_obj=self.pool.get('punish.lines.info')
        res={}
        for id in ids:
            my=self.browse(cr,uid,id)
            lines_rec=my.punish_lines_info_ids
            app_rec=my.punish_approver_lines_ids
            lines_number=[]
            lines_name=[]
            lines_info=False
            l_names=False
           
            if lines_rec:
                for line in lines_rec:
                    if line.name:
                        lines_number.append(line.name.job_number)
                        lines_name.append(line.name.name)
                   
                if lines_number and lines_name:
                    lines_info=','.join(lines_number)+':'+','.join(lines_name)
                    l_names=','.join(lines_name)
           
               
            if field_name=='is_responsible':
                lines_rec=my.punish_lines_info_ids
                user_obj=self.pool.get('res.users')
                user_rec=user_obj.browse(cr,uid,uid)
                u_dpt=user_rec.context_department_id
                
                if lines_rec:
                    for line in lines_rec:
                        if uid==1:
                            line_obj.write(cr,uid,line.id,{'is_responsible':True})
                        else:
                            if line.name:
                                u_flg=u_dpt.dpt_code =='E' and user_rec.login == '16' and line.name.department_id.dpt_code =='E'
                                #if uid == line.name.user_id.id:
                                if uid == line.name.user_id.id or u_flg:
                                    line_obj.write(cr,uid,line.id,{'is_responsible':True})
                                    #res[id]=True
                            else:
                                line_obj.write(cr,uid,line.id,{'is_responsible':False})
                                #res[id]=False
            elif field_name=='responsible_info':
                res[id]=lines_info
            elif field_name=='responsible_name':
                res[id]=l_names  
            #===================================================================
            # elif field_name=='approver_sel':
            #    app_sel=False
            #    if app_rec:
            #        for line in app_rec:
            #            if line.approver_state=='w_director':
            #                print line.approver_state
            #                app_sel=line.approver_sel
            #    res[id]=app_sel
            #===================================================================
        return res
    
    def _responsible_search(self,cr,uid,ids,field_name,args,context=None):
      
        res_ids=[]
        resp_ser=self.search(cr,uid,[])
        s=args[0][2]
        
        for resp_id in resp_ser:
            my=self.browse(cr,uid,resp_id)
            lines_number=None
            lines_name=None
            if my.responsible_info:
                lines_number,lines_name=my.responsible_info.split(':')
                numbers=lines_number.split(',')
                names=lines_name.split(',')
             
                if s in numbers or s in names:
                    res_ids.append(resp_id)
      
        return [('id','in',res_ids)]
    
    def _pun_info_get(self,cr,uid,ids,fields_name,args,context=None):
        return self._repu_info_get(cr, uid, ids, fields_name, args, context)
     
    
    _columns={
              'punish_number':fields.char('punish_number',size=32,required=True,select=True),#处罚单号
              'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id',),#工序
              'name':   fields.many2one('hr.employee','punish name',select=True),#被处罚人姓名
              'applicant_id':fields.many2one('res.users','applicant_id',required=True),#申请人
              'dpt_id':fields.many2one('hr.department','dpt_id',select=True,required=True),
              'punish_lines_info_ids':fields.one2many('punish.lines.info','punish_lines_id','punsih_lines_info_ids',), 
              'reward_lines_id':fields.many2one('reward.lines','reward_lines_id'),
              'punish_type':fields.selection(_pu_type,'punish_type',select=True),
              'punish_category_id':fields.many2one('reward.punish.category','punish_type',change_default=True),
              'punish_config':fields.many2one('reward.punish.config','punish clause',domain=[('type','=','punish')]),
              'result_economic_losses':fields.boolean('result_economic_losses'),#造成经济损失
              'not_result_losses':fields.boolean('not_result_economic_losses'),#未造成经济损失
              'result_description':fields.text('result_description'),
              'if_economic_compensate':fields.boolean('if_economic_compensate'),#是否经济赔偿
              'if_personnel_punish':fields.boolean('if_personnel_punish'),
              'uncheck_one':fields.boolean('uncheck_one'),#免检1
              'uncheck_two':fields.boolean('uncheck_two'),#免检2
              'uncheck_three':fields.boolean('uncheck_three'),#免检3
              'mistake_one':fields.boolean('mistake_one'),#差错类1
              'mistake_two':fields.boolean('mistake_two'),#差错类2
              'mistake_three':fields.boolean('mistake_three'),#差错类3
              'reproduction':fields.boolean('reprodcution'),#复投
              'punish_description':fields.char('punish_description',size=128),
              'total_amount':fields.float('compensate_total_amount',digits_compute=dp.get_precision('Account')),#赔偿金额
              'punish_clause':fields.related('punish_config','description',type='text',string='punish_clause',readonly=True),    
            
              'punish_clause_amount':fields.related('punish_config','amount',type='float',relation='reward.punish.config',string='punish_clause_amount',readonly=True),
              'responsible_id':fields.many2one('res.users','responsible_id'),
              
              'top_responsible_idea':fields.text('process_idea'),#工序负责人意见
              'top_responsible_sel':fields.selection([('agree','agree'),('disagree','disagree'),('not_have','not_have')],'top_responsible_sel',),
              
              'state':fields.selection(_state_list,'state',readonly=True,size=32,select=True),
              'is_responsible':fields.function(_info_get,method=True,type='boolean',string='is_responsible'),
              'is_wapprover':fields.function(_pun_info_get,method=True,type='boolean',string='is_wapprover',select=True),
              'punish_approver_lines_ids':fields.one2many('punish.approver.lines','punish_lines_id','punish_approver_lines_ids'),
              'responsible_info':fields.function(_info_get,fnct_search=_responsible_search,method=True,type='char',size=256,string='responsible'),
              'org_punish_number':fields.char('org_punish_number',size=64),
              'responsible_name':fields.function(_info_get,method=True,type='char',size=256,string='responsible'),
              'make_name':fields.char('make_name',size=256),
              'review_name':fields.char('review_name',size=256),
              'sequence':fields.char('sequence',size=32),
              'return_time':fields.datetime('return_time'),
              'approver_sel':fields.function(_info_get,method=True,type='selection',selection=_app_list,string='approver_sel',select=True),
    }
    
    _defaults={
               'punish_number':lambda self,cr,uid,context:self.pool.get('ir.sequence').get(cr,uid,'punish.lines'),
               'type': lambda *a:'punish',
               'state':lambda *a:'draft',
               'applicant_id':lambda self,cr,uid,context:uid,
                #'create_time':lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    _constraints=[#(check_punish_amount,"All punish line amount must be <= punish_clause_amount!",['punish_lines_info_ids']), ]
                              #(check_punish_config,'Clause error: Punish clause not found in punish category',['punish_config']) ,
                              (check_punish_lines,"punish lines error: punish lines not found in 'w_responsible' state!, please create... ",['state'])
                              ]
                   
    def updata_state(self,cr,uid,ids,state=None,button_type=None,context=None):
        my=self.browse(cr,uid,ids[0])
        org_state=my.state
        self.check_approver_sel(cr,uid,ids)
        self.write(cr,uid,ids,{'state':state})
        self.action_updata_state(cr,uid,ids,state=state,org_state=org_state,button_type=button_type,context=context)
        return True
        
    def action_updata_state(self,cr,uid,ids,state=None,org_state=None,button_type=None,context=None):
        my=self.browse(cr,uid,ids[0])
        user_obj=self.pool.get('res.users')
      
     
        dpt_rec=user_obj.browse(cr,uid,uid).context_department_id
        dpt_name=uid==1 and 'admin' or dpt_rec.name
        ap_time=time.strftime('%Y-%m-%d %H:%M:%S')
     
        ap_info=[uid,ap_time]
        lines_info=my.punish_lines_info_ids
        approver_lines=my.punish_approver_lines_ids
        
        wkf_ser=netsvc.LocalService('workflow')
        puapprover_obj=self.pool.get('punish.approver.lines')
        dpt_obj=self.pool.get('hr.department')
      
        human_ser=dpt_obj.search(cr,uid,[('dpt_code','=','A')])[0]
        gmg_ser=dpt_obj.search(cr,uid,[('dpt_code','=','G')])[0]
        pu_dpt=my.dpt_id.id
        ap_dpt=False
        if uid !=1:
            ap_dpt=my.applicant_id.context_department_id.id
        
        state_dpt={'top_responsible':pu_dpt,'w_director':pu_dpt,'w_dpt_manager':ap_dpt,
                            'w_personnel':human_ser,'w_gmanager':gmg_ser,'done':''}
        
        state_list=['w_dpt_confirm','w_responsible','top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','done']
        
        state_idea={'top_responsible':[['top_responsible_amount','top_responsible_idea'],['top_responsible_idea']],
                    'w_director':[['top_responsible_amount','top_responsible_idea'],['director_idea']],
                    'w_dpt_manager':[['director_amount','director_idea','top_responsible_idea'],['responsible_director_idea']],
                    'w_personnel':[['responsible_dpt_amount','responsible_director_idea','director_idea','top_responsible_idea'],['personnel_idea']],
                    'w_gmanager':[['personnel_amount','personnel_idea','director_idea','top_responsible_idea','responsible_director_idea'],['gmanager_idea']],
                   }
        
        if state in state_dpt:
            if not approver_lines:
                puapprover_obj.create(cr,uid,{
                                                                        'approver_dpt':state_dpt[state],
                                                                        'punish_lines_id':ids[0],
                                                                        'approver_state':state,
                                                                       'approver_sel':'agree',
                                                                       
                                                                })
            else:
                lines_state=[line.approver_state for line in approver_lines]
                lines_state=lines_state+['done']
                amount=None
                idea=None
                line_dic={}
                if state in state_dpt:
                    if state not in lines_state:
                        for line in approver_lines:
                            if line.approver_state == org_state:
                                suggest_note=''
                                if line.if_alter_amount:
                                    for  line_info in line.punish_lines_id.punish_lines_info_ids:
                                        if line_info.name:
                                            suggest_note+="punish people name:%s ; suggest  punish amount: %s ;\n"%(line_info.name.name,line_info.reality_punish_amount)
                                if suggest_note:
                                    suggest_note+='  approver_name:%s ;approver_time: %s \n'%(user_obj.browse(cr,uid,uid).name,ap_time)
                                if line.alter_note:
                                    suggest_note=line.alter_note+suggest_note
                                puapprover_obj.write(cr,uid,line.id,{'approver_name':ap_info[0],'approver_time':ap_info[1],'alter_note':suggest_note,})   
                                
                                puapprover_obj.copy(cr,uid,line.id,{
                                                    'approver_dpt':state_dpt[state],
                                                    'approver_name':False,
                                                    'approver_time':False,
                                                    'approver_state':state, 
                                                    'approver_sel':'agree',
                                                    'if_alter_amount':False,
                                                    'approver_note':False,
                                                })
                       
                                
                            
                    else:
                        if  state_list.index(state) < state_list.index(org_state):
                            if org_state not in lines_state:
                                for line in approver_lines:
                                    if line.approver_state == org_state:
                                        puapprover_obj.copy(cr,uid,line.id,{
                                                                        'approver_dpt':state_dpt[state],
                                                                        'approver_name':False,
                                                                        'approver_time':False,
                                                                        'approver_state':state, 
                                                                        'approver_sel':'agree',
                                                                        'if_alter_amount':False,
                                                                        'approver_note':False,
                                                                       
                                                                })
                        elif state_list.index(state) > state_list.index(org_state):
                            up_id=None
                            org_id=None
                            org_note=''
                            
                            for line in approver_lines:
                                if line.approver_state == org_state:
                                    org_id=line.id
                                elif line.approver_state == state:
                                    up_id=line.id
                           
                            if org_id:
                                org_rec=puapprover_obj.browse(cr,uid,org_id)
                                if org_rec.if_alter_amount:
                                    for  org_line in org_rec.punish_lines_id.punish_lines_info_ids:
                                        if org_line.name:
                                            org_note+="punish people name:%s ; suggest  punish amount: %s ;\n"%(org_line.name.name,org_line.reality_punish_amount)
                                if org_note:
                                    org_note+='  approver_name:%s ; approver_time:%s; \n'%(user_obj.browse(cr,uid,uid).name,ap_time)
                                if org_rec.alter_note:
                                    org_note=org_rec.alter_note+org_note
                                puapprover_obj.write(cr,uid,org_id,{'approver_name':ap_info[0],'approver_time':ap_info[1],'alter_note':org_note})   
                                
                                rem_idea=[idea[1][0] for idea in state_idea.values() if idea[1][0] != state_idea[org_state][1][0] ]
                              
                                rem_list=rem_idea+['approver_dpt','approver_name',
                                                    'approver_time','approver_sel',
                                                    'punish_lines_id','approver_state','approver_note',
                                                    'punish_state','if_alter_amount','if_wapprover']
                                rec=puapprover_obj.read(cr,uid,org_id,)
                                for key in rem_list:
                                    del rec[key]
                                line_dic=rec
                          
                            puapprover_obj.write(cr,uid,up_id,line_dic)                        
                            
        if state in ['w_dpt_confirm','w_responsible','draft','done']:
           
            if state == 'w_responsible':
                flg=True
                make_name=None
                review_name=None
                if lines_info:
                    for line in lines_info:
                         ##updata:make,reviewer
                        if line.name:
                            if line.responsible_des =='make':
                                make_name=line.name.name
                            else:
                                review_name=line.name.name
                        
                        if not line.name and line.without_responsible=='have':
                            flg=False
                    if flg:
                        for line in lines_info:
                            wkf_ser.trg_validate(uid,'punish.lines.info',line.id,'button_approver',cr)
                    else:
                        raise osv.except_osv(('lines name error'),('line name must be not null!'))
                else:
                    raise osv.except_osv(('punish lines not found error!'),('please create punish lines info!'))
            
                print make_name,review_name,
                self.write(cr,uid,ids,{'make_name':make_name,'review_name':review_name})
            
            elif state =='w_dpt_confirm' and button_type=='return':
                self.write(cr,uid,ids,{'return_time':time.strftime('%Y-%m-%d %H:%M:%S')})
                if lines_info:
                    for line in lines_info:
                        wkf_ser.trg_validate(uid,'punish.lines.info',line.id,'button_return',cr)
                        wkf_ser.trg_validate(uid,'punish.lines.info',line.id,'button_return',cr)
         
            
            elif state =='done':
                self.write(cr,uid,ids,{'finish_date':time.strftime('%Y-%m-%d')})
            #    if lines_info:
            #        for line in lines_info:
            #            wkf_ser.trg_validate(uid,'punish.lines.info',line.id,'button_approver',cr)
        return True
    
    #===========================================================================
    # def pu_exist_position(self, cr, uid, ids,position=None,context=None):
    #    my=self.browse(cr,uid,ids[0])
    #    dep_obj=self.pool.get('hr.department')
    #    user_obj=self.pool.get('res.users')
    #    
    #    if (not position):
    #        raise TypeError('argument position cant be None')
    #    u_dpt = self.pool.get('res.users').browse(cr,uid,uid).context_department_id.id
    #    dpt_list=[]
    #    if uid == 1:
    #        return True
    #    else:
    #        if position in ['user_cf','manager_cf']:
    #            if my.applicant_id.context_department_id:
    #                res_dptid=my.applicant_id.context_department_id.id
    #                dpt_list.append(res_dptid)
    #            if position =='user_cf':
    #                dpt_list.append(my.dpt_id.id)
    #        else:
    #            if my.dpt_id:
    #                res_dptid=my.dpt_id.id
    #                dpt_list=self.parent_dpt_search(cr,uid,ids,dpt_id=res_dptid)
    #    group_ids=self.pool.get('res.groups').search(cr,uid,[('name', '=', position)])
    #    
    #    if (group_ids):
    #        
    #      
    #        dpt_post_list=user_obj.search(cr,uid, [
    #                            ('groups_id','=',group_ids[0]),
    #                            ('context_department_id','=',res_dptid),                    
    #        ])
    #        if (dpt_post_list):
    #            if u_dpt in dpt_list:
    #                return True
    #            else:
    #                raise osv.except_osv(('user department error!'),('user department not in punish department,please check'))
    #                return False
    #        
    #        else:
    #            dpt_temp=dpt_list[:]
    #            dpt_temp.remove(res_dptid)
    #        
    #            flg=False
    #          
    #            for dptid in dpt_temp:
    #                user_ser=user_obj.search(cr,uid, [
    #                            ('groups_id','=',group_ids[0]),
    #                            ('context_department_id','=',dptid),                    
    #                            ])
    #               
    #                if user_ser:
    #                    if u_dpt in dpt_list:
    #                        flg=True
    #                        break
    #                else:
    #                    raise osv.except_osv(('user not in groups error!'),('user not found in %s groups ,please check!')%position)
    #           
    #            if flg:
    #                return flg
    #            else:
    #                raise osv.except_osv(('department error!'),('user department not found ,please check!'))
    #                
    #===========================================================================
    
    def pu_exist_position(self, cr, uid, ids,position=None,context=None):
        my=self.browse(cr,uid,ids[0])
        dep_obj=self.pool.get('hr.department')
        user_obj=self.pool.get('res.users')
        
        if (not position):
            raise TypeError('argument position cant be None')
        u_dpt = self.pool.get('res.users').browse(cr,uid,uid).context_department_id.id
        dpt_list=[]
        if uid == 1:
            return True
        else:
            if position in ['user_cf','manager_cf']:
                if my.applicant_id.context_department_id:
                    res_dptid=my.applicant_id.context_department_id.id
                    dpt_list.append(res_dptid)
                if position =='user_cf':
                    dpt_list.append(my.dpt_id.id)
            else:
                if my.dpt_id:
                    res_dptid=my.dpt_id.id
                    dpt_list=self.parent_dpt_search(cr,uid,ids,dpt_id=res_dptid)
        group_ids=self.pool.get('res.groups').search(cr,uid,[('name', '=', position)])
        
        if (group_ids):
            
          
            dpt_post_list=user_obj.search(cr,uid, [
                                ('groups_id','=',group_ids[0]),
            ])
            if (dpt_post_list):
                if u_dpt in dpt_list:
                    return True
                else:
                    raise osv.except_osv(('user department error!'),('user department not in punish department,please check'))
                    return False
            
            else:
                dpt_temp=dpt_list[:]
                dpt_temp.remove(res_dptid)
            
                flg=False
              
                for dptid in dpt_temp:
                    user_ser=user_obj.search(cr,uid, [
                                ('groups_id','=',group_ids[0]),
                                ('context_department_id','=',dptid),                    
                                ])
                   
                    if user_ser:
                        if u_dpt in dpt_list:
                            flg=True
                            break
                    else:
                        raise osv.except_osv(('user not in groups error!'),('user not found in %s groups ,please check!')%position)
               
                if flg:
                    return flg
                else:
                    raise osv.except_osv(('department error!'),('user department not found ,please check!'))
                                  
    def check_without_responsible(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_rec=my.punish_lines_info_ids
        if lines_rec:
            for line in lines_rec:
                if line.without_responsible == 'not_have':
                    if my.dpt_id.dpt_code !='E': 
                        if line.without_reason:
                            self.write(cr,uid,ids,{'top_responsible_sel':'not_have','top_responsible_idea':line.without_reason})
                            return True
                        else:
                            raise osv.except_osv(('without responsible reason error!'),('please explain withount responsible reason!')) 
                    elif my.dpt_id.dpt_code=='E' :
                        
                        return 'E'
                else:
                   
                    self.write(cr,uid,ids,{'top_responsible_sel':'agree','top_responsible_idea':'',})
                    return False 
      
    def check_line_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        lines_rec=my.punish_lines_info_ids
        if lines_rec:
            lines_amount=0.0
            for line in lines_rec:
                lines_amount+=line.reality_punish_amount
                #lines_amount+=line.compensate_amount
            #if lines_amount == my.total_amount:
            if not my.punish_clause_amount:
                if lines_amount <= my.total_amount:
                    return True
                else:
                    return False
                
            elif lines_amount <= my.punish_clause_amount:
                return True
            else:
                raise osv.except_osv(('line amount error!'),('lines all amount must be equal to total_amount or punish_clause_amount'))
                #raise osv.except_osv(('line amount error!'),('lines all amount must be equal to total_amount'))
                return False
            
    def action_update_lines(self,cr,uid,context=None):
        app_obj=self.pool.get('punish.approver.lines')
        state_idea={'top_responsible':'top_responsible_idea',
                    'w_director':'director_idea',
                    'w_dpt_manager':'responsible_director_idea',
                    'w_personnel':'personnel_idea',
                    'w_gmanager':'gmanager_idea',
                   }
        pu_ids=self.search(cr,uid,[])
        for pu_id in pu_ids:
            my=self.browse(cr,uid,pu_id)
            
            app_lines=my.punish_approver_lines_ids
            if app_lines:
                for line in app_lines:
                    if line.approver_state in state_idea.keys():
                        f_idea=state_idea[line.approver_state]
                        app_idea=app_obj.read(cr,uid,line.id,[f_idea])[f_idea]
                        app_obj.write(cr,uid,line.id,{'approver_note':app_idea})
        return True
    
punish_lines()

class punish_lines_info(osv.osv):
    _name='punish.lines.info'
    _order='create_date desc'
    _inherit='reward.punish'
    punish_line_state=('draft','w_dpt_confirm','w_responsible','top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','done','cancel')
    _state_list=[(i,i.title()) for i in punish_line_state]
    
    pu_list=('replenish','scrap_residual','delivery_delay','customer_complain','inspect_violation','f_eng_question','f_order_question','tech_energy_question','personnel_inspect','other')
    _pu_type=[(i,i.title()) for i in pu_list]
    def get_compensate_amount(self,cr,uid,context=None):
        act_id=context.get('punish_id',False)
        default_value=0.0
        if act_id:
            my=self.pool.get('punish.lines').browse(cr,uid,act_id)
            lines_rec=context.get('lines_ids',False)
           
            if lines_rec:
                line_amount=0.0
                for line in lines_rec:
                    if line[2]:
                        line_amount+=line[2]['compensate_amount']
                #default_value=my.total_amount - line_amount
                default_value=my.punish_clause_amount - line_amount
            else:
                #default_value=my.total_amount
                default_value=my.punish_clause_amount
        return default_value
    
    def _info_get(self,cr,uid,ids,field_name,agrs,context=None):
        app_obj=self.pool.get('punish.approver.lines')
        act_id=context.get('punish_id',False)
        res={}
        for id in ids:
            if act_id:
                my=self.pool.get('punish.lines').browse(cr,uid,act_id)
                lines_ids=[line.id for line in my.punish_approver_lines_ids if line.if_wapprover==True]
                
                if lines_ids:
                    if field_name=='edit_state':
                        if app_obj.browse(cr,uid,lines_ids[0]).if_alter_amount:
                        #if my.state in ['w_dpt_confirm','w_responsible','w_dpt_manager']:
                            res[ids[0]]=True
                        else:
                            res[ids[0]]=False
                else:
                    res[id]=False
            else:
                res[id]=False
            
        return res 
   
    def check_reality_punish_amount(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        dpt_code=None
        cur_dpt=my.punish_lines_id.dpt_id
        if cur_dpt:
            dpt_code=cur_dpt.dpt_code
        if my.without_responsible =='not_have':
            return True
        elif my.reality_punish_amount <= my.compensate_amount and my.without_responsible=='have':
            return True
        elif not my.compensate_amount and my.reality_punish_amount and my.without_responsible=='have' and dpt_code=='E':
            self.write(cr,uid,ids,{'compensate_amount':my.reality_punish_amount})
            return True
        else:
            return False
       
    _columns={
            'punish_lines_id':fields.many2one('punish.lines','punish_lines_id',ondelete='cascade'),
            'name':   fields.many2one('hr.employee','punish name',select=True,),#姓名
            'is_responsible':fields.boolean('is_responsible'),
            'workcenter_id':fields.many2one('mrp.workcenter','workcenter_id',select=True),#工序
            'if_economic_compensate':fields.related('punish_lines_id','if_economic_compensate',type='boolean',string='if_economic_compensate',readonly=True),#是否经济赔偿
            'compensate_amount':fields.float('compensate_amount',digits_compute=dp.get_precision('Account'),states={'w_responsible':[('required',True)]}),#赔偿金额
            'reality_punish_amount':fields.float('reality_punish_amount',digits_compute=dp.get_precision('Account')),
            'state':fields.selection(_state_list,'state',readonly=True,select=True),
            'dpt_id':fields.related('punish_lines_id','dpt_id',type='many2one',relation='hr.department',string='dpt_id',change_default=True,select=True),
            'edit_state':fields.function(_info_get,method=True,type='boolean',string='edit_state'),
           
            'without_responsible':fields.selection([('have','have'),('not_have','not_have')],'without_responsible'),#是否有责任人
            'without_reason':fields.text('without_reason'),
            'punish_state':fields.selection([('have_punish','have_punish'),('not_have_punish','not_have_punish')],'punsih_state',select=True,readonly=True),
            'product_description':fields.related('punish_lines_id','product_description',type='char',string='product_description'),
            'result_description':fields.related('punish_lines_id','result_description',type='text',string='result_description'),
            'punish_type':fields.related('punish_lines_id','punish_type',type='selection',selection=_pu_type,string='punish_type'),
            'org_state':fields.related('punish_lines_id','state',type='selection',selection=_state_list,string='org punish state',size=32),
            'responsible_des':fields.selection([('make','make'),('review','review')],'responsible_des',),
            'if_have_reviewer':fields.selection([('have','have'),('exempt_check','exempt_check')],'if_have_reviewer',change_default=True),
            'applicant_id':fields.related('punish_lines_id','applicant_id',type='many2one',relation='res.users',string='applicant_id'),
            'finish_date':fields.related('punish_lines_id','finish_date',type='datetime',string='finish_date',readonly=True,select=True),
            'pu_create_date':fields.related('punish_lines_id','create_date',type='datetime',string='pu_create_date',select=True)
    }
    
    _constraints=[(check_reality_punish_amount,'Amount error:reality punish amount must be <= compensate amount ,please check!',['reality_punish_amount'])]
    
    _defaults={
               'responsible_sel':lambda *a:'agree',
                'if_have_reviewer':'have',
               'compensate_amount':lambda self,cr,uid,context:self.get_compensate_amount(cr,uid,context),
               'reality_amount':0.0,
               #'reality_amount':lambda self,cr,uid,context:self.get_compensate_amount(cr,uid,context),
               'without_responsible':lambda *a:'have',
               #'punish_state':lambda *a:'not_have_punish',
               'state':lambda *a:'draft',
             
    }
    def onchange_without_res(self,cr,uid,ids,field_value,context=None):
      
        if field_value =='not_have':
            return {'value':{'compensate_amount':0.0,'responsible_sel':'not_have'}}
        else:
            return {'value':{'without_responsible':'have','responsible_sel':'agree','without_reason':''}}
    
    def onchange_punish_name(self,cr,uid,ids,res_id,field_value,context=None):
        emp_obj=self.pool.get('hr.employee')
       
            
        if res_id:
            rec=emp_obj.browse(cr,uid,res_id)
            
            if rec.department_id:
                if rec.department_id.dpt_code=='E':
                    if rec.job_id:
                        if 'QAE' in rec.job_id.name and field_value=='have':
                            return {'value':{'responsible_des':'make'}}
                        elif field_value=='exempt_check':
                            return {'value':{'responsible_des':False}}
                        else:    
                            return {'value':{'responsible_des':'review'}}
                else:
                    return {'value':{'responsible_des':False}}
                
    def updata_line_state(self,cr,uid,ids,state=None,context=None):
        self.write(cr,uid,ids,{'state':state})
        my=self.browse(cr,uid,ids[0])
        flg=True
        line_ids=self.search(cr,uid,[('punish_lines_id','=',my.punish_lines_id.id)])
        for line in self.browse(cr,uid,line_ids):
            if line.state !='done':###w_punish
                flg=False
       
        if flg and state =='done':###w_punish
            
            wkf_ser=netsvc.LocalService('workflow')
            wkf_ser.trg_validate(uid,'punish.lines',my.punish_lines_id.id,'button_approver',cr)
        return True
    
    #===========================================================================
    # def check_have_punish(self,cr,uid,ids,context=None):
    #    my=self.browse(cr,uid,ids[0])
    #    if my.punish_state =='not_have_punish':
    #        self.write(cr,uid,ids,{'punish_state':'have_punish'})
    #    return True
    #===========================================================================
    
punish_lines_info()

class reward_lines_info(osv.osv):
        _name='reward.lines.info'
        _order='create_date desc'
        _inherit='reward.punish'
        re_list=('m_delivery','m_scrap_replenish','m_energy_standard','f_order_question','f_eng_question','fn_go_erp','personnel_reward','project_reward','other')
        _re_type=[(i,i.title()) for i in re_list]
        reward_state=('draft','w_director','w_dpt_director','w_quality_manager','w_personnel','w_gmanager','done','cancel')
        _state_list=[(i,i.title()) for i in reward_state]
        def get_reward_amount(self,cr,uid,context=None):
            act_id=context.get('reward_id',False)
            default_value=0.0
            if act_id:
                my=self.pool.get('reward.lines').browse(cr,uid,act_id)
                lines_rec=context.get('lines_ids',False)
               
                if lines_rec:
                    line_amount=0.0
                    for line in lines_rec:
                        if line[2]:
                            line_amount+=line[2]['reward_amount']
                    #default_value=my.total_amount - line_amount
                    if my.reward_amount:
                        default_value=my.reward_amount - line_amount
                    elif my.reward_clause_amount:
                        default_value=my.reward_clause_amount - line_amount
                else:
                    #default_value=my.total_amount
                    if my.reward_amount:
                        default_value=my.reward_amount
                    elif my.reward_clause_amount:
                        default_value=my.reward_clause_amount
            return default_value
                    
        def _info_get(self,cr,uid,ids,field_name,agrs,context=None):
            app_obj=self.pool.get('reward.approver.lines')
            act_id=context.get('reward_id',False)
            res={}
            for id in ids:
                if act_id:
                    my=self.pool.get('reward.lines').browse(cr,uid,act_id)
                    lines_ids=[line.id for line in my.reward_approver_lines_ids if line.if_wapprover==True]
                    info_ids=[line.id for line in my.reward_lines_info_ids]
                    if lines_ids:
                        #=======================================================
                        # if field_name=='edit_state':
                        #    
                        #    if app_obj.browse(cr,uid,lines_ids[0]).if_alter_amount:
                        #    #if my.state in ['w_responsible','w_director','w_dpt_manager','done']:
                        #        res[id]=True
                        #    else:
                        #        res[id]=False
                        #=======================================================
                        if field_name=='if_confirm':
                            
                            if my.state not in ['draft',]:
                                res[id]=True
                            else:
                                res[id]=False
                    else:
                        if field_name=='if_confirm':
                         
                            if self.browse(cr,uid,ids[0]).reward_state=='draft':
                                res[id]=False
                else:
                    if field_name=='if_confirm':
                        res[id]=True
                
            return res 
        
        def check_reality_reward_amount(self,cr,uid,ids,context=None):
            my=self.browse(cr,uid,ids[0])
            if my.reality_reward_amount <= my.reward_amount:
                return True
            else:
                return False
            
        def onchange_alter_amount(self,cr,uid,ids,field_value,res_id,context=None):
            my=None
            app_lines=None
            line_id=False
            app_obj=self.pool.get('reward.approver.lines')
            if res_id:
                my=self.pool.get('reward.lines').browse(cr,uid,res_id)
                app_lines=my.reward_approver_lines_ids
                if app_lines:
                    for line in app_lines:
                        if line.if_wapprover:
                            line_id=line.id
            if field_value:
                app_obj.write(cr,uid,line_id,{'if_alter_amount':True})
                return {'value':{'edit_state':True}}
            else:
                app_obj.write(cr,uid,line_id,{'if_alter_amount':False})
                return {'value':{'edit_state':False}}
        def check_amount(self,cr,uid,ids,context=None):
            my=self.browse(cr,uid,ids[0])
            if my.reward_amount<=30:
                return True 
            else:
                return False     
       
            
        _columns={
                    'reward_lines_id':fields.many2one('reward.lines','reward_lines_id',ondelete='cascade',select=True),
                    'product_description':fields.related('reward_lines_id','product_description',type='char',string='product_description',select=True),
                    'reward_type':fields.related('reward_lines_id','reward_type',type='selection',selection=_re_type,string='reward_type'),
                    'name':   fields.many2one('hr.employee','reward name',select=True),#姓名
                    'reward_amount':fields.float('reward_amount',digits_compute=dp.get_precision('Account')),
                    'reality_reward_amount':fields.float('reality_reward_amount',digits_compute=dp.get_precision('Account'),),
                    'reward_state':fields.related('reward_lines_id','state',type='selection',selection=_state_list,string='reward_state',size=32,select=True),
                    'edit_state':fields.function(_info_get,method=True,type='boolean',string='edit_state'),
                    'if_confirm':fields.function(_info_get,method=True,type='boolean',string='if_confirm'),
                    'event_note':fields.related('reward_lines_id','event_note',type='text',string='event_note'),
                    'applicant_id':fields.related('reward_lines_id','applicant_id',type='many2one',relation='res.users',string='applicant_id',select=True),
                    'reward_date':fields.related('reward_lines_id','create_date',type='datetime',string='reward_date',readonly=True,select=True),
                    'finish_date':fields.related('reward_lines_id','finish_date',type='datetime',string='finish_date',readonly=True,select=True),
                  }
        #_constraints=[(check_reality_reward_amount,'Amount error:reality reward amount must be <= reward amount ,please check!',['reality_reward_amount'])]
        
        _defaults={
                   'reward_amount':lambda self,cr,uid,context:self.get_reward_amount(cr,uid,context),
                   }
        _constraints=[(check_amount,'amount error: reward amount is not more than thirty !',['reward_amount'])]
reward_lines_info()

class punish_approver_lines(osv.osv):
        _name='punish.approver.lines'
        _inherit='reward.punish'
        approver_state=('top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','w_punish','done','cancel')
        _state_list=[(i,i.title()) for i in approver_state]
        
        def _info_get(self,cr,uid,ids,fields_name,agrs,context=None):
            res={}
            for id in ids:
                my=self.browse(cr,uid,id)
                if fields_name =='if_wapprover':
                    if my.approver_state=='done':
                        res[id]=False
                    else:
                        if my.approver_state == my.punish_state:
                            res[id]=True
                        else:
                                res[id]=False
            return res
        _columns={
                    'name':   fields.many2one('hr.employee','punish name',select=True,),#姓名
                    'punish_lines_id':fields.many2one('punish.lines'),
                    'approver_state':fields.selection(_state_list,'approver_state',readonly=True,select=True),
                    'punish_state':fields.related('punish_lines_id','state',type='char',string='punish_state',size=32),
                    'approver_dpt':fields.many2one('hr.department','approver_dpt'),
                    'if_wapprover':fields.function(_info_get,method=True,type='boolean',string='if_wapprover'),
                    'sequence':fields.integer('sequence'),
                    
                   
                  }
        _defaults={
               
                   }
               
punish_approver_lines()

class reward_approver_lines(osv.osv):
        _name='reward.approver.lines'
        _inherit='reward.punish'
        reward_state=('w_director','w_dpt_director','w_quality_manager','w_personnel','w_gmanager','done','cancel')
        _state_list=[(i,i.title()) for i in reward_state]
        
        def _info_get(self,cr,uid,ids,fields_name,agrs,context=None):
            res={}
            for id in ids:
                my=self.browse(cr,uid,id)
                if fields_name =='if_wapprover':
                    if my.approver_state=='done':
                        res[id]=False
                    else:
                        if my.approver_state == my.reward_state:
                            res[id]=True
                        else:
                                res[id]=False
            return res
        _columns={
                    'reward_lines_id':fields.many2one('reward.lines'),
                    'name':   fields.many2one('hr.employee','punish name',select=True,),#姓名
                    'approver_state':fields.selection(_state_list,'approver_state',readonly=True,select=True),
                    'reward_state':fields.related('reward_lines_id','state',type='char',string='reward_state',size=32),
                    'approver_dpt':fields.many2one('hr.department','approver_dpt'),
                    'if_wapprover':fields.function(_info_get,method=True,type='boolean',string='if_wapprover'),
                    'sequence':fields.integer('sequence'),
                  }
reward_approver_lines()