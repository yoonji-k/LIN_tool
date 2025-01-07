from PLinApi import *
from ctypes import c_ushort, byref, sizeof, create_string_buffer
import time

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
    hHw = hardware_buffer[1]

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

def linmsg_injection():
    messages = [
         {
            'FrameId': 0x08,
            'Length' : 5,
            'ChecksumType' : TLIN_CHECKSUMTYPE_ENHANCED,
            'Direction' : TLIN_DIRECTION_PUBLISHER,
            'Data' : (0xFF, 0x03, 0x01, 0x18, 0x18),
            'Checksum' : 0xC3           
        },
    
        {
             'FrameId': 0x08,
             'Length' : 5,
             'ChecksumType' : TLIN_CHECKSUMTYPE_ENHANCED,
             'Direction' : TLIN_DIRECTION_PUBLISHER,
             'Data' : (0xFF, 0x03, 0x01, 0x81, 0x81),
             'Checksum' : 0xF0
         },
        {
            'FrameId': 0x08,
            'Length' : 5,
            'ChecksumType' : TLIN_CHECKSUMTYPE_ENHANCED,
            'Direction' : TLIN_DIRECTION_PUBLISHER,
            'Data' : (0xFF, 0x03, 0x01, 0x04, 0x0E),
            'Checksum' : 0xE1
        },
        {
            'FrameId': 0x08,
            'Length' : 5,
            'ChecksumType' : TLIN_CHECKSUMTYPE_ENHANCED,
            'Direction' : TLIN_DIRECTION_PUBLISHER,
            'Data' : (0xFF, 0x03, 0x01, 0x02, 0x07),
            'Checksum' : 0xEA
        },
       
    ]

# LIN 메시지 전송
    for message in messages:
        injection_test = TLINMsg()
        injection_test.FrameId = int(message['FrameId'])
        injection_test.Length = message['Length']
        injection_test.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
        injection_test.Direction = TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH
        injection_test.Data = message['Data']
        injection_test.Checksum = message['Checksum']

        for i in range(100):
            wResult = LIN.Write(hClient, hHw, injection_test)
            if wResult == TLIN_ERROR_OK:
                print(f"Write Success! Frame ID: 0x{message['FrameId']}")
            else:
                print("Error: ", wResult)

            time.sleep(0.1)

linmsg_injection()

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