
/*
 * Main 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Dependancies: JQuery >=1.8 and < 2.0
 *
 *  This is the main Javascript class for launching the app/web site.
*/

//create a custom namespace for our app
var App = App || {};


App.Main = (function(window, document, $, App, Utils){

	"use strict";

	function Main() {

		this.navController = {};

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

			this.navController = new App.NavController();

			//avoid using the :hover pseudo class when touching elements
			if ('ontouchstart' in document) {
				$('body').removeClass('no-touch');
			}

		}

	};

	return Main;


})(window, document, jQuery, App, Utils);