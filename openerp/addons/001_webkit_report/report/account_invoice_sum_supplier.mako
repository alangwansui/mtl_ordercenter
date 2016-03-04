<html>
<head>
    <style type="text/css">
    	body{
    	}
			c1 { 
				width:200px;
				position:absolute; 
				border-style:groove;
				white-space:normal;
			}    	
			c2 { 
				width:100px;
				white-space:normal;
				position:absolute; 
				left:215px; 
				border-style:groove;
			}
    </style>
</head>

<body>
    <%
    setLang("zh_CN")
    sum_amount=0.0
    for i  in  objects:
        print i
        info_list=[]
        total=i.amount_total or 0.0
        untaxed=i.amount_untaxed or 0.0
        sum_untaxed+=untaxed
        sum_total+=total
        partner_name=i.partner_name
        partner_address=i.address_invoice_id.street
        partner_phone=i.address_invoice_id.phone
        partner_info_list=[partner_name,partner_address,partner_phone,sum_untaxed,sum_total]
    for inv in objects:
        res={}
        res[inv.partner_id]=partner_info_list
   
        
        
	
       
	%>
    
	<br />
	<br />
    %for inv in res:
       
        <table> 
		<%count_page=0%>
		<tr><center><b><font size=5>深圳市牧泰莱电路技术有限公司</font></b></center></tr>
		</br>
		<tr>供应商发票明细:${time.strftime('%Y%m%d%H%M%S')|entity}</tr> </br>
		<tr>日&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp期:${time.strftime('%Y')}年${time.strftime('%M')}月${time.strftime('%d')}日</tr>
            <th>供应商</th><th>地址</th><th>电话</th><th>未完税金额</th><th>总金额</th>
        %for obj in objects:
        
            <tr>
                <th width="300">${obj.partner_id.name |entity}</th>
                <th width="300">${res[inv] |entity}</th>
                <th width="300">${res[inv] |entity}</th>
                <th width="300">${res[inv] |entity}</th>
				<th width="300">${sum_supplier(obj.partner_id,obj) |entity}</th>
				
			</tr>
        %endfor
        </table>
    %endfor
       
</body>
</html>




<!--     
c1 { 
		width:200px;
		position:absolute; 
		border-style:groove;
	}    	
	c2 { 
		width:300px;
		position:absolute; 
		left:215px; 
		border-style:groove;
	}		
-->....