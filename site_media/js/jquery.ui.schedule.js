(function($) {


$.widget("ui.schedule", {
	
	options: {
		minPerCell: 60,
		startMinute: 480,
		endMinute: 1380,
		dayList: ['Poniedzialek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek'],
		minutesPerCell : 60, 
		cellHeight: 32,
		hourColumnWidth: 40,
		dayColumnWidth: 110
	},
	
	_create: function() {
		
		var self = this,
			o = this.options;
		
		self.initialTerms = self.element.find('div');
		
		self.scheduleTable = (self.scheduleTable = $('<table></table>'))
			.appendTo(self.element)
			.addClass('schedule-table')
			.append(self._daysRow());
		
		var $row = $('<tr></tr>')
			.append(self._hoursColumn())
			.appendTo(self.scheduleTable);
		
		self.dayColumnList = [];
		$.each(o.dayList, function(idx, itm) {
			self.dayColumnList.push( 
				self._dayColumn()
					.appendTo($row)
					.children()
					.first()
			);
		});
	
		self.initialTerms.each(function(){
			self._addDivTerm($(this));
			self._makeTermFixed($(this));
		});		
	},
	
	_daysRow: function() {
		
		var o = this.options,
			$row = $('<tr></tr>').append($('<td></td>'));
		for (var d = 0; d < o.dayList.length; d++) {
		    $row.append(
				$('<td></td>').append(
					$('<div></div>')
						.addClass('schedule-days-cell')
						.append($('<span>'+o.dayList[d]+'</span>'))
				)
			);
		}
		return $row;
	},
	
	_hoursColumn: function() {
		
		var self = this,
			o = this.options,
			$column = $('<td></td>'),
			$placeIndicator = $('<div>&nbsp;</div>')
					.addClass('schedule-column-place-indicator')
					.css({
						height: (o.endMinute-o.startMinute)*o.cellHeight/o.minutesPerCell,
						width: o.hourColumnWidth})
					.appendTo($column);
			
		for (var h = o.startMinute; h < o.endMinute; h=h+o.minutesPerCell) {
		    $placeIndicator
				.append($('<div></div>')
					.addClass('schedule-hour-separator')
					.css({
						left: o.hourColumnWidth + 5,
						width: (o.dayColumnWidth + 5) * o.dayList.length,
						top: self._minuteAbsoluteTop(h-o.startMinute)}))
				.append($('<div></div>')
					.addClass('schedule-hours-cell')
					.append($('<span>'+(h/60 >= 10 ? h/60 : '0'+h/60)+':'+(h%60 >= 10 ? h%60 : '0'+h%60)+'</span>'))
					.css({
						height: self._termHeight(o.minutesPerCell),
						top: self._minuteAbsoluteTop(h-o.startMinute)})
			);
		}
		return $column;
	},
	
	_dayColumn: function() {
		
		var o = this.options,
			$column = $('<td></td>')
				.addClass('schedule-day-cell')
				.append($('<div>&nbsp;</div>')
					.addClass('schedule-column-place-indicator')
					.css({width: o.dayColumnWidth}));
		return $column;
	},
	
	_subjectTermClass: function(subjectID) {
		if(subjectID == undefined) {
			return 'schedule-unknown-subject-term';
		}
		else {
			return 'schedule-subject-' + subjectID + '-term';
		}
	},
	
	_subjectTermId: function(termID) {
		if(termID == undefined) {
			throw 'GroupID undefined.';
		}
		else {
			return 'schedule-' + termID + '-term';
		}
	},
	
	addTerm: function(content, day, from, minutes, subjectID, termID) {
		var self = this,
			add = true;
		
		$('#'+self._subjectTermId(termID)).each(function(){
			add = false;	
		});
		
		if(add) {
			this._addDivTerm($('<div></div>').attr({
				minutes: minutes,
				day: day,
				from: from,
				subjectID: subjectID,
				termID: termID
			}).html(content));
		}
	},
	
	_makeTermFixed: function(termDiv) {
		termDiv.addClass('schedule-fixed');
	},
	
	deleteTerms: function(subjectID){
		var self = this;
		$('.'+self._subjectTermClass(subjectID)+':not(.schedule-fixed)').remove();
		for(var i=0; i<self.dayColumnList.length; i++){
			self._orderColumnContent(self.dayColumnList[i]);
		}
	},
	
	_addDivTerm: function(divTerm) {
		var self = this;
		
		$('<div></div>')
			.addClass('schedule-group-term-m')
			.append(divTerm.html())
			.appendTo(divTerm
				.empty()
				.addClass('schedule-group-term')
				.addClass(self._subjectTermClass(divTerm.attr('subjectid')))
				.attr('id', self._subjectTermId(divTerm.attr('termid')))
				.css({
					height: self._termHeight(parseInt(divTerm.attr('minutes'))),
					top: self._minuteAbsoluteTop(parseInt(divTerm.attr('from')))})
				.appendTo(this.dayColumnList[parseInt(divTerm.attr('day'))]));
				
		this._orderColumnContent(this.dayColumnList[parseInt(divTerm.attr('day'))]);
	},
	
	_termHeight: function(minutes) {
		var o = this.options;
		return minutes*o.cellHeight/o.minutesPerCell - 5;
	},
	
	_minuteAbsoluteTop: function(minute_offset) {
		var o = this.options;
		return minute_offset*o.cellHeight/o.minutesPerCell;
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
