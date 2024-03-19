# echo-server.py
# <0203SCN 001        NoRead                           >

import socket
from datetime import datetime
import sys, os

usage = f"""
Usage:
{os.path.basename(__file__)} <IP> <PORT> [directions]
    - IP:           TCP Server IP address
    - PORT:         TCP Server port number
    - directions:   [optional] list of direction to 
                    use in CMD responses
Example:
#   Connect to 172.19.51.11:4001
# and respond without changing the adr2 fields
# received in SCN:
py {os.path.basename(__file__)} 172.19.51.11 4001   

#   Connect to 172.19.51.11:4002
# and respond with adr2 
# - 000F for the first SCN
# - 000L for the second SCN
# - 000R for the third SCN
# - back to 000F for the fourth SCN
py {__file__} 172.19.51.11 4002 000F 000L 000R

"""

if len(sys.argv) < 2:
    print(usage)
    exit()

HOST = sys.argv[1]  # Standard loopback interface address (localhost)
PORT = int(sys.argv[2])  # Port to listen on (non-privileged ports are > 1023)

if len(sys.argv) >= 3:
    directions = sys.argv[3:]
else:
    directions = None
direction_index = 0

def setDirection(telegram, arr, index) ->(bytes, int):
    if not arr:
        return (telegram, index)
    index = (index + 1) % len(arr)
    current_direction = arr[index]
    telegram = telegram[0:16] + current_direction + telegram[20:]
    return (telegram, index)

current_telegram = b""
current_telegram_len = 0
current_telegram_str = ""
closed = False
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    print(f"Connected! {HOST}:{PORT}") 
    s.settimeout(10)
    while not closed:
        try:
            data = s.recv(128)
        except socket.timeout:
            continue
        except KeyboardInterrupt:
            closed = True
            continue
        current_telegram += data

        if not data:
            break
        if len(current_telegram) >= 54:
            current_telegram_str = current_telegram[0:54].decode("ascii")
            current_telegram = b""
            if "SCN " in current_telegram_str:
                response = current_telegram_str
                response = response.replace("SCN ", "CMD ")
                (response, direction_index) = setDirection(response, directions, direction_index) 

                s.sendall(response.encode("ascii"))
                print(
                    datetime.now().strftime("[%H:%M:%S:%f] ")
                    + current_telegram_str
                    + " -> "
                    + response
                )
            elif "WGH " in current_telegram_str:
                response = current_telegram_str
                response = response.replace("WGH ", "CMD ")
                (response, direction_index) = setDirection(response, directions, direction_index) 

                s.sendall(response.encode("ascii"))
                print(
                    datetime.now().strftime("[%H:%M:%S:%f] ")
                    + current_telegram_str
                    + " -> "
                    + response
                )
            else:
                print(
                    datetime.now().strftime("[%H:%M:%S:%f] ") + current_telegram_str
                )
