var data = {}

function recompute() {
	var sum = 0;
	$('table#hours-table td input:not(:hidden)').each(function(){
	        val = parseInt($(this).val(),10);
	        if (!isNaN(val))
	        	sum += val;
	});
	shouldbe = parseInt($('#hours_should_be').html(),10);
	color = '#00FF00';
	if (Math.abs(shouldbe-sum)>20) {
		color = '#FF0000';
	}
	$('#target_sum').html('<span style="color:'+color+'">'+sum+'</span>');
}

$(function() {
	$('tr.dynamic-formset').formset({
		'removed': function() {
			recompute();
		}
	});

	$('select#id_entity-type').change(function() {
		for (var key in data[$(this).val()]) {
			if (data[$(this).val()][key]) {
				$('#id_entity-'+key).val(30);
			} else {
				$('#id_entity-'+key).val('');
			}
		}
		recompute();
		$('html, body').animate({
		        scrollTop: $("#hours-table").offset().top
		    }, 1000);
	});

	$('table#hours-table input').live('change', function() {
		recompute();
	});

	recompute();
})

function proposal_init(types_data) {
	data = types_data;
}