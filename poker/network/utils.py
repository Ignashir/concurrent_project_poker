ENDIAN  = "big"

def send_msg(msg, conn):
    data = msg.encode()
    length = len(data).to_bytes(4, ENDIAN)
    conn.sendall(length + data)

def recv_exact(conn, n):
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            raise ConnectionError("Socket closed")
        data.extend(packet)
    return bytes(data)

def recive_msg(conn) -> str:
    length = int.from_bytes(recv_exact(conn, 4), ENDIAN)
    return recv_exact(conn, length).decode()


def send_msg_with_ack(conn, msg) -> bool:
    send_msg(msg, conn)

    try:
        ack = recv_exact(conn, 3).decode()
        return ack == "ACK"
    except Exception:
        return False


def recive_msg_with_ack(conn) -> str:
    msg = recive_msg(conn)

    conn.sendall(b"ACK")

    return msg