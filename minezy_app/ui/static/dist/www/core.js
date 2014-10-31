
/*
 * Matthew Quinn, GRAND Creative Inc.
 * Copyright 2012
 *
 * Dependancies: JQuery 1.8, easing.js
 *
*/


//create a custom namespace for our Utilities
var Utils = Utils || {};



/* Utility Funcitons,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Description:
 *    Detects various platforms environments. Mostly used for platform hacks/polyfills.
 *
 *
*/


/* Detect Android 2 */

Utils.isAndroid2 = function() {
    var ua = navigator.userAgent.toLowerCase();

  if( ua.indexOf("android 2") > -1 ) {
    return true;
  }

  return false;
};

/* Detect BlackBerry7 and under */

Utils.isBlackBerry = function() {
  var ua = navigator.userAgent.toLowerCase();


  if( ua.indexOf("blackberry") > -1 ) {
    return true;
  }

  return false;
};

/* Detect Windows Phone and under */

Utils.isWindowsPhone = function() {
  return ( navigator.userAgent.match(/(windows phone)/i) ? true : false );
};

/* Detect BlackBerry7 and under */

Utils.isiOS = function() {
  return ( navigator.userAgent.match(/(iPad|iPhone|iPod)/i) ? true : false );
};

/* Detect if the browser can play H264 mp4s */

Utils.canPlayh264 = function() {
  var v = document.createElement('video'),
      canPlayVideo = false;

  if( v.canPlayType && v.canPlayType('video/mp4').replace(/no/, '') ) {
    return true;
  }

  return false;

};

Utils.hexToRBG = function(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  console.log('yup!');
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
};

Utils.isTouch = function() {
  return 'ontouchstart' in window;
};

Utils.pixelDensity = function() {
  var dpr = 1;
  if(window.devicePixelRatio !== undefined) dpr = window.devicePixelRatio;

  return dpr;
};

Utils.hasHistoryAPI = function() {
  return !!(window.history && history.pushState);
};

Utils.validEmail =function(email) {
    var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(email);
};

;
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