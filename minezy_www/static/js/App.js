
/*
 * Main 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Dependancies: JQuery >=1.8 and < 2.0
 *
 *  This is the main Javascript class for launching the app/web site.
*/

//create a custom namespace for our app
var App = App || {};


App.Main = (function(window, document, $, App){

	"use strict";

	function Main() {


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

			//avoid using the :hover pseudo class when touching elements
			if ('ontouchstart' in document) {
				$('body').removeClass('no-touch');
			}


			$('#mce-EMAIL').on('focus',function(e) {
				$('#mce-EMAIL').removeClass('error');

				if( $('#mce-EMAIL').val() === 'Type your e-mail address here' ) {
					$('#mce-EMAIL').val('');
				}
			});

			$('#mce-EMAIL').on('blur',function(e) {
				if( $('#mce-EMAIL').val() === '' ) {
					$('#mce-EMAIL').val('Type your e-mail address here');
				} else if( !Utils.validEmail($('#mce-EMAIL').val() ) ) {
					$('#mce-EMAIL').addClass('error');
				} else {
					$('#mce-EMAIL').removeClass('error');
				}
			});

			$('#subscribeButton').on('click',function(e) {

				if( !Utils.validEmail( $('#mce-EMAIL').val() ) ) {
					$('#mce-EMAIL').addClass('error');
					e.preventDefault();
					return;
				}

				$('#mce-EMAIL').removeClass('error');

				$('#mc-embedded-subscribe-form').submit();
				$('#mce-EMAIL').val('Type your e-mail address here');
			});



		}

	};

	return Main;


})(window, document, jQuery, App);