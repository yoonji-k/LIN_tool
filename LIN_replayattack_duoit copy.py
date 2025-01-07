from PLinApi import *
import time
import sys
import os
from datetime import datetime

IFrameEntry = TLINFrameEntry()

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
        exit()
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

def send_message(msg_id, data):
    IFrameEntry.FrameId = int(msg_id, 16)
    IFrameEntry.Length = len(data)
    IFrameEntry.Direction = TLIN_DIRECTION_SUBSCRIBER_AUTOLENGTH
    IFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
    IFrameEntry.Flags =  FRAME_FLAG_RESPONSE_ENABLE

    hex_data = " ".join([f"{byte:02X}" for byte in data])
    print(f"{parts[0]} ID: 0x{msg_id}, Data: {hex_data}")

    LIN.SetFrameEntry(hClient, hHw, IFrameEntry)

    LIN.GetFrameEntry(hHw, IFrameEntry)

    c_data_array = (c_ubyte * len(data))(*data)

    result = LIN.UpdateByteArray(hClient, hHw, IFrameEntry.FrameId, 0, len(c_data_array), c_data_array)  # ID 0x10에 데이터 업데이트
    if result != TLIN_ERROR_OK:
        print("Replay Error")
    else:
        return result
    
last_timestamp = None

def send_message_with_timing(msg_id, data, current_timestamp):
    global last_timestamp
    if last_timestamp is not None:
        time_diff = (current_timestamp - last_timestamp) / 1000  # 현재 타임스탬프와 이전 타임스탬프의 차이
        #print(f"ID {msg_id}에 대해 {time_diff}초 대기")
        time.sleep(time_diff)  # 주기 대기
    else:
        print(f"ID {msg_id}에 대해 처음 메시지, 바로 전송")

    last_timestamp = current_timestamp

#base_path = "C:\\Users\\LISA\\Desktop\\LIN\\data\\"
#filename = os.path.join(base_path, sys.argv[1]) #커맨드 라인에서 파일명 받기
#filename = sys.argv[1]
filename = "C:\\Users\\LISA\\Desktop\\dataset\\LIN_message.txt"

with open(filename, 'r', encoding='cp949') as f:
    next(f)  # 첫 번째 줄(헤더)은 건너뜀
    
    for line in f:
        parts = line.split()
        try:
            # 타임스탬프와 메시지 ID, 데이터 추출
            timestamp_str = parts[1]  # 타임스탬프가 위치한 열 (초 단위로 기록)
            current_timestamp = float(timestamp_str)  # 타임스탬프를 float로 변환
            msg_id = parts[2].strip().upper()  # 메시지 ID
            # 데이터 추출
            data = [int(parts[i], 16) for i in range(4, 9)] if msg_id == '08' else [int(parts[i], 16) for i in range(4, 6)]
            
            # 타임스탬프에 따른 메시지 주입
            send_message_with_timing(msg_id, data, current_timestamp)
            
        except ValueError as e:
                print(f"Error parsing line: {line}")
                print(e)
                continue
        
        result = send_message(msg_id, data)
        if result != TLIN_ERROR_OK:
             print("Send_message is Failed")


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