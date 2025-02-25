import network
import socket
from machine import SPI, Pin
from time import sleep

COMMAND_READ = b'\x01'
COMMAND_READINTO = b'\x02'
COMMAND_WRITE = b'\x04'
COMMAND_WRITE_READINTO = b'\x08'

COMMAND_CS_LOW = b'\x10'
COMMAND_CS_HIGH = b'\x20'

# Configure the SPI interface (adjust parameters and SPI bus as needed)
spi = SPI(1, baudrate=5000000, polarity=0, phase=0, sck=18, mosi=17, miso=5)

led_pin = Pin(2, Pin.OUT)
cs_pin = Pin(19, Pin.OUT)
cs_pin.value(1)  # Start with chip select inactive

def handle_client(conn):
    try:
        while True:
            # Read one byte command code
            command = conn.recv(1)
            if not command:
                break  # Connection closed
            if command == COMMAND_READINTO:
                # SPI transfer command.
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break

                length = int.from_bytes(len_bytes, 'big')
               
                # Prepare buffers for SPI transfer.
                rx_buf = bytearray(length)
                spi.readinto(rx_buf)
                
                # Send back the SPI response.
                conn.send(rx_buf)

            elif command == COMMAND_WRITE:
                # SPI transfer command.
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')
               # Receive SPI data bytes.
                data = b''
                while len(data) < length:
                    chunk = conn.recv(length - len(data))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != length:
                    break  # Incomplete data received
                print("WRITE ({}): {}".format(length, data))
                
                # Prepare buffers for SPI transfer.
                spi.write(data)

            elif command == COMMAND_READ:
                # SPI transfer command.
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')
                                
                data = spi.read(length)
                print("READ ({}): {}".format(length, data))
              
                # Send back the SPI response.
                conn.send(data)

            elif command == COMMAND_WRITE_READINTO:
                # SPI transfer command.
                len_bytes = conn.recv(4)
                if not len_bytes or len(len_bytes) < 4:
                    break
                length = int.from_bytes(len_bytes, 'big')
                
                # Receive SPI data bytes.
                data = b''
                while len(data) < length:
                    chunk = conn.recv(length - len(data))
                    if not chunk:
                        break
                    data += chunk
                if len(data) != length:
                    break  # Incomplete data received

                # Prepare buffers for SPI transfer.
                tx_buf = bytearray(data)
                rx_buf = bytearray(length)
                spi.write_readinto(tx_buf, rx_buf)
                print("WRITE_READINTO ({})".format(length))
                print("  TX: {}".format(tx_buf))
                print("  RX: {}".format(rx_buf))
 
                # Send back the SPI response.
                conn.send(rx_buf)

            elif command == COMMAND_CS_LOW:
                cs_pin.value(0)
                led_pin.value(1)
                conn.send(b'\x00')

            elif command == COMMAND_CS_HIGH:
                cs_pin.value(1)
                led_pin.value(0)
                conn.send(b'\x00')

            else:
                # Unknown command; for safety, break out of loop.
                break
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()


# Change SSID and PSK
wl = network.WLAN()
wl.active(1)
wl.connect("", "")

sleep(2)

print(wl.ifconfig())

# Set up the TCP server on port 12345 (or your chosen port)
addr = socket.getaddrinfo("0.0.0.0", 12345)[0][-1]
s = socket.socket()
s.bind(addr)
s.listen(1)
print("SPI-to-LAN server listening on", addr)


while True:
    conn, client_addr = s.accept()
    print("Client connected from", client_addr)
    handle_client(conn)
