
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


App.Main = (function(window, document, $, App, Utils){

	"use strict";

	function Main() {

		this.navController = {};

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

			this.navController = new App.NavController();

			//avoid using the :hover pseudo class when touching elements
			if ('ontouchstart' in document) {
				$('body').removeClass('no-touch');
			}

		}

	};

	return Main;


})(window, document, jQuery, App, Utils);;

App.Column = ( function($,document,window, U) {

	function Column(options) {
		//console.log('COLUMN INIT > ', options);

		this.API = new App.API();
		this.at = new App.ActionTree();
		this.HTMLFactory = new App.HTMLFactory();
		this.index = options.index;
		this.element = null;
		this.active = false;
		this.params = $.extend({},options.params);
		this.action = options.action;
		this.subaction = options.subaction;
		this.columnActions = options.columnActions;
		this.path = options.path;
		this.optionsOpen = false;
		this.colName = '#Column';
		this.width = 340;
		this.childOptions = this.at.getActions(this.path);
		this.nodeName = options.nodeName;
		this.minTime = options.minTime;
		this.maxTime = options.maxTime;
		this.page = 1;
		this.scrollPos= 0;
		this.account = options.account;

		this.setupColumn();

		this.API.getData(this.account,this.action, this.params, $.proxy(this.receivedData,this) );


	}

	Column.prototype = {

		setupColumn: function() {

			this.element = $('#template').clone();
			$(this.element).hide();
			$(this.element).attr('id','Column'+this.index);
			$('.columnContainer').append(this.element);
			this.colName = this.colName + this.index;

			var resultContainer = $( this.colName + ' .results');
			resultContainer.empty();

			$( this.colName + ' .loader').hide();
			$( this.colName + ' .showMore').hide();

			$( this.colName + ' .searchFilter').on('change',$.proxy( this.searchFilter, this ) );
			$( this.colName + ' .showMore').on('click',$.proxy( this.getMoreRows, this ) );

			if( this.action === 'emails/meta' ) {
				$( this.colName + ' .searchFilter').hide();
			} else {
				$( this.colName + ' .emailTitle').hide();
			}

			this.setColumnActions();
			this.setFilterOptions();

			//hide or show close button
			if( this.index === 0 ) {
				$(this.colName + ' a.closeButton').hide();
			} else {
				$(this.colName + ' a.closeButton').on( 'click', $.proxy(this.handleColumnClose,this) );
			}

		},


		handleColumnClose: function(e) {
			$(this).trigger('Closing',[this.index]);
		},

		setColumnActions: function() {

			$( this.colName + ' .searchFilter').empty();

			for(var i = 0; i<this.columnActions.length;i++) {
				var opParam = this.columnActions[i].split('-');
				var selected = '';
				if(i===0){
					selected = ' selected';
				}

				if(this.columnActions[i] == 'contacts-right') {
					opParam[0] = 'Observers';
				}

				var option = '<option value="'+this.columnActions[i]+'" '+selected+'>'+opParam[0]+'</option>';
				$( this.colName + ' .searchFilter').append(option);
			}

		},

		searchFilter: function() {

			delete this.params.page;
			this.page = 1;
			this.setFilterOptions();
			this.searchColumn();

		},

		setFilterOptions: function() {

			this.nodeName = $( this.colName + ' .searchFilter').val();
			var opParam = this.nodeName.split('-');
			var val = opParam[0];
			var options;

			$( this.colName + ' .additionalOptions a').off('click');

			if( val === 'contacts' ) {
				options = $('#template .searchOptionWidgets .contacts').clone();

				$( this.colName + ' .additionalOptions').empty();
				$( this.colName + ' .additionalOptions').append(options);
				$( this.colName + ' .keyword').on('focus',$.proxy( this.searchFocus, this ) );
				$( this.colName + ' .keyword').on('blur',$.proxy( this.searchBlur, this ) );

				if( this.params.rel ) {
					$( this.colName + ' .additionalOptions .relationship').remove();
				}

			} else if( val === 'emails' ) {
				options = $('#template .searchOptionWidgets .emails').clone();

				$( this.colName + ' .additionalOptions').empty();
				$( this.colName + ' .additionalOptions').append(options);
				$( this.colName + ' .keyword').on('focus',$.proxy( this.searchFocus, this ) );
				$( this.colName + ' .keyword').on('blur',$.proxy( this.searchBlur, this ) );
			} else if( val === 'dates' ) {
				console.log(opParam);
				if( !opParam[1] || opParam[1] != 'day' ) {
					options = $('#template .searchOptionWidgets .dates').clone();

					$( this.colName + ' .additionalOptions').empty();
					$( this.colName + ' .additionalOptions').append(options);

					$( this.colName + ' .start_date_year').on('change',$.proxy( this.searchColumn, this ) );

					//$( this.colName + ' .end_date_year').val( new Date().getFullYear() );
					//$( this.colName + ' .end_date_month').val( new Date().getMonth()+1 );
				} else {
					$( this.colName + ' .additionalOptions').empty();
					$( this.colName + ' .start_date_year').off('change');
				}
			} else if( val === 'words' ) {
				$( this.colName + ' .additionalOptions').empty();
			} else if( val === 'cliques' ) {
				$( this.colName + ' .additionalOptions').empty();
			} else if( val === 'observers' ) {
				$( this.colName + ' .additionalOptions').empty();
			}

			//$( this.colName + ' .searchOptions a').on('click',$.proxy( this.searchColumn, this ) );
			$( this.colName + ' .additionalOptions a').on('click',$.proxy( this.searchColumn, this ) );

		},

		searchColumn:function() {

			console.log('SEARCHING!',this.action, this.params);

			if( this.page == 1 ) {
				$( this.colName + ' .loader' ).fadeIn();
				$(this.colName + ' .showMore').hide();
			}

			var params = $.extend({},this.params);

			this.nodeName = $( this.colName + ' .searchFilter').val();
			var opParam = this.nodeName.split('-');

			if( this.action !== this.nodeName ) {
				this.action = opParam[0];
			}

			var keyword = '';

			//field
			if( this.action == 'contacts') {

				keyword = $( this.colName + ' .additionalOptions .keyword').val();

				if( keyword !== '' && keyword !== 'enter keyword'  ) {
					params.keyword = keyword;
				} else {
					delete params.keyword;
				}

				if( opParam[1] ) {
					//params.count = 'to';
				} else {
					//params.count = 'to|cc|bcc|sent';
				}

				if( !params.rel ) {
					params.rel = $( this.colName + ' .additionalOptions select.relationship' ).val();
				} else if ( $( this.colName + ' .additionalOptions select.relationship' ).val() ) {
					if( params.rel != $( this.colName + ' .additionalOptions select.relationship' ).val() ) {
						params.rel = $( this.colName + ' .additionalOptions select.relationship' ).val();
					}
				}

				if( params.count )
					delete params.count;

				if( !params.start )
					delete params.end;

				if( params.rel == 'any' )
					delete params.rel;

				params.order = 'desc';

			} else if( this.action == 'emails' ) {

				keyword = $( this.colName + ' .additionalOptions .keyword').val();

				if( keyword !== '' && keyword !== 'enter keyword' && keyword !== this.params.keyword ) {
					params.keyword = keyword;
				} else {
					delete params.keyword;
				}

				params.order = 'asc';

			} else if( this.action == 'dates' ) {

				if(opParam[1] === 'to') {
					opParam.pop();
				}

				if( !opParam[1] ) {
					var sy = $( this.colName + ' .start_date_year').val();
					/*var sm = $( this.colName + ' .start_date_month').val();
					var ey = $( this.colName + ' .end_date_year').val();
					var em = $( this.colName + ' .end_date_month').val();
					var sd,ed;

					if( sm !== '' && sy !== '' ) {
						sd = new Date(sy, sm-1, 1, 0, 0, 0, 0);

						if( sd.getTime() < 0){
							sd.setTime(0);
						}

						params.start = sd.getTime()/1000;
					}


					if( em !== '' && ey !== '' ) {
						ed = new Date(ey, em, 0, 0, 0, 0, 0);

						params.end = ed.getTime()/1000;
					}*/

					if( sy !== '' ) {
						sd = new Date(sy, 0, 1, 0, 0, 0, 0);

						params.year = sy;
					} else {
						delete params.year;
					}


					params.count = 'MONTH';
				} else {
					params.order = 'asc';
					params.start = this.params.start;
					params.end = this.params.end;
					params.count = opParam[1];
				}

			} else if( this.action == 'observers' ) {

			}

			if( !$.isEmptyObject(params) ) {

				params.limit = 20;
				if(!params.start) {
					params.start = this.params.start;
					if(!params.start) {
						delete params.end;
					}
				}

				//if(!params.end)
				//	params.end = this.params.end;

				if(this.page > 1) {
					params.page = this.page;
				}

				this.updateAll(this.action,params);

				$(this).trigger('RefreshingData',[this.index,this.nodeName]);

				this.path[this.index+1] = this.nodeName;
				this.childOptions = this.at.getActions(this.path);
			}

		},

		searchFocus: function(e) {

			var elm = $( this.colName + ' .keyword');
			elm.removeClass('error');

			if( elm.val() === 'enter keyword' ) {
				elm.val('');
			}
		},

		searchBlur: function(e) {

			var elm = $( this.colName + ' .keyword');

			if( elm.val() === '' ) {
				elm.val('enter keyword');
			} else {
				elm.removeClass('error');
			}
		},

		receivedData: function(data) {

			var resultContainer = $(this.colName + ' .results');
			var rows = {};
			var maxVal = 0;

			$(this).trigger('DataReceived',[this.index]);


			if( this.action == 'contacts' ) {
				rows = data.contacts.contact;
			} else if( this.action == 'dates' ) {
				rows = data.dates.dates;
			} else if( this.action == 'emails' ) {
				rows = data.emails.email;
			} else if( this.action == 'emails/meta' ) {
				rows = data.emails.email;
			} else if( this.action == 'words' ) {
				rows = data.words.word;
			} else if( this.action == 'cliques' ) {
				rows = data;
			} else if( this.action == 'observers' ) {
				rows = data;
			}


			if(this.page == 1)
				$(resultContainer).hide();

			if( rows.length === 0 && this.page == 1 ) {
				resultContainer.append( this.HTMLFactory.generateNoResults() );
			} else {

				if( this.action == 'emails/meta' ) {
					this.renderEmails(rows);
				} else {
					this.renderRows(rows);
				}

			}

			//fade in column
			if(this.page == 1)
				$(resultContainer).fadeIn();

			//update the controller if the column is new
			if( !this.active ) {
				this.active = true;
				$(this).trigger('Ready');
			} else {
				$(this).trigger('Updated');
			}

			$( this.colName + ' .loader' ).fadeOut();
			$( this.colName + ' .scrollContainer' ).scrollTop(this.scrollPos);

		},

		renderEmails: function(email) {
			var resultContainer = $(this.colName + ' .results');

			resultContainer.append( this.HTMLFactory.generateEmail( email,this.params ) );

			$( this.colName ).addClass('wider');

		},

		renderRows: function(rows) {

			var resultContainer = $(this.colName + ' .results');
			var maxVal = 0;

			for(var i = 0; i < rows.length;i++) {
				resultContainer.append( this.HTMLFactory.generateRow( this.action, this.params, rows[i] ) );
			}

			var bars = resultContainer.children('.resultContainer');

			for(i = 0; i < bars.length;i++) {
				var barVal = parseInt($(bars[i]).children('.tally').text());
				if( barVal > maxVal )
					maxVal =  barVal;
			}

			var rowClicked = 0;
			for(i = 0; i < bars.length;i++) {

				var barVal2 = parseInt($(bars[i]).children('.tally').text());
				var bar = resultContainer.children('.resultContainer').eq(i).children('.bar');
				var rowMaxWidth = $(this.element).width() - (parseInt($(bar).css('left'))*2);
				var size = Math.round( ( barVal2 / maxVal ) * rowMaxWidth );

				$(bar).css('width',size);

				if( $(bars[i]).hasClass('on') ) {
					rowClicked = i;
				}

				if( this.action == 'emails' ) {
					$(bar).css('width',rowMaxWidth);
				}

			}

			if( rowClicked ) {
				resultContainer.children('.resultContainer').addClass('dim');
				resultContainer.children('.resultContainer').eq(rowClicked).removeClass('dim');
			}


			//enable row clicking
			count=0;
			$( this.colName + ' .resultContainer').each($.proxy(function(i,v) {
				$(v).on('click',$.proxy(this.newColumnRequest,this,[count]) );
				count++;
			},this));


			if( rows.length == 20 ) {
				$( this.colName + ' .showMore' ).fadeIn();
			} else {
				$( this.colName + ' .showMore' ).hide();
			}


		},

		newColumnRequest: function(index,e) {

			$( this.colName + ' .resultContainer' ).removeClass('on');

			var row = $( this.colName + ' .resultContainer' ).eq(index);

			var key = row.children('input').val();
			var actionLock = this.childOptions[0].split('-');
			var action = '';
			var lock = '';
			var relationship = $( this.colName + ' .additionalOptions select.relationship' ).val();
			action = actionLock[0];

			if( actionLock.length > 1 ) {
				lock = actionLock[1];
			}

			var new_params = $.extend({},this.params);
			delete new_params.keyword;
			delete new_params.count;
			delete new_params.page;
			delete new_params.order;

			if( action === 'contacts' ) {

				if( this.action == 'dates' ) {
					new_params.start = key.split('-')[0];
					new_params.end = key.split('-')[1];
					//new_params.count = 'to|cc|bcc|sent';
				} else {
					new_params[lock] = key;
					new_params.count = 'to';

					if( !new_params.rel ) {
						new_params.rel = relationship;
					}
				}


			} else if( action === 'dates' ) {

				if( this.action == 'dates' ) {
					var sd = new Date();
					sd.setTime( key.split('-')[0] * 1000 );

					new_params.year = sd.getFullYear();
					new_params.month = sd.getMonth()+1;
				} else if( this.action == 'contacts' ) {

					if(this.params.left && this.params.right )
						new_params.observer = key;
					else if( this.params.left ) {
						new_params.right = key;
					}

					//new_params.count = 'to';
				} else if( this.action == 'words' ) {
					new_params.word = key;
				}

				new_params.count = 'month';

				if( lock == 'day' ) {
					new_params.order = 'asc';
					new_params.count = 'day';
					lock = '';
				}

			} else if( action === 'emails' ) {

				new_params.order = 'asc';

				if( this.action == 'dates' ) {
					new_params.start = key.split('-')[0];
					new_params.end = key.split('-')[1];
				} else if( this.action == 'contacts' ) {
					if(this.params.left && this.params.right )
						new_params.observer = key;
					else if( this.params.left )
						new_params.right = key;
					else
						new_params.left = key;
				} else if( this.action == 'emails' ) {
					new_params.id = key;
				} else if( this.action == 'words' ) {
					new_params.word = key;
				}

			} else if( action === 'emails/meta' ) {
				new_params.id = key;
				delete new_params.limit;
				//delete new_params.from;

			} else if( this.action == 'observers' ) {

			} else if( action === 'words' ) {
				if( this.action == 'dates' ) {
					new_params.start = key.split('-')[0];
					new_params.end = key.split('-')[1];
					//new_params.count = 'to|cc|bcc|sent';
				} else if( this.action == 'contacts' ) {
					if(this.params.left && this.params.right )
						new_params.observer = key;
					else if( this.params.left ) {
						new_params.right = key;
					}
				} else {
					new_params[lock] = key;
					new_params.count = 'to';

					if( !new_params.rel ) {
						new_params.rel = relationship;
					}
				}
			}

			console.log(this.index,'P-A:',new_params,action);

			$( this.colName + ' .resultContainer' ).addClass('dim');
			row.removeClass('dim');
			row.addClass('on');
			row.children('.loading').fadeIn(100);

			$(this).trigger('NewColumn',[this.index, action, new_params, index]);

		},

		getMoreRows: function() {

			//disable row clicks first
			$( this.colName + ' .resultContainer').each($.proxy(function(i,v) {
				$(v).off('click');
			},this));

			this.page++;
			this.searchColumn();

			this.scrollPos = $( this.colName + ' .scrollContainer' ).scrollTop();

		},

		removeHighlight: function() {
			$( this.colName + ' .resultContainer' ).removeClass('dim');
			$( this.colName + ' .resultContainer' ).removeClass('on');
		},

		updateAll: function(action,params) {

			this.action = action;
			this.params = $.extend( {}, params );

			if( !this.params.page ) {
				this.clearData();
			}

			if( action == 'emails/meta') {
				this.clearData();
			}


			this.API.getData(this.account, this.action, this.params, $.proxy(this.receivedData,this) );

		},

	/*	updateParams: function(params) {

			//merge the params
			this.params = $.extend( this.params, params );

			this.clearData();
			this.API.getData(this.action, this.params, $.proxy(this.receivedData,this) );

		},*/

		clearData: function() {

			$( this.colName + ' .noresults').remove();
			$( this.colName + ' .resultContainer').remove();
			$( this.colName + ' .emailContainer').remove();

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;

			$(this.element).remove();
		}

	};

	return Column;

})(jQuery,document,window, Utils);;

App.ColumnController = ( function($,document,window, U) {


	function ColumnController(account_id) {
		//console.log('COLUMN MANAGER INIT');

		this.columns = [];
		this.activeColumn = -1;
		this.activeRow = -1;
		this.totalColWidth = 0;
		this.path = ['root'];
		this.at = new App.ActionTree();
		this.dateSettings = {};
		this.account = account_id;

		$(window).resize( $.proxy( this.handleResize, this ) );

		this.adjustColumnHeight();

		$('#loader').fadeIn();

	}

	ColumnController.prototype = {

		setDates: function(dateSettings) {

			this.dateSettings = dateSettings;

			//setup the dates
			var sd = new Date(dateSettings.minTime);
			var ed = new Date(dateSettings.maxTime);

			$('.optionContainer.dates .year').empty();
			$('.optionContainer.dates .year').append('<option value="">all</option>');
			for( var y = sd.getFullYear(); y <= ed.getFullYear(); y++ ) {
				$('.optionContainer.dates .year').append('<option value="' + y + '">'+ y + '</option>');
			}

		},

		addColumn: function(action,params) {

			var ops = this.at.getActions(this.path);
			//var action = ops[0].split('-'); //default action is the first node

			this.path.push(ops[0]);

			var new_col = new App.Column({
				'action':action,
				'params':params,
				'index':this.columns.length,
				'path':this.path.slice(0),
				'columnActions':ops,
				'nodeName':ops[0],
				'maxTime': this.dateSettings.maxTime,
				'minTime': this.dateSettings.minTime,
				'account': this.account
			});

			$(new_col).on('Ready', $.proxy( this.displayColumn, this, [this.columns.length] ) );
			$(new_col).on('Updated', $.proxy( this.updatedColumn, this ) );
			$(new_col).on('NewColumn', $.proxy( this.newColumnRequest, this ) );
			$(new_col).on('Closing', $.proxy( this.closingColumn, this ) );
			$(new_col).on('DataReceived', $.proxy( this.columnDataRecieved, this ) );
			$(new_col).on('RefreshingData', $.proxy( this.updatePath, this ) );

			this.columns.push( new_col );

		},

		updatedColumn: function(e) {
			this.adjustColumnHeight();
		},

		updatePath: function(e,index,nodeName) {

			if( nodeName != this.path[index+1] ) {

				this.path[index+1] = nodeName;

				if( this.columns.length > index )
					this.removeColumns(index+1);

			}

		},

		columnDataRecieved: function(e,index) {

			if( index > 0 ) {
				$("#Column" + (index-1) + ' .loading').hide();
				$("#Column" + (index-1) + ' .resultContainer').eq(this.activeRow).children('.arrow').fadeIn();
			}
		},

		newColumnRequest: function(e,column,action,params,rowIndex) {

			if( this.columns[column+1] ) {
				if( this.columns.length > column+1 ) {
					this.removeColumns(column+2);

					console.log('NEWCOL',column,action,params);

					//if a child column is open and you click a new row on the parent, keep the state of the child but supply the changed params
					if( this.path[column+2] != action  ) {
						//keep the old action
						action = this.columns[column+1].action;

						//keep the old count
						params.count = this.columns[column+1].params.count;

						if( this.columns[column+1].params.start && !params.start )
							params.start = this.columns[column+1].params.start;

						if( this.columns[column+1].params.end && !params.end )
							params.end = this.columns[column+1].params.end;

						//if( params.to != this.columns[column+1].params.to )
						//	params.to

					}

				}


				//


				$( this.columns[column+1].colName + ' .loader' ).fadeIn();
				this.columns[column+1].updateAll(action,params);
			} else {
				this.addColumn(action,params);
			}

			this.activeRow = rowIndex;

			//console.log(this.path);

		},

		displayColumn: function(params,e) {
			var index = params[0];

			if( this.columns.length > 0 ) {
				$('#loader').fadeOut();
			}

			var column = this.columns[index].element;
			var offset = index * this.columns[index].width;

			this.totalColWidth += this.columns[index].width;

			$(column).css('left',offset-80);
			$(column).hide().fadeIn(300,$.proxy(function() {

				if( this.totalColWidth > $(window).width() ) {
					var sl = this.totalColWidth - $(window).width();
					$('.columnContainer').animate({scrollLeft:sl},300);
				}

			},this));
			$(column).css('left',offset);

			this.adjustColumnHeight();
			this.activeColumn = index;


		},

		removeColumns: function(rootIndex) {

			if( this.columns.length > rootIndex ) {
				var totalDelay = ( this.columns.length - rootIndex ) * 100;

				for(var i = this.columns.length-1; i >= rootIndex; i-- ) {
					this.removeColumn(i, totalDelay-(i*100) );
					this.path.pop();
				}
			}

			if( rootIndex-1 >= 0 ) {
				this.columns[rootIndex-1].removeHighlight();
			}

		},

		removeColumn: function(index,delay) {

			$(this.columns[index].element).delay(delay).fadeOut( 300, $.proxy(function(){
				this.columns[index].destroy();
				this.columns.splice(index,1);
			},this));

		},

		closingColumn: function(e,index) {
			this.removeColumns(index);
		},

		adjustColumnHeight: function(e) {
			var h = 0;
			var maxh = 0;

			h = $(window).height() - $('header').outerHeight();
			//console.log($(window).height(),$('header').outerHeight(),$('nav.dates').outerHeight());
			$('.columnContainer').css('height',h);

			var cols = $('.column');
			$('.column').css('height','');

			for(var i =0;i<cols.length;i++){
				if( $(cols[i]).height() > maxh )
					maxh = $(cols[i]).height();

				var colh= h - $(cols[i]).children('.colHeader').height() - (parseInt($(cols[i]).children('.colHeader').css('padding-left'))*2);

				$(cols[i]).children('.scrollContainer').css('height',colh);

			}

			if( maxh < h )
				maxh = h;

			$('.column').css('height',h);
		},

		handleResize: function(e) {
			this.adjustColumnHeight();
		},

		destroy: function() {
			//do any clean up when destroying the section
			this.removeColumns(0);
		}

	};

	return ColumnController;

})(jQuery,document,window, Utils);;

App.HTMLFactory = ( function($,document,window, U) {

	var numDaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
	var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];


	function HTMLFactory() {
		console.log('HTML FACTORY INIT');


	}

	HTMLFactory.prototype = {

		generateNoResults: function() {

			noResults = $('#template .noresults').eq(0).clone();

			return noResults;

		},

		generateColumn: function() {

		},

		generateRow: function(action,params, data) {

			newRow = $('#template .resultContainer').eq(0).clone();

			var newBar = $(newRow).children('.bar');
			//resultContainer.append(newRow);

			$(newRow).children('.tally').text(data.count);

			if( action == 'contacts' ) {

				$(newRow).find('.title span').text(data.name);
				$(newRow).find('.title i').addClass('fa-user');
				$(newRow).children('input').val(data.email);

			} else if( action == 'dates' ) {
				var sd,ed;

				if( params.count.toUpperCase() === 'MONTH' ) {
					sd = new Date(data.year, data.month-1, 1, 0, 0, 0, 0);
					ed = new Date(data.year, data.month-1, numDaysInMonth[data.month-1], 23, 59, 59, 0);

					$(newRow).find('.title>span').text( months[data.month-1] + ', ' + data.year);
				} else if( params.count.toUpperCase() === 'DAY' ) {
					sd = new Date(data.year, data.month-1, data.day, 0, 0, 0, 0);
					ed = new Date(data.year, data.month-1, data.day, 23, 59, 59, 999);

					$(newRow).find('.title>span').text( months[data.month-1] + ' ' + data.day +', ' + data.year);
				}

				$(newRow).find('.title>i').addClass('fa-calendar');
				$(newRow).children('input').val( sd.getTime()/1000 + '-' + ed.getTime()/1000 );

			} else if( action == 'emails' ) {

					var date = new Date();
					date.setTime(data.date.utc * 1000);
					$(newRow).find('.title>span').text( date.toLocaleTimeString() + ' ' + data.subject );
					$(newRow).children('.title').attr('title', data.subject );

					$(newRow).children('input').val( data.id );
					$(newRow).find('.title i').addClass('fa-envelope');
			} else if( action == 'words' ) {
				$(newRow).find('.title span').text(data.word);
				$(newRow).find('.title i').addClass('fa-file-word-o');
				$(newRow).children('input').val(data.word);
			}

			return newRow;

		},

		generateEmail: function(data,params) {

			newEmail = $('#template .emailContainer').eq(0).clone();

			var eDate = new Date();
			eDate.setTime( data.date.utc * 1000 );

			newEmail.children('.subjectContainer').text(data.subject);
			newEmail.children('.date').text(data.date.date);
			newEmail.find('.fromContainer .name').text(data.contacts.from[0].name);
			newEmail.find('.fromContainer .email').text(data.contacts.from[0].email);

			if( data.contacts.from[0].email == params.left || data.contacts.from[0].email == params.right ) {
				newEmail.find('.fromContainer .contact').eq(0).addClass('found');
			}


			if( data.contacts.to ) {
				for(var i=0;i<data.contacts.to.length;i++ ) {
					newEmail.children('.toContainer').append(this.generateContact(data.contacts.to[i]));
					if( data.contacts.to[i].email == params.left || data.contacts.to[i].email == params.right ) {
						newEmail.find('.toContainer .contact').eq(i).addClass('found');
					}
				}
			}

			if( data.contacts.cc ) {
				for(var k=0;k<data.contacts.cc.length;k++ ) {
					newEmail.children('.ccContainer').append(this.generateContact(data.contacts.cc[k]));
					console.log(data.contacts.cc[k].email, params.observer);
					if( data.contacts.cc[k].email == params.left || data.contacts.cc[k].email == params.right || data.contacts.cc[k].email == params.observer  ) {
						newEmail.find('.ccContainer .contact').eq(k).addClass('found');
					}
				}
			} else {
				newEmail.children('.ccContainer').hide();
			}

			if( data.contacts.bcc) {
				for(var j=0;j<data.contacts.bcc.length;j++ ) {
					newEmail.children('.bccContainer').append(this.generateContact(data.contacts.bcc[j]));

					if( data.contacts.bcc[j].email == params.left || data.contacts.bcc[j].email == params.right || data.contacts.bcc[j].email == params.observer ) {
						newEmail.find('.bccContainer .contact').eq(j).addClass('found');
					}

				}
			} else {
				newEmail.children('.bccContainer').hide();
			}

			if( data.body )
				newEmail.find('.bodyContainer .bodyContent').html(data.body.replace(/(?:\r\n|\r|\n)/g, '<br />'));

			return newEmail;

		},

		generateContact: function(contact) {

			var contactContainer = $('#template .emailContainer .contact').eq(0).clone();

			if(contact.name !== 'null') {
				contactContainer.children('.name').text(contact.name);
				contactContainer.children('.email').text('<'+contact.email+'>');
			} else {
				contactContainer.children('.name').text('<'+contact.email+'>');
				contactContainer.children('.email').hide();
			}

			return contactContainer;

		},

		generateDIV: function(classes,html) {

			var newDiv = $('<div></div>');

			if( classes.length ) {
				for( var i = 0; i < classes.length;i++ ) {
					newDiv.addClass(classes[i]);
				}
			}

			newDiv.html(html);

			return newDiv;

		},


		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return HTMLFactory;

})(jQuery,document,window, Utils);;

App.MinezyController = ( function($,document,window, U) {


	function MinezyController(options) {
		console.log('MINEZY INIT');

		this.accounts = {};
		this.account = undefined;
		this.progressTimer = 0;
		this.tmpcount = 0;

		//init page based on size
		$(window).on('mediaQueryChange', $.proxy( this.handleMediaQueryChange, this ) );
		$(window).resize( $.proxy( this.handleResize, this ) );

		if( !U.isTouch() ) {
			$(window).scroll( $.proxy( this.handleScroll, this ) );
		} else {
			$(window).on( 'touchmove', $.proxy( this.handleScroll, this ) );
		}

		this.dateSettings = {};
		this.API = new App.API();

		/*if( !$.cookie('account') ) {
			this.showSettings();
		} else {
			this.API.getData(0, 'accounts', {}, $.proxy(this.checkAccount,this) );
		}*/

		this.account = 100;
		this.API.getData(0, 'accounts', {}, $.proxy(this.checkAccount,this) );

		$('.info.about .button').on('click',$.proxy(this.showInfo,this) );


	}

	MinezyController.prototype = {

		checkAccount: function(data) {
			var accts = data.accounts.account;

			for(var i =0; i < accts.length; i++ ) {
				if( accts[i].id == $.cookie('account') ) {

					this.account = $.cookie('account');
				}
			}

			if( this.account > 0 ) {
				this.loadAccount();
			} else {
				this.showSettings();
			}

		},

		initAccounts: function() {

			$('#account_id').empty();

			for(var i =0; i < this.accounts.length; i++ ) {
				var selected  = '';

				if( this.account == this.accounts[i].id )
					selected = ' selected';

				$('#account_id').append('<option value="'+this.accounts[i].id+'" '+selected+'>'+this.accounts[i].account+'</option>');
			}


		},

		showInfo: function() {

			$('.siteOverlay').fadeIn(500);

			setTimeout( $.proxy(function(){
				console.log('here');
				$('section.admin.info').removeClass('hide');
			},this), 100);

			$('section.admin.info .closeButton').on( 'click', $.proxy(this.hideInfo,this) );
			$('section.admin.info .button.ok').on( 'click', $.proxy(this.hideInfo,this) );


		},

		showSettings: function(e) {

			$('.siteOverlay').fadeIn(500);

			setTimeout( $.proxy(function(){
				console.log('here');
				$('section.admin').removeClass('hide');
			},this), 100);

			$('section.admin .closeButton,section.admin .button.cancel').on('click',$.proxy(this.hideSettings,this) );
			$('section.admin .button.ok').on('click',$.proxy(this.saveSettings,this) );

			$('section.admin .filename').hide();

			$(':file').change($.proxy(function(e){
				$('.filename').fadeIn();
				$('.filename>span').text(e.currentTarget.files[0].name);
				$('.button.ok>i').removeClass('fa-check');
				$('.button.ok>i').addClass('fa-upload');
				$('.button.ok>span').text('Upload');
				$('select.databases').prop('disabled', 'disabled');
				$('.dbSelect').addClass('disabled');

				$('section.admin .button.ok').off('click');
				$('section.admin .button.ok').on('click',$.proxy(this.uploadFile,this) );
			},this) );

			this.API.getData(0, 'accounts', {}, $.proxy(this.getAccounts,this) );

		},

		uploadFile: function(e) {

			$('section.admin .button.ok').off('click');
			$('section.admin .button.ok').addClass('disabled');
			$('.button.ok>span').text('Uploading');
			$('.button.ok>i').removeClass('fa-upload');
			$('.button.ok>i').addClass('fa-refresh');
			$('.button.ok>i').addClass('rotating');

			$('section.admin .progressBar').hide();
			$('section.admin .progressBar').slideDown();
			$('section.admin .progressBar>.bar').width(0);
			$('section.admin .progressBar>span').text('0%');

			console.log($('#uploadFile').ajaxForm());

			$('#uploadFile').ajaxSubmit({
			    beforeSend: function() {
			        var percentVal = '0%';
			        $('section.admin .progressBar>.bar').width(percentVal);
			        $('section.admin .progressBar>span').html(percentVal);
			        console.log('BEGIN UPLOAD');
			    },
			    uploadProgress: function(event, position, total, percentComplete) {
			        var percentVal = percentComplete + '%';
			        $('section.admin .progressBar>.bar').width(percentVal);
			        $('section.admin .progressBar>span').html(percentVal);
			        console.log(percentComplete);
			    },
			    success: function() {
			        var percentVal = '100%';
			        $('section.admin .progressBar>.bar').width(percentVal);
			        $('section.admin .progressBar>span').html(percentVal);
			    },
				complete: $.proxy(function(xhr) {
					if( xhr.responseText ) {

						$('section.admin .progressBar>.bar').width(0);
						$('section.admin .progressBar>span').text('0%');

						$('.button.ok>span').text('Processing');

						this.API.getData(0, 'new_account', {'file':xhr.responseText}, $.proxy(this.startProcessing,this) );

					}
				},this)
			});



		},

		startProcessing: function(data) {

			$.cookie('account', data.account, { expires: 365, path: '/' });
			this.account = data.account;
			this.tmpcount = 0;

			this.progressTimer = setInterval( $.proxy( function() { 
				this.API.getData(0, 'new_account/progress', {}, $.proxy(this.updateProcessingProgress,this) );
			},this ), 1000 );

		},

		updateProcessingProgress: function(data) {

	        var percentVal = this.tmpcount + '%';
	        $('section.admin .progressBar>.bar').width(percentVal);
	        $('section.admin .progressBar>span').html(percentVal);

	        if( this.tmpcount == 100 ) {
	        	clearInterval( this.progressTimer );

	        	this.API.getData(0, 'accounts', {}, $.proxy(this.getAccounts,this) );

	        	this.hideSettings();
	        }

			this.tmpcount += 10;


		},

		hideInfo: function() {

			$('section.admin.info .closeButton,section.admin .button.cancel').off('click');
			$('section.admin.info .button.ok').off('click');

			$('section.admin.info').addClass('hide');

			setTimeout( $.proxy(function(){
				$('.siteOverlay').fadeOut(500);
				this.resetSettings();
			},this),300);

		},

		hideSettings: function() {

			$('section.admin .closeButton,section.admin .button.cancel').off('click');
			$('section.admin .button.ok').off('click');

			$('section.admin').addClass('hide');

			$(':file').off('change');

			setTimeout( $.proxy(function(){
				$('.siteOverlay').fadeOut(500);
				this.resetSettings();
			},this),300);

		},

		resetSettings: function() {
			$('section.admin .button.ok>i').removeClass();
			$('section.admin .button.ok>i').addClass('fa fa-check');
			$('.button.ok>span').text('OK');
			$('section.admin .progressBar').slideUp();

			$('section.admin select.databases').prop('disabled', false);
			$('section.admin .dbSelect').removeClass('disabled');
		},

		saveSettings: function() {

			this.account = $('#account_id').val();
			$.cookie('account', this.account, { expires: 365, path: '/' });

			this.hideSettings();
			this.loadAccount();

		},

		getAccounts: function(data) {

			this.accounts = data.accounts.account;

			this.initAccounts();

		},

		loadAccount: function() {

			if( this.colManager ) {
				this.colManager.destroy();
				delete this.colManager;
			}

			this.colManager = new App.ColumnController(this.account);

			this.API.getData( this.account, 'dates/range', {}, $.proxy(this.getDateRange,this) );

		},

		getDateRange: function(data) {

			var dateFirst = new Date(data.dates.range.first.year,data.dates.range.first.month,data.dates.range.first.day,0,0,0,0);
			var dateLast = new Date(data.dates.range.last.year,data.dates.range.last.month,data.dates.range.last.day,0,0,0,0);

			this.dateSettings.minTime = dateFirst.getTime();
			this.dateSettings.maxTime = dateLast.getTime();

			this.colManager.setDates(this.dateSettings);
			this.colManager.addColumn('contacts',{'limit':20});

		},

		handleScroll: function(e) {
		},


		handleResize: function(e) {
		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return MinezyController;

})(jQuery,document,window, Utils);;

App.NavController = ( function( $, document, window, A, U ) {

	"use strict";

	function NavController(pageName, data) {
		console.log('NAV CONTROLLER INIT');

		this.currentPage = '';
		this.router = new U.Router();
		this.pageNotFound = false;

		this.createRoutes();

		//create the page controller
		this.pageController = this.loadController();

	}

	NavController.prototype = {

		createRoutes: function() {

			this.router.addRoutes([
				{ 'path' : '/app', 'controller' : 'MinezyController' }
			]);


		},

		loadController: function() {

			if( $('#404').length ) {
				this.pageNotFound = true;
			}

			//try {
				var route = {};

				if( !this.pageNotFound ) {
					route = this.router.route();
				}

				if( route ) {
					return route.createController();
				} else {
					throw new Error("Undefined route: " + window.location.pathname);
				}
			//} catch(err) {
			//	console.error(err);
			//}

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return NavController;

})(jQuery,document,window,App,Utils);;

App.API = ( function($,document,window, U) {


	function API() {

        this.api_root = "http://"+window.location.hostname+":5000";
		this.api_version = 1;
		this.current_call = null;

	}

	API.prototype = {

		getData: function(id,action,params,callback) {

			if(this.current_call) {
				this.current_call.abort();
				delete this.current_call;
			}

			this.current_call = $.ajax({
				type: "GET",
				url: this.constructURL(id,action,params),
				data: params,
				dataType: "json"
			})
			.done($.proxy(function( data ) {
				callback(data);
			},this));

		},

		constructURL: function(id,action,params) {
			var account = '';
			
			if( id ) {
				account = id + '/';
			}
console.log(id,account,action);
			var url = this.api_root + '/' + this.api_version + '/' + account + action ;
console.log(url);
			/*if( typeof subaction !== "string" ) {
				params = subaction;
			} else {
				url = url + '/' + subaction;
			}*/

			/*if( typeof params !== undefined ) {
				url = url + '?' + $.param(params);
			}*/

			return url;

		},


		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return API;

})(jQuery,document,window, Utils);;

App.ActionTree = ( function($,document,window, U) {

	var tree = {
		'root' : {
			'contacts' : {
				'contacts-left': {
					'dates-to': {
						'dates-day': {
							'emails-list': {
								'emails/meta' : false
							},
						},
						'emails-list': {
							'emails/meta' : false
						},
					},
					'emails-list': {
						'emails/meta' : false
					},
					'contacts-right' : {
						'dates-to': {
							'dates-day': {
								'emails-list': {
									'emails/meta' : false
								},
							},
							'emails-list': {
								'emails/meta' : false
							},
						},
						'emails-list': {
							'emails/meta' : false
						}
					},
					'words': {
						'dates-day': {
							'emails-list': {
								'emails/meta' : false
							},
							'contacts-left' : {
								'emails-list': {
									'emails/meta' : false
								}							
							}
						},
						'emails-list': {
							'emails/meta' : false
						}
					}
				},
				'words': {
					'dates-day': {
						'emails-list': {
							'emails/meta' : false
						},
						'contacts-left' : {
							'emails-list': {
								'emails/meta' : false
							}							
						}
					},
					'emails-list': {
						'emails/meta' : false
					}
				},
				'dates': {
					'dates-day': {
						'emails-list': {
							'emails/meta' : false
						},
						'contacts-left' : {
							'emails-list': {
								'emails/meta' : false
							}							
						}
					},
					'contacts-left': {
						'dates-day': {
							'emails-list': {
								'emails/meta' : false
							},
						},
						'emails-list': {
							'emails/meta' : false
						},
						'contacts-right' : false
					},
					'emails-list': {
						'emails/meta' : false
					},
				},
				'emails-list': {
					'emails/meta' : false
				}
			},
			'dates': {
				'contacts' : {
					'contacts-left': {
						'dates-day': {
							'emails-list': {
								'emails/meta' : false
							},
						},
						'emails-list': {
							'emails/meta' : false
						},
						'contacts-right' : {
							'dates-day': {
								'emails-list': {
									'emails/meta' : false
								},
							},
							'emails-list': {
								'emails/meta' : false
							},
						}
					},
					'dates-day': {
						'contacts-left': {
							'emails-list': {
								'emails/meta' : false
							},
							'contacts-right' : false
						},
						'emails-list': {
							'emails/meta' : false
						},
					},
					'emails-list': {
						'emails/meta' : false
					}
				},
				'dates-day': {
					'contacts' : {
						'contacts-left': {
							'emails-list': {
								'emails/meta' : false
							},
							'contacts-right' : false
						},
						'emails-list': {
							'emails/meta' : false
						}
					},
					'emails-list': {
						'emails/meta' : false
					},
				}
			},
			'words' : {
				'dates': {
					'dates-day': {
						'emails-list': {
							'emails/meta' : false
						},
						'contacts-left' : {
							'emails-list': {
								'emails/meta' : false
							}							
						}
					},
					'emails-list': {
						'emails/meta' : false
					},
				},
				'emails-list': {
					'emails/meta' : false
				}
			},
		}
	};


	function ActionTree() {
		//console.log('ACTION TREE INIT');
	}

	ActionTree.prototype = {

		getActions: function(node) {

			var nodeCopy = node.slice(0);
			var optTree = this.traverse(tree,nodeCopy);
			var ops = [];

			for( var key in optTree ) {
				ops.push(key);
			}

			nodeCopy = null;

			//console.log('AT-OPS: ', ops);
			return ops;

		},

		traverse: function(smallerTree,node) {
			var branch;

			if( node.length == 1 ) {
				return smallerTree[node.shift()];
			}

			branch = node.shift();
			return this.traverse(smallerTree[branch],node);
		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return ActionTree;

})(jQuery,document,window, Utils);;



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
;



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
					//console.log('GMR FOUND ROUTE: ' + route);
					foundRoute = route;
				}
			});

			return foundRoute;
		},

		route: function() {
			var foundRoute = false;

			$.each(this.routes, function(i,route) {
				if( route.match(window.location.pathname) && !foundRoute ) {
					//console.log('FOUND ROUTE: ' + route);
					foundRoute = route;
				}
			});

			return foundRoute;
		}


	};

	return Router;

})(jQuery, Utils);
