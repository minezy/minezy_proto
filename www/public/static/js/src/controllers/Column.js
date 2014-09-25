

App.Column = ( function($,document,window, U) {


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
				if( key !== 'end' && key !== 'limit' && key !== 'start' ) {
					var filter = $('#template .searchParams span').clone();
					var param = this.params[key];

					$(filter).children('strong').text(key+": ");
					$(filter).children('em').text(param);

					$( this.colName + ' .searchParams').append(filter);
				}
			}

		},

		handleColumnClose: function(e) {
			$(this).trigger('Closing',[this.index]);
		},

		setColumnActions: function() {

			$( this.colName + ' .searchFilter').empty();

			for(var i = 0; i<this.columnActions.length;i++) {
				var option = '<option value="'+this.columnActions[i]+'">'+this.columnActions[i]+'</option>';
				$( this.colName + ' .searchFilter').append(option);
			}

		},

		searchFilter: function() {

			var val = $( this.colName + ' .searchFilter').val();
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
			}

			$( this.colName + ' .searchOptions a').on('click',$.proxy( this.searchColumn, this ) );
		},

		parseFilter: function(val) {

			var action = '';
			var params = {};

			var segs = val.split('/');
			this.action = segs[0];

			for(var i=1;i<segs.length;i++) {
				var psegs = segs[i].split(':');
				params[psegs[0]] = psegs[1];
			}

			return params;

		},

		searchColumn:function() {

			var params = {};


			if( this.action !== $( this.colName + ' .searchFilter').val() ) {
				this.action = $( this.colName + ' .searchFilter').val();
			}

			//field
			if( this.action == 'actors') {

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

				field = field.substring(0, field.length - 1);
				//console.log('FIELD: '+field,$( this.colName + ' .field-to'));
				if( field !== 'to|cc|bbc')
					params.field = field;
			} else if( this.action == 'emails' ) {

			} else if( this.action == 'dates' ) {

			}

			if( !$.isEmptyObject(params) ) {
				$( this.colName + ' .additionalOptions a').off('click');
				params.limit = 20;
				params.start = this.params.start;
				params.end = this.params.end;
				this.updateAll(this.action,params);
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
				rows = data;
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
				$(newRow).children('.title').text(rows[i].name);
				$(newRow).children('input').val(rows[i].email);
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
			var keyVal = row.children('input').val();

			var actionParam = this.childOptions[0].split('-');
			var action = '';
			var key = '';

			//console.log('AP:',actionParam);

			if( actionParam.length > 1 ) {
				action = actionParam[0];
				key = actionParam[1];
			}


			var new_params = {};

			if( key !== '' ) {
				new_params[key] = keyVal;
			}

			var params = $.extend(this.params,new_params);

			//console.log(this.index,'P-A:',params,action);

			row.addClass('on');
			row.children('.loader').fadeIn(100);

			$(this).trigger('NewColumn',[this.index, action, params, index]);

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