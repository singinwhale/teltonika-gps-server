# Teltonika GPS Server

This project is a basic implementation of a GPS server that receives AVL data from Teltonika devices, decodes the data, and stores it into a SQLite database. It includes two main components:

1. **database.py** - Handles saving the decoded data into a SQLite database.
2. **gps_server.py** - Listens for incoming connections from Teltonika devices, receives AVL data, decodes it, and saves it using `database.py`.

## Requirements

- Python 3.x

No external dependencies required - uses only Python standard library.

## Usage

1. Start the GPS server:
    ```bash
    python gps_server.py
    ```
    The server will start listening on `0.0.0.0:40123`.

2. The server will accept incoming connections from Teltonika devices, decode the AVL data, and store it into the SQLite database (`gps.db`).

## Database Schema

The SQLite database is created automatically with the following schema:

```sql
CREATE TABLE gps_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    imei VARCHAR(15) NOT NULL,
    timestamp DATETIME NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    altitude INT NOT NULL,
    angle INT NOT NULL,
    satellites INT NOT NULL,
    speed INT NOT NULL,
    google_maps_url VARCHAR(255) NOT NULL
);
```

## How It Works

- When a Teltonika device connects to the server, it sends an IMEI which is used to identify the device.
- The server responds with 0x01 to accept the connection (0x00 would reject it).
- The device then starts sending AVL data packets using Codec 8 format.
- The server decodes the AVL data to extract GPS information such as timestamp, latitude, longitude, altitude, angle, satellites, and speed.
- Coordinates are converted from Teltonika format (divided by 10,000,000) to standard decimal degrees.
- The extracted data is saved into the SQLite database using the `database.py` script.

## Troubleshooting

- Make sure that port `40123` is open and not blocked by any firewall.
- Verify that the Teltonika device is correctly configured to send data to the server's IP address and port.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Teltonika for their AVL data protocol.
