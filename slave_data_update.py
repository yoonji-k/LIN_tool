from PLinApi import *
from ctypes import c_ubyte, c_ushort, byref, sizeof, create_string_buffer
import time
import sys
import threading

IFrameEntry = TLINFrameEntry()
pMsg = TLINMsg()
iRcvMask = c_uint64(0xFFFFFFFFFFFFFFFF)

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

init_result = LIN.InitializeHardware(hClient, hHw, master, 19200)
if init_result != TLIN_ERROR_OK:
    print("Failed to initialize hardware.")
    LIN.GetErrorText(init_result, language_id, error_text_buffer, len(error_text_buffer))
    print(error_text_buffer.value)
    exit()
else:
    print("Hardware Initialized Successfully!")

# filter_result = LIN.SetClientFilter(hClient, hHw, iRcvMask) # iRcvMask를 사용하여 클라이언트 필터를 설정합니다.
# if filter_result != TLIN_ERROR_OK:
#     print("Failed to set filter.")
#     LIN.GetErrorText(filter_result, 0, error_text_buffer, len(error_text_buffer))
#     print(error_text_buffer.value.decode())
# else:
#     print("Filtering Successful!!")


IFrameEntry.FrameId = 0x00
if(LIN.GetFrameEntry(hHw, IFrameEntry)==TLIN_ERROR_OK):
    IFrameEntry.Length = 2
    IFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
    IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
    IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE
    IFrameEntry.InitialData[0] = 0x09
    IFrameEntry.InitialData[1] = 0xFF
    LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

# #IFrameEntry.InitialData = (c_ubyte * 8)(0x00, 0xFF, 0, 0, 0, 0, 0, 0)
IFrameEntry.FrameId = 0x01
if(LIN.GetFrameEntry(hHw, IFrameEntry)==TLIN_ERROR_OK):
    IFrameEntry.Length = 2
    IFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH
    IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
    IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE
    IFrameEntry.InitialData[0] = 0x00
    IFrameEntry.InitialData[1] = 0xFF
    LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

IFrameEntry.FrameId = 0x02
if(LIN.GetFrameEntry(hHw, IFrameEntry)==TLIN_ERROR_OK):
    IFrameEntry.Length = 2
    IFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH
    IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
    IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE
    IFrameEntry.InitialData[0] = 0x00
    IFrameEntry.InitialData[1] = 0xFF
    LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

slots = (TLINScheduleSlot*3)()

# slot= TLINScheduleSlot()
# slot.Type = TLIN_SLOTTYPE_UNCONDITIONAL
# slot.FrameId = (c_ubyte * 8)()
# slot.FrameId[0] = 0x00
# slot.Delay = 1000
# slot.CountResolve = 0

slots[0] = TLINScheduleSlot()
slots[0].Type = TLIN_SLOTTYPE_EVENT
slots[0].FrameId = (c_ubyte * 8)()
slots[0].FrameId[0] = 0x00
slots[0].Delay = 1000
slots[0].CountResolve = 0
#pMsg.Checksum = 0xF5
slots[1] = TLINScheduleSlot()
slots[1].Type = TLIN_SLOTTYPE_EVENT
slots[1].FrameId = (c_ubyte * 8)()
slots[1].FrameId[0] = 0x01
# slots[1].Delay = 1000
# slots[1].CountResolve = 0

slots[2] = TLINScheduleSlot()
slots[2].Type = TLIN_SLOTTYPE_EVENT
slots[2].FrameId = (c_ubyte * 8)()
slots[2].FrameId[0] = 0x02
slots[2].Delay = 1000
slots[2].CountResolve = 0

if(LIN.SetSchedule(hClient, hHw, 0, slots, 3) == TLIN_ERROR_OK):
    LIN.StartSchedule(hClient, hHw, 0)

# suspend = LIN.SuspendSchedule(hClient, hHw)
# if suspend != TLIN_ERROR_OK: print("suspend Error: Try again...")

pMsg.Data = (0x09, 0xFF)
pMsg.Lentgh = 2
for i in range(50):
    update = LIN.UpdateByteArray(hClient, hHw, IFrameEntry.FrameId, 0, IFrameEntry.Length, pMsg.Data)
    if update != TLIN_ERROR_OK:
        print("Failed to UpdateFrameEntry!")
        LIN.GetErrorText(update, language_id, error_text_buffer, len(error_text_buffer))
        print(error_text_buffer.value.decode('utf-8'))
    else:    
        print("Update Success")
    time.sleep(0.18)

# resume = LIN.ResumeSchedule(hClient, hHw)
# if resume != TLIN_ERROR_OK: print("resume Error: Try again...", resume)

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