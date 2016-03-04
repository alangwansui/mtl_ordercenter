<html>
<head>
    <style type="text/css">
      <!--
    	body{font-size:18;}
	-->
    </style>
</head>
<body>
	<%setLang("zh_CN")%>
	<br />
	<br />
	  
	



    %for inv in objects:
        <tr><td ><b>单据编号      :   ${inv.name           |entity}</b></td></tr>        <br />
        <tr><td ><b>单据日期      :   ${inv.create_time    |entity}</b></td></tr>   <br />
        <tr><td ><b>更新前价格 :   ${inv.old_price      |entity}</b></td></tr>        <br />
        <tr><td ><b>更新后价格  ：     ${inv.new_price      |entity}</b></td></tr>        <br />
        <tr><td ><b>产品                :   ${inv.product_id.name    |entity}</b></td></tr>   <br />
        <tr><td ><b>型号                :   ${inv.variants           |entity}</b></td></tr>   <br />
        <tr><td ><b>物料编号      :   ${inv.defult_code        |entity}</b></td></tr>   <br />
        <tr><td ><b>负责人           :   ${inv.responsible.name   |entity}</b></td></tr>   <br />
        
      
        
    %endfor
</body>
</html>