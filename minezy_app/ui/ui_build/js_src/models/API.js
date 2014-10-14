

App.API = ( function($,document,window, U) {


	function API() {

		this.api_root = 'http://localhost:5000';
		//this.api_root = 'http://ec2-54-69-178-96.us-west-2.compute.amazonaws.com:5000';
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
			var url = this.api_root + '/' + this.api_version + '/' + account + action + '/';
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

})(jQuery,document,window, Utils);