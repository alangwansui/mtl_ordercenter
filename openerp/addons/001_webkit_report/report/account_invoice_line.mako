<html>
<head>
<style type="text/css">

	c1 { 
		width:150px;
		position:absolute; 
		left:600px; 
	}	
	c2 { 
		width:150px;
		position:absolute; 
		left:800px; 
	}	

table th { vertical-align:top; text-align:left; border-style:groove;}
</style>

</head>

<body>
	<%
	setLang("zh_CN")
	count_all=0.0
	for i  in  objects:
		price=i.price_subtotal or 0.0
		count_all+=price
	arr_arr=[[]]
	
	(k,flage)=(1,0)
	for inv in objects:
		arr_arr[flage].append(inv)
		if ( not k%12  ):
			flage+=1
			arr_arr.append([])
		k+=1
	%>
	
	
	<br />
	%for j,arr in enumerate(arr_arr):		
		<table> 
		<%count_page=0%>
		<tr><center><b><font size=5>深圳市牧泰莱电路技术有限公司</font></b></center></tr>
		</br>
		<tr>收料单号:${time.strftime('%Y%m%d%H%M%S')}P${j+1}</tr> </br>
		<tr>日&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp期:${time.strftime('%Y')}年${time.strftime('%M')}月${time.strftime('%d')}日</tr>
			
		
		<th>供应商</th><th>物料编号</th><th>材料名称</th><th>规格型号</th><th>实收数量</th><th>单位</th><th>单价</th><th>小计</th>
		%for inv in arr:
			<%
				price=i.price_subtotal or 0.0
				count_page+=price
			%>
			<tr>
				<th width="300">${inv.partner_id.name|entity}</th>
				<th width="120">${inv.product_id.default_code|entity}</th>
				<th width="150">${inv.product_id.name_template|entity}</th>
				<th width="150">${inv.product_id.variants|entity}</th>
				<th width="100">${inv.quantity|entity}</th>
				<th width="80">${inv.product_id.uom_id.name |entity}</th>
				<th width="70">${inv.price_unit |entity}</th>
				<th width="150">${inv.price_subtotal |entity}</th>
			</tr>
		%endfor
			<th>本页小计: ${count_page |entity}</th>
		
		</table> 
		
        %if	j < len(arr_arr)-1:
        	<div STYLE="page-break-after: always;">         </div>
        %endif
		
	%endfor
  
    
   
  
     
</body>
</html>




<!--  




		%for i,inv in enumerate(objects):
		

		<tr>
			<th width="300">${inv.partner_id.name|entity}</th>
			<th width="120">${inv.product_id.default_code|entity}</th>
			<th width="150">${inv.product_id.name_template|entity}</th>
			<th width="150">${inv.product_id.variants|entity}</th>
			<th width="100">${inv.quantity|entity}</th>
			<th width="80">${inv.product_id.uom_id.name |entity}</th>
			<th width="50">${inv.price_unit |entity}</th>
			<th width="150">${inv.price_subtotal |entity}</th>
		</tr>
		
	    %endfor


 
 new_page  <div STYLE="page-break-before: always;"> 第2页 </div>

   





  
<li><span class="date">${inv.product_id.name|entity}</span><a href="">${inv.partner_id.name|entity}</a></li>
 
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
	
	
<style type="text/css">
table td { vertical-align:top; text-align:left; }
table th { vertical-align:top; text-align:left; }
</style>





<table>
	<tr>
		<th width="50">cpt 1</th><th>cpt 2</th><th>cpt 3</th><th>cpt 4</th>
	</tr>
	<tr>
		<td width="50">xxx xxxxxxxx xxxxx</td><td>data 2</td><td>data 3</td><td>data 4</td>
	</tr>
	<tr>
		<td>data 1</td><td>data 2</td><td>data 3</td><td>data 4</td>
	</tr>
	<tr>
		<td>data 1</td><td>data 2</td><td>data 3</td><td>data 4</td>
	</tr>
</table>
	
	
	
	
	
		
-->