

App.MinezyController = ( function($,document,window, U) {


	function MinezyController(options) {
		console.log('MINEZY INIT');

		//init page based on size
		$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );
		$(window).resize( $.proxy( this.handleResize, this ) );

		if( !U.isTouch() ) {
			$(window).scroll( $.proxy( this.handleScroll, this ) );
		} else {
			$(window).on( 'touchmove', $.proxy( this.handleScroll, this ) );
		}

		this.settings = {};
		this.API = new App.API();

		this.API.getData('dates', {'limit':1,'order':'asc','count':'month'}, $.proxy(this.getMinDate,this) );

	}

	MinezyController.prototype = {

		getMinDate: function(data) {

			var date = new Date(data.dates.dates[0].year,data.dates.dates[0].month,1,0,0,0,0);
			this.settings.minTime = date.getTime();

			this.API.getData('dates', {'limit':1,'order':'desc','count':'month'}, $.proxy(this.getMaxDate,this) );

		},

		getMaxDate: function(data) {

			var date = new Date(data.dates.dates[0].year,data.dates.dates[0].month,1,0,0,0,0);
			this.settings.maxTime = date.getTime();

			this.colManager = new App.ColumnController(this.settings);
			this.colManager.addColumn('contacts',{'limit':20});

		},


		changeDateRange: function() {

			var sy = $('#start_date_year').val();
			var sm = $('#start_date_month').val();
			var ey = $('#end_date_year').val();
			var em = $('#end_date_month').val();

			var sd = new Date(sy, sm-1, 1, 0, 0, 0, 0);
			var ed = new Date(ey, em, 0, 0, 0, 0, 0);

			//console.log(sm,sy,sd.getTime()/1000,ed.getTime()/1000);

			if(isNaN(sd)){
				sd.setTime(0);
			}

			//console.log(sd.getTime()/1000,ed.getTime()/1000);

			this.colManager.updateDates(sd.getTime()/1000,ed.getTime()/1000);

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
		}

	};

	return MinezyController;

})(jQuery,document,window, Utils);