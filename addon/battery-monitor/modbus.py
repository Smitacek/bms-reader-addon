import logging
import serial


logger = logging.getLogger(__name__)



def request_device_info(
    port: str,
    address: int = 0x01,
    baudrate: int = 9600,
    timeout: float = 2.0  # Optimized timeout
) -> bytes:
    """
    Sends RS-485 ASCII frame for Service 42 'GetDeviceInfo' and reads back response until CR.
    
    Request (hex-ASCII): "~22014A42E00201FD28␍" 
    Response: ASCII hex data ending with '\r'
    """
    # Build ASCII frame exactly according to README-2.md
    frame = f"~22{address:02X}4A42E002{address:02X}FD28\r".encode('ascii')
    
    logger.debug(f"📤 Sending: {frame}")
    
    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout
    ) as ser:
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send request
        ser.write(frame)
        ser.flush()
        
        logger.debug("📥 Waiting for response...")
        
        # Read response - BMS responds with ASCII hex data ending with '\r'
        # Important: Do NOT append bytes after the first CR as it corrupts framing
        response = ser.read_until(expected=b'\r')

        logger.debug(f"📨 Received ({len(response)} bytes): {response}")

        return response


def compute_crc16(data: bytes) -> int:
    """
    Vypočítá Modbus CRC-16 (polynom 0xA001) pro zadaná data.
    Vrací 16-bitovou CRC (nižší Byte první).
    """
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def send_modbus_request(
    port: str,
    slave_addr: int,
    function_code: int,
    start_addr: int,
    quantity: int,
    baudrate: int = 9600,
    timeout: float = 1.0
) -> bytes:
    """
    Builds and sends Modbus RTU frame and reads response.
    """
    # Build request without CRC
    frame = bytearray([
        slave_addr & 0xFF,
        function_code & 0xFF,
        (start_addr >> 8) & 0xFF,
        start_addr & 0xFF,
        (quantity >> 8) & 0xFF,
        quantity & 0xFF,
    ])
    
    # Append CRC
    crc = compute_crc16(bytes(frame))
    frame.append(crc & 0xFF)
    frame.append((crc >> 8) & 0xFF)
    
    # Communication
    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout
    ) as ser:
        ser.write(frame)
        expected = 1 + 1 + 1 + quantity * 2 + 2
        response = ser.read(expected)
    
    return response

# Example usage:
if __name__ == "__main__":
    print("=== Test modbus.py module ===")
    
    try:
        raw_response = request_device_info(
            port="/dev/tty.usbserial-B003BHLO",
            address=0x01,
            baudrate=9600,
            timeout=5.0
        )
        print(f"✅ Service 42 response: {len(raw_response)} bytes")
        print(f"📄 Hex: {raw_response.hex()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
