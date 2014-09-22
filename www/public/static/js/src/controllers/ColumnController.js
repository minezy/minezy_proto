

App.ColumnController = ( function($,document,window, U) {


	function ColumnController(options) {
		console.log('COLUMN MANAGER INIT');

		this.columns = [];
		this.activeColumn = -1;
		this.activeRow = -1;
		this.totalColWidth = 0;

		$(window).resize( $.proxy( this.handleResize, this ) );

		this.adjustColumnHeight();

	}

	ColumnController.prototype = {

		addColumn: function(action,params) {

			var new_col = new App.Column({'action':action,'params':params,'index':this.columns.length});
			$(new_col).on('Ready', $.proxy( this.displayColumn, this, [this.columns.length] ) );
			$(new_col).on('NewColumn', $.proxy( this.newColumnRequest, this ) );
			$(new_col).on('Closing', $.proxy( this.closingColumn, this ) );
			$(new_col).on('DataReceived', $.proxy( this.columnDataRecieved, this ) );

			this.columns.push( new_col );

		},

		columnDataRecieved: function(e,index) {

			if( index > 0 ) {
				$("#Column" + (index-1) + ' .loader').hide();
				$("#Column" + (index-1) + ' .resultContainer').eq(this.activeRow).children('.arrow').fadeIn();
			}
		},

		newColumnRequest: function(e,column,action,params,rowIndex) {

			if( this.columns[column+1] ) {
				if( this.columns.length > column+1 ) {
					this.removeColumns(column+2);
				}
				this.columns[column+1].updateAll(action,params);
			} else {
				this.addColumn(action,params);
			}

			this.activeRow = rowIndex;

		},

		displayColumn: function(params,e) {
			var index = params[0];

			if( this.columns.length > 0 ) {
				$('#loader').fadeOut();
			}

			var column = this.columns[index].element;
			var offset = index * this.columns[index].width;

			this.totalColWidth += this.columns[index].width;

			$(column).css('left',offset-80);
			$(column).hide().fadeIn(300,$.proxy(function() { 

				if( this.totalColWidth > $(window).width() ) {
					var sl = this.totalColWidth - $(window).width();
					$('.columnContainer').animate({scrollLeft:sl},300);
				}

			},this));
			$(column).css('left',offset);

			this.adjustColumnHeight();

			this.activeColumn = index;

			console.log(this.totalColWidth, $('.columnContainer').innerWidth());
			

		},

		updateDates: function(start,end) {

			for(var i = 0; i < this.columns.length; i++ ) {
				this.columns[i].updateParams({'start':start,'end':end});
			}

		},

		removeColumns: function(rootIndex) {

			if( this.columns.length > rootIndex ) {
				var totalDelay = ( this.columns.length - rootIndex ) * 100;

				for(var i = this.columns.length-1; i >= rootIndex; i-- ) {
					this.removeColumn(i, totalDelay-(i*100) );
				}
			}

		},

		closingColumn: function(e,index) {
			//console.log('CLOSE COLUMN: ',index);
			this.removeColumns(index);
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
			//console.log($(window).height(),$('header').outerHeight(),$('nav.dates').outerHeight());
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