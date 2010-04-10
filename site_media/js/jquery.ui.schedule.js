(function($) {


$.widget("ui.schedule", {
	
	options: {
		minPerCell: 60,
		startMinute: 480,
		endMinute: 1380,
		dayList: ['Poniedzialek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'],
		minutesPerCell : 60, 
		cellHeight: 32
	},
	
	_create: function() {
		
		var self = this,
			dayList = this.options.dayList || [],
			startMinute = this.options.startMinute || 480,
			endMinute = this.options.endMinute || 1380,
			minPerCell = this.options.minPerCell || 60,
			minutesPerCell = this.options.minutesPerCell || 60, 
			cellHeight = this.options.cellHeight || 32, 
			cellWidth = this.options.cellWidth || 105;
		
		self.initialTerms = self.element.find('div');
		
		self.scheduleTable = (self.scheduleTable = $('<table></table>'))
			.appendTo(self.element)
			.addClass('schedule-table')
			.append(self._daysRow(dayList));
		
		var $row = $('<tr></tr>')
			.append(self._hoursColumn(startMinute, endMinute, minPerCell))
			.appendTo(self.scheduleTable);
		
		/* there is no map in ie:( 
		 self.dayColumnList = dayList.map(
			function() { 
				return self._dayColumn(startMinute, endMinute, minPerCell)
					.appendTo($row)
					.children()
					.first(); 
			}
		);*/
		
		self.dayColumnList = [];
		$.each(dayList, function(idx, itm) {
			self.dayColumnList.push( 
				self._dayColumn(startMinute, endMinute, minPerCell)
					.appendTo($row)
					.children()
					.first()
			);
		});
	
		self.initialTerms.each(function(){
			self._addDivTerm($(this), minutesPerCell, cellHeight, cellWidth);
		});		
	},
	
	_daysRow: function(dayList) {
		
		var $row = $('<tr></tr>').append($('<td></td>'));
		for (var d = 0; d < dayList.length; d++) {
		    $row.append(
				$('<td></td>').append(
					$('<div></div>')
						.addClass('schedule-days-cell-content')
						.append($('<span>'+dayList[d]+'</span>'))
				)
			);
		}
		return $row;
	},
	
	_hoursColumn: function(startMinute, endMinute, minPerCell) {
		
		var $column = $('<td></td>');
		for (var h = startMinute; h < endMinute; h=h+minPerCell) {
		    $column.append(
				$('<div></div>')
					.addClass('schedule-hours-cell-content')
					.append($('<span>'+(h/60 >= 10 ? h/60 : '0'+h/60)+':'+(h%60 >= 10 ? h%60 : '0'+h%60)+'</span>'))
			);
		}
		return $column;
	},
	
	_dayColumn: function(startMinute, endMinute, minPerCell) {
		
		var $column = $('<td></td>')
			.addClass('schedule-day-cell')
			.append($('<div>&nbsp;</div>')
				.addClass('schedule-column-place-indicator'));
				
	    for (var h = startMinute; h < endMinute; h=h+minPerCell) {
		    $column.append(
				$('<div>&nbsp;</div>')
					.addClass('schedule-grid-cell')
			);
		}
		
		return $column;
	},
	
	addTerm: function(content, day, from, minutes) {
		
		this._addDivTerm(
			$('<div></div>')
				.attr({
					minutes: minutes,
					day: day,
					from: from}),
			this.options.minutesPerCell,
			this.options.cellHeight
		);
	},
	
	_addDivTerm: function(divTerm, minutesPerCell, cellHeight) {
		
		$('<div></div>')
			.addClass('schedule-group-term-m')
			.append(divTerm.html())
			.appendTo(divTerm
				.empty()
				.addClass('schedule-group-term')
				.css({
					height: parseInt(divTerm.attr('minutes'))*cellHeight/minutesPerCell - 5,
					top: parseInt(divTerm.attr('from'))*cellHeight/minutesPerCell})
				.appendTo(this.dayColumnList[parseInt(divTerm.attr('day'))-1]));
		this._orderColumnContent(this.dayColumnList[parseInt(divTerm.attr('day'))-1]);
	},
	
	_orderColumnContent: function(column) {
		
		var self = this,
			lastOccHourInCol = [0],
			termsList = column.children('.schedule-group-term').get();
		
		termsList.sort(function(a, b){
			var startA = $(a).attr('from'),
		   	 	startB = $(b).attr('from');
		   	return (startA < startB) ? -1 : (startA > startB) ? 1 : 0;
		}); 
		
		$.each(termsList, function(idx, itm) {
			var $itm = $(itm),
				from = parseInt($itm.attr('from')),
				minutes = parseInt($itm.attr('minutes'));
			for(var i=0; i<lastOccHourInCol.length; i++) {
				if(lastOccHourInCol[i] <= from) {
					lastOccHourInCol[i] = from + minutes;
					$itm.attr('column', i);
					break;
				} else if (i == lastOccHourInCol.length - 1) {
					lastOccHourInCol.push(from + minutes);
					$itm.attr('column', i+1);
					break;
				}
			}
		});
		
		$.each(termsList, function(idx, itm) {
			
			var $itm = $(itm),
			 	col = parseInt($itm.attr('column')),
				day = parseInt($itm.attr('day')),
			 	cols = 1,
				intersect = new Array(lastOccHourInCol.length);
				
			$.each(termsList, function(idx2, itm2) {
				var $itm2 = $(itm2),
				 	col2 = parseInt($itm2.attr('column')),
					day2 = parseInt($itm2.attr('day'));
				if(day==day2 && self._termsIntersect($itm,$itm2)) {
					intersect[col2] = 1;
				}
			});
			
			for(var i = col-1; i>=0; i--) {
				if(intersect[i] != 1) cols++;
			}
			
			for(var i = col+1; i<intersect.length; i++) {
				if(intersect[i] != 1) cols++;
			}
			
			$itm.css({
				'left' : (col*100.0/lastOccHourInCol.length)+'%',
				'width' : ((col+cols >= lastOccHourInCol.length ? cols : cols+0.5)*100.0/lastOccHourInCol.length)+'%',
				'z-index' : 1000 + col
			});
			
		});
	},
	
	_termsIntersect: function($term1, $term2) {
		
		var from1 = parseInt($term1.attr('from')),
			to1 = from1 + parseInt($term1.attr('minutes')),
			from2 = parseInt($term2.attr('from')),
			to2 = from2 + parseInt($term2.attr('minutes'));
			
		return (from1 <= from2 && from2 < to1 ||
				from1 < to2 && to2 <= to1 ||
				from2 <= from1 && to1 <= to2)
	}
	
	
});

})(jQuery);
