

App.Column = ( function($,document,window, U) {


	function Column(options) {
		console.log('COLUMN INIT > ', options);

		this.API = new App.API();
		this.index = options.index;
		this.element = null;
		this.active = false;
		this.params = options.params;
		this.action = options.action;
		this.optionsOpen = false;
		this.colName = '#Column';

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
			$( this.colName + ' .searchOptions a').on('click',$.proxy( this.searchColumn, this ) );
			$( this.colName + ' .searchOptions input').on('focus',$.proxy( this.searchFocus, this ) );
			$( this.colName + ' .searchOptions input').on('blur',$.proxy( this.searchBlur, this ) );
			$( this.colName + ' .searchFilter').on('change',$.proxy( this.searchFilter, this ) );
		},

		searchFilter: function() {

			var val = $( this.colName + ' .searchFilter').val();

			$.extend(this.params,this.parseFilter(val) );

			this.updateParams();

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


			var keyword = $( this.colName + ' .searchOptions input').val();

			console.log('search',keyword);

			if( keyword !== '' && keyword !== 'enter keyword' ) {
				$( this.colName + ' .searchOptions a').off('click');

				var params = {'keyword':keyword};
				this.updateParams(params);
			}

		},

		searchFocus: function(e) {
			console.log('focus');
			var elm = $( this.colName + ' .searchOptions input');
			elm.removeClass('error');

			if( elm.val() === 'enter keyword' ) {
				elm.val('');
			}
		},

		searchBlur: function(e) {
			console.log('blur');
			var elm = $( this.colName + ' .searchOptions input');

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
				$( this.colName + ' .searchMore i').addClass('fa-search-plus');
				$( this.colName + ' .searchMore i').removeClass('fa-search-minus');
			} else{
				$( this.colName + ' .searchOptions').slideDown();
				this.optionsOpen = true;
				$( this.colName + ' .searchMore i').removeClass('fa-search-plus');
				$( this.colName + ' .searchMore i').addClass('fa-search-minus');
			}

		},

		recievedData: function(data) {

			console.log('GOT THE DATA!',data,this.active);

			var actors = data.actors.actor;
			var maxVal = 0;
			var count = 0;
			var resultContainer = $(this.element).children('.results');

			$.each(actors, $.proxy(function(i,v) {
				if( v.count > maxVal )
					maxVal = v.count;
			},this));

			console.log(maxVal);

			$(resultContainer).hide();

			$.each(actors, $.proxy(function(i,v) {
				var newRow = $('<div class="resultContainer"><div class="bar"></div><div class="tally"></div><div class="title"></div><div class="arrow"><i class="fa fa-caret-right"></i></div><input type="hidden" name="email" value=""></div>');

				var newBar = $(newRow).children('.bar');
				resultContainer.append(newRow);

				var rowMaxWidth = $(this.element).width() - (parseInt($(newBar).css('left'))*2);
				var size = Math.round( ( v.count / maxVal ) * rowMaxWidth );

				$(newBar).css('width',size);
				$(newRow).children('.tally').text(v.count);
				$(newRow).children('.title').text(v.name);
				$(newRow).children('input').val(v.email);
				count++;

			},this));

			//enable row clicking
			$( this.colName + ' .resultContainer').each($.proxy(function(i,v) {
				$(v).on('click',$.proxy(this.newColumnRequest,this,[i]) );
			},this));

			//fade in rows
			$(resultContainer).fadeIn();

			//enable search again
			$( this.colName + ' .searchOptions a').on('click',$.proxy( this.searchColumn, this ) );

			//update the controller if the column is new
			if( !this.active ) {
				this.active = true;
				$(this).trigger('Ready');
			}


		},

		newColumnRequest: function(index,e) {

			$( this.colName + ' .resultContainer' ).removeClass('on');

			var row = $( this.colName + ' .resultContainer' ).eq(index);
			var email = row.children('input').val();
			var action = 'actors';
			var params = {'from':email,'start':this.params.start,'end':this.params.end,'limit':this.params.limit};

			row.addClass('on');

			$(this).trigger('NewColumn',[action,params]);

		},

		updateParams: function(params) {
console.log('HERE!');
			//merge the params
			$.extend( this.params, params );

			this.clearData();
			this.API.getData(this.action, this.params, $.proxy(this.recievedData,this) );

		},

		clearData: function() {

			$('.resultContainer').fadeOut( 100, function(){ this.remove(); } );

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