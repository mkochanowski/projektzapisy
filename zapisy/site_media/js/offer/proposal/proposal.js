var data = {}

function recompute() {
	var sum = 0;
	$('table#hours-table td input:not(:hidden)').each(function(){
	        val = parseInt($(this).val(),10);
	        if (!isNaN(val))
	        	sum += val;
	});
	$('#target_sum').html(sum);
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
	});

	$('table#hours-table input').live('change', function() {
		recompute();
	});
})

function proposal_init(types_data) {
	data = types_data
}