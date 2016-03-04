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
    
    
        <tr><td ><b>单据编号      :   ${inv.name          |entity}</b></td></tr>        <br />
        <tr><td ><b>单据日期      :   ${inv.create_time    |entity}</b></td></tr>   <br />
        <tr><td ><b>产品                :   ${inv.product_id.name    |entity}</b></td></tr>   <br />
		<tr><td ><b>型号                :   ${inv.variants           |entity}</b></td></tr>   <br />
        <tr><td ><b>物料编号      :   ${inv.defult_code        |entity}</b></td></tr>   <br /> 
		<tr><td ><b>加工内容      :   ${inv.out_content    |entity}</b></td></tr>   <br />
		<tr><td ><b>加工目的      :   ${inv.purpose    |entity}</b></td></tr>   <br />
		<tr><td ><b>供应商        :   ${inv.partner_id.name   |entity}</b></td></tr>   <br />
		<tr><td ><b>联系电话      :   ${inv.mobile    |entity}</b></td></tr>   <br />
		<tr><td ><b>联系人        :   ${inv.link_man    |entity}</b></td></tr>   <br />
		<tr><td ><b>数量          :   ${inv.amount    |entity}</b></td></tr>   <br />
		<tr><td ><b>负责人        :   ${inv.responsible.name    |entity}</b></td></tr>   <br />
		<tr><td ><b>品质意见      :   ${inv.quality_opinion    |entity}</b></td></tr>   <br />
		<tr><td ><b>样品进料检验记录     :   ${inv.sample_check_record    |entity}</b></td></tr>   <br />
		<tr><td ><b>样品试验记录      :   ${inv.sample_experiment_record    |entity}</b></td></tr>   <br />
		<tr><td ><b>品质部评定意见     :   ${inv.quality_evaluation    |entity}</b></td></tr>   <br />
		<tr><td ><b>样品选择是否合适      :   ${inv.difficulty_suitable    |entity}</b></td></tr>   <br />
		<tr><td ><b>样品难度      :   ${inv.difficulty_content    |entity}</b></td></tr>   <br />
		<tr><td ><b>要派品质人员跟进      :   ${inv.followup_is   |entity}</b></td></tr>   <br />
		<tr><td ><b>IOS14001通过      :   ${inv.iso    |entity}</b></td></tr>   <br />
		<tr><td ><b>IOS附件      :   ${inv.iso_number    |entity}</b></td></tr>   <br />
        <tr><td ><b>测试内容      :   ${inv.test_content    |entity}</b></td></tr>   <br />
		<tr><td ><b>附件1      :   ${inv.attachment_one    |entity}</b></td></tr>   <br />
		<tr><td ><b>附件2      :   ${inv.attachment_two    |entity}</b></td></tr>   <br />
		

	
		<%state_name=state_username('outsource.evaluation',inv.id)%>
		${state_name['draft']}
		

    %endfor
    
    
    
</body>
</html>


<!--

	
	
-->