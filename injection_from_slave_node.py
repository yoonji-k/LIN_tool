from PLinApi import *
from ctypes import c_ubyte, c_ushort, byref, sizeof, create_string_buffer
import time
import sys
import threading
import keyboard

IFrameEntry = TLINFrameEntry()
pMsg = TLINMsg()
language_id = 0 
error_text_buffer = create_string_buffer(256)
master = TLIN_HARDWAREMODE_MASTER
slave = TLIN_HARDWAREMODE_SLAVE
LIN = PLinApi() # PLIN API 객체 생성
client_name = "MyLINClient" # LIN 클라이언트 등록
hWnd = None
hClient = HLINCLIENT()

register_result = LIN.RegisterClient(client_name, hWnd, hClient)
if register_result == TLIN_ERROR_OK:
    print("Client registered successfully with handle: ", hClient.value)
else:
    print("Failed to register client. Error code: ", register_result)

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

init_result = LIN.InitializeHardware(hClient, hHw, slave, 19200)
if init_result != TLIN_ERROR_OK:
    print("Failed to initialize hardware.")
    LIN.GetErrorText(init_result, language_id, error_text_buffer, len(error_text_buffer))
    print(error_text_buffer.value)
    exit()
else:
    print("Hardware Initialized Successfully!")

status = TLINHardwareStatus()
getstatus = LIN.GetStatus(hHw, status)
if getstatus == TLIN_ERROR_OK:
    print(status.Status)

IFrameEntry.FrameId = 0x00
IFrameEntry.Length = 2
IFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE
IFrameEntry.InitialData = (c_ubyte * 8)(0x00, 0xFF)
pMsg.Length = 2
pMsg.Data = (c_ubyte * 8)(0x01, 0xFF, 0, 0, 0, 0, 0, 0)
#IFrameEntry.InitialData = (c_ubyte * 8)(0x00, 0xFF, 0, 0, 0, 0, 0, 0)

setFrame = LIN.SetFrameEntry(hClient, hHw, IFrameEntry)
if setFrame != TLIN_ERROR_OK:
    print("Failed to setFrame Entry!")
    LIN.GetErrorText(setFrame, language_id, error_text_buffer, len(error_text_buffer))
    print(error_text_buffer.value)
else:
    print("SetFrameEntry Success")
    #print(f"0x{IFrameEntry.FrameId:02x}")

getFrame = LIN.GetFrameEntry(hHw, IFrameEntry)
if getFrame != TLIN_ERROR_OK:
    print("Failed to getFrameEntry!")
    LIN.GetErrorText(getFrame, language_id, error_text_buffer, len(error_text_buffer))
    print(error_text_buffer.value.decode('utf-8'))
else:    
    print("getFrameEntry Success")

message = [(0x00, 0xFF), (0x00, 0xFF), (0x00, 0xFF), (0x00, 0xFF), (0x03, 0xFF), (0x03, 0xFF), (0x03, 0xFF)]

try:
    while True:
        for data in message:
            byte_array = (c_ubyte * 2)(*data)
            update = LIN.UpdateByteArray(hClient, hHw, IFrameEntry.FrameId, 0, 2, byte_array)
            if update != TLIN_ERROR_OK:
                print("Failed to UpdateFrameEntry!")
                LIN.GetErrorText(update, language_id, error_text_buffer, len(error_text_buffer))
                print(error_text_buffer.value.decode('utf-8'))
            else:    
                byte_array1 = '\t'.join([f"0x{d:02x}" for d in byte_array])
                print("Update Success: ", byte_array1)

            time.sleep(0.18)

            if keyboard.is_pressed('esc'):  # ESC 키를 누르면 루프를 빠져나옵니다
                print("Stopping transmission...")
                break
        if keyboard.is_pressed('esc'):
            break

finally:
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