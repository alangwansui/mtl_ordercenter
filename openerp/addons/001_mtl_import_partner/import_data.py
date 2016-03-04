#usr/bin/python
# -*- coding:utf-8 -*-

from osv import  fields,osv
import time
import _mssql
import tools

import tempfile
import os
import xlrd
import re
import csv
from lxml import etree
import threading

class import_data(osv.osv):
    _name='import.data'
    _inherit='ir.model'
    tb_map={}
    w_untb=[]
    relat_info=[]
    iter_count=0
    def get_table_all(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        fp_all = file(r'c:\table_field.txt', 'w')
        
        if my.server and my.user and my.password:
            conn = _mssql.connect(server=my.server , user=my.user, password=my.password,database=my.database)            
            conn.execute_query(' select fieldname,displaylabel from TSFunctionFieldSet where functioncode=0102' ) 
            #fileno,filename=tempfile.mkstemp('.txt','Dosure_tableinfo_')
            #print fileno,filename
            i=0
            for row in conn:
                print row,'field'
                if row['fieldname']:
                    print >>fp_all,row['fieldname']+' ' *3+row['displaylabel']
        return [('','')]
    
    def import_reward(self,cr,uid,ids,context=None):
       
        rew_obj=self.pool.get('reward.lines')
        
        pun_obj=self.pool.get('punish.lines')++- 014
        dpt_obj=self.pool.get('hr.department')
        ##reward update:
        reward_ser=rew_obj.search(cr,uid,[])
        print reward_ser,'serrrrrrr'
     
        for res_id in reward_ser:
            rew_rec=rew_obj.read(cr,uid,res_id)
            my=rew_obj.browse(cr,uid,res_id)
          
            rew_name=my.name.id
            rew_amount=my.reward_amount
            rew_state=my.state
            ##not same field: dpt_id,
            ##new reward:reward.approver.lines.top_responsible_idea => org reward:responsible_idea
            ##new reward:reward.approver.lines.director_idea => org reward:dpt_director_idea
            ##new reward:reward:reward.approver.lines.agree_sel => 
            ## org responsible_sel,dpt_sel,quality_sel,personnel_sel,gmanager_sel
            
            ##new reward:reward:reward.approver.lines.reality_reward_amount => 
            ## org reward:responsible_amount,dpt_amount,quality_amount,personnel_amount,gmanager_amount
            
            qua_ser=dpt_obj.search(cr,uid,[('dpt_code','=','Q')])[0]
            human_ser=dpt_obj.search(cr,uid,[('dpt_code','=','A')])[0]
            gmg_ser=dpt_obj.search(cr,uid,[('dpt_code','=','G')])[0]
            dpt_id=False
            if my.name.department_id:
                dpt_id=my.name.department_id.id
                
            ap_dpt=[dpt_id,dpt_id,qua_ser,human_ser,gmg_ser]
            
            org_state=['w_dpt_director','w_director','w_quality_manager','w_personnel','w_gmanager','draft','done','cancel']
            org_sel=['responsible_sel','dpt_sel','quality_sel','personnel_sel','gmanager_sel']
            org_amount=['responsible_amount','dpt_amount','quality_amount','personnel_amount','gmanager_amount']
            org_idea=['responsible_idea','dpt_director_idea','quality_manager_idea','personnel_amount','gmanager_amount']
        
          
            info_dic={}
            ap_dic={}
            info_data=[(5,)]
            app_data=[(5,)]    
             
            index=None
            app_sel=None
            if rew_state not in ['draft']:
                if rew_state=='done':
                    if my.reward_amount >=50.0:
                        index=4
                        app_sel=rew_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                    else:
                         index=3
                         app_sel=rew_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                elif rew_state=='cancel':
                    index=0
                    app_sel='disagree'
                else:
                    index=org_state.index(rew_state)
                    app_sel=rew_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                app_idea=rew_obj.read(cr,uid,res_id,org_idea)
                app_idea.update({'approver_dpt':ap_dpt[index],'approver_state':rew_state,'approver_sel':app_sel,'reward_lines_id':res_id})
                
                ap_dic.update(app_idea)
                    
            if my.name:
                info_dic['name']=my.name.id
                info_dic['reward_amount']=my.reward_amount
                info_dic['reality_reward_amount']=my.reward_amount
                info_dic['reward_lines_id']=res_id
                
            info_data.append((0,0,info_dic))
            app_data.append((0,0,ap_dic))
            
            print dpt_id,'dpt',info_data,app_data
            ##update current record end
            rew_obj.write(cr,uid,res_id,{'dpt_id':dpt_id,'reward_lines_info_ids':info_data,'reward_approver_lines_ids':app_data})
              
        return True
    
      
    def import_punish(self,cr,uid,ids,context=None):
        rew_obj=self.pool.get('reward.lines')
        pun_obj=self.pool.get('punish.lines')
        dpt_obj=self.pool.get('hr.department')
        puninfo_obj=self.pool.get('punish.lines.info')
        ##punish update:
        punish_ser=pun_obj.search(cr,uid,[])
         
        for res_id in punish_ser:
        
            test_rec=pun_obj.read(cr,uid,res_id)
            my=pun_obj.browse(cr,uid,res_id)
            lines_info=my.punish_lines_info_ids
            pun_state=my.state
            ##not same field: dpt_id,
            ##new reward:reward.approver.lines.top_responsible_idea => org reward:responsible_idea
            ##new reward:reward.approver.lines.director_idea => org reward:dpt_director_idea
            ##new reward:reward:reward.approver.lines.agree_sel => 
            ## org responsible_sel,dpt_sel,quality_sel,personnel_sel,gmanager_sel
            
            ##new reward:reward:reward.approver.lines.reality_reward_amount => 
            ## org reward:responsible_amount,dpt_amount,quality_amount,personnel_amount,gmanager_amount
            
            qua_ser=dpt_obj.search(cr,uid,[('dpt_code','=','Q')])[0]
            human_ser=dpt_obj.search(cr,uid,[('dpt_code','=','A')])[0]
            gmg_ser=dpt_obj.search(cr,uid,[('dpt_code','=','G')])[0]
            
            ap_dpt=[my.dpt_id.id,my.dpt_id.id,qua_ser,human_ser,gmg_ser]
            
            org_state=['top_responsible','w_director','w_dpt_manager','w_personnel','w_gmanager','draft','done','cancel','w_dpt_confirm',]
            org_sel=['top_responsible_sel','director_sel','responsible_dpt_sel','personnel_sel','gmanager_sel']
            #org_amount=['responsible_amount','dpt_amount','quality_amount','personnel_amount','gmanager_amount']
            org_idea=['top_responsible_idea','director_idea','responsible_director_idea','personnel_idea','gmanager_idea']
            
            
            info_dic={}
            ap_dic={}
            info_data=[(5,)]
            app_data=[(5,)]    
            
            index=None
            app_sel=None
            if pun_state not in ['draft','w_dpt_confirm','w_responsible']:
                if pun_state =='done':
                    if my.total_amount >=50.0:
                        index=4
                        app_sel=pun_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                    else:
                        index=3
                        app_sel=pun_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                elif pun_state == 'cancel':
                    index=0
                    app_sel='disagree'
                else:
                    index=org_state.index(pun_state)
                    app_sel=pun_obj.read(cr,uid,res_id,[org_sel[index]])[org_sel[index]]
                app_idea=pun_obj.read(cr,uid,res_id,org_idea)
                app_idea.update({'approver_dpt':ap_dpt[index],'approver_state':pun_state,'approver_sel':'agree','punish_lines_id':res_id})
                
                ap_dic.update(app_idea)
            if ap_dic:
                app_data.append((0,0,ap_dic))
            
            if lines_info:
                for line in lines_info:
                    pun_amount=line.compensate_amount
                    puninfo_obj.write(cr,uid,line.id,{'reality_punish_amount':pun_amount})
                   
            ##update current record end
            flg=pun_obj.write(cr,uid,res_id,{'punish_approver_lines_ids':app_data,})
            if flg:
                print 'update success....'
        return True
           
    
    def import_department(self,cr,uid,ids,context=None):
    
        my=self.browse(cr,uid,ids[0])
        dpt_obj=self.pool.get('hr.department')
      
        book=xlrd.open_workbook(r'E:\import_data\department.xls')
        
        sheet=book.sheets()[0]
        ncols=sheet.ncols
        nrows=sheet.nrows
        dep_dic={
                 'G':['A','D','M','F','S','W','O'],
                 'M':['E','I','P','Q','T'],
                 'S':['S01','S02','S03']
                 }
      
        for line_number in range(0,nrows):
            row=sheet.row(line_number)
          
            lis=[cell.value for cell in row]
            (dpt_code,name,dpt_type,dpt_responsible,dpt_telephone,dpt_address,dpt_note)=lis[0:7] 
          
            dep_ids=dpt_obj.search(cr,uid,[])
            dpt_search=dpt_obj.search(cr,uid,[('dpt_code','=',dpt_code)])
            if not dpt_type:
                dpt_type=None
            else:
                dpt_type=str(int(dpt_type))
            if not dpt_search:
               
                dpt_id=dpt_obj.create(cr,uid,{
                       'dpt_code':dpt_code,
                       'name':name,
                       'dpt_responsible':None or dpt_responsible,
                       'dpt_telephone':None or dpt_telephone,
                       'dpt_address':None or dpt_address,
                       'dpt_type':dpt_type ,
                       'dpt_note':None or dpt_note,
                               })
            else:
                dpt_id=dpt_search[-1]
            if dpt_id:
                resp=dpt_obj.browse(cr,uid,dpt_id).dpt_responsible
                adres=dpt_obj.browse(cr,uid,dpt_id).dpt_address
                dp_type=dpt_obj.browse(cr,uid,dpt_id).dpt_type
                dp_note=dpt_obj.browse(cr,uid,dpt_id).dpt_note
                if not resp or not adres or not dp_type or not dp_note:
                    dpt_obj.write(cr,uid,dpt_id,{'dpt_responsible':dpt_responsible,'dpt_address':dpt_address,'dpt_type':dpt_type,'dpt_note':dpt_note,})
                if dpt_code == 'G':
                    continue    
                elif dpt_code in dep_dic['G']:
                    domain=[('dpt_code','=','G')]
                    
                elif dpt_code in dep_dic['M']:
                    domain=[('dpt_code','=','M')]
                elif dpt_code in dep_dic['S']:
                    domain=[('dpt_code','=','S')]
                elif dpt_code =='E01':
                    domain=[('dpt_code','=','Q')]
                else:
                    
                    if 'S01' in dpt_code:
                       domain=[('dpt_code','=','S01')]
                    else:
                        domain=[('dpt_code','=',dpt_code[0])] 
                parent_id=dpt_obj.search(cr,uid,domain) 
              
                if len(parent_id) >1:
                    parent_id=parent_id[-1]
                elif parent_id:
                    parent_id=parent_id[0]
                
                if parent_id:
                    dpt_obj.write(cr,uid,dpt_id,{'parent_id':parent_id})
                    
        return True
        
    def import_employee(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        f=open(r'E:\import_data\employee.txt','w')
        emp_obj=self.pool.get('hr.employee')
        dpt_obj=self.pool.get('hr.department')
        dpt_csv=open(r'E:\import_data\employee.csv')
        dpt_rec=csv.reader(dpt_csv)
        emp_file=file(r'e:\import_data\emp_id.txt')
        #book=xlrd.open_workbook(r'E:\import_data\employee.xls')
        #sheet=book.sheets()[0]
        #ncols=sheet.ncols
        #nrows=sheet.nrows
        
        def res_search(obj,cr,uid,obj_name,field,value,if_cre=None):
            res_obj=obj.pool.get(obj_name)
           
            if '长沙' in value:
                value='湖南'
            elif '湖南省' in value:
                value='湖南'
            elif '深圳' in value:
                value='广东'
            res_sear=res_obj.search(cr,uid,[(field,'ilike',value)])

            if res_sear:
                res_id=res_sear[0]
            else:
                if if_cre:
                    res_id=res_obj.create(cr,uid,{field:value})
                else:
                    res_id=None
            return res_id
        def convent_str(value):
            
            if not value:
                value=False
            return value
        #for line_number in range(1,nrows):
        #    row=sheet.row(line_number)
        #    line_list=[cell.value for cell in row]
        for line in dpt_rec:
            if dpt_rec.line_num ==1:
                continue
            else:
                emp_search=emp_obj.search(cr,uid,[('job_number','=',line[0])])
               
                if not emp_search:
                   print str(line[0]),line[1], 
                   emp_id=emp_obj.create(cr,uid,{
                           'job_number':str(line[0]),
                           'name':line[1],
                           'gender':line[2] =='男'  and 'male' or 'female',
                           'job_code':None or line[3],
                           'job_name':None or line[5],
                           'department_id':dpt_obj.search(cr,uid,[('name','=',line[6])])[0],
                           'job_id': res_search(self,cr,uid,'hr.job','name',line[7],True),
                           'culture_level':line[11],
                           'in_factory':convent_str(line[12]),
                           'home_telephone':line[13],
                           'mobile_phone':None or line[14],
                           'work_phone':None or str(line[15]),
                           #'identification_id':str(line[16]),
                           'home_address':line[17],
                           'identification_address':line[18],
                           'country_id':res_search(self,cr,uid,'res.country.state','name',line[19]),
                           'job_type':line[20] =='正式工' and 'regular' or 'not_regular',
                           'major':None or line[21],
                           'birthday':convent_str(line[28]),
                           'out_factory':convent_str(line[29]),
                           'notes':None or line[30],
                           'marital':line[31] =='已婚' and 2 or 1,
                           'contract_date_start':convent_str(line[32]),
                           'contract_data_end':convent_str(line[33]),
                           'deal_dpt_id':dpt_obj.search(cr,uid,[('dpt_code','=',line[34])])[0],
                           'if_yanglao_insure':line[35] == '是' and True or False,
                           'if_social_security':line[36] == '是' and True or False,
                           
                   })
                   
                   if emp_id:
                       print 'create emp_id sucess!'
        emp_list=emp_file.read().split('\n')
         
        for emp_info in emp_list:
            if emp_info:
                emp_sp=emp_info.split('\t')
              
                emp_search=emp_obj.search(cr,uid,[('name','=',str(emp_sp[0]))])
                if emp_search:
                    emp_obj.write(cr,uid,emp_search[0],{'identification_id':emp_sp[1]})
        return True   
    def test_sql(self,cr,uid,ids,context=None,sub_tb=[]):
        my=self.browse(cr,uid,ids[0])
        irm_obj=self.pool.get('ir.model')
        
        if my.w_untable:
            
            mtb_name=irm_obj.browse(cr,uid,my.w_untable.id).model

            m_tb=re.sub('\.','_',mtb_name)
         
            if not sub_tb:
                sub_tb=[]
                if self.w_untb:
                    self.w_untb=[]
                sub_tb.append(m_tb)
            for tb in sub_tb:
                print tb,'tbbb',cr.dbname
                cr.execute('''select constraint_name from information_schema.constraint_column_usage  
                                    where table_catalog='%s' and table_name='%s' '''% (tb,cr.dbname))
              
                #dic=cr.dictfetchall()
                info=[line[0] for  line in cr.fetchall() if 'pkey' not in line[0]]
                con_table=[]
                for constraints_name in info:
                    cr.execute('''select table_name from information_schema.table_constraints where constraint_name='%s' and constraint_type='FOREIGN KEY' '''% constraints_name)
                    tb_name=[cr.fetchone()]
                    tbl_name=[name for name in tb_name if name !=None]
                    if tbl_name:
                        con_table.append((tbl_name[0][0],constraints_name))
                for con in con_table:
                    if  m_tb in con:
                        del con_table[con_table.index(con)]
           
                w_ptable={}
                for ta in con_table:
                   
                    cr.execute('''select column_name from information_schema.key_column_usage where table_name='%s' and constraint_name='%s' '''%(ta[0],ta[1]))
                    f_name=[cr.fetchone()[0]]
             
                    ta_re=re.sub('_','.',ta[0])
                    ta_obj=self.pool.get(ta_re)
                    view_obj=self.pool.get('ir.ui.view')
                    view_ids=view_obj.search(cr,uid,[('model','=',ta_re),('type','=','form')])
                    
                    if ta_obj in self.pool.obj_pool.values():
                        ta_search=ta_obj.search(cr,uid,[(f_name[0],'!=',False)])
                        
                        if view_ids:
                            for view_rec in view_obj.browse(cr,uid,view_ids):
                    
                                tr=etree.XML(str(view_rec.arch))
                            
                                for n in tr.getiterator():
                                    if n.tag=='field':
                                        if n.attrib.get('name')==f_name[0]:
                                            if 'attrs' in n.attrib and ta_search:
                                                if  'required' in n.attrib.get('attrs'):
                                                    w_ptable[ta_obj._name]=(ta[0],ta[1])
                                                    if tb in self.tb_map:
                                                        self.tb_map[tb].append(ta[0])
                                                    else:
                                                        self.tb_map[tb]=[ta[0]]
                                            elif 'required' in n.attrib and ta_search:
                                                w_ptable[ta_obj._name]=(ta[0],ta[1])
                                                if tb in self.tb_map:
                                                        self.tb_map[tb].append(ta[0])
                                                else:
                                                        if tb != 'resource_resource':
                                                            self.tb_map[tb]=[ta[0]]
                        if f_name:
                            if f_name[0] in ta_obj._columns:
                                if ta_obj._columns[f_name[0]].required:
                                    if ta_search:
                                      
                                        if tb in self.tb_map:
                                                self.tb_map[tb].append(ta[0])
                                        else:
                                            if tb != 'resource_resource':
                                                self.tb_map[tb]=[ta[0]]
                                        w_ptable[ta_obj._name]=(ta[0],ta[1])
               
                print w_ptable,'w_patable',self.tb_map
               
                if w_ptable:
              
                    for key in w_ptable:
                        r_info=''
                        if tb=='res_users' and w_ptable[key][0]=='hr_employee':
                            flg=True
                            emp_ids=self.pool.get('hr.employee').search(cr,uid,[])
                            for emp in self.pool.get('hr.employee').browse(cr,uid,emp_ids):
                                if emp.resource_id.user_id:
                                    flg=False
                            if not flg:
                                r_info=key+' ' *8+w_ptable[key][0]+'\n'
                        elif w_ptable[key][0] =='resource_resource':
                                pass
                        if my.related_table_info:
                            new_info=my.related_table_info+'\n'+str(r_info)
                        else:
                            new_info=r_info
               
                        if new_info not in self.relat_info:
                            self.relat_info.append(new_info)
                    w_qutable=[val[0] for val in w_ptable.values()]
                    
                    if self.iter_count ==15:
                        break
                    self.iter_count+=1
                    self.test_sql(cr,uid,ids,sub_tb=w_qutable,context=None)
                 
                else:
                    for table in self.tb_map.items():
                        if tb in table[1]:
                            table[1].remove(tb)
                            if tb not in self.w_untb:
                                if tb !=  'resource_resource':
                                    self.w_untb.append(tb)
                                    cr.execute('''select * from %s'''% tb)
                                    if cr.fetchall:
                                        info=re.sub('_','.',tb)+' ' * 8+tb+'\n'
                                        if info not in self.relat_info:
                                            self.relat_info.append(info)
                            
                                    
        print self.tb_map,'mpppppp' ,self.w_untb           
        if self.tb_map:
            if m_tb in self.tb_map.keys():
                if 'resource_resource'  in self.tb_map[m_tb]:
                    self.tb_map[m_tb].remove('resource_resource')
                if self.iter_count <15:
                    if self.tb_map[m_tb]:
                        self.test_sql(cr,uid,ids,sub_tb=self.tb_map[m_tb],context=None)
              
        r_info=','.join(self.relat_info)
        if r_info:
            self.write(cr,uid,ids,{'related_table_info':str(r_info)})
        else:
            self.write(cr,uid,ids,{'related_table_info':'not found relation table!'})
        return True
        
    def test_unlink(self,cr,uid,ids,context=None):
        my=self.browse(cr,uid,ids[0])
        irm_obj=self.pool.get('ir.model')
        mtb_name=irm_obj.browse(cr,uid,my.w_untable.id).model
        m_tb=re.sub('\.','_',mtb_name)
        
        tb_map=self.tb_map.copy()
        if self.w_untb:
            for untb in self.w_untb:
                if untb !=m_tb:  
                    cr.execute('''delete from %s '''% untb)
                
        if not self.tb_map or not self.tb_map[m_tb]:
            if m_tb =='res_users':
                user_obj=self.pool.get('res.users')
                res_ids=user_obj.search(cr,uid,[('id','!=',1)])
                unk=user_obj.unlink(cr,uid,res_ids)
                if unk:
                    print 'unlink res_users record success!'
            else:
                cr.execute('delete from %s' % m_tb)
      
        if my.related_table_info and not self.w_untb:
            self.write(cr,uid,ids,{'related_table_info':'unlink relation table sucess!'})
        return True
    
    def create_users(self,cr,uid,ids,context=None):
        emp_obj=self.pool.get('hr.employee')
        user_obj=self.pool.get('res.users')
        res_obj=self.pool.get('resource.resource')
        emp_ids=emp_obj.search(cr,uid,[])
        
        if emp_ids:
            for ep_id in emp_ids:
              
                ep_rec=emp_obj.browse(cr,uid,ep_id)
                user_ser=user_obj.search(cr,uid,[('name','=',ep_rec.resource_id.name),('login','=',ep_rec.job_number)])
                if not user_ser:
                    user_id=user_obj.create(cr,uid,{
                        'name':ep_rec.name,
                        'login':ep_rec.job_number,
                        'password':'Mtloe'+ep_rec.job_number,
                        'context_department_id':ep_rec.department_id.id ,
                    })
                    
                    if user_id:
                        res_obj.write(cr,uid,ep_rec.resource_id.id,{'user_id':user_id})
                
        return True
        
        
    
    _columns={
        #'import_number': fields.char('name', size=32, ),
        'oe_table':fields.many2one('ir.model','oe_table'),
        'field_ids':fields.one2many('import.data.model','import_data_id','field_ids'),
        'dosure_table_all':fields.selection([('','')],'dosure_table',select=True),
        'dosure_line_ids':fields.one2many('dosure.table.info','import_id','dosure_line_ids'),
        'server': fields.char('服务器', size=64, required=True, select=True),
        'user': fields.char('用户名', size=256, required=True, select=True),
        'password': fields.char('密码', size=256, required=True, select=True),
        'database': fields.char('数据库', size=256, required=True, select=True),
        'file_path':fields.char('file_path',size=256),
        'w_untable':fields.many2one('ir.model','w_untable'),
        'related_table_info':fields.text('related_table_info'),
    } 
    _defaults={
        'server': lambda *a:'192.168.0.2',
        'user': lambda *a: 'sa',
        'password': lambda *a: '719799',
        'database': lambda *a:'mtltest',
    }
    def auto_create_map(self,cr,uid,ids,context=None):
        return True
    def get_dosure_table(self,cr,uid,ids,context=None):
        return True
import_data()

class import_data_model(osv.osv):
    _inherit='ir.model.fields'
    _name='import.data.model'
    _columns={
        'dosure_field_name':fields.char('dosure_field_name',size=32),
        'dosure_field_description':fields.char('dosure_field_description',size=32),
        'dosure_field_selection':fields.selection([('','')],'dosure_field_selection'),
       'import_data_id':fields.many2one('import.data','import_data_id'),
    }
import_data_model()

class dosure_table_info(osv.osv):
    _inherit='ir.model.fields'
    _name='dosure.table.info'
    _columns={
              'table_name':fields.char('table_name',size=32),
              'import_id':fields.many2one('import.data','import_id'),
              'relation_table_dosure':fields.char('relation_table_dosure',size=64),
              'relation_field_dosure':fields.char('relation_field_dosure',size=64), 
    }
dosure_table_info()