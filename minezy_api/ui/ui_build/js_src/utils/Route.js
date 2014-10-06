



/* Route 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2014
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

Utils.Route = (function() {

	"use strict";

	//private properties

	function Route(path, controller) {

		// retreive options
		this.path = path;
		this.controller = controller;

	}

	//Public Functions
	Route.prototype = {

		match: function(uri) {
			var re = new RegExp( '^/?' + this.path + '/?$' );
			var matches = uri.match( re );

			//console.log('URI: ' + uri, matches, re);

			if( matches !== null ) {
				return true;
			}

			return false;
		},


		createController: function(options) {
			if ( typeof App[this.controller] !== 'undefined' ) {
    			return new App[this.controller]( options );
			} else {
				throw new Error("Controller cannot be created! ("+ this.controller +")");
			}
		}

	};

	return Route;

})();
