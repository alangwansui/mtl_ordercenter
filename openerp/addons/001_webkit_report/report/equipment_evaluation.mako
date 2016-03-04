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
        <tr><td ><b>负责部门    :   ${inv.department_id.name  |entity}</b></td></tr>   <br />
        <tr><td ><b>产品编号      :   ${inv.defult_code        |entity}</b></td></tr>   <br /> 
		<tr><td ><b>产品名称     :   ${inv.product_id.name   |entity}</b></td></tr>   <br />
		<tr><td ><b>产品规格      :   ${inv.variants    |entity}</b></td></tr>   <br />
		<tr><td ><b>申请原因与要求      :   ${inv.reason_request    |entity}</b></td></tr>   <br />
		<tr><td ><b>设备产能和操作要求      :   ${inv.handle_request    |entity}</b></td></tr>   <br />
		<tr><td ><b>供应部门要求      :   ${inv.tech_request    |entity}</b></td></tr>   <br />
		<tr><td ><b>机修班要求      :   ${inv.maintain_request    |entity}</b></td></tr>   <br />
		<tr><td ><b>候选设备与商务条件      :   ${inv.parameter_analysis    |entity}</b></td></tr>   <br />
		<tr><td ><b>候选设备与商务条件      :   ${inv.parameter_analysis    |entity}</b></td></tr>   <br />
		<tr><td ><b>生产能力与操作方法     :   ${inv.capacity    |entity}</b></td></tr>   <br />
		<tr><td ><b>工艺参数与加工能力     :   ${inv.tech_parameter    |entity}</b></td></tr>   <br />
		<tr><td ><b>加工质量评估     :   ${inv.process_quality  |entity}</b></td></tr>   <br />
		<tr><td ><b>安装保养与维护维修     :   ${inv.install_maintain_   |entity}</b></td></tr>   <br />
    %endfor
</body>
</html>