

App.ColumnController = ( function($,document,window, U) {


	function ColumnController(settings) {
		//console.log('COLUMN MANAGER INIT');

		this.columns = [];
		this.activeColumn = -1;
		this.activeRow = -1;
		this.totalColWidth = 0;
		this.path = ['root'];
		this.at = new App.ActionTree();
		this.settings = settings;

		$(window).resize( $.proxy( this.handleResize, this ) );

		this.adjustColumnHeight();

		//setup the dates
		var sd = new Date(this.settings.minTime);
		var ed = new Date(this.settings.maxTime);

		$('.optionContainer.dates .year').empty();
		$('.optionContainer.dates .year').append('<option value="--">--</option>');
		for( var y = sd.getFullYear(); y <= ed.getFullYear(); y++ ) {
			$('.optionContainer.dates .year').append('<option value="' + y + '">'+ y + '</option>');
		}

	}

	ColumnController.prototype = {

		addColumn: function(action,params) {

			var ops = this.at.getActions(this.path);
			//var action = ops[0].split('-'); //default action is the first node

			this.path.push(ops[0]);

			var new_col = new App.Column({
				'action':action,
				'params':params,
				'index':this.columns.length,
				'path':this.path,
				'columnActions':ops,
				'nodeName':ops[0],
				'maxTime': this.settings.maxTime,
				'minTime': this.settings.minTime
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

			this.path[index+1] = nodeName;

			if( this.columns.length > index )
				this.removeColumns(index+1);

		},

		columnDataRecieved: function(e,index) {

			if( index > 0 ) {
				$("#Column" + (index-1) + ' .loader').hide();
				$("#Column" + (index-1) + ' .resultContainer').eq(this.activeRow).children('.arrow').fadeIn();
			}
		},

		newColumnRequest: function(e,column,action,params,rowIndex) {

			if( this.columns[column+1] ) {
				if( this.columns.length > column+1 ) {
					this.removeColumns(column+2);
				}
				this.columns[column+1].updateAll(action,params);
			} else {
				this.addColumn(action,params);
			}

			this.activeRow = rowIndex;

			console.log(this.path);

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

			//console.log(this.totalColWidth, $('.columnContainer').innerWidth());

		},

		updateDates: function(start,end) {

			for(var i = 0; i < this.columns.length; i++ ) {
				this.columns[i].updateParams({'start':start,'end':end});
			}

		},

		removeColumns: function(rootIndex) {

			if( this.columns.length > rootIndex ) {
				var totalDelay = ( this.columns.length - rootIndex ) * 100;

				for(var i = this.columns.length-1; i >= rootIndex; i-- ) {
					this.removeColumn(i, totalDelay-(i*100) );
					this.path.pop();
				}
			}

		},

		closingColumn: function(e,index) {
			//console.log('CLOSE COLUMN: ',index);
			this.removeColumns(index);
		},

		removeColumn: function(index,delay) {

			$(this.columns[index].element).delay(delay).fadeOut( 300, $.proxy(function(){
				this.columns[index].destroy();
				this.columns.splice(index,1);
			},this));

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
				console.log( 'maxh', maxh );
			}

			if( maxh < h )
				maxh = h;

			$('.column').css('height',maxh);
		},

		handleScroll: function(e) {
		},


		handleResize: function(e) {
			this.adjustColumnHeight();
		},

		handleMediaQueryChange: function(e,width) {

		},

		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return ColumnController;

})(jQuery,document,window, Utils);