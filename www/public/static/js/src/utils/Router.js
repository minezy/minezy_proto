



/* Router 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2014
 *
 *  Description:
 *
 *  Input:
 *
 *  Dependancies:
 *
 *  Implementation
 *
 *
*/

Utils.Router = (function($,U) {

	"use strict";

	//private properties

	function Router(options) {

		// retreive options
		this.options = options || {};
		this.routes = [];

	}

	//Public Functions
	Router.prototype = {

		addRoute: function(path,controller){
			var r = new U.Route(path,controller);
			this.routes.push(r);
		},

		addRoutes: function(routes) {
			$.each(routes, $.proxy(function(i,route) {
				this.addRoute(route.path,route.controller);
			},this));
		},

		getManualRoute: function(controllerName) {
			var foundRoute = false;

			$.each(this.routes, function(i,route) {

				if( route.controller === controllerName ) {
					console.log('GMR FOUND ROUTE: ' + route);
					foundRoute = route;
				}
			});

			return foundRoute;
		},

		route: function() {
			var foundRoute = false;

			$.each(this.routes, function(i,route) {
				if( route.match(window.location.pathname) && !foundRoute ) {
					console.log('FOUND ROUTE: ' + route);
					foundRoute = route;
				}
			});

			return foundRoute;
		}


	};

	return Router;

})(jQuery, Utils);
