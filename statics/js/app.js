var app = this.app || {};

app.homepage = function(){
	var today = new Date();
	var dd = today.getDate();
	var hr = today.getHours();
	$("#id_start_time").val(hr);
	$("#id_end_time").val(hr+2);
	var dname = today.getDay();
	$("#id_day_of_week").val(dname);
	//alert(dname);
}

app.init = function(){
    //alert('App initialized...');
    this.homepage();
}

$(document).ready(function() {
    app.init();
        

})