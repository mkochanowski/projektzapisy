
(function($) {

$.widget("ui.filter", {
	options: {
		elemsToFilterSelector : undefined,
		emptyFilterText : "Filter",
		hideClass: 'item-hide'
	},
	_create: function() {
		var self = this,
			o = this.options;
		
		self.element.find('input[type=text]')
			.keypress(function(e){
			   		if (e.which == 10 || e.which == 13) {
			   			return false;
			   		}
				})
			.keyup(function(){
	        		$(this)
					self.runFilter();
	    		});
				
		self.element.find('input[type=checkbox], select')
			.change(function(){
			        self.runFilter();
			    });
				
		$('.main-filter-input')
			.each(function(){
				var $finp = $(this),
					filterField = $finp.children('.text')[0],
					filterReset = $finp.children('.reset')[0];
		
				$(filterField).focus(function()
				{
					if ($(this).attr('value') == o.emptyFilterText)
						$(this).attr('value', '');
				});
				
				$(filterField).blur(function()
				{
					if ($(this).attr('value') == '')
						$(this).attr('value', o.emptyFilterText);
				});
		
				$(filterReset).css('display','inline-block');
		
				if ($(filterField).attr('value') == '')
					$(filterField).attr('value', o.emptyFilterText);
			});
		
		self.runFilter();
	},
	_collectFiltersInfo : function() {
		var self = this, 
			o = this.options,
			filtersArray = new Array();
		
		self.element.find('input[type=checkbox]')
			.each(function(){
		        var $inp = $(this);
		        filtersArray.push({ 
					matchtype : $inp.attr("matchtype"), 
					attrs : $inp.attr("filtrattrs"), 
					value : $inp.val(), 
					onmatch : $inp.is(':checked') ? $inp.attr("oncheckedmatch") : $inp.attr("onuncheckedmatch"), 
					onmismatch : $inp.is(':checked') ? $inp.attr("oncheckedmismatch") : $inp.attr("onuncheckedmismatch") });
		 
		   });
	    self.element.find('input[type=text],select')
		   .each(function(){
		        var $inp = $(this);
				if (o.emptyFilterText != $inp.val()) {
					filtersArray.push({
						matchtype: $inp.attr("matchtype"),
						attrs: $inp.attr("filtrattrs"),
						value: $inp.val(),
						onmatch: $inp.attr("onmatch"),
						onmismatch: $inp.attr("onmismatch")
					});
				}
		   });
		return filtersArray;
	},
	runFilter : function()
	{
	   	var self = this,
	   		o = this.options,
			filtersArray = this._collectFiltersInfo();
		
	   	$(o.elemsToFilterSelector).each(function(){
			var $elem = $(this);
			//console.log($elem.attr('subjectname'));
			$elem.removeClass(o.hideClass);
			jQuery.each(filtersArray, function(){
				 var filter = this;
				 var arrValues = filter.attrs.split(",");
				 //console.log(filter.attrs + ',' + filter.value);
				 for(var i=0;i<arrValues.length; i++) {
				 	arrValues[i] = $elem.attr(arrValues[i]);
				 }
				 if(filter.matchtype == "starts"){
				 	if(self._anyStartsWith(arrValues, filter.value)){
						if(filter.onmatch == "hide"){
				            $elem.addClass(o.hideClass);
				        }
					}
				 	else {
						if(filter.onmismatch == "hide"){
							$elem.addClass(o.hideClass);
				        }
					}
				 }
				 else if(filter.matchtype == "exact"){
				 	if(self._anyEquals(arrValues, filter.value)) {
						if(filter.onmatch == "hide"){
				            $elem.addClass(o.hideClass);
				        }
					}
					else {
						if(filter.onmismatch == "hide"){
			            	$elem.addClass(o.hideClass);
			        	}
					}
				 }
				 //console.log($elem.hasClass(o.hideClass));
			});
	   });
	},
	_anyStartsWith : function (haystackArr, needle) {
        for (var i = 0; i < haystackArr.length; i++) {
			//console.log("haystackArr"+haystackArr[i]);
			if((haystackArr[i].toLowerCase()+'').indexOf(needle.toLowerCase()) >=0) {
				//console.log("starts");
				return true;	
			}
		}
		return false;
    },
	_anyEquals : function (haystackArr, needle) {
        for (var i = 0; i < haystackArr; i++) {
			if(haystackArr[i] == needle) {
				return true;	
			}
		}
		return false;
    }
});
})(jQuery);
