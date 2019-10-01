import os
import fcntl
import socket
import select
import threading as th


HOST = "192.168.4.182"
PORT = 5000
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind((HOST, PORT))
srv.listen(20)
fcntl.fcntl(srv, fcntl.LOCK_NB)
storage = {srv: (HOST, PORT, "SERVER")}
work = True
send_socks = []
send_list = None
chat_message = None
try:
    while work:
        rlist, wlist, _ = select.select(
            list(storage.keys()),
            send_socks,
            [],
        )
        for sock in rlist:
            if sock != srv:
                data = sock.recv(2048)
                try:
                    user_data, message = data.decode(
                        "utf-8"
                    ).split("\r\n")
                    user_type, user_name = user_data.split(":")
                except ValueError:
                    chat_message = "ERROR"
                except UnicodeDecodeError:
                    chat_message = "ERROR"
                else:
                    chat_message = (f"{user_type} {user_name} сказал\n{message}")
                for s in wlist:
                    if s != sock:
                        s.send(chat_message.encode("utf-8"))
            else:
                client, addr = srv.accept()
                fcntl.fcntl(client, fcntl.LOCK_NB)
                try:
                    login = client.recv(1024)
                except ConnectionResetError:
                    client.close()
                else:
                    data = addr + (login.decode("utf-8"),)
                    storage[client] = data
                    send_socks.append(client)
finally:
    srv.close()
