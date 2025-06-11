# BMS Reader - Systém pro čtení dat z Battery Management System

Tento projekt poskytuje kompletní řešení pro vyčítání dat z BMS (Battery Management System) pro LiFePO₄ baterie pomocí RS-485 komunikace.

## Funkce

- **Univerzální komunikace**: Podporuje ASCII rámce, Modbus RTU a DD A5 protokoly
- **Real-time monitoring**: Kontinuální čtení a zobrazování dat baterie
- **Robustní architektura**: Založeno na abstraktní třídě Battery s konkrétní implementací
- **Testovací nástroje**: Kompletní testovací suite pro ověření funkčnosti
- **Flexibilní konfigurace**: Podporuje různé sériové porty a rychlosti

## Podporované protokoly

1. **ASCII rámce** (~HEX\r) - OBD2-PID protokol podle protokol.md
   - Service 42: GetDeviceInfo (SOC, napětí, teploty, číslo článků)
   - Service 47: GetSystemParams (limity napětí a teploty)
   - Service 51: GetDeviceManufacturerInfo (HW verze, SW verze)
   - Service 84: Specifická data napětí článků
2. **Modbus RTU** - validace CRC-16 a parsování registrů
3. **DD A5 rámce** - validace součtu a dekódování napětí/proudu/SOC

## Požadavky

- Python 3.8+
- `pyserial` pro sériovou komunikaci
- BMS kompatibilní s podporovanými protokoly

## Instalace

```bash
# Naklonování projektu
git clone <repository-url>
cd MBS

# Instalace závislostí
pip install pyserial

# Nebo pomocí uv
uv sync
```

## Použití

### Základní spuštění
```bash
python main.py
```

### Spuštění s vlastními parametry
```bash
python main.py run --port /dev/ttyUSB0 --baud 9600
```

### Testování spojení
```bash
python main.py test
```

### Zobrazení raw dat
```bash
python main.py run --raw
```

### Nápověda
```bash
python main.py help
```

## Konfigurace

### Sériový port
- **macOS**: `/dev/tty.usbserial-XXXXX`
- **Linux**: `/dev/ttyUSB0` nebo `/dev/ttyACM0`
- **Windows**: `COM3`, `COM4`, atd.

### Rychlost komunikace
- Výchozí: 9600 baud
- Podporováno: 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200

## Struktura projektu

```
MBS/
├── main.py                 # Hlavní spouštěcí soubor
├── BMS_complete.py        # Kompletní implementace BMS readeru
├── test_bms_complete.py   # Testovací suite
├── simple_utils.py        # Pomocné funkce
├── config.ini            # Konfigurace
└── source_code/
    ├── battery.py         # Abstraktní třída Battery
    ├── com.py            # Komunikační funkce
    ├── utils.py          # Původní utils
    └── daren_485.py      # Specifická implementace
```

## Výstup programu

Program zobrazuje:
- **Stav spojení**: Informace o úspěšnosti připojení
- **Real-time data**: Napětí, proud, SOC, teplota
- **Diagnostické informace**: CRC kontroly, parsované rámce
- **Periodické souhrny**: Kompletní stav baterie každých 10 sekund

### Příklad výstupu
```
BMS Data Reader - Inicializace...
✅ Spojení s BMS úspěšné!
▶ /dev/tty.usbserial-B003BHLO otevřen (9600 Bd), poslouchám BMS data...

[14:30:15] Modbus ID 1: [5120, -150, 850, 1000, 85, 25]

==================================================
           STAV BATERIE
==================================================
Typ:              LiFePO4_BMS
Online:           ANO
Napětí:           51.20 V
Proud:            -1.50 A
SOC:              85.0 %
Kapacita:         100.0 Ah
Zbývá:            85.0 Ah
Teplota 1:        25.0 °C
Počet článků:     16
Posl. aktualizace: před 1.2 s
==================================================
```

## Troubleshooting

### Nejčastější problémy

1. **Spojení selhalo**
   - Zkontrolujte připojení USB kabelu
   - Ověřte správnost portu (`ls /dev/tty*` na macOS/Linux)
   - Ujistěte se, že BMS je zapnuté

2. **Žádná data**
   - Zkuste jiný baudrate
   - Zkontrolujte kabeláž RS-485
   - Ověřte, že BMS komunikuje

3. **Chybné parsování**
   - Zkuste zapnout raw data (`--raw`)
   - Zkontrolujte protokol BMS v dokumentaci

### Debug režim

Pro detailní diagnostiku zapněte raw data:
```bash
python main.py run --raw
```

## Vývoj

### Přidání nového protokolu

1. Upravte `_process_data_buffer()` v `BMS_complete.py`
2. Přidejte parsovací funkci podobnou `_parse_modbus_registers()`
3. Aktualizujte testy v `test_bms_complete.py`

### Rozšíření battery třídy

Implementace se řídí abstraktní třídou `Battery` ze `source_code/battery.py`. 
Povinné metody:
- `test_connection()`
- `get_settings()`
- `refresh_data()`

## Licence

Tento projekt je určen pro vzdělávací a vývojové účely.

## Podpora

Pro dotazy a problémy vytvořte issue v repository nebo kontaktujte vývojáře.
