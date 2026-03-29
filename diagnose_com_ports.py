#!/usr/bin/env python3
"""Diagnose available COM ports and their status"""

import serial
import serial.tools.list_ports
import sys

def diagnose_com_ports():
    """List all available COM ports and try to open each one."""
    print("=" * 70)
    print("COM PORT DIAGNOSTIC TOOL")
    print("=" * 70)
    
    # List all available ports
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("\n❌ NO COM PORTS FOUND!")
        print("   Possible causes:")
        print("   - ELTIMA virtual port pair not created")
        print("   - ELTIMA driver not installed")
        print("   - No physical COM ports available")
        return
    
    print(f"\n✓ Found {len(ports)} COM port(s):\n")
    
    for port in ports:
        print(f"  Port: {port.device}")
        print(f"    Description: {port.description}")
        print(f"    Hardware ID: {port.hwid}")
        print()
    
    # Try to open each port
    print("\n" + "=" * 70)
    print("TESTING PORT ACCESS")
    print("=" * 70 + "\n")
    
    for port in ports:
        print(f"Testing {port.device}...", end=" ")
        try:
            s = serial.Serial(port.device, 115200, timeout=0.5)
            print("✓ OPEN (can use this port)")
            s.close()
        except PermissionError:
            print("✗ PERMISSION DENIED (port already in use or locked)")
        except Exception as e:
            print(f"✗ ERROR: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)
    print("\n1. If you see 'OPEN' next to a port, use that port in the launcher")
    print("2. If all ports show 'PERMISSION DENIED':")
    print("   - Close LabVIEW or other applications using COM ports")
    print("   - Restart the Python script")
    print("3. If no ports appear:")
    print("   - Create virtual COM port pair in ELTIMA")
    print("   - Restart Windows")
    print()

if __name__ == "__main__":
    diagnose_com_ports()
