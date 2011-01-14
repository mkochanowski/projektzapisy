/**
 * Funkcje i klasy odpowiedzialne za moduł newsów.
 */

News = Object();

News.init = function()
{
	var category = $('#od-news-search-form').attr('action').split('/')[2];
	$('#od-news-search-form').submit(function()
	{
		News.loadPage('/news/' + category + '/search/?json=true&' +
			'q=' + $('#od-news-search-q').attr('value'));
		return false;
	});
	$('#od-news-search-reset').click(function()
	{
		News.loadPage('/news/' + category + '/?json=true');
	});
};

$(News.init);

News.loadPage = function(url)
{
	MessageBox.clear();
	$.getJSON(url, function(data)
	{
		if (typeof(data.message) != "undefined")
			MessageBox.display(data.message);
		else
		{
			$('#news-nav-groups').html(data.newer_group + data.older_group);
			$('#news-content').html(data.content);
			if (data.archive_view)
				$('#news-nav').text('Archiwum aktualności');
			else if (data.search_view)
				$('#news-nav').text('Wyniki wyszukiwania aktualności');
			else
				$('#news-nav').text('Aktualności');
		}
	});
};
