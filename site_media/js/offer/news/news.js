function load_data(url) {
    $.getJSON(url, function(data) {
	$('#news-newer-group').html(data.newer_group);
	$('#news-older-group').html(data.older_group);
	$('#news-content').html(data.content);
	if (data.archive_view) {
	    $('#news-archive-nav').css("display", "inline");
	} else {
	    $('#news-archive-nav').css("display", "none");
	}
    })
};