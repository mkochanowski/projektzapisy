function load_data(url) {
    MessageBox.clear();
    $.getJSON(url, function(data) {
	if (typeof(data.message) != "undefined") {
        MessageBox.display(data.message);
	} else {
	    $('#news-nav-groups').html(data.newer_group + data.older_group);
	    $('#news-content').html(data.content);
	    if (data.archive_view) {
		$('#news-archive-nav').css("display", "inline");
	    } else {
		$('#news-archive-nav').css("display", "none");
	    }
	    if (data.search_view) {
		$('#news-search-nav').css("display", "inline");
	    } else {
		$('#news-search-nav').css("display", "none");
	    }
	}
    });
};

$(document).ready(function() {
    $('#od-news-search-form').submit(function() {
	load_data('/news/ajax/search/' +
		  '?q=' + $('#od-news-search-q').attr('value'));
	return false;
    });
    $('#od-news-search-reset').click(function() {
	load_data('/news/ajax/latest/');
    });
});
