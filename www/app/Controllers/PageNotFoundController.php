<?php

namespace GRAND\Controllers;

use GRAND;
use GRAND\Interfaces;
use GRAND\Lib;

class PageNotFoundController extends Lib\ActionController implements Interfaces\ControllerInterface {

  private $ajax = false;

  public function __construct($request, $response) {

  	parent::__construct();

  	$this->request = $request;
  	$this->response = $response;

    $this->pageNotFound = $request->getParam('404');

  }

  /**
   * Generate all the data necessary for the page to render
   * 	return an array that holds your tokens and data pairs.
   */

  private function compileData() {

		$data = array();
		$data['site_section'] = 'Landing';
		$data['pageNotFound'] = $this->pageNotFound;

		return $data;

  }

  /**
   * Generate the page
   * 	return html ready for display
   */

  public function execute() {

  	$cache_item = $this->cache_pool->getItem('404');

  	if($cache_item->isMiss()) {

  		$cache_item->lock();

  		$template = $this->twig->loadTemplate('404.html');

  		//comment out line below to turn off caching (be sure to $cache_pool->flush to wipe everything out)
  		//$cache_item->set($cache_data, $cache_TTL);

  		$cache_data = $template->render( $this->compileData() );


  	}

  	$this->response->addHeader('Content-Type: text/html; charset=UTF-8');

  	return $cache_data;

  }


}