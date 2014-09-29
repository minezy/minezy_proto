

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

		this.dateSettings = {};
		this.API = new App.API();
		this.colManager = new App.ColumnController();

		this.API.getData('dates', {'limit':1,'order':'asc','count':'month'}, $.proxy(this.getMinDate,this) );

	}

	MinezyController.prototype = {

		getMinDate: function(data) {

			var date = new Date(data.dates.dates[0].year,data.dates.dates[0].month,1,0,0,0,0);
			this.dateSettings.minTime = date.getTime();

			this.API.getData('dates', {'limit':1,'order':'desc','count':'month'}, $.proxy(this.getMaxDate,this) );

		},

		getMaxDate: function(data) {

			var date = new Date(data.dates.dates[0].year,data.dates.dates[0].month,1,0,0,0,0);
			this.dateSettings.maxTime = date.getTime();

			this.colManager.setDates(this.dateSettings);
			this.colManager.addColumn('contacts',{'limit':20});

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