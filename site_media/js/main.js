/**
 * Plik dołączany razem z głównym szablonem.
 */

Fereol = new Object();

Fereol.init = function()
{
    $('.main-labelledSelect').change(function()
    {
        $(this).children('.label').remove();
    });
};

$(Fereol.init);

function DisableControlDrag(control)
{
	if (typeof control != 'object')
		throw new Exception('disableControlDraggable: zły parametr');
    $(control).bind('mousedown mousemove', function(e)
    {
        if (e && e.preventDefault)
            e.preventDefault();
    });
    $(control).bind('selectstart mousedown', function() { return false; });
	control.style.MozUserSelect = 'none';
}

DisableControlDrag.jQueryCallback = function(index, element)
{
    DisableControlDrag(element);
};
