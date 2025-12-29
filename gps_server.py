import datetime
import socket
import struct
import threading
import traceback

from database import save_data

# Server configuration
HOST = "0.0.0.0"
PORT = 40123


def read_avl_data(client_socket, imei) -> int:
    print("Decoding AVL data packet...")

    avl_header_format = "!QB"
    avl_header_size = struct.calcsize(avl_header_format)
    (timestamp, priority) = struct.unpack(
        avl_header_format, client_socket.recv(avl_header_size)
    )

    avl_gps_format = "!iihhBh"
    avl_gps_size = struct.calcsize(avl_gps_format)
    (longitude, latitude, altitude, angle, satellites, speed) = struct.unpack(
        avl_gps_format, client_socket.recv(avl_gps_size)
    )

    timestamp_datetime = datetime.datetime.fromtimestamp(
        timestamp / 1000, datetime.timezone.utc
    )
    print(timestamp_datetime)
    print(f"Longitude: {longitude}, Latitude: {latitude} ({latitude},{longitude})")
    print(f"Altitude: {altitude} meters, Angle: {angle} degrees")
    print(f"Satellites: {satellites} visible, Speed: {speed} km/h")
    save_data(
        imei,
        timestamp_datetime,
        latitude,
        longitude,
        altitude,
        angle,
        satellites,
        speed,
    )
    return avl_header_size + avl_gps_size


def read_avl_io_data(client_socket: socket.SocketType):
    event_id = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    n_total = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    if event_id > 0 or n_total > 0:
        print(f"Received IO Event {event_id}:")
    n1_total = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    for i in range(n1_total):
        (prop_id, value) = struct.unpack("!BB", client_socket.recv(2))
        print(f"\tprop {prop_id:#0{1}x}\tvalue {value:#0{1}x}")

    n2_total = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    for i in range(n2_total):
        (prop_id, value) = struct.unpack("!BH", client_socket.recv(3))
        print(f"\tprop {prop_id:#0{1}x}\tvalue {value:#0{1}x}")

    n4_total = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    for i in range(n4_total):
        (prop_id, value) = struct.unpack("!BI", client_socket.recv(5))
        print(f"\tprop {prop_id:#0{1}x}\tvalue {value:#0{1}x}")

    n8_total = int.from_bytes(struct.unpack("!B", client_socket.recv(1)))
    for i in range(n8_total):
        (prop_id, value) = struct.unpack("!BQ", client_socket.recv(9))
        print(f"\tprop {prop_id:#0{1}x}\tvalue {value:#0{1}x}")


def send_command(client_socket, start_sending):
    command = b"\x01" if start_sending else b"\x00"
    client_socket.sendall(command)
    print(f"Sent {'start' if start_sending else 'stop'} command to device.")


def handle_client(client_socket):
    try:
        imei_length = int.from_bytes(client_socket.recv(2))
        imei_data = client_socket.recv(imei_length)
        if not imei_data:
            raise ValueError("No IMEI received")
        imei_data_decoded = imei_data.decode()
        print(f"Received IMEI: {imei_data_decoded}")

        # Accept connection after receiving IMEI
        send_command(client_socket, start_sending=True)

        while True:
            header_data = client_socket.recv(10)
            (data_length, codec, num_avl_packets) = struct.unpack(
                "!xxxxIBB", header_data
            )

            print(
                f"Receiving {data_length} bytes with {num_avl_packets} packets in codec {codec}"
            )

            for i in range(num_avl_packets):
                read_avl_data(client_socket, imei_data_decoded)
                read_avl_io_data(client_socket)

            (num_avl_packets2, crc16ibm) = struct.unpack("!BI", client_socket.recv(5))
            assert num_avl_packets == num_avl_packets2, (
                f"Mismatched num avl frames {num_avl_packets} != {num_avl_packets2}"
            )

            client_socket.sendall(num_avl_packets.to_bytes(4))

    except Exception as e:
        print(f"Error handling client: {e}")
        print(traceback.format_exc())
    finally:
        client_socket.close()


def main():
    print(f"Trying to bind {HOST}:{PORT}")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    main()
