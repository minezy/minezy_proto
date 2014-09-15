<?php

namespace GRAND\Lib;

class Router {
  private $routes = array();

  public function __construct($routes) {
    $this->addRoutes($routes);
  }

  public function addRoute($path,$controller) {
    $this->routes[] = new Route($path,$controller);
    return $this;
  }

  public function addRoutes(array $routes) {
    foreach ($routes as $path => $controller) {
      $this->addRoute($path,$controller);
    }
    return $this;
  }

  public function getRoutes() {
    return $this->routes;
  }

  public function route(Request $request, Response $response) {
    foreach ($this->routes as $route) {
      if ($route->match($request)) {
        return $route;
      }
    }
    $response->addHeader("HTTP/1.0 404 Not Found");
  }
}