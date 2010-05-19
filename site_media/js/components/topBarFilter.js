/**
 * Funkcje odpowiedzialne za panel filtrowania.
 */

TopBarFilter = new Object();

TopBarFilter.emptyFilterText = 'Filtruj';

TopBarFilter.init = function()
{
	var filterInputs = $('.main-filter-input');
	for (var i = 0; i < filterInputs.length; i++)
	{
		var filterField = $(filterInputs[i]).children('.text')[0];
		var filterReset = $(filterInputs[i]).children('.reset')[0];

		$(filterField).focus(function()
		{
			if ($(this).attr('value') == TopBarFilter.emptyFilterText)
				$(this).attr('value', '');
		});
		
		$(filterField).blur(function()
		{
			if ($(this).attr('value') == '')
				$(this).attr('value', TopBarFilter.emptyFilterText);
		});

		$(filterReset).css('display','inline-block');

		if ($(filterField).attr('value') == '')
			$(filterField).attr('value', TopBarFilter.emptyFilterText);
	}
};

$(TopBarFilter.init);
