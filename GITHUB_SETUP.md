# BMS Reader Repository Structure

## 📁 Pro GitHub publikaci

Vytvořte dva GitHub repositories:

### 1. 🏠 Home Assistant Add-on Repository
```
bms-reader-addon/
├── README.md                    # Add-on dokumentace
├── CHANGELOG.md                 # Historie změn
├── .github/
│   └── workflows/
│       └── build.yml           # CI/CD pipeline
└── bms-reader/                 # Add-on složka
    ├── config.yaml
    ├── Dockerfile
    ├── run.sh
    ├── requirements.txt
    ├── addon_config.py → config.py
    ├── main.py
    ├── modbus.py
    ├── bms_parser.py
    ├── mqtt_helper.py
    ├── README.md
    └── icon.png                # Add-on ikona
```

### 2. 💻 Standalone Repository  
```
bms-reader/
├── README.md                   # Hlavní dokumentace
├── SETUP.md                    # Rychlé nastavení
├── config.ini.example          # Příklad konfigurace
├── main.py                     # Hlavní aplikace
├── bms_read_once.py            # Test verze
├── modbus.py                   # BMS komunikace
├── bms_parser.py               # Parsování
├── mqtt_helper.py              # MQTT
├── config.py                   # Konfigurace
├── pyproject.toml              # Python deps
├── requirements.txt            # Pro non-uv instalace
└── docs/                       # Detailní dokumentace
    ├── MQTT.md
    ├── HARDWARE.md
    └── TROUBLESHOOTING.md
```

## 🚀 Publikace Add-on

### 1. Příprava repository
```bash
# Vytvořte nový repository na GitHub
gh repo create your-username/bms-reader-addon --public

# Zkopírujte addon/ strukturu
mkdir bms-reader-addon
cd bms-reader-addon
cp -r ../addon bms-reader/
```

### 2. Add-on Store registrace
Do Home Assistant Add-on Store přidejte:
```
https://github.com/your-username/bms-reader-addon
```

### 3. Build & Release
```bash
# Tag release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions automaticky sestaví multi-arch images
```

## 📋 Checklist publikace

### Add-on Repository
- [ ] Repository vytvořeno
- [ ] Soubory zkopírovány do správné struktury
- [ ] README.md s instalačními pokyny
- [ ] Icon.png přidán (128x128px)
- [ ] GitHub Actions pro build
- [ ] Release tag vytvořen

### Standalone Repository  
- [ ] Repository vytvořeno
- [ ] Hlavní dokumentace
- [ ] Příklady konfigurace
- [ ] Requirements.txt
- [ ] Instalační skripty

### Dokumentace
- [ ] Instalační návody
- [ ] Hardware požadavky
- [ ] Troubleshooting guide
- [ ] Příklady použití
- [ ] Screenshots

## 🔧 Příklad GitHub Actions

`.github/workflows/build.yml`:
```yaml
name: Build Add-on

on:
  release:
    types: [published]

jobs:
  build:
    name: Build ${{ matrix.arch }}
    runs-on: ubuntu-latest
    strategy:
      matrix:
        arch: [amd64, armv7, armhf, aarch64]
    
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      
      - name: Build
        uses: home-assistant/builder@master
        with:
          args: |
            --${{ matrix.arch }} \
            --target bms-reader
```
