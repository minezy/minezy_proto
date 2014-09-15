

App.LandingController = ( function($,document,window,Utils) {


	function LandingController(nc) {
		console.log('LANDING INIT');

		this.navController = nc;

		this.navController.smoothNav.addLink( 'navLandVideos' );
		this.navController.smoothNav.addLink( 'navLandPhotos' );
		this.navController.smoothNav.addLink( 'navLandContact' );


		//init page based on size
		$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );
		$(window).resize( $.proxy( this.handleResize, this ) );

		if( !Utils.isTouch() ) {
			$(window).scroll( $.proxy( this.handleScroll, this ) );
		} else {
			$(window).on( 'touchmove', $.proxy( this.handleScroll, this ) );
		}

		//setup size
		this.handleMediaQueryChange(null,$(window).width());

	}

	LandingController.prototype = {

		//transition functions
		animateIn: function() {

			//animate the page in
			$('.landing').animate( { opacity: 1 }, { duration: 1000, ease: 'easeOutQuad', queue: false } );

		},

		animateOut: function() {
			console.log('landing animating out!!');
			$('.landing').animate( { opacity: 0 },
			{
				duration: 300,
				ease: 'easeInQuad',
				complete: $.proxy(
					function(){
						$(this).trigger( 'animateOutComplete' );
						console.log('landing done animating out!');
					},
					this )
			});
		},

		setBackground: function( size ) {

			var random = Math.round(Math.random() * (10 - 1) + 1);
			var path = 'bg-mobile';
			var widths = new Array(370,290,294,424,330,470,470,470,370,310,202);
			var heights = new Array(158,119,220,220,140,158,158,176,168,168,93);
			var height = 0;
			var width = 0;

			if( size === 'large' ) {
				path = 'bg-desktop';
			}


			$('section.landing').css('background-image',"url('/static/images/"+path+"/" + random + ".jpg')");

			if( $('.logo').hasClass('pageNotFound') ) {
				random = 11;
			}

			if( size === 'large' ) {
				height = heights[random-1];
				width = widths[random-1];
			} else {
				height = heights[random-1] * 0.60;
				width = widths[random-1] * 0.60;
			}


			$('.menu').css('margin-top', -((heights[random-1]+70)/2) + "px");
			$('.menu .logo').css('background-image',"url('/static/images/illustration/" + random + ".png')");
			$('.menu .logo').css({'height': height + "px",'width': width + "px" });


		},

		//standing screen size & scroll events
		handleScroll: function(e) {
		},


		handleResize: function(e) {
		},

		handleMediaQueryChange: function(e,width) {

			if( width < 640 ) {
				this.setBackground('small');
			} else {
				this.setBackground('large');
			}

			if( width >= 640 && width < 1024) {
			}

			if( width >= 1024  ) {
			}

		},

		destroy: function() {
			this.navController.smoothNav.removeLink( 'navLandVideos' );
			this.navController.smoothNav.removeLink( 'navLandPhotos' );
			this.navController.smoothNav.removeLink( 'navLandContact' );
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return LandingController;

})(jQuery,document,window,Utils);