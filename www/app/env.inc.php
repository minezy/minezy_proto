<?php

	if ( defined('APP_ENV') ) {

		if( APP_ENV == 'development-matt' ) {
			require(APP_PATH . 'envs/settings.matt.php');
		} else if(APP_ENV == 'stage') {
			require(APP_PATH . 'envs/settings.stage.php');
		} else if(APP_ENV == 'production') {
			require(APP_PATH . 'envs/settings.prod.php');
		} else {
			exit( "Application Environment '".APP_ENV."'' Not Found." );
		}

	// -- production
	} else {
		exit('No Application Environment Found.');
	}