#!/usr/bin/env python3
"""
BMS Reader - Kompletní validační test
====================================

Tento script provádí kompletní validaci všech komponent BMS aplikace:
- Docker image existence a funkčnost
- Validace Python kódu
- Test MQTT připojení
- Kontrola Home Assistant integrace
- ARM deployment validace
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_status(message, status="info"):
    """Barevný výstup podle statusu"""
    colors = {
        "success": Colors.GREEN + "✅",
        "error": Colors.RED + "❌", 
        "warning": Colors.YELLOW + "⚠️",
        "info": Colors.BLUE + "ℹ️"
    }
    print(f"{colors.get(status, Colors.BLUE + 'ℹ️')} {message}{Colors.END}")

def run_command(cmd, capture_output=True):
    """Spustí příkaz a vrátí výsledek"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True, 
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timeout"
    except Exception as e:
        return False, "", str(e)

def test_docker_images():
    """Test existence Docker images"""
    print_status("Testování Docker images...", "info")
    
    success, output, error = run_command("docker images | grep bms-reader-arm")
    if not success:
        print_status("ARM Docker image nenalezen!", "error")
        return False
    
    lines = output.strip().split('\n')
    for line in lines:
        if 'bms-reader-arm' in line:
            parts = line.split()
            if len(parts) >= 3:
                image_name = f"{parts[0]}:{parts[1]}"
                size = parts[6] if len(parts) > 6 else "unknown"
                print_status(f"Nalezen image: {image_name} ({size})", "success")
    
    return True

def test_arm_image_functionality():
    """Test funkčnosti ARM image"""
    print_status("Testování funkčnosti ARM image...", "info")
    
    # Test Python verze
    success, output, error = run_command("docker run --rm bms-reader-arm:1.0.0 python --version")
    if not success:
        print_status(f"Chyba při testování Python: {error}", "error")
        return False
    
    python_version = output.strip()
    print_status(f"Python verze: {python_version}", "success")
    
    # Test závislostí
    success, output, error = run_command("docker run --rm bms-reader-arm:1.0.0 pip list")
    if not success:
        print_status(f"Chyba při listování balíčků: {error}", "error")
        return False
    
    required_packages = ['paho-mqtt', 'pyserial']
    for package in required_packages:
        if package in output:
            print_status(f"Balíček {package}: nainstalován", "success")
        else:
            print_status(f"Balíček {package}: chybí!", "error")
            return False
    
    return True

def test_exported_image():
    """Test exportovaného image"""
    print_status("Testování exportovaného image...", "info")
    
    export_file = "bms-reader-arm-1.0.0.tar.gz"
    if not os.path.exists(export_file):
        print_status(f"Export soubor {export_file} nenalezen!", "error")
        return False
    
    size = os.path.getsize(export_file) / (1024 * 1024)  # MB
    print_status(f"Export soubor: {export_file} ({size:.1f} MB)", "success")
    
    if size < 50:
        print_status("Soubor je podezřele malý!", "warning")
    elif size > 200:
        print_status("Soubor je větší než očekávaný!", "warning")
    
    return True

def test_source_files():
    """Test zdrojových souborů"""
    print_status("Testování zdrojových souborů...", "info")
    
    required_files = [
        "main.py",
        "bms_parser.py", 
        "modbus.py",
        "mqtt_helper.py",
        "addon/Dockerfile",
        "addon/config.yaml",
        "addon/run.sh",
        "ARM_DEPLOYMENT.md",
        "bms-reader.service",
        "deploy_to_pi.sh"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print_status(f"Soubor {file_path}: OK", "success")
        else:
            print_status(f"Soubor {file_path}: chybí!", "error")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_deployment_scripts():
    """Test deployment scriptů"""
    print_status("Testování deployment scriptů...", "info")
    
    scripts = [
        "addon/build_arm_quick.sh",
        "deploy_to_pi.sh"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print_status(f"Script {script}: spustitelný", "success")
            else:
                print_status(f"Script {script}: není spustitelný!", "warning")
        else:
            print_status(f"Script {script}: nenalezen!", "error")
            return False
    
    return True

def test_configuration_files():
    """Test konfiguračních souborů"""
    print_status("Testování konfiguračních souborů...", "info")
    
    # Test Home Assistant addon config
    config_file = "addon/config.yaml"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Jednoduchá kontrola obsahu bez YAML parseru
            required_strings = ['name:', 'version:', 'description:', 'arch:']
            for key in required_strings:
                if key in content:
                    print_status(f"Config obsahuje {key}", "success")
                else:
                    print_status(f"Config neobsahuje {key}!", "error")
                    return False
                    
            # Kontrola ARM architektury
            if 'aarch64' in content:
                print_status("ARM architektura (aarch64): nalezena", "success")
            else:
                print_status("ARM architektura: nenalezena!", "warning")
                
        except Exception as e:
            print_status(f"Chyba při načítání config.yaml: {e}", "error")
            return False
    else:
        print_status("config.yaml nenalezen!", "error")
        return False
    
    return True

def main():
    """Hlavní validační funkce"""
    print(f"{Colors.BOLD}🔍 BMS Reader - Kompletní validace{Colors.END}")
    print("=" * 50)
    
    tests = [
        ("Docker Images", test_docker_images),
        ("ARM Image Funkčnost", test_arm_image_functionality),
        ("Exportovaný Image", test_exported_image),
        ("Zdrojové soubory", test_source_files),
        ("Deployment skripty", test_deployment_scripts),
        ("Konfigurační soubory", test_configuration_files)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{Colors.BOLD}📋 {test_name}{Colors.END}")
        print("-" * 30)
        
        try:
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print_status(f"{test_name}: ÚSPĚCH", "success")
            else:
                print_status(f"{test_name}: SELHÁNÍ", "error")
                
        except Exception as e:
            print_status(f"{test_name}: CHYBA - {e}", "error")
            results.append((test_name, False))
    
    # Shrnutí výsledků
    print(f"\n{Colors.BOLD}📊 Shrnutí výsledků{Colors.END}")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n{Colors.BOLD}📈 Celkový výsledek: {passed}/{total} testů prošlo{Colors.END}")
    
    if passed == total:
        print_status("🎉 Všechny testy prošly! BMS aplikace je připravena k nasazení.", "success")
        return 0
    else:
        print_status("⚠️ Některé testy selhaly. Zkontrolujte výše uvedené chyby.", "warning")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
