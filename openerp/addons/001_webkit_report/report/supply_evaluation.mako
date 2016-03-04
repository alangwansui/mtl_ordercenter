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
		<tr><td ><b>供应商        :   ${inv.partner_id.name     |entity}</b></td></tr>   <br />
        <tr><td ><b>联系人        :   ${inv.link_man       |entity}</b></td></tr>   <br />
		<tr><td ><b>联系电话      :   ${inv.mobile         |entity}</b></td></tr>   <br />
		<tr><td ><b>原材料资料    :   ${inv.mat_eva_ids.name |entity}</b></td></tr>   <br />
		<tr><td ><b>体系调查表    :   ${inv.system_questionnaire    |entity}</b></td></tr>   <br />
		<tr><td ><b>品质部评估    :   ${inv.quality_evaluation    |entity}</b></td></tr>   <br />
		<tr><td ><b>使用评估    :   ${inv.use_evaluation    |entity}</b></td></tr>   <br />
		<tr><td ><b>最终评估    :   ${inv.final_assessment    |entity}</b></td></tr>   <br />
		<tr><td ><b>备注   :   ${inv.note_1    |entity}</b></td></tr>   <br />
    %endfor
</body>
</html>