

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

	}

	NavController.prototype = {

		createRoutes: function() {

			this.router.addRoutes([
				{ 'path' : '/', 'controller' : 'MinezyController' }
			]);


		},

		loadController: function() {

			if( $('#404').length ) {
				this.pageNotFound = true;
			}

			//try {
				var route = {};

				if( !this.pageNotFound ) {
					route = this.router.route();
				}

				if( route ) {
					return route.createController();
				} else {
					throw new Error("Undefined route: " + window.location.pathname);
				}
			//} catch(err) {
			//	console.error(err);
			//}

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return NavController;

})(jQuery,document,window,App,Utils);