from PLinApi import *

LIN = PLinApi()

def update_byte_array_in_slave_mode(hardware_handle, client_handle):
    # 1. 하드웨어 초기화 및 마스터 모드 설정
    LIN.InitializeHardware(client_handle, hardware_handle, 19200, TLIN_HARDWAREMODE_MASTER)

    # 2. 마스터 모드에서 스케줄 중단
    LIN.SuspendSchedule(client_handle, hardware_handle)

    # 3. 슬레이브 모드로 전환
    LIN.InitializeHardware(client_handle, hardware_handle, 19200, TLIN_HARDWAREMODE_SLAVE)

    # 4. Byte Array 업데이트
    data = (c_ubyte * 4)(0x01, 0x02, 0x03, 0x04)  # 예시 데이터
    LIN.UpdateByteArray(client_handle, hardware_handle, 0x00, 0, len(data), data)  # ID 0x10에 데이터 업데이트

    # 5. 다시 마스터 모드로 전환
    LIN.InitializeHardware(client_handle, hardware_handle, 19200, TLIN_HARDWAREMODE_MASTER)

    # 6. 마스터 모드에서 스케줄 재개
    LIN.ResumeSchedule(client_handle, hardware_handle)

def main():
    # 하드웨어 및 클라이언트 핸들 초기화
    hardware_handle = HLINHW()
    client_handle = HLINCLIENT()

    # 클라이언트 등록 및 하드웨어 연결
    name = "Client"
    num_hw = c_ushort()
    hardware_buffer = (HLINHW * 10)()
    LIN.RegisterClient(name, None, client_handle)
    available_hardware = LIN.GetAvailableHardware(hardware_buffer, sizeof(hardware_buffer), num_hw)
    if available_hardware > 0:
        hardware_handle = hardware_buffer[0]  # 첫 번째 하드웨어 핸들 가져오기
        LIN.ConnectClient(client_handle, hardware_handle)

    # Byte Array 업데이트 수행
    update_byte_array_in_slave_mode(hardware_handle, client_handle)

    # 클라이언트 및 하드웨어 해제
    LIN.DisconnectClient(client_handle, hardware_handle)
    LIN.RemoveClient(client_handle)

if __name__ == "__main__":
    main()