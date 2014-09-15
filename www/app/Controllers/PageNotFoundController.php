<?php

namespace GRAND\Controllers;

use GRAND;
use GRAND\Interfaces\ControllerInterface;
use GRAND\Lib\ActionController;

class PageNotFoundController extends LandingController implements ControllerInterface {


  public function __construct($request, $response) {

    parent::__construct($request, $response);

  }

}