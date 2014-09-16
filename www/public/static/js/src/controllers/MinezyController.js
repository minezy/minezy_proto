

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

		this.adjustColumnHeight();
		this.getFirstColumn();
	}

	MinezyController.prototype = {


		getFirstColumn: function(e) {

			$.ajax({
				type: "GET",
				url: "http://localhost:5000/1/actors/",
				data: { limit: 10 },
				dataType: "json"
			})
			.done(function( data ) {
				var newCol = $('#template').clone();
				var row = $('#template .resultContainer:first-child').clone();

				newCol.children('.results').empty();

					$('#loader').fadeOut();

					console.log(data);



			});

		},

		adjustColumnHeight: function(e) {
			var h = 0;

			h = $(window).height() - $('header').outerHeight() - $('nav.dates').outerHeight();
			console.log($(window).height(),$('header').outerHeight(),$('nav.dates').outerHeight());
			$('.columnContainer,.column').height(h);
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

	return MinezyController;

})(jQuery,document,window, Utils);