<?php

namespace GRAND\Lib;

class Route {

  private $controllerClass;
  private $path;

  public function __construct($path, $controllerClass) {
    $this->path = $path;
    $this->controllerClass = $controllerClass;
  }

  public function __get($name){
    return $this->$name;
  }

  public function match(Request $request) {

    return preg_match('#^/?' . $this->path . '/?$#', $request->getUri(), $match);

  }

  public function createController($request, $response) {
    $classname = 'GRAND\Controllers\\'.$this->controllerClass.'Controller';
    return new $classname($request, $response);
  }
}
