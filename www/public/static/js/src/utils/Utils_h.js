
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

  v.canPlayType && v.canPlayType('video/mp4').replace(/no/, '') ? canPlayVideo = true : canPlayVideo = false;

  return canPlayVideo;

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
}

Utils.pixelDensity = function() {
  var dpr = 1;
  if(window.devicePixelRatio !== undefined) dpr = window.devicePixelRatio;

  return dpr;
}

Utils.hasHistoryAPI = function() {
  return !!(window.history && history.pushState);
}


