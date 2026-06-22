import sys
try:
    with open('/usr/local/bin/blitzfetcher', 'rb') as f:
        header = f.read(128)
        print("ELF Magic:", header[:4])
        print("Class (32/64):", header[4]) # 1 = 32-bit, 2 = 64-bit
        print("Data (endianness):", header[5]) # 1 = little-endian, 2 = big-endian
        print("OS/ABI:", header[7])
except Exception as e:
    print("Error:", e)
