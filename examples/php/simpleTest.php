<?php
#--------------------------------------------------------
 # Module Name : examples
 # Version : 1.0.0
 #
 # Software Name : SerialCom
 # Version : 1.0
 #
 # Copyright (c) 2015 Zorglub42
 # This software is distributed under the Apache 2 license
 # <http://www.apache.org/licenses/LICENSE-2.0.html>
 #
 #--------------------------------------------------------
 # File Name   : simpleTest.php
 #
 # Created     : 2015-12
 # Authors     : Zorglub42 <contact(at)zorglub42.fr>
 #
 # Description :
 #     PHP example to connect socket server
 #--------------------------------------------------------
 # History     :
 # 1.0.0 - 2015-12-03 : Release of the file
 #
 
$fp = fsockopen("localhost", 9999, $errno, $errstr, 30);


if (!$fp) {
    echo "$errstr ($errno)<br />\n";
} else {
    $out = "V\n";

    fwrite($fp, $out);
    while (!feof($fp)) {
        echo fgets($fp, 128) . "<br>";
    }
    fclose($fp);
}
?>
