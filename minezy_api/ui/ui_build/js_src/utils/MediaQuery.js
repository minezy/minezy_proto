/* MediaQuery 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Description:
 *    Injects a media query detector div on the page. When the div changes size via your css media queries
 *    it will handle any javascript that needs to be executed that is geared for that view.
 *
 *
 *  Input:
 *
 *
 *
 *  Dependancies: JQuery 1.8
 *
 *  Implementation
 *    within your css file, set the dector div width for each media query you need to detect.
 *
*/

Utils.MediaQuery = (function($){

  "use strict";

  var instantiated;


  function init (){

    //private
    var detector = $(document.createElement('div')),

        compareWidth = 0,

        handleResize = function() {

          if(detector.width() != compareWidth){

            //a change has occurred so update the comparison variable
            compareWidth = detector.width();

            $(window).trigger( 'mediaQueryChange', [ compareWidth ] );

          }

        };

    detector.attr('id','mediaQueryDetector');
    detector.css({ 'position' : 'absolute', 'top' : '-100px', 'background-color' : '#ccc',  'z-index' : 0, height: '40px' });

    $('body').prepend( detector );

    compareWidth = detector.width();

    $(window).resize( handleResize );

    //no public funcitons so return nothing
    return true;
  }

  return {
    getInstance :function(){

      if (!instantiated){
        instantiated = init();
      }

      return this;
    }
  };
})(jQuery,document,window);
