<?php

namespace GRAND\Lib;

class Response {
  private $headers;

  public function addHeader($header) {
    $this->headers[] = $header;
    return $this;
  }

  public function addHeaders(array $headers) {
    foreach ($headers as $header) {
      $this->addHeader($header);
    }
    return $this;
  }

  public function getHeaders() {
    return $this->headers;
  }

  public function send($data) {
    if (!headers_sent()) {
      foreach($this->headers as $header) {
        header($header);
      }
    }

    echo $data;

  }



}