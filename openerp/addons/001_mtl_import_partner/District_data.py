#!/usr/bin/python

import os,sys
data_file='e:/tmp.txt'
fh=open(data_file, 'r')


for line in fh:
    code,name=line.split()

    if  (code[2:4] == '00' and  code[4:6] == '00' ):
        print  code  ,  name
		

		
		
	
	
	

        

    
    
    