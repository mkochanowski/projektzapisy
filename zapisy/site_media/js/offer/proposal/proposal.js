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
	$(':button[type="submit"]').removeAttr("disabled");
	if (Math.abs(shouldbe-sum)>20) {
		color = '#FF0000';
 		$(':button[type="submit"]').attr("disabled", true);
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
			if (key=='default_ects') {
				new_ects = data[$(this).val()][key];
				$('#id_entity-ects').val(new_ects);
				$('#hours_should_be').html(new_ects*25)
			} else
			{
				if (data[$(this).val()][key]) {
					$('#id_entity-'+key).val(30);
				} else {
					$('#id_entity-'+key).val('');
				}
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

	$("tr:has(ul.errorlist)").addClass("haserrors");

	recompute();
})

function proposal_init(types_data) {
	data = types_data;
}