

App.NavController = ( function( $, document, window, A, U ) {

	"use strict";

	function NavController(pageName, data) {
		console.log('NAV CONTROLLER INIT');

		this.currentPage = '';
		this.router = new U.Router();
		this.pageNotFound = false;

		this.createRoutes();

		//create the page controller
		this.pageController = this.loadController();

		//based on the page, do specific site wide transitions
		this.handleMediaQueryChange( null,$(window).width() );

		$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );
		$(window).scroll( $.proxy( this.handleScroll, this ) );

		this.handleScroll();
	}

	NavController.prototype = {

		createRoutes: function() {

			this.router.addRoutes([
				{ 'path' : '/', 'controller' : 'MinezyController' },
				{ 'path' : '.*', 'controller' : 'PageNotFoundController' }
			]);


		},

		loadController: function() {

			if( $('#404').length ) {
				this.pageNotFound = true;
			}

			try {
				var route = {};

				if( !this.pageNotFound ) {
					route = this.router.route();
				} else {
					route = this.router.getManualRoute('PageNotFoundController');
				}

				if( route ) {
					return route.createController({'shopify':this.shopify});
				} else {
					throw new Error("Undefined route: " + window.location.pathname);
				}
			} catch(err) {
				console.error(err);
			}

		},

		handleScroll: function(e) {


		},

		handleMediaQueryChange: function(e,width) {

			console.log("WIDTH: " + width);


		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return NavController;

})(jQuery,document,window,App,Utils);