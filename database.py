import sqlite3


def save_data(imei, timestamp, latitude, longitude, altitude, angle, satellites, speed):
    connection = sqlite3.connect("gps.db")
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gps_data (
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
            """)
        google_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
        sql = """
        INSERT INTO gps_data (imei, timestamp, latitude, longitude, altitude, angle, satellites, speed, google_maps_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            sql,
            (
                imei,
                timestamp,
                latitude/10000000,
                longitude/10000000,
                altitude,
                angle,
                satellites,
                speed,
                google_maps_url,
            ),
        )
        connection.commit()
    finally:
        connection.close()
