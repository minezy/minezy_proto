
/* PhoneMenu 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Description:
 *    animates a mobile menu much like what is popular in iOS to date. Menu will appear on the left and shift the whole site over when
 *    opened.
 *
 *  Input:
 *    element   your navigation bar that you want to move back and forth
 *    options   config options - none as of yet
 *
 *  Dependancies: JQuery 1.8, easing.js, Modernizer
 *
 *  Implementation
 *    apply the 'slide' class to any objects you want to shift over to make room for the nav menu.
 *
*/

Utils.PhoneMenu = (function($, Utils, Modernizr) {

	"use strict";

	//private properties
	var menuWidth;
	//var container;

	function PhoneMenu(options) {

		// retreive options
		this.options = options || {};

		this.direction = this.options.direction ? this.options.direction : 1;

		this.opened = false;
		//container = element;
		menuWidth = this.options.width ? this.options.width : $(window).width();

		if( Modernizr.csstransitions && !Utils.isAndroid2() && !Utils.isWindowsPhone()  ) {
			$('.slide').each( $.proxy(function(i,v) {

				$(v).css('-webkit-transition-property','-webkit-transform');
				$(v).css('-moz-transition-property','-moz-transform');
				$(v).css('-o-transition-property','-o-transform');
				$(v).css('transitionDuration','250ms');
				//$(this).css('transitionTimingFunction','cubic-bezier(0.175, 0.885, 0.320, 1.275)');
				$(v).css('transitionTimingFunction','ease');

				if( i === 1 ) { //fire the end transition only once.
					$(v).on('webkitTransitionEnd', $.proxy( this.animateComplete, this) );
					$(v).on('msTransitionEnd', $.proxy( this.animateComplete, this) );
					$(v).on('oTransitionEnd', $.proxy( this.animateComplete, this) );
					$(v).on('transitionEnd', $.proxy( this.animateComplete, this) );
				}

			},this ) );
		}

	}

	//Public Functions
	PhoneMenu.prototype = {

		setMenuWidth: function(w){
			menuWidth = w;
			if(this.opened)
				this.moveMenu(menuWidth);
		},

		setDirection: function(d) {
			this.direction = d;
		},

		moveMenu : function(distance) {

		$('.slide').each( $.proxy( function(i,v) {

				if( Modernizr.csstransitions && !Utils.isAndroid2() && !Utils.isWindowsPhone()  ) {
				if( Modernizr.csstransforms3d )
					$(v).css('transform','translate3d(' + ( this.direction * distance ) + 'px,0,0)' );
				else
					$(v).css('transform','translateX(' + ( this.direction * distance ) + 'px)' );
			} else {
				$(v).stop();

				//run the complete function once.
				if( i === 0 ) {
					$(v).animate( { left: ( this.direction * distance ) + "px" }, { duration: 250, complete: this.animateComplete, queue: false } );
				} else {
					$(v).animate( { left: ( this.direction * distance ) + "px" }, { duration: 250, queue: false } );
				}

			}

			}, this ) );


		},

		animateComplete : function(e) {
			console.log('COMPLETE', this.opened);
			if( this.opened )
				$(this).trigger('openComplete');
			else
				$(this).trigger('closeComplete');
		},

		toggle: function() {

			if( this.opened )
				this.close();
			else
				this.open();
		},

		open: function() {
			this.opened = true;
			this.moveMenu(menuWidth);
		},

		close: function() {
			this.opened = false;
			this.moveMenu(0);
		}

	};

	return PhoneMenu;

})(jQuery, Utils, Modernizr,document,window);
