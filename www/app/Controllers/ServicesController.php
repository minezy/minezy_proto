<?php

namespace GRAND\Controllers;

use GRAND;
use GRAND\Interfaces;
use GRAND\Lib;
use GRAND\Models;

  /**
   * This class is the traffic controller for generating data for the UI. This list 
   */

class ServicesController extends Lib\ActionController implements Interfaces\ControllerInterface {

  private $ajax = false;
  private $action;
  private $actions_wl = ['data'];

  public function __construct($request, $response) {

  	parent::__construct();

  	$this->request = $request;
  	$this->response = $response;

  	$this->ajax = $request->getParam('ajax');
    $this->parseURI();

    $this->execute();

  }

  /**
   * Grab the params from the URI for this section
   */


  private function parseURI() {

    $uri_parts = explode('/', trim($this->request->getUri(),'/')  );

    if( in_array($uri_parts[1],$this->actions_wl) ) {
      $this->action = $uri_parts[1];
    }

    //sub-action
    /*if( isset($uri_parts[2]) ) {

    }*/


  }

  /**
   * Generate the page
   * 	return html ready for display
   */

  public function execute() {

    switch( $this->action ) {

      case 'data':
        //load sub-controller in most cases, however this action is really small/quick
        return $this->getWoodsData();
        break;

      default:
        break;

    }

  }

  private function getWoodsData() {

    $cache_item = $this->cache_pool->getItem('woodsdata');
    $cache_data = $cache_item->get();

    if($cache_item->isMiss()) {
      $cache_item->lock();
      $wdata = new Models\WoodsData();
      $cache_data = $wdata->getJSON();

      //$cache_item->set($cache_data, $cache_TTL);
    }


    $this->response->addHeader('Content-Type: application/json; charset=UTF-8');
    return $cache_data;

  }


}