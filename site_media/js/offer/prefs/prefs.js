Prefs = new Object();

Prefs.initPref = function(elem, url)
{
	var li = elem.parentNode;
	var ul = li.parentNode;
	$(li).remove();

	if ($(ul).children('li').length == 0)
		$(ul).remove();

	$.ajax({
		type: 'post',
		url: url,
		success: function(data)
		{
			alert('Wynik zapytania: ' + data); // TODO
		}
	});
};

Prefs.toggleHidden = function(elem, hide, url)
{
//	var li = elem.parentNode;
//	var ul = li.parentNode;
//	$(li).remove();

//	if ($(ul).children('li').length == 0)
//		$(ul).remove();

	$.ajax({
		type: 'post',
		url: url,
		success: function(data)
		{
			alert('Wynik zapytania: ' + data); // TODO
		}
	});
};

Prefs.toggleCollapse = function(elem)
{
	var coll = $(elem.parentNode);
	if (coll.hasClass('subtree-visible'))
	{
		elem.value = '+';
		coll.removeClass('subtree-visible');
	}
	else
	{
		elem.value = '-';
		coll.addClass('subtree-visible');
	}
};
