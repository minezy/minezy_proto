<?php

namespace GRAND\Lib;

class ConnectionFactory {
    private static $factory;

    public static function getFactory() {
        if (!self::$factory)
            self::$factory = new ConnectionFactory();
        return self::$factory;
    }

    private $db;

    public function getConnection($db_name) {

		if (!$this->db) {
			try {
				$file = APP_PATH.'/data/'.$db_name.'.json';
				$this->db = json_decode(file_get_contents($file), true);
			}
			catch(Exception $e) {
			    echo 'An error occured: ' . $e->getMessage();
			}

		}

        return $this->db;
    }
}