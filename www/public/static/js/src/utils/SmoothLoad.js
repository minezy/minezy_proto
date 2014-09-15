
/* SmoothLoad 1.0,  Matthew Quinn, GRAND Creative Inc.  Copyright 2014
 *
 *  Description:
 *
 *
 *  Input:
 *
 *  Dependancies: JQuery 1.8, easing.js, Modernizer
 *
 *  Implementation
 *
*/

Utils.SmoothLoad = (function($, Utils, Modernizr) {

	"use strict";

	//private properties

	function SmoothLoad(options) {

		this.options = options || {};
		this.target = $("#" + this.options.target );
		this.links = [];
		this.currentLink = {};
		this.currentPage = this.options.startPage;
		this.previousPage = 0;

		this.url = '';
		this.url_vars = '';

		$(window).on('popstate', $.proxy(this.handlePopState, this) );

	}

	//Public Functions
	SmoothLoad.prototype = {

		initHistory: function() {

			//on load modify this exist state with the data we need to properly use the history buttons
			if( Modernizr.history ) {
				history.replaceState( { page: this.currentPage, type: 'load' }, '', window.location.pathname );
			}

		},

		addLink: function( id, url_vars ) {

			if( $('#'+id).length ) {
				var page = $('#'+id).data('page');
				var url = $('#'+id).attr('href');
				url_vars === undefined ? url_vars = {} : url_vars = url_vars;
				this.links[id] = { page: page, url: url, url_vars: url_vars };
				$('#'+id).on( 'click', { page : page }, $.proxy( this.handleChangePage, this ) );
				return true;
			}

			console.error('ERROR: Cannot create link to ID: ' + id);
			return false;

		},

		removeLink: function( id ) {

			if( id in this.links ) {
				$('#'+id).off( 'click' );
				//delete this.links[id];
				return true;
			}

			return false;
		},

		changeFromLink: function( link_id, fromHistory ) {

			//make sure the link exists
			if( !(link_id in this.links) ) return;

			this.change( this.links[link_id].page, this.links[link_id].url, this.links[link_id].url_vars );

			if( !fromHistory && Modernizr.history ) {
				history.pushState( { page: this.links[link_id].page, type: 'link', id: link_id, data: this.links[link_id].url_vars }, this.links[link_id].page, this.links[link_id].url );
			}

		},

		change: function( page, url, url_vars ) {

console.log(page, this.currentPage);
			//don't change the page if the current page was changed
			if( page == this.currentPage ) return;

			this.previousPage = this.currentPage;
			this.currentPage = page;
			this.url = url;
			this.url_vars = url_vars;

			$(this).trigger( 'navItemClicked' );

		},

		loadNewPage: function(e) {

			$(this).trigger( 'oldPageClosed', [this.previousPage] );

			//ajax call to get the new content
			$.ajax({
				type: "GET",
				dataType: 'html',
				url: this.url + "?ajax=true&" + $.param(this.url_vars),
				success : $.proxy(this.handlePageLoaded, this),

				error : function(data,b,c) {
					console.log ( "Error getting new page." );
				}

			});

		},

		handleChangePage: function(e) {

			if( Modernizr.history ) {
				e.preventDefault();
				this.changeFromLink( $(e.currentTarget).attr('id'), false );
			}

			return true;

		},

		handlePageLoaded: function(data) {

			//blow away old content
			this.target.empty();

			//inject new content
			this.target.html(data);

			$(this).trigger( 'newPageLoaded', [this.currentPage] );

		},

		handlePopState: function(e) {

			if( e.originalEvent.state ) {

				switch( e.originalEvent.state.type ) {

					case 'link':

						if(e.originalEvent.state.page != this.currentPage ) {
							this.changeFromLink( e.originalEvent.state.id, true );
						} else {
							$(this).trigger( 'pageAction', [e.originalEvent.state.data] );
						}
						break;

					case 'load':

						if(e.originalEvent.state.page != this.currentPage ) {
							this.change( e.originalEvent.state.page, window.location.pathname, {} );
						} else {
							var data = {};

							if( typeof e.originalEvent.state.data != undefined ) {
								data = e.originalEvent.state.data;
							}

							$(this).trigger( 'pageAction', data );
						}

						break;

					case 'action':

						if( e.originalEvent.state.page != this.currentPage ) {
							this.change( e.originalEvent.state.page, e.originalEvent.state.slug, e.originalEvent.state.data );
						} else {
							$(this).trigger( 'pageAction', [e.originalEvent.state.data] );
						}


						break;

				}

			}

		}

	};

	return SmoothLoad;

})(jQuery, Utils, Modernizr,document,window);
