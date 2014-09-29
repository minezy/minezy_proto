

App.ActionTree = ( function($,document,window, U) {

	var tree = {
		'root' : {
			'contacts' : {
				'contacts-from': {
					'contacts-to': {
						'dates-to': {
							'dates-day': {
								'emails-list': {
									'emails-meta' : false
								},
							},
							'emails-list': {
								'emails-meta' : false
							},
						},
						'emails-list': {
							'emails-meta' : false
						},
					},
					'dates-to': {
						'dates-day': {
							'emails-list': {
								'emails-meta' : false
							},
						},
						'emails-list': {
							'emails-meta' : false
						},
					},
					'emails-list': {
						'emails-meta' : false
					},
				},
				'dates': {
					'dates-day': {
						'emails-list': {
							'emails-meta' : false
						},
					},
					'contacts-from': {
						'dates-day': {
							'emails-list': {
								'emails-meta' : false
							},
						},
						'emails-list': {
							'emails-meta' : false
						},
					},
					'emails-list': {
						'emails-meta' : false
					},
				},
				'emails-list': {
					'emails-meta' : false
				}
			},
			'dates': {
				'contacts' : {
					'contacts-from': {
						'dates-day': {
							'emails-list': {
								'emails-meta' : false
							},
						},
						'emails-list': {
							'emails-meta' : false
						},
					},
					'dates-day': {
						'emails-list': {
							'emails-meta' : false
						},
					},
					'emails-list': {
						'emails-meta' : false
					}
				},
				'dates-day': {
					'contacts' : {
						'contacts-from': {
							'emails-list': {
								'emails-meta' : false
							},
						},
						'emails-list': {
							'emails-meta' : false
						}
					},
					'emails-list': {
						'emails-meta' : false
					},
				}
			}
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

})(jQuery,document,window, Utils);