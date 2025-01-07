from PLinApi import *
from ctypes import c_ubyte, c_ushort, byref, sizeof, create_string_buffer
import time
import sys
import threading

IFrameEntry = TLINFrameEntry()

# PLIN API 객체 생성
LIN = PLinApi()

# LIN 클라이언트 등록
client_name = "MyLINClient"
hWnd = 0
hClient = HLINCLIENT()

register_result = LIN.RegisterClient(client_name, hWnd, hClient)
# if register_result == TLIN_ERROR_OK:
#     print("Client registered successfully with handle: ", hClient.value)
# else:
#     print("Failed to register client. Error code: ", register_result)
#     exit()

# 사용 가능한 하드웨어 가져오기
num_hw = c_ushort()
hardware_buffer = (HLINHW * 10)()

avail_result = LIN.GetAvailableHardware(hardware_buffer, sizeof(hardware_buffer), num_hw)

if avail_result != TLIN_ERROR_OK:
    print(f"Failed to get available hardware. Error code: {avail_result}")
else:
    print(f"Number of Available Hardware: {num_hw.value}")

    # if num_hw.value > 0:
    #     for i in range(num_hw.value):
    #         print(f"Hardware {i + 1} Handle: {hardware_buffer[i]}")
    # else:
    #     print("No hardware available.")
    hHw = hardware_buffer[0]

# 클라이언트와 하드웨어 연결
connect_result = LIN.ConnectClient(hClient, hHw)
# if connect_result == TLIN_ERROR_OK:
#     print("Success Connection!!")
# else:
#     print("Failed to connect. Error code: ", connect_result)
#     exit()

# 하드웨어 초기화
language_id = 0 
error_text_buffer = create_string_buffer(256)
master = TLIN_HARDWAREMODE_MASTER
slave = TLIN_HARDWAREMODE_SLAVE

init_result = LIN.InitializeHardware(hClient, hHw, slave, 19200)

IFrameEntry.FrameId = 0x08
IFrameEntry.Length = 5
IFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE
#IFrameEntry.InitialData = (c_ubyte * 8)(0x01, 0xFF, 0x00, 0, 0, 0, 0, 0)

setFrame = LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

getFrame = LIN.GetFrameEntry(hHw, IFrameEntry)

data_sets = [ (0x0E, 0x03, 0x01, 0x04, 0x0E, 0, 0, 0), (0x00, 0x03, 0x01, 0x08, 0x08, 0,0,0), 
             (0x01, 0x03, 0x01, 0x01, 0x01,0,0,0), (0x07, 0x03, 0x01, 0x02, 0x07,0,0,0)]
pMsg = TLINMsg()
pMsg.FrameId = int(0x42)
pMsg.Direction = TLIN_DIRECTION_PUBLISHER
pMsg.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
pMsg.Length = 5
#pMsg.Data = (0x01, 0x03, 0x01, 0x01, 0x01)
#pMsg.Checksum = 0xF5

for data_set in data_sets:
    pMsg.Data = (c_ubyte * 8)(*data_set)
    update = LIN.UpdateByteArray(hClient, hHw, IFrameEntry.FrameId, 0, pMsg.Length, pMsg.Data)
    if update != TLIN_ERROR_OK:
        print("Failed to UpdateFrameEntry!")
        LIN.GetErrorText(update, language_id, error_text_buffer, len(error_text_buffer))
        print(error_text_buffer.value.decode('utf-8'))
    else:    
        print("Update Success")
    time.sleep(0.1)

disconnect_result = LIN.DisconnectClient(hClient, hHw)
# if disconnect_result == TLIN_ERROR_OK:
#     print("Disconnected successfully.")
# else:
#     print("Failed to disconnect. Error code: ", disconnect_result)

# 클라이언트 해제
unregister_result = LIN.RemoveClient(hClient)
# if unregister_result == TLIN_ERROR_OK:
#     print("Client unregistered successfully.")
# else:
#     print("Failed to unregister client. Error code: ", unregister_result)