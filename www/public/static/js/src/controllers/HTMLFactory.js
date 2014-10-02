

App.HTMLFactory = ( function($,document,window, U) {

	var numDaysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
	var months = ["January","February","March","April","May","June","July","August","September","October","November","December"];


	function HTMLFactory() {
		console.log('HTML FACTORY INIT');


	}

	HTMLFactory.prototype = {

		generateColumn: function() {

		},

		generateRow: function(action,params, data) {

			newRow = $('#template .resultContainer').eq(0).clone();

			var newBar = $(newRow).children('.bar');
			//resultContainer.append(newRow);

			$(newRow).children('.tally').text(data.count);

			if( action == 'contacts' ) {

				$(newRow).children('.title').text(data.name);
				$(newRow).children('input').val(data.email);

			} else if( action == 'dates' ) {
				var sd,ed;

				if( params.count.toUpperCase() === 'MONTH' ) {
					sd = new Date(data.year, data.month-1, 1, 0, 0, 0, 0);
					ed = new Date(data.year, data.month-1, numDaysInMonth[data.month-1], 23, 59, 59, 0);

					$(newRow).children('.title').text( months[data.month-1] + ', ' + data.year);
				} else if( params.count.toUpperCase() === 'DAY' ) {
					sd = new Date(data.year, data.month-1, data.day, 0, 0, 0, 0);
					ed = new Date(data.year, data.month-1, data.day, 23, 59, 59, 999);

					$(newRow).children('.title').text( months[data.month-1] + ' ' + data.day +', ' + data.year);
				}

				$(newRow).children('input').val( sd.getTime()/1000 + '-' + ed.getTime()/1000 );

			} else if( action == 'emails' ) {

					var date = new Date();
					date.setTime(data.date.utc * 1000);
					$(newRow).children('.title').text( date.toLocaleTimeString() + ' ' + data.subject );
					$(newRow).children('.title').attr('title',data.subject );

					$(newRow).children('input').val( data.id );
			}

			return newRow;

		},

		generateEmail: function(data) {

			newEmail = $('#template .emailContainer').eq(0).clone();

			var eDate = new Date();
			eDate.setTime( data.date.utc * 1000 );

			newEmail.children('.subjectContainer').text(data.subject);
			newEmail.children('.date').text(data.date.date);
			newEmail.find('.fromContainer .name').text(data.contacts.from[0].name);
			newEmail.find('.fromContainer .email').text(data.contacts.from[0].email);

			if( data.contacts.to ) {
				for(var i=0;i<data.contacts.to.length;i++ ) {
					newEmail.children('.toContainer').append(this.generateContact(data.contacts.to[i]));
				}
			}

			if( data.contacts.cc ) {
				for(var k=0;k<data.contacts.cc.length;k++ ) {
					newEmail.children('.ccContainer').append(this.generateContact(data.contacts.cc[k]));
				}
			}

			if( data.contacts.bcc) {
				for(var j=0;j<data.contacts.bcc.length;j++ ) {
					newEmail.children('.bccContainer').append(this.generateContact(data.contacts.bcc[j]));
				}
			}

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

})(jQuery,document,window, Utils);