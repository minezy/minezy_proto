<?php

/** Define Site Paths */
define('ROOT_PATH',  		realpath(__DIR__.'/../'). '/' );
define('APP_PATH',   		ROOT_PATH . 'app/' );
define('VENDOR_PATH',   	ROOT_PATH . 'vendor/' );
define('CACHE_PATH',       '/tmp/cache');

/**
 * Set the current environment. This MUST exist or site will fail to start.
 */
define('APP_ENV',	'development-matt' );
require(APP_PATH . 'env.inc.php' );

/**
 * start the composer autoloader
 */
require( VENDOR_PATH.'autoload.php' );



/**
 * Start loading the section
 */

$request_uri = strtok($_SERVER["REQUEST_URI"],'?');

$request = new GRAND\Lib\Request( $request_uri, $_REQUEST );
$response = new GRAND\Lib\Response();

$response->addHeader('X-UA-Compatible: IE=edge');

$router = new GRAND\Lib\Router( array(
	"/" => "Landing",
	"/(director|photographer)/?(archive)?/?" => "Thumbs",
	"/(director|photographer)/(archive)?/?([A-Za-z0-9_-]+)/?" => "Gallery",
	"/contact/?" => "Contact",
	"/services/[A-Za-z0-9]+" => "Services",
));

$route = $router->route($request,$response);

if( $route ) {
	$response->send( $route->createController($request, $response)->execute() );
} else {
	$request->setParam('404',true);
	$pageNotFound = new GRAND\Controllers\PageNotFoundController($request,$response);
	$response->send( $pageNotFound->execute() );
}


