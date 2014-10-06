

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

		this.API.getData('dates/range', {}, $.proxy(this.getDateRange,this) );

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

		getDateRange: function(data) {

			var dateFirst = new Date(data.dates.range.first.year,data.dates.range.first.month,data.dates.range.first.day,0,0,0,0);
			var dateLast = new Date(data.dates.range.last.year,data.dates.range.last.month,data.dates.range.last.day,0,0,0,0);

			this.dateSettings.minTime = dateFirst.getTime();
			this.dateSettings.maxTime = dateLast.getTime();

			this.colManager.setDates(this.dateSettings);
			this.colManager.addColumn('contacts',{'limit':20});

		},

		handleScroll: function(e) {
		},


		handleResize: function(e) {
		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return MinezyController;

})(jQuery,document,window, Utils);