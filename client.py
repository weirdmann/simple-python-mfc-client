# echo-server.py

import socket
from datetime import datetime
import sys

HOST = sys.argv[1]  # Standard loopback interface address (localhost)
PORT = int(sys.argv[2])  # Port to listen on (non-privileged ports are > 1023)

current_telegram = b""
current_telegram_len = 0
current_telegram_str = ""
closed = False
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.settimeout(10)
    try:
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
    except:
        pass
