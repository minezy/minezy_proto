
/*
 * Main 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Dependancies: JQuery >=1.8 and < 2.0
 *
 *  This is the main Javascript class for launching the app/web site.
*/


App.Main = (function($, window, document, Utils){

	"use strict";


	function Main(options) {

		// retreive options
		this.options = options || {};
		this.sitePage = this.options.page;
		this.navController;
		this.woodsData;

		$('document').ready( $.proxy( this.handleAppReady, this ) );

		this.alertFallback = false;
		if (typeof console === "undefined" || typeof console.log === "undefined") {
			console = {};
			if (this.alertFallback) {
				console.log = function(msg) {
					alert(msg);
				};
			} else {
				console.log = function() {};
			}
		}

	}


	Main.prototype = {

		handleAppReady: function() {

			//init the media query detector
			this.mq = Utils.MediaQuery.getInstance();
			this.mq.compareWidth = $('#mediaQueryDetector').width();

			$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );
			//$(window).scroll( $.proxy( this.handleScroll, this ) );

			this.woodsData = new App.WoodsData();
			this.navController = new App.NavController(this.sitePage,this.woodsData);

			//hide address bar on mobile
			//$(window).scrollTop(0);

			//avoid using the :hover pseudo class when touching elements
			if ('ontouchstart' in document) {
				$('body').removeClass('no-touch');
			}


			//this.handleMediaQueryChange(null,$(window).width());

			//$(window).scroll( $.proxy(this.handleScroll, this) );
			//$(window).resize( $.proxy(this.handleScroll, this) );

		},

		/*handleScroll: function(e) {

		},

		handleResize: function(e) {

		},

		handleMediaQueryChange: function(e,width) {

			console.log("WIDTH: " + width);

			// Do -Site Wide- specific actions when the browser is resized to a particular break point 

			if( width < 460 ) {	//PHONES VERT

			}

			if( width >= 460 && width <= 640 ) {	//PHONES HORZ

			}

			if( width < 640 ) { ///PHONES & TINY TABS - BOTH ORIENTATIONS
			}

			if( width >= 640 && width <= 1024 ) { // TABS
			}

			if( width >= 640 ) { // TABS & DESKTOP
			}

			if( width > 640 && width <= 768 ) {	//TABS VERT

			}

			if( width > 768 && width <= 1024 ) {	//TABS HORZ

			}

			if( width <= 1024 ) { //PHONES & TABS
			}

			if( width > 1024 ) { //DESKTOPS

			}

		}*/

	};

	return Main;


})(jQuery, window, document, Utils);