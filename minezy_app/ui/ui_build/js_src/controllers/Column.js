

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
				$( this.colName + ' .keyword').on('focus',$.proxy( this.searchFocus, this ) );
				$( this.colName + ' .keyword').on('blur',$.proxy( this.searchBlur, this ) );
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
				} else if( action === 'words' ) {
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

})(jQuery,document,window, Utils);