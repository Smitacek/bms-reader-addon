import serial
from typing import Tuple



def request_device_info(
    port: str,
    address: int = 0x01,
    baudrate: int = 9600,
    timeout: float = 2.0  # Optimalizovaný timeout
) -> bytes:
    """
    Odesílá RS-485 ASCII rámec pro Service 42 'GetDeviceInfo' a čte zpět odpověď až do CR.
    
    Request (hex-ASCII): "~22014A42E00201FD28␍" 
    Response: ASCII hex data končící '\r'
    """
    # Sestavíme ASCII rámec přesně podle README-2.md
    frame = f"~22{address:02X}4A42E002{address:02X}FD28\r".encode('ascii')
    
    print(f"📤 Odesílám: {frame}")
    
    with serial.Serial(
        port=port,
        baudrate=baudrate,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout
    ) as ser:
        # Vyčistíme buffer
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Pošleme request
        ser.write(frame)
        ser.flush()
        
        print("📥 Čekám na odpověď...")
        
        # Čteme odpověď - BMS odpovídá ASCII hex daty končícími '\r'
        response = ser.read_until(expected=b'\r')
        
        print(f"📨 Přijato ({len(response)} bytů): {response}")
        
        # Zkontrolujeme, zda jsou ještě dostupná data bez čekání
        if ser.in_waiting > 0:
            remaining = ser.read(ser.in_waiting)
            print(f"📨 Další data ({len(remaining)} bytů): {remaining}")
            response += remaining
            
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
    Sestaví a odešle Modbus RTU frame a přečte odpověď.
    """
    # Sestav požadavek bez CRC
    frame = bytearray([
        slave_addr & 0xFF,
        function_code & 0xFF,
        (start_addr >> 8) & 0xFF,
        start_addr & 0xFF,
        (quantity >> 8) & 0xFF,
        quantity & 0xFF,
    ])
    
    # Připoj CRC
    crc = compute_crc16(bytes(frame))
    frame.append(crc & 0xFF)
    frame.append((crc >> 8) & 0xFF)
    
    # Komunikace
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

# Příklad použití:
if __name__ == "__main__":
    print("=== Test modulu modbus.py ===")
    
    try:
        raw_response = request_device_info(
            port="/dev/tty.usbserial-B003BHLO",
            address=0x01,
            baudrate=9600,
            timeout=5.0
        )
        print(f"✅ Service 42 odpověď: {len(raw_response)} bytů")
        print(f"📄 Hex: {raw_response.hex()}")
        
    except Exception as e:
        print(f"❌ Chyba: {e}")