Sidebar = new Object();

Sidebar.shown = true;

Sidebar.init = function()
{
	var sidebarNode = $('#main-sidebar');
	if (sidebarNode.length != 1)
		return;
	sidebarNode = sidebarNode[0];

	Sidebar.sidebarNode = sidebarNode;
	Sidebar.mainContentContainer = $('#main-content-container')[0];

	Sidebar.isRightSidebar = $(Sidebar.mainContentContainer).hasClass('sidebar-right');
	if (!Sidebar.isRightSidebar &&
		!$(Sidebar.mainContentContainer).hasClass('sidebar-left'))
		throw 'Błąd: mainContentContainer powinien mieć przynajmniej jedną z klas: sidebar-right, sidebar-left';

	Sidebar.hideButton = document.createElement('a');
	sidebarNode.appendChild(Sidebar.hideButton);
	Sidebar.hideButton.className = 'main-sidebar-toggle-button hide';
	Sidebar.hideButton.appendChild(document.createTextNode(Sidebar.isRightSidebar?'>':'<'));
	$(Sidebar.hideButton).click(Sidebar.toggleVisibility);

	Sidebar.showButton = document.createElement('a');
	Sidebar.showButton.style.display = 'none';
	Sidebar.mainContentContainer.appendChild(Sidebar.showButton);
	Sidebar.showButton.className = 'main-sidebar-toggle-button show';
	Sidebar.showButton.appendChild(document.createTextNode(Sidebar.isRightSidebar?'<':'>'));
	$(Sidebar.showButton).click(Sidebar.toggleVisibility);

	var cookieStatus = $.cookies.get('sidebar-visible');
	if (cookieStatus !== null)
		Sidebar.setVisible(cookieStatus);
	else
		Sidebar.setVisible($(Sidebar.mainContentContainer).hasClass('sidebar-visible'));
};

Sidebar.toggleVisibility = function()
{
	Sidebar.setVisible(!Sidebar.shown);
};

Sidebar.setVisible = function(visible)
{
	visible = !!visible;
	
	Sidebar.shown = visible;
	$.cookies.set('sidebar-visible', Sidebar.shown);

	Sidebar.sidebarNode.style.display = visible?'block':'none';
	Sidebar.showButton.style.display = visible?'none':'block';

	if (visible)
		$(Sidebar.mainContentContainer).addClass('sidebar-visible');
	else
		$(Sidebar.mainContentContainer).removeClass('sidebar-visible');
		
};

$(Sidebar.init);
