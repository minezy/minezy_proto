

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
				data: { limit: 30, field: 'TO' },
				dataType: "json"
			})
			.done(function( data ) {
				var newCol = $('#template').clone();
				var resultContainer = $(newCol).children('.results');

				resultContainer.empty();
				$('.columnContainer').append(newCol);

				$('#loader').fadeOut();

				var actors = data.actors.actor;
				var maxVal = 0;

				$.each(actors, $.proxy(function(i,v) {
					if( v.count > maxVal )
						maxVal = v.count;
				},this));

				console.log(maxVal);

				$.each(actors, $.proxy(function(i,v) {
					var newRow = $('<div class="resultContainer"><div class="bar"></div><div class="tally"></div><div class="title"></div><div class="arrow"><i class="fa fa-caret-right"></i></div></div>');

					var newBar = $(newRow).children('.bar');
					resultContainer.append(newRow);

					var rowMaxWidth = $(newCol).width() - (parseInt($(newBar).css('left'))*2);
					var size = Math.round( ( v.count / maxVal ) * rowMaxWidth );

					$(newBar).css('width',size);
					$(newRow).children('.tally').text(v.count);
					$(newRow).children('.title').text(v.email);

				},this));

				$(newCol).fadeIn();

			});

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

	return MinezyController;

})(jQuery,document,window, Utils);