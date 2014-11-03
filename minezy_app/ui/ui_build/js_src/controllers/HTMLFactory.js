

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

			newEmail.find('.bodyContainer .bodyContent').html('<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam sollicitudin eros ac lacus pulvinar, cursus hendrerit quam interdum. Vestibulum rutrum mi vel magna dignissim, sit amet elementum erat mollis. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Morbi ullamcorper nec velit quis tristique. Suspendisse potenti. Donec feugiat vitae nibh id maximus. Etiam maximus ultricies eros sed fermentum. Phasellus pulvinar at risus a euismod. Nulla facilisi. Curabitur sed sem eros. Nunc non metus auctor, pulvinar enim vitae, aliquam velit. Morbi vel ante lorem. Proin non dapibus nisi, sed venenatis risus. Nulla et lobortis orci, quis tempor lectus. Suspendisse pharetra, tortor sit amet pellentesque placerat, dolor nisl fermentum orci, vitae facilisis dolor augue id risus. Ut semper quam ut lorem malesuada, id scelerisque nisi aliquet.</p><p>Aenean lacinia scelerisque ipsum id feugiat. Cras id vulputate ex, in hendrerit nulla. Vestibulum congue fermentum nisi id vestibulum. Vivamus viverra congue arcu, a tempor orci scelerisque eu. Praesent non egestas nibh. Suspendisse tempus lacinia sapien. Vivamus sit amet erat maximus, tincidunt lorem et, tincidunt lorem. Ut mi leo, malesuada pulvinar nisi sollicitudin, placerat rutrum tellus. Vivamus vehicula, purus sit amet accumsan commodo, ante mauris egestas orci, eget tristique arcu mauris eget sapien. Maecenas nec elit nibh. Morbi non porta felis.</p><p>Duis imperdiet, libero vitae posuere hendrerit, ante lectus porta dolor, at mollis lacus sapien quis leo. Sed fringilla purus at dui laoreet aliquet. Vestibulum sodales massa vitae sapien bibendum ullamcorper eu sit amet diam. Phasellus pretium sollicitudin ligula at posuere. Praesent feugiat, sem tempor fermentum finibus, diam mi ultricies nunc, ac egestas lorem felis eu tellus. Phasellus nec nibh nec quam tristique varius eu eu velit. Quisque scelerisque pharetra enim, molestie rutrum mi mollis nec. Nullam mauris nisl, tincidunt ut est id, sodales rhoncus enim. Donec molestie vehicula tincidunt. Aliquam erat volutpat. Sed sollicitudin orci velit, ac sollicitudin sapien luctus quis. Donec dignissim lectus a leo laoreet volutpat. Phasellus ut velit eget lectus dictum mollis et vitae nisl. Morbi egestas, magna volutpat porta tristique, magna velit consequat dolor, a faucibus nunc nisl eu diam. Maecenas auctor ex non orci dignissim, vitae sagittis elit vehicula. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>'.replace(/(?:\r\n|\r|\n)/g, '<br />'));



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