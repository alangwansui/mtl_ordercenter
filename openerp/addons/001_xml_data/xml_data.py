
'''
# @author:  zhouqiang <alangwansui AT gmail.com>
# @date:     2012-3-6
# @Created on: 
# @Description:   trans line to xml formart

'''
import re

fw=open('e:/group.xml','w')
f=open('e:/xx.txt','r')
for line in f:
    lis=line.split()    ## if space line
    if lis :
        oid = re.sub(r'[\/]','_',line)
        oid = re.sub('[\s]','',oid).lower()
        name=re.sub(' ','',line)
        name=re.sub('[\s]','',name)
        
        
        context=r'''
<record id="%s" model="res.groups">
        <field name="name">%s</field>
</record>
'''    % (oid, name)

        print context
        fw.write(context)
