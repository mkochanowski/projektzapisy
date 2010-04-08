(function($) {

/*
$.widget("ui.dialog", {
	options: {
		minutesPerCell: 60,
	},
	_create: function() {
		this.minutesPerCellFromAttr = parseInt(this.element.attr('minutesPerCell'));

		var self = this,
			options = self.options,

			minutesPerCell = options.minutesPerCell || self.minutesPerCellFromAttr || 60,
			
			uiSchedule = (self.uiDialog = $('<div></div>'))
				.appendTo(document.body)
				.hide()
				.addClass(uiDialogClasses + options.dialogClass)
				.css({
					zIndex: options.zIndex
				})
				// setting tabIndex makes the div focusable
				// setting outline to 0 prevents a border on focus in Mozilla
				.attr('tabIndex', -1).css('outline', 0).keydown(function(event) {
					if (options.closeOnEscape && event.keyCode &&
						event.keyCode === $.ui.keyCode.ESCAPE) {
						
						self.close(event);
						event.preventDefault();
					}
				})
				.attr({
					role: 'dialog',
					'aria-labelledby': titleId
				})
				.mousedown(function(event) {
					self.moveToTop(false, event);
				}),
	},
	
	widget: function() {
		return this.uiDialog;
	}
});*/
	
$.fn.scheduleAddBox = function(minutesPerCell, cellHeight, cellWidth){
	$(this).each(function(){
		divTerm = $(this);
		divTerm.css({
			height: parseInt(divTerm.attr('minutes'))*cellHeight/minutesPerCell - 5,
			width: cellWidth,
			top: parseInt(divTerm.attr('from'))*cellHeight/minutesPerCell,
		});
		$('#schedule-column-day-'+divTerm.attr('day')).append(divTerm);
	});
	return this;
}

})(jQuery);

$(function(){
	$('.schedule-table-simple tr:even').addClass('even');
});

$(function(){
	$('.schedule-group-term').scheduleAddBox(60, 32, 105);
});

