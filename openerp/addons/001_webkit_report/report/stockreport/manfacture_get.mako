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
    o= objects
   
    %>
    
	<br />
	<br />
   
       
        <table border=1 > 
		<%count_page=0%>
		<tr><center><b><font size=5>深圳市牧泰莱电路技术有限公司</font></b></center></tr>
		</br>
        <tr>领料单明细:${time.strftime('%Y%m%d%H%M%S')|entity}&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp部门: ${o.dpt_id[0].name}&nbsp&nbsp&nbsp&nbsp&nbsp负责人：${o.responsible[0].name}</tr> </br>
		<tr>日&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp期:${time.strftime('%Y')}年${time.strftime('%m')}月${time.strftime('%d')}日</tr>
  
    <br>
    <th>产品编号</th><th>名称</th><th>规格</th><th>单位</th><th>数量</th><th>实发数量</th>
    </br>
         %for i in objects:
            %for line in i.move_lines:
        
            <tr>
                <th width="200">${line.product_id.default_code |entity}</th>
                <th width="250">${line.product_id.name|entity}</th>
                <th width="200">${line.product_id.variants|entity}</th>
				<th width="50">${line.product_uom.name|entity}</th>
                <th width="100">${line.product_qty|entity}</th>
                <th width="100"></th>
			</tr>
            %endfor
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