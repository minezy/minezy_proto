<?php

namespace GRAND\Lib;

class Request {

  private $request;
  private $uri;

  public function __construct($uri, $request) {
    $this->uri = $uri;
    $this->request = $request;
  }

  public function getUri() {
    return $this->uri;
  }

  public function setParam($key, $value) {
    $this->request[$key] = $value;
    return $this;
  }

  public function getParam($key) {
    if (!isset($this->request[$key])) {
      return false;
    }
    return $this->request[$key];
  }

  public function getParams() {
    return $this->request;
  }

}