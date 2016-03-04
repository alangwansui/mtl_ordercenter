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
        <tr><td ><b>单据编号      :   ${inv.name           |entity}</b></td></tr>   <br />
        <tr><td ><b>单据日期      :   ${inv.create_time    |entity}</b></td></tr>   <br />

        
    %endfor
</body>
</html>