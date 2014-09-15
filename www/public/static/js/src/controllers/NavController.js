

App.NavController = ( function($,document,window,Utils) {

	"use strict";

	function NavController(pageName, data) {
		console.log('WOODS NAV CONTROLLER INIT');

		this.pageName = pageName;
		this.mobileMenuOpen = false;
		this.galleryMenuOpen = false;
		this.woodsdata = data;
		this.fromHistory = false;

		this.smoothNav = new Utils.SmoothLoad( {
				target 		:'pageContainer',
				startPage	: this.pageName
		});

		//setup the main nav links (site wide)
		this.smoothNav.addLink( 'navLanding' );
		this.smoothNav.addLink( 'navVideos' );
		this.smoothNav.addLink( 'navVideosArchive' );
		this.smoothNav.addLink( 'navPhotos' );
		this.smoothNav.addLink( 'navPhotosArchive' );
		this.smoothNav.addLink( 'navContact' );

		//setup nav events
		$(this.smoothNav).on( 'navItemClicked', $.proxy( this.handleNavClick, this ) );
		$(this.smoothNav).on( 'newPageLoaded', $.proxy( this.setupNewPage, this ) );
		$(this.smoothNav).on( 'pageAction', $.proxy( this.handlePageActionHistory, this ) );


		//setup data
		if( !this.woodsdata.ready ) {
			$(this.woodsdata).on( 'dataReady', $.proxy( this.handleDataReady, this ) );
		}

		this.setupNewPage();

		//setup history for inital load.
		this.setupHistory();

		$('.navButton').on('click', $.proxy( this.showMainMenu, this) );
		$('.closeButton').on('click', $.proxy( this.hideMainMenu, this) );

		$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );

	}

	NavController.prototype = {

		setupHistory: function() {

			if (typeof this.pageController.initHistory == 'function') {
				this.pageController.initHistory();
			} else{
				this.smoothNav.initHistory();
			}

		},

		showMainMenu: function(e) {
			this.mobileMenuOpen = true;
			$('nav.main').show();
			$('nav.main').animate( { top: 0 }, { duration: 500, easing: 'easeOutBack', queue: false } );
		},

		hideMainMenu: function(e) {
			this.mobileMenuOpen = false;
			$('nav.main').animate( { top: '100%' }, { duration: 300, easing: 'easeInQuad', queue: false, complete: $.proxy(function(){ $('nav.main').hide(); },this) } );
		},

		setupNewPage: function() {

			//create the page controller
			this.pageController = this.loadController(this.smoothNav.currentPage);

			//based on the page, do specific site wide transitions
			this.handleMediaQueryChange( null,$(window).width() );

			//check to see if teh controller has a custom animation
			if (typeof this.pageController.animateIn == 'function') {
				this.pageController.animateIn();
			} else {
				this.animateIn();
			}

			//scroll back to the top.
			$(window).scrollTop(0);
			this.setPageTitle();
			this.highlightNav();

			// add analytics
			_gaq.push(['_trackPageview']);
			console.log(_gaq);

		},

		highlightNav: function() {

			$('nav.main a.navLink').removeClass('on');

			if( this.smoothNav.currentPage == 'Photos' || this.smoothNav.currentPage == 'PhotosArchive' || this.smoothNav.currentPage == 'Videos' || this.smoothNav.currentPage == 'VideosArchive' || this.smoothNav.currentPage == 'Gallery' ) {
				$('#navContact').animate({opacity:1});

				if( $('section.content').hasClass('photographer') ) {
					$('#navPhotos').addClass('on');
				} else if( $('section.content').hasClass('photographer_archive') ) {
					$('#navPhotosArchive').addClass('on');
				} else if( $('section.content').hasClass('director') ) {
					$('#navVideos').addClass('on');
				} else if( $('section.content').hasClass('director_archive') ) {
					$('#navVideosArchive').addClass('on');
				}

			} else if( this.smoothNav.currentPage == 'Contact' ) {
				$('#navContact').animate({opacity:0});
			}

		},

		setPageTitle : function() {

			switch( this.smoothNav.currentPage ) {
				case 'Landing':
					document.title = 'Chris Woods - Photographer & Director'
					break;
				case 'Contact':
					document.title = 'Chris Woods - Contact'
					break;
				case 'Videos':
				case 'VideosArchive':
					document.title = 'Chris Woods - Director'
					break;
				case 'Photos':
				case 'PhotosArchive':
					document.title = 'Chris Woods - Photographer'
					break;
			}

		},

		loadController: function(page) {

			if(page == 'PhotosArchive' || page == 'Photos' || page == 'Videos' || page == 'VideosArchive') {
				page = 'Thumbs';
			}

			//launch the current page's controller if its available
			if( page+"Controller" in App ) {
				return new App[page+"Controller"]( this );
			}

		},

		animateIn : function() {
			$('.'+this.smoothNav.currentPage.toLowerCase()).animate( { opacity: 1 }, { duration: 1000, ease: 'easeOutQuad', queue: false } );
		},

		animateOut : function() {
			$('.'+this.smoothNav.previousPage.toLowerCase()).animate( { opacity: 0 }, { duration: 3000, ease: 'easeInQuad', queue: false, complete: $.proxy( this.transitionPage, this ) } );
		},

		transitionPage: function(e) {

			//destroy old page controller
			$(this.pageController).off('animateOutComplete');
			this.pageController.destroy();
			delete this.pageController;

			//make the ajax call to get the HTML for the next page.
			this.smoothNav.loadNewPage();

		},

		handleNavClick: function(e) {
			this.fromHistory = true;

			//check to see if teh controller has a custom animation
			if (typeof this.pageController.animateOut == 'function') {
				this.pageController.animateOut();
				$(this.pageController).on('animateOutComplete', $.proxy( this.transitionPage, this ) );
			} else {
				this.animateOut();
			}

			this.setPageTitle();

			if(this.mobileMenuOpen) {
				this.hideMainMenu();
			}

		},

		handleDataReady: function(e) {

			if (typeof this.pageController.dataReady == 'function') {
				this.pageController.dataReady();
			}

		},


		handlePageActionHistory: function(e,data) {

			if( 'handleHistory' in this.pageController ) {
				this.pageController.handleHistory(data);
			}

		},

		handleMediaQueryChange: function(e,width) {

			$('nav.main').stop();

			if( width < 640 ) { ///PHONES & TINY TABS - BOTH ORIENTATIONS
				$('nav.main').css('top','');
				$('nav.main').hide();


				if( this.smoothNav.currentPage != 'Landing' ) {
					//show nav
					$('nav.logo').animate( { top: 0 }, { duration: 500, easing: 'easeOutQuad', queue: false } );
				} else  {
					//hide nav
					$('nav.logo').animate( { top: '-80px' }, { duration: 300, easing: 'easeInQuad', queue: false } );
				}


			}

			if( width >= 640 ) { // TABS & DESKTOP
				this.mobileMenuOpen = false;
				$('nav.main').show();

				if( this.smoothNav.currentPage != 'Landing' || parseInt($('nav.main').css('top')) < 0 ) {
					$('nav.main,nav.logo').animate( { top: '0px' }, { duration: 300, easing: 'easeInQuad', queue: false } );
				}

				$('.drawer').removeClass('on');

				if( this.smoothNav.currentPage == 'Photos' || this.smoothNav.currentPage == 'PhotosArchive' ) {
					$('.drawer.photos').addClass('on');
				} else if( this.smoothNav.currentPage == 'Videos' || this.smoothNav.currentPage == 'VideosArchive' ) {
					$('.drawer.videos').addClass('on');
				} else if( this.smoothNav.currentPage == 'Landing' ) {
					$('nav.main,nav.logo').animate( { top: '-60px' }, { duration: 300, easing: 'easeInQuad', queue: false } );
				} else if( this.smoothNav.currentPage == 'Gallery' ) {
					if(this.pageController.section == 'photographer' || this.pageController.section == 'photographer_archive') {
						//$('.drawer.photos').addClass('on');
					} else if(this.pageController.section == 'director' || this.pageController.section == 'director_archive') {
						//$('.drawer.videos').addClass('on');
					}

				}


			}

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return NavController;

})(jQuery,document,window,Utils);