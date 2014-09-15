<?php

namespace GRAND\Lib;

use Stash;

class ActionController {

  protected $cache_pool;
  protected $db;
  protected $cache_TTL = 600; // -- 10min
  protected $twig;
  protected $response;
  protected $request;

  public function __construct() {

	\Twig_Autoloader::register();

	$TwigLoader = new \Twig_Loader_Filesystem(array(ROOT_PATH . 'views'));
	$this->twig = new \Twig_Environment( $TwigLoader, array('cache' => ROOT_PATH . 'cache', 'auto_reload' => true) );

	// Create Driver with default options
	$driver = new Stash\Driver\FileSystem();
	$driver->setOptions(array('path' => CACHE_PATH));

	// Inject the driver into a new Pool object.
	$this->cache_pool = new Stash\Pool($driver);

  }




}