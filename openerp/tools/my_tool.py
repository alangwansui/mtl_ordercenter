# -*- coding: utf-8 -*-
##############################################################################

class limit_long_dic(object):
    def __init__(self,long):
        self.dic={}
        self.dic_limit=long
    def update(self,dic):
        if len( self.dic ) < self.dic_limit:
            self.dic.update( dic )
        else:
            key_list= self.dic.keys()
            key_list.sort()
            self.dic.pop(key_list[0])
            self.dic.update( dic )
            
     
def instance_arg_check(self, *arg, **args):
    class_name=type(self).__name__            
    for k in args:
        if not args[k]:
            raise Exception,"%s args error! ,attr %s cant be none "  % (class_name,k)
        
    return True