<?php
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
