

App.API = ( function($,document,window, U) {


	function API() {
		console.log('API INIT');

		this.api_root = 'http://localhost:5000';
		this.api_version = 1;
		this.current_call = null;

	}

	API.prototype = {

		getData: function(action,params,callback) {

			if(this.current_call) {
				this.current_call.abort();
				delete this.current_call;
			}

			this.current_call = $.ajax({
				type: "GET",
				url: this.constructURL(action,params),
				data: params,
				dataType: "json"
			})
			.done($.proxy(function( data ) {
				callback(data);
			},this));

		},

		constructURL: function(action,params) {

			var url = this.api_root + '/' + this.api_version + '/' + action + '/';

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

})(jQuery,document,window, Utils);