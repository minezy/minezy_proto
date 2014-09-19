

App.ColumnController = ( function($,document,window, U) {


	function ColumnController(options) {
		console.log('COLUMN MANAGER INIT');

		this.columns = [];

		$(window).resize( $.proxy( this.handleResize, this ) );

		this.adjustColumnHeight();

	}

	ColumnController.prototype = {

		addColumn: function(action,params) {

			var new_col = new App.Column({'action':action,'params':params,'index':this.columns.length});
			$(new_col).on('Ready', $.proxy( this.displayColumn, this, [this.columns.length] ) );
			$(new_col).on('NewColumn', $.proxy( this.newColumnRequest, this ) );

			this.columns.push( new_col );

		},

		newColumnRequest: function(e,column,action,params) {

			if( this.columns[column+1] ) {
				this.columns[column+1].updateAll(action,params);
			} else {
				this.addColumn(action,params);
			}

		},

		displayColumn: function(params,e) {
			var index = params[0];

			if( this.columns.length > 0 ) {
				$('#loader').fadeOut();
			}

			var column = this.columns[index].element;
			var offset = index * 340;

			$(column).css('left',offset);
			$(column).hide().fadeIn();
			$(column).css('top','0px');

			this.adjustColumnHeight();

			console.log(index,column);

		},

		updateDates: function(start,end) {

			for(var i = 0; i < this.columns.length; i++ ) {
				this.columns[i].updateParams({'start':start,'end':end});
			}

		},

		removeColumns: function(rootIndex) {

			if(!rootIndex) {
				rootIndex = 1;
			}

			if( this.columns.length > rootIndex ) {
				var totalDelay = this.columns.length * 200;

				for(var i = this.columns.length; i >= rootIndex; i-- ) {
					this.removeColumn(i, totalDelay-(i*200) );
				}
			}



		},

		removeColumn: function(index,delay) {

			$(this.columns[index].element).delay(delay).fadeOut( 300, $.proxy(function(){
				this.columns[index].destroy();
				this.columns.splice(index,1);
			},this));

		},

		adjustColumnHeight: function(e) {
			var h = 0;

			h = $(window).height() - $('header').outerHeight() - $('nav.dates').outerHeight();
			console.log($(window).height(),$('header').outerHeight(),$('nav.dates').outerHeight());
			$('.columnContainer,.column').css('min-height',h);
		},

		handleScroll: function(e) {
		},


		handleResize: function(e) {
			this.adjustColumnHeight();
		},

		handleMediaQueryChange: function(e,width) {

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return ColumnController;

})(jQuery,document,window, Utils);