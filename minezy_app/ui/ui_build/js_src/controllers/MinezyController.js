

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

})(jQuery,document,window, Utils);