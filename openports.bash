#!/bin/bash
# Ethical Exploration - High-Performance Parallel Bash Port Scanner
# License: GNU General Public License v3.0 (GPL-3.0)
# Usage: ./openports.bash [TARGET_IP] [START_PORT] [END_PORT]

TARGET="${1:-127.0.0.1}"
START_PORT="${2:-1}"
END_PORT="${3:-1024}"
TIMEOUT_SEC=1
MAX_CONCURRENT=64

# Parse range format like 1-1024 if passed in $2
if [[ "$START_PORT" == *"-"* ]]; then
    IFS='-' read -r START_PORT END_PORT <<< "$START_PORT"
fi

echo "=========================================================="
echo "    Ethical Exploration - Bash Parallel Port Scanner     "
echo "=========================================================="
echo "[*] Target Host : $TARGET"
echo "[*] Port Range  : $START_PORT to $END_PORT"
echo "[*] Timeout     : ${TIMEOUT_SEC}s"
echo "----------------------------------------------------------"

scan_port() {
    local host="$1"
    local port="$2"
    if timeout "$TIMEOUT_SEC" bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
        local service
        service=$(getent services "$port/tcp" 2>/dev/null | awk '{print $1}')
        [ -z "$service" ] && service="unknown"
        printf "[+] Port %-5d/tcp OPEN  (Service: %s)\n" "$port" "$service"
    fi
}

export -f scan_port
export TIMEOUT_SEC

running_jobs=0
for ((port=START_PORT; port<=END_PORT; port++)); do
    scan_port "$TARGET" "$port" &
    ((running_jobs++))

    if (( running_jobs >= MAX_CONCURRENT )); then
        wait -n 2>/dev/null || wait
        ((running_jobs--))
    fi
done

wait

echo "----------------------------------------------------------"
echo "[*] Bash port scan completed on $TARGET."
