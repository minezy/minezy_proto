

App.Column = ( function($,document,window, U) {

	var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
	var numDaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

	function Column(options) {
		//console.log('COLUMN INIT > ', options);

		this.API = new App.API();
		this.at = new App.ActionTree();
		this.index = options.index;
		this.element = null;
		this.active = false;
		this.params = $.extend({},options.params);
		this.action = options.action;
		this.subaction = options.subaction;
		this.columnActions = options.columnActions;
		this.path = options.path;
		this.optionsOpen = false;
		this.colName = '#Column';
		this.width = 340;
		this.childOptions = this.at.getActions(this.path);
		this.nodeName = options.nodeName;

		this.setupColumn();
		this.API.getData(this.action, this.params, $.proxy(this.recievedData,this) );


	}

	Column.prototype = {

		setupColumn: function() {

			this.element = $('#template').clone();
			var resultContainer = $(this.element).children('.results');

			resultContainer.empty();
			$('.columnContainer').append(this.element);

			$(this.element).hide();
			$(this.element).attr('id','Column'+this.index);
			this.colName = this.colName + this.index;

			$( this.colName + ' .searchMore').on('click',$.proxy( this.showMoreSearchOptions, this ) );
			$( this.colName + ' .searchOptions').hide();
			$( this.colName + ' .keyword').on('focus',$.proxy( this.searchFocus, this ) );
			$( this.colName + ' .keyword').on('blur',$.proxy( this.searchBlur, this ) );
			$( this.colName + ' .searchFilter').on('change',$.proxy( this.searchFilter, this ) );

			this.setColumnActions();

			//hide or show close button
			if( this.index === 0 ) {
				$(this.colName + ' a.closeButton').hide();
			} else {
				$(this.colName + ' a.closeButton').on( 'click', $.proxy(this.handleColumnClose,this) );
			}

		},

		updateUI: function(data) {

			$( this.colName + ' .searchAction').text(this.action);
			$( this.colName + ' .searchParams').empty();

			for (var key in this.params) {
				var filter = $('#template .searchParams span').clone();
				var param = this.params[key];

				$(filter).children('strong').text(key+": ");
				$(filter).children('em').text(param);

				$( this.colName + ' .searchParams').append(filter);
			}

		},

		handleColumnClose: function(e) {
			$(this).trigger('Closing',[this.index]);
		},

		setColumnActions: function() {

			$( this.colName + ' .searchFilter').empty();

			for(var i = 0; i<this.columnActions.length;i++) {
				var opParam = this.columnActions[i].split('-');
				var option = '<option value="'+this.columnActions[i]+'">'+this.columnActions[i]+'</option>';
				$( this.colName + ' .searchFilter').append(option);
			}

		},

		searchFilter: function() {


			this.nodeName = $( this.colName + ' .searchFilter').val();
			var opParam = this.nodeName.split('-');

			var val = opParam[0];
			var options;

			$( this.colName + ' .additionalOptions a').off('click');

			if( val === 'contacts' ) {
				options = $('#template .searchOptionWidgets .actors').clone();

				$( this.colName + ' .additionalOptions').empty();
				$( this.colName + ' .additionalOptions').append(options);
			} else if( val === 'emails' ) {
				options = $('#template .searchOptionWidgets .emails').clone();

				$( this.colName + ' .additionalOptions').empty();
				$( this.colName + ' .additionalOptions').append(options);
			} else if( val === 'dates' ) {
				options = $('#template .searchOptionWidgets .dates').clone();

				$( this.colName + ' .additionalOptions').empty();
				$( this.colName + ' .additionalOptions').append(options);

				$( this.colName + ' .end_date_year').val( new Date().getFullYear() );
				$( this.colName + ' .end_date_month').val( new Date().getMonth()+1 );

			}

			$( this.colName + ' .searchOptions a').on('click',$.proxy( this.searchColumn, this ) );
		},

		searchColumn:function() {

			console.log('SEARCHING!',this.params);

			var params = $.extend({},this.params);
			this.nodeName = $( this.colName + ' .searchFilter').val();
			var opParam = this.nodeName.split('-');

			if( this.action !== this.nodeName ) {
				this.action = opParam[0];
			}

			//field
			if( this.action == 'contacts') {

				var keyword = $( this.colName + ' .additionalOptions .keyword').val();

				if( keyword !== '' && keyword !== 'enter keyword' ) {
					$( this.colName + ' .searchOptions a').off('click');

					params.keyword = keyword;
				}

				var field = '';
				if( $( this.colName + ' .additionalOptions .field-to').is(':checked') )
					field += 'to|';
				if( $( this.colName + ' .additionalOptions .field-cc').is(':checked') )
					field += 'cc|';
				if( $( this.colName + ' .additionalOptions .field-bcc').is(':checked') )
					field += 'bcc|';
				if( $( this.colName + ' .additionalOptions .field-sent').is(':checked') )
					field += 'sent|';

				field = field.substring(0, field.length - 1);
				//console.log('FIELD: '+field,$( this.colName + ' .field-to'));
				if( field !== 'to|cc|bbc|sent')
					params.count = field;
			} else if( this.action == 'emails' ) {

			} else if( this.action == 'dates' ) {
				var sy = $( this.colName + ' .start_date_year').val();
				var sm = $( this.colName + ' .start_date_month').val();
				var ey = $( this.colName + ' .end_date_year').val();
				var em = $( this.colName + ' .end_date_month').val();

				var sd = new Date(sy, sm-1, 1, 0, 0, 0, 0);
				var ed = new Date(ey, em, 0, 0, 0, 0, 0);

				console.log(sm,sy,sd.getTime()/1000,ed.getTime()/1000);

				if( sd.getTime() < 0){
					sd.setTime(0);
				}

				console.log(sm,sy,sd.getTime()/1000,ed.getTime()/1000);

				params.start = sd.getTime()/1000;
				params.end = ed.getTime()/1000;
				params.count = 'MONTH';

				if(opParam.length > 1) {
					params.count = opParam[1];
				}

			}

			if( !$.isEmptyObject(params) ) {
				$( this.colName + ' .additionalOptions a').off('click');
				params.limit = 20;
				if(!params.start)
					params.start = this.params.start;

				if(!params.end)
					params.end = this.params.end;

				params.key = this.params.key;
				params.lock = this.params.lock;
				params.fromAction = this.params.fromAction;
				this.updateAll(this.action,params);

				$(this).trigger('RefreshingData',[this.index,this.nodeName]);
				this.path[this.index+1] = this.nodeName;
				this.childOptions = this.at.getActions(this.path);
			}

		},

		searchFocus: function(e) {

			var elm = $( this.colName + ' .keyword');
			elm.removeClass('error');

			if( elm.val() === 'enter keyword' ) {
				elm.val('');
			}
		},

		searchBlur: function(e) {

			var elm = $( this.colName + ' .keyword');

			if( elm.val() === '' ) {
				elm.val('enter keyword');
			} else {
				elm.removeClass('error');
			}
		},

		showMoreSearchOptions: function(e) {

			if(this.optionsOpen){
				$( this.colName + ' .searchOptions').slideUp();
				this.optionsOpen = false;
				$( this.colName + ' .searchMore i').addClass('fa-plus');
				$( this.colName + ' .searchMore i').removeClass('fa-minus');
			} else{
				$( this.colName + ' .searchOptions').slideDown();
				this.optionsOpen = true;
				$( this.colName + ' .searchMore i').removeClass('fa-plus');
				$( this.colName + ' .searchMore i').addClass('fa-minus');
			}

		},

		recievedData: function(data) {

			//console.log('GOT THE DATA!',data,this.active, this.colName,this.element);
			$(this).trigger('DataReceived',[this.index]);

			var rows = {};
			var maxVal = 0;
			var count = 0;
			var resultContainer = $(this.element).children('.results');

			if( this.action == 'contacts' ) {
				rows = data.contacts.contact;
			} else if( this.action == 'dates' ) {
				rows = data.dates.dates;
			} else if( this.action == 'emails' ) {
				rows = data;
			} else {
				return;
			}


			for(var i = 0; i < rows.length;i++) {
				if( rows[i].count > maxVal )
					maxVal = rows[i].count;
			}
			//console.log(maxVal);

			$(resultContainer).hide();

			for(i = 0; i < rows.length;i++) {

				var newRow = $('<div class="resultContainer"><div class="bar"></div><div class="tally"></div><div class="title"></div><div class="arrow"><i class="fa fa-caret-right"></i></div><input type="hidden" name="email" value=""><div class="loader"></div></div>');

				var newBar = $(newRow).children('.bar');
				resultContainer.append(newRow);

				var rowMaxWidth = $(this.element).width() - (parseInt($(newBar).css('left'))*2);
				var size = Math.round( ( rows[i].count / maxVal ) * rowMaxWidth );

				$(newBar).css('width',size);
				$(newRow).children('.tally').text(rows[i].count);

				if( this.action == 'contacts' ) {

					$(newRow).children('.title').text(rows[i].name);
					$(newRow).children('input').val(rows[i].email);

				} else if( this.action == 'dates' ) {
					var sd,ed;

					if( data.dates._params.count[0] === 'MONTH' ) {
						sd = new Date(rows[i].year, rows[i].month-1, 1, 0, 0, 0, 0);
						ed = new Date(rows[i].year, rows[i].month-1, numDaysInMonth[rows[i].month-1], 23, 59, 59, 0);
					} else if( data.dates._params.count[0] === 'DAY' ) {
						sd = new Date(rows[i].year, rows[i].month-1, rows[i].day, 0, 0, 0, 0);
						ed = new Date(rows[i].year, rows[i].month-1, rows[i].day, 23, 59, 59, 999);
					}

					$(newRow).children('.title').text( months[rows[i].month] + ', ' + rows[i].year);
					$(newRow).children('input').val( sd.getTime()/1000 + '-' + ed.getTime()/1000 );

				}

				count++;

			}

			this.updateUI();

			//enable row clicking
			count=0;
			$( this.colName + ' .resultContainer').each($.proxy(function(i,v) {
				$(v).on('click',$.proxy(this.newColumnRequest,this,[count]) );
				count++;
			},this));

			//fade in rows
			$(resultContainer).fadeIn();

			//enable search again
			$( this.colName + ' .additionalOptions a').on('click',$.proxy( this.searchColumn, this ) );

			//update the controller if the column is new
			if( !this.active ) {
				this.active = true;
				$(this).trigger('Ready');
			}


		},

		newColumnRequest: function(index,e) {

			$( this.colName + ' .resultContainer' ).removeClass('on');

			var row = $( this.colName + ' .resultContainer' ).eq(index);

			var key = row.children('input').val();
			var actionLock = this.childOptions[0].split('-');
			var action = '';
			var lock = '';

			action = actionLock[0];

			if( actionLock.length > 1 ) {
				lock = actionLock[1];
			}

			var new_params = $.extend({},this.params);

			if( action === 'contacts' ) {
				new_params[lock] = key;
				new_params.count = 'to|cc|bcc|sent';

			} else if( action === 'dates' ) {
				if( this.action == 'dates' ) {
					console.log('here',key);
					new_params.start = key.split('-')[0];
					new_params.end = key.split('-')[1];
				} else if( this.action == 'contacts' ) {
					new_params[lock] = key;
				}

				new_params.count = 'month';

				if( lock == 'day' ) 
					new_params.count = 'day';
			}

			/*var fromLock = '';
			if( this.params.lock ) {
				fromLock = '-' + this.params.lock;

			}*/

			//new_params.fromAction = this.action + fromLock;
			//new_params.key = key;
			//new_params.lock = lock;
			//new_params.limit = 20;


			console.log(this.index,'P-A:',new_params,action);

			row.addClass('on');
			row.children('.loader').fadeIn(100);

			$(this).trigger('NewColumn',[this.index, action, new_params, index]);

		},

		updateAll: function(action,params) {

			this.action = action;
			this.params = $.extend( {}, params );

			this.clearData();
			this.API.getData(this.action, this.params, $.proxy(this.recievedData,this) );

		},

		updateParams: function(params) {

			//merge the params
			this.params = $.extend( this.params, params );

			this.clearData();
			this.API.getData(this.action, this.params, $.proxy(this.recievedData,this) );

		},

		clearData: function() {

			$( this.colName + ' .resultContainer').remove();

		},

		handleScroll: function(e) {
		},


		handleResize: function(e) {
		},

		handleMediaQueryChange: function(e,width) {

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;

			$(this.element).remove();
		}

	};

	return Column;

})(jQuery,document,window, Utils);