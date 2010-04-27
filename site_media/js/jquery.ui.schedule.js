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
		dayColumnWidth: 110,
		boxClass: ['box-1', 'box-2', 'box-3', 'box-4', 'box-5', 'box-6', 'box-7', 'box-8'],
		pinUrl: undefined,
		unpinUrl: undefined
	},
	
	_create: function() {
		
		var self = this,
			o = this.options;
		
		self.subjectList = [];	
		
		self.initialTerms = self.element.find('div');
		
		var pinUrl = self.element.attr('pinUrl'),
			unpinUrl = self.element.attr('unpinUrl');
		
		if(pinUrl != undefined) {
			o.pinUrl = pinUrl;
		}
		if(unpinUrl != undefined) {
			o.unpinUrl = unpinUrl;
		}
		
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
						top: self._minuteAbsoluteTop(h)}))
				.append($('<div></div>')
					.addClass('schedule-hours-cell')
					.append($('<span>'+(h/60 >= 10 ? h/60 : '0'+h/60)+':'+(h%60 >= 10 ? h%60 : '0'+h%60)+'</span>'))
					.css({
						height: self._termHeight(o.minutesPerCell),
						top: self._minuteAbsoluteTop(h)})
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
	
	_groupClass: function(groupID) { 
		if(groupID == undefined) {
			return 'schedule-group-unknown';
		}
		else {
			return 'schedule-group-' + groupID;
		}
	},
	
	_subjectClass: function(subjectID) {
		if(subjectID == undefined) {
			return 'schedule-subject-unknown';
		}
		else {
			return 'schedule-subject-' + subjectID;
		}
	},
	
	_termEntityId: function(groupID, termID) {
		if(termID == undefined) {
			throw 'TermID undefined.';
		}
		else {
			return 'schedule-term-' + groupID + '-' + termID;
		}
	},
	
	_nextBoxClass: function(){
		if(this.colorIndex == undefined )
			this.colorIndex = 0;
		else 
			this.colorIndex = (this.colorIndex+1) % this.options.boxClass.length;
		return this.options.boxClass[this.colorIndex];
	}, 
	
	_termWithSameIdAlreadyAdded: function(groupID, termID){
		var self = this,
			added = false;
		$('#'+self._termEntityId(groupID, termID)).each(function(){
			added = true;	
		});
		return added;
	},
	
	addTerm: function(content, day, from, minutes, subjectID, groupID, termID, status) {
		var self = this;
		
		if(!self._termWithSameIdAlreadyAdded(groupID, termID)) {
			this._addDivTerm($('<div></div>')
				.attr({
					minutes: minutes,
					day: day,
					from: from,
					subjectID: subjectID,
					groupID: groupID,
					termID: termID,
					status: status})
				.html(content));
		}
	},
	
	_makeTermFixed: function(termDiv) {
		termDiv.removeClass('schedule-pinned').addClass('schedule-fixed');
	},
	
	_makeTermPinned: function(termDiv) {
		termDiv.removeClass('schedule-unpinned').addClass('schedule-pinned');
	},
	
	_makeTermUnPinned: function(termDiv) {
		termDiv.removeClass('schedule-pinned').addClass('schedule-unpinned');
	},
	
	_ajaxGroupPin: function(groupID, successCallback) {
		var self = this;
		if (self.options.pinUrl == undefined) {
			alert("Pin url undefined");
		}
		else {
			$.ajax({
				type: "POST",
				url: self.options.pinUrl,
				data: {
					GroupId: groupID
				},
				success: function(msg){
					alert(msg);
					successCallback();
				}
			});
		}
	},
	
	_ajaxGroupUnpin: function(groupID, successCallback) {
		var self = this;
		if (self.options.unpinUrl == undefined) {
			alert("Unpin url undefined");
		}
		else {
			$.ajax({
				type: "POST",
				url: self.options.unpinUrl,
				data: {
					GroupId: groupID
				},
				success: function(msg, callback){
					alert(msg);
					successCallback();
				}
			});
		}
	},
	
	deleteSubjectTerms: function(subjectID){
		var self = this;
		$('.'+self._subjectClass(subjectID)+':not(.schedule-fixed,.schedule-pinned)').remove();
		for(var i=0; i<self.dayColumnList.length; i++){
			self._orderColumnContent(self.dayColumnList[i]);
		}
	},
	
	_toolBox: function(divTerm) {
		var self = this,
			$toolBox = $('<div></div>')
				.append($('<a>Pin</a>')
					.addClass('toolPin')
					.click(function(){
						self._ajaxGroupPin(
							divTerm.attr('groupid'),
							function() {
								$('.'+self._groupClass(divTerm.attr('groupid'))).each(function(){
									self._makeTermPinned($(this));
								});
							}
						);
					}))
				.append($('<a>UnPin</a>')
					.addClass('toolUnPin')
					.click(function(){
						self._ajaxGroupUnpin(
							divTerm.attr('groupid'),
							function() {
								$('.'+self._groupClass(divTerm.attr('groupid'))).each(function(){
									self._makeTermUnPinned($(this));
								});
							}
						);
					}));
		return $toolBox;
	},
	
	_addDivTerm: function(divTerm) {
		var self = this;
		
		if(self.subjectList[divTerm.attr('subjectid')] == undefined) {
			self.subjectList[divTerm.attr('subjectid')] = { boxClass : self._nextBoxClass() };
		}
		
		$('<div></div>')
			.addClass('box ' + self.subjectList[divTerm.attr('subjectid')].boxClass) 
			.append($('<div></div>')
				.addClass('middle')
				.append(divTerm.html())
				.append(self._toolBox(divTerm)))
			.appendTo(divTerm
				.empty()
				.addClass('schedule-group-term')
				.addClass(self._subjectClass(divTerm.attr('subjectid')))
				.addClass(self._groupClass(divTerm.attr('groupid')))
				.attr('id', self._termEntityId(divTerm.attr('groupid'), divTerm.attr('termid')))
				.css({
					height: self._termHeight(parseInt(divTerm.attr('minutes'))),
					top: self._minuteAbsoluteTop(parseInt(divTerm.attr('from')))})
				.appendTo(this.dayColumnList[parseInt(divTerm.attr('day'))]));
		
		if(divTerm.attr('status') === 'fixed'){
			self._makeTermFixed(divTerm);
		}
		else if(divTerm.attr('status') === 'pinned'){
			self._makeTermPinned(divTerm);
		}
		else {
			self._makeTermUnPinned(divTerm);
		}
				
		this._orderColumnContent(this.dayColumnList[parseInt(divTerm.attr('day'))]);
	},
	
	_termHeight: function(minutes) {
		var o = this.options;
		return minutes*o.cellHeight/o.minutesPerCell - 5;
	},
	
	_minuteAbsoluteTop: function(minute_of_day) {
		var o = this.options;
		return (minute_of_day-o.startMinute)*o.cellHeight/o.minutesPerCell;
	},
	
	_orderColumnContent: function(column) {
		
		var self = this,
			lastOccHourInCol = [0],
			termsList = column.children('.schedule-group-term').get();
		
		termsList.sort(function(a, b){
			var startA = parseInt($(a).attr('from')),
		   	 	startB = parseInt($(b).attr('from'));
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
