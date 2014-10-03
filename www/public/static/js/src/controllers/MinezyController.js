

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

		$('.account .button').on('click',$.proxy(this.showSettings,this) );


	}

	MinezyController.prototype = {

		showSettings: function(e) {

			$('.siteOverlay').fadeIn(500);

			setTimeout( $.proxy(function(){
				console.log('here');
				$('section.admin').removeClass('hide');
			},this), 100);

			$('section.admin .closeButton,section.admin .button.cancel').on('click',$.proxy(this.hideSettings,this) );
		},

		hideSettings: function() {

			$('section.admin .closeButton,section.admin .button.cancel').off('click');

			$('section.admin').addClass('hide');

			setTimeout( $.proxy(function(){
				$('.siteOverlay').fadeOut(500);
			},this),300);

		},

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