import serial
import time

PAGE_SIZE=128
FLASH_APP_OFFSET=0x8000

def ignore_nl(s):
    c = b'\x10'
    while c == b'\x10':
        c = s.read()
    return c

def load_addr(addr, ser):
    addr = addr >> 1
    ser.write(bytes([0x55,addr&0xff,(addr>>8)&0xff,0x20]))
    ser.flush()
    return ser.read(2) == b'\x14\x10'

def read_page(ser):
    ser.write(bytes([0x74,0,PAGE_SIZE,0,0x20]))
    ser.flush()
    if ser.read(1) != b'\x14':
        return None
    data = ser.read(PAGE_SIZE)
    return data if ser.read(1) == b'\x10' else None

def write_page(data, ser):
    ser.write(bytes([0x64,0,len(data),0]))
    ser.write(data)
    ser.write(b'\x20')
    ser.flush()
    return ser.read(2) == b'\x14\x10'

def write_file(name, ser):
    pos = 0
    with open(name, 'rb') as f:
        while True:
            data = f.read(PAGE_SIZE)
            print(data)
            if len(data) <= 0:
                break
            if not load_addr(pos, ser):
                print('Cant load addr', pos)
                break
            if not write_page(data, ser):
                print('Cant write page', pos)
                break
            if not load_addr(pos + FLASH_APP_OFFSET, ser):
                print('Cant load verif addr', pos)
                break
            if read_page(ser)[:len(data)] != data:
                print('Verification error', pos)
                break
            print('Write', pos, 'ok')
            pos += len(data)


with serial.Serial('COM5', 57600, timeout=.5) as ser:
    for i in range(200):
        ser.reset_input_buffer()
        ser.write(b'0 ')
        ser.flush()
        print('send',i)
        rd = ser.read(2)
        print(rd)
        if rd == b'\x14\x10':
            print('Got SYNC!')
            break

    write_file(r'C:\Users\Dell\Documents\ExpressLRS\src\.pio\build\Jumper_RX_R900MINI_via_BetaflightPassthrough\firmware.bin',ser)