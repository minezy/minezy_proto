
/* Scroller 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2012
 *
 *  Description:
 *    A horizontally scrolling set of dom elements. Can be swiped via or animated via calling the scroll function.
 *    Inspired in part by swipe.js
 *
 *  Input:
 *    element - this is the container element for the scroller.
 *    options:
 *      widthMod  - the width modifier. It's assumed the width will be 100% page width. This modifies that width by a % or a value (ie: 80% (% of page width) or -40px (page width - 40pixels))
 *      perpage   - how many children are on a page
 *
 *  Dependancies: JQuery 1.8, easing.js, Modernizer
 *
 *  Implementation
 *
 *
*/


Utils.Scroller = (function($, Modernizr, Utils) {

	"use strict";

	function Scroller(element,options) {
		if( !element ) return null;

		this.container = element;
		this.slideElement = $(this.container.get()[0].children[0]);

		this.updateOptions(options);

		this.perpage = 1;
		this.page = -1;
		this.prevPage = 0;
		this.nextPageThreshold = 80;
		this.minNextPageThreshold = 10;
		this.dir = 0;
		this.enabled = false;
		this.initOffset = 0;
		this.maxWidth = 0;

		this.gestureDeltaX = 0;

		if( Modernizr.csstransitions ) {
			$(this.slideElement).on( 'transitionend webkitTransitionEnd msTransitionEnd', $.proxy( this.handleTransitionEnd, this ) );
		}

		this.maxpages = this.slideElement.find('>li').length / this.perpage;

		$(window).resize( $.proxy( this.size, this ) );

		this.enable();
		this.size();

	}

	//Public Functions
	Scroller.prototype = {

		enable: function() {
			this.enabled = true;
			this.container.on( "touchstart", $.proxy( this.touchStart, this ) );
			this.container.on( "touchmove", $.proxy( this.touchMove, this ) );
			this.container.on( "touchend", $.proxy( this.touchEnd, this ) );
		},


		disable: function() {
			this.enabled = false;
			this.container.off( "touchstart" );
			this.container.off( "touchmove" );
			this.container.off( "touchend" );
		},

		updateOptions: function(options) {
			this.options = options || {};

			this.maxWidth = this.options.max ? this.options.max : 0;
			this.duration = this.options.duration ? this.options.duration : 300;
			this.peekWidth = this.options.peek ? this.options.peek : 0;
			this.tileSize = this.options.size ? this.options.size : 1;
			this.maxpages = this.slideElement.find('>li').length / this.perpage;

			this.size();
		},

		size: function() {

			/* Dom Hiarchy
			DIV: SLIDER CONTAINER
			UL: SLIDING ELEMENT
			LI: TILE CONTAINER (PAGES)
			DIV: TILE CONTENT

			Horizontal Screen Layout:
			1                    2                     3
			- LI ------ ---------- LI ----------- ------ LI -
			PEEK | PAD | PAD | CONTENT DIV | PAD | PAD | PEEK
			*/

			//Compute the desired width of the content div with respect to the slider container width
			var div_w   = Math.round( this.tileSize * this.container.width() );

			//if there is a max width option set, make sure we cap it at that number
			if( this.maxWidth > 0 && div_w > this.maxWidth )
				div_w = this.maxWidth;

			//if the peek width is 0 (no peeks) then we only have 2 pads to deal with (see 2 above w/o peeks)
			var pad_count = 2;
			if( this.peekWidth > 0 )
				pad_count = 4;

			//calculate the padding that sits on the left and right of the tile content div.
			var pad_w   = Math.round( ( this.container.width() - div_w - ( this.peekWidth * 2 ) ) / pad_count );

			//compute the li tile container width by adding two padding widths to the content div (2 in the diagram above)
			var li_w    = Math.round( div_w + ( pad_w * 2 ) );

			//calculate the initial offset of the sliding element based on the peek width (1 in the diagram above)
			var init_x  = 0;

			if( this.peekWidth > 0 )
				init_x = pad_w + this.peekWidth;


			// check to see if css transitions are supported
			if( Modernizr.csstransitions ) {
				this.slideElement.css( 'transition-duration', '0ms' );

				if( Modernizr.csstransforms3d )
					this.slideElement.css( 'transform', 'translate3d(' + init_x + 'px,0,0)' );
				else
					this.slideElement.css( 'transform', 'translateX(' + init_x + 'px)' );

				//revert to moving the element via css's left attributte
			} else {
				this.slideElement.css( 'left', init_x + "px" );
			}

			//set the page width for moving between pages and the initial offset (used in this.move and this.touchMove)
			this.width = this.liwidth = li_w;
			this.initOffset = -init_x;

			//set the slider element's width.
			this.slideElement.width( this.maxpages * (this.width+1) + 'px' );

			//set the tile container's width
			this.slideElement.find('>li').width( this.width );

			if( Utils.isAndroid2() || Utils.isBlackBerry() )
				this.slideElement.find('>li').css('margin-left','-2px');

			//this.slideElement.find('>li').css('border','solid 1px red');

			//set the tile content div's width
			this.slideElement.find('>li>div').width( div_w );

			//translate to the proper spot in
			this.move(0);

		},

		next: function() {

			if( this.page + 1 < this.maxpages ) {
				this.prevPage = this.page;
				this.page++;
				this.dir = 1;
				this.move(this.duration);
			}

		},

		prev: function() {

			if( this.page - 1 >= 0 ) {
				this.prevPage = this.page;
				this.page--;
				this.dir = -1;
				this.move(this.duration);
			}

		},

		jumpTo: function(page,dur) {

			if( page + 1 <= this.maxpages && page - 1 >= -1 ) {
				this.dir = page > this.page ? 1 : -1;
				this.prevPage = this.page;
				this.page = page;
				this.move(dur);
			}

		},

		touchStart: function(e) {

			this.oldMousePosX = e.originalEvent.touches[0].pageX;
			this.oldMousePosY = e.originalEvent.touches[0].pageY;
			this.isScrolling = undefined;
			e.stopPropagation();

		},

		touchMove: function(e) {

			// ensure swiping with one touch and not pinching
			if(e.originalEvent.touches.length > 1 || e.originalEvent.scale && e.originalEvent.scale !== 1) return;

			//get the current touch position
			var posX = e.originalEvent.touches[0].pageX;
			var posY = e.originalEvent.touches[0].pageY;

			//calculate the distance travelled since the touch started
			this.gestureDeltaX = this.oldMousePosX - posX;
			this.gestureDeltaY = this.oldMousePosY - posY;

			//only concerned with horizonal swipes, so if its a vertical swipe use the default action.
			// detect the vertical movement is the dominant delta.
			if ( typeof this.isScrolling == 'undefined') {
				this.isScrolling = !!( this.isScrolling || Math.abs(this.gestureDeltaX) < Math.abs(this.gestureDeltaY) );
			}

			//if the page isn't scrolling, calculate the distance the scroll element should move.
			if( !this.isScrolling ) {

				//stop browser scrolling.
				e.preventDefault();

				//var sliderOffset = this.page * this.width;
				var sliderOffset = (this.page * this.width) + this.initOffset;


				if( this.page < this.maxpages && Math.abs(this.gestureDeltaX) > 5 ) {  //setup swipe enforcements
					if( Modernizr.csstransitions ) {      // check to see if css transitions are supported
						this.slideElement.css( 'transition-duration', '0ms' );
						if( Modernizr.csstransforms3d )
							this.slideElement.css( 'transform', 'translate3d(' + -( sliderOffset + this.gestureDeltaX ) + 'px,0,0)' );
						else
							this.slideElement.css( 'transform', 'translateX(' + -( sliderOffset + this.gestureDeltaX ) + 'px)' );
					} else {                              //revert to moving the element via css's left attributte
						this.slideElement.css( 'left', -(sliderOffset+this.gestureDeltaX) + "px" );
					}
				}

				e.stopPropagation();

			}

		},

		touchEnd: function() {

			var sliderOffset = this.page * this.width;

			if( !this.isScrolling ) {

				if( this.gestureDeltaX < 0 && Math.abs( this.gestureDeltaX ) >= this.nextPageThreshold && this.page > 0   ) {
					this.prevPage = this.page;
					this.page--;
					this.dir = -1;
				} else if( this.gestureDeltaX > 0 && Math.abs( this.gestureDeltaX ) >= this.nextPageThreshold && this.page < this.maxpages-1 )  {
					this.prevPage = this.page;
					this.page++;
					this.dir = 1;
				}

				if( Math.abs(this.gestureDeltaX) > 5 ) {
					this.move(this.duration);
				}

				this.gestureDeltaX = 0;
			}

		},

		move: function(duration) {

			if( duration > 0 ) {
				$(this).trigger( 'scrollStart', [this.dir] );
			}

			var sliderOffset = (this.page * this.width) + this.initOffset;

			if( Modernizr.csstransitions ) {             // check to see if css transitions are supported

				this.slideElement.css( 'transition-timing-function', 'ease' );
				//this.slideElement.css( 'transition-timing-function', 'cubic-bezier(0.175, 0.885, 0.320, 1.275)' );
				this.slideElement.css( 'transition-duration', duration + 'ms' );

				if( Modernizr.csstransforms3d )
					this.slideElement.css( 'transform', 'translate3d(' + -sliderOffset + 'px,0,0)' );
				else
					this.slideElement.css( 'transform', 'translateX(' + -( sliderOffset ) + 'px)' );

			} else {    //revert to moving the element via css's left attributte

				$(this.slideElement).animate({ left: -sliderOffset }, { duration: duration,  complete: $.proxy( this.handleTransitionEnd, this) } );

			}

		},

		handleTransitionEnd: function() {
			$(this).trigger( 'scrollComplete' );
		}

	};

	return Scroller;

})(jQuery, Modernizr, Utils, document, window);



