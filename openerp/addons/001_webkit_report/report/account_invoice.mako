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
    res_untaxed={}
    res_total={}
    res_add={}
   
    res_date={}
    for i  in  objects:
       	kn=i.partner_id.name
        res_total[kn]=res_total.has_key(kn) and res_total[kn]+i.amount_total  or  i.amount_total
    	res_untaxed[kn]=res_untaxed.has_key(kn) and res_untaxed[kn]+i.amount_untaxed   or  i.amount_untaxed 
        res_add[kn]=i.partner_id
       
        res_date[kn]=res_date.has_key(kn) and (res_date[kn] > i.date_due and res_date[kn] or  i.date_due)  or i.date_due

    %>
    
	<br />
	<br />
   
       
        <table> 
		<%count_page=0%>
		<tr><center><b><font size=5>深圳市牧泰莱电路技术有限公司</font></b></center></tr>
		</br>
		<tr>供应商发票明细:${time.strftime('%Y%m%d%H%M%S')|entity}</tr> </br>
		<tr>日&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp期:${time.strftime('%Y')}年${time.strftime('%m')}月${time.strftime('%d')}日</tr>
        <th>供应商</th><th>供应商代码</th><th>未完税金额</th><th>总金额</th><th>付款日期</th>
        %for k in res_total:
        
            <tr>
                <th width="300">${k |entity}</th>
                <th width="300">${res_add[k].ref|entity}</th>
                <th width="300">${res_untaxed[k] |entity}</th>
				<th width="300">${res_total[k]|entity}</th>
                <th width="300">${res_date[k] |entity}</th>
			</tr>
        %endfor
        </table>
    
       
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