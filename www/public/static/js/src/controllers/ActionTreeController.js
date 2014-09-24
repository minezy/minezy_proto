

App.ActionTreeController = ( function($,document,window, U) {


	function ActionTreeController(options) {
		console.log('ACTION TREE CONTROLLER INIT');

		this.at = new App.ActionTree();

	}

	ActionTreeController.prototype = {


		destroy: function() {
			//do any clean up when destroying the section
			//delete this.homePhotos;
		}

	};

	return ActionTreeController;

})(jQuery,document,window, Utils);