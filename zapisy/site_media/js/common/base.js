$(function () {
    var loginDropdown = $('#login-dropdown');
    var btnShowLoginForm = $('#btn-no-usos');
    var loginForm = $('#login-without-usos');
    var loginDropdown = $('#login-dp');

    loginDropdown.bind('click', function () {
	btnShowLoginForm.show();
	loginForm.hide();
    });

    btnShowLoginForm.bind('click', function (event) {
	event.stopPropagation();
	$(this).hide();
	loginForm.show();
    });

    loginDropdown.bind('click', function (event) {
	event.stopPropagation();
    });
});
