<html>
<head>
    <style type="text/css">
      <!--

      
    	body{font-size:18; 
    		 background: #fff;
    		  line-height: 1.8;
    		  text-align: left;
    		  text-indent: 2em;
    	     color:red;}
	-->
    </style>
</head>
<body>
	<%setLang("zh_CN")%>
	<br />
	<tr><td ><b>物料试用评估报告</b></td></tr>        <br />
	<br />

    %for inv in objects:
        <tr><td ><b>单据编号      :   ${inv.name          |entity}</b></td></tr>        <br />
        <tr><td ><b>产品                :   ${inv.product_id.name    |entity}</b></td></tr>   <br />
        <tr><td ><b>型号                :   ${inv.variants           |entity}</b></td></tr>   <br />
        <tr><td ><b>物料编号      :   ${inv.defult_code        |entity}</b></td></tr>   <br /> 
        <tr><td ><b>供应商     :   ${inv.partner_id        |entity}</b></td></tr>   <br />
        <tr><td ><b>产品规格     :   ${inv.variants        |entity}</b></td></tr>   <br />
        <tr><td ><b>联系电话     :   ${inv.mobile        |entity}</b></td></tr>   <br />
        <tr><td ><b>联系人      :   ${inv.link_man        |entity}</b></td></tr>   <br />
        <tr><td ><b>负责人    :   ${inv.responsible       |entity}</b></td></tr>   <br />
        <tr><td ><b>日期     :   ${inv.create_time        |entity}</b></td></tr>   <br />
		<tr><td ><b>数量     :   ${inv.amount        |entity}</b></td></tr>   <br />
		<tr><td ><b>样品进料检验      :   ${inv.sample_check_record        |entity}</b></td></tr>   <br />
		<tr><td ><b>样品试用记录     :   ${inv.sample_experiment_record        |entity}</b></td></tr>   <br />
		<tr><td ><b>样品试用过程检验记录    :   ${inv.experiment_process_record        |entity}</b></td></tr>   <br />
		<tr><td ><b>品质部评定      :   ${inv.quality_evaluation        |entity}</b></td></tr>   <br />
    %endfor
</body>
</html>