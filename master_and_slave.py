from PLinApi import *
from ctypes import c_ubyte, c_ushort, byref, sizeof, create_string_buffer
import time

class LINbus():
    def __init__(self, baudrate, name):
        self.LIN = PLinApi()
        self.hClient = HLINCLIENT()
        self.hHw = HLINHW(0)
        self.hwMode = TLIN_HARDWAREMODE_MASTER
        self.hHWBaudrate = c_ushort(baudrate)
        self.hardware_buffer = (HLINHW * 10)()
        self.num_hw = c_ushort()
        self.baudrate = c_ushort(baudrate)

        register_result = self.LIN.RegisterClient(name, None, self.hClient)
        if register_result != TLIN_ERROR_OK: print("(Regsiter error) Try again...")

        avail_result = self.LIN.GetAvailableHardware(self.hardware_buffer, sizeof(self.hardware_buffer), self.num_hw)
        if avail_result == TLIN_ERROR_OK:
            print(f"Number of Available Hardware: {self.num_hw.value}")
            if self.num_hw.value > 0:
                for i in range(self.num_hw.value):
                    print(f"Hardware {i + 1} Handle: {self.hardware_buffer[i]}")
            self.hHw = self.hardware_buffer[0]
        else:
            print("Try again...")

        connect_result = self.LIN.ConnectClient(self.hClient, self.hHw)
        if connect_result != TLIN_ERROR_OK: print("(Connection Error) Try again...")

        initialized_result = self.LIN.InitializeHardware(self.hClient, self.hHw, self.hwMode, self.baudrate)
        if initialized_result != TLIN_ERROR_OK: print("(Initialize Error) Try again...")

        masterFrameEntry = TLINFrameEntry()
        masterFrameEntry.FrameId = 0x00
        masterFrameEntry.Length = 2
        masterFrameEntry.Direction = TLIN_DIRECTION_PUBLISHER
        masterFrameEntry.ChecksumType = TLIN_CHECKSUMTYPE_ENHANCED
        masterFrameEntry.Flags = FRAME_FLAG_RESPONSE_ENABLE

        setframe = self.LIN.SetFrameEntry(self.hClient, self.hHw, masterFrameEntry)
        if setframe != TLIN_ERROR_OK: print("(SetFrameEntry Error) Try again...")
        getframe = self.LIN.GetFrameEntry(self.hHw, masterFrameEntry)
        if getframe != TLIN_ERROR_OK: print("(GetFrameEntry Error) Try again...")

        suspend_result = self.LIN.SuspendSchedule(self.  hClient, self.hHw)
        if suspend_result != TLIN_ERROR_OK: print("(Suspend Error) Try again...")

    def update_byte_array(self, frameId, payload):
        len_payload = len(payload)
        data = (c_ubyte * 8)()

        for i in range(0, 8):
            data[i] = c_ubyte(0)

        for i in range(0, len_payload):
            data[i] = c_ubyte(payload[i])

        update = self.LIN.UpdateByteArray(self.hClient, self.hHw, frameId, 0, len_payload, data)
        if update != TLIN_ERROR_OK: print("(Update Error) Try again...")

    # def resume_shecule(self):
    #     resume = self.LIN.ResumeSchedule(self.hClient, self.hHw)
    #     if resume != TLIN_ERROR_OK: print("(Resume Error) Try again...")

    def close_connection(self):
        close_result = self.LIN.DisconnectClient(self.hClient, self.hHw)
        if close_result != TLIN_ERROR_OK: print("(Disconnect Error) Try again...")

if __name__ == "__main__":
    Connection1 = LINbus(19200, "Client 1")
    #Connection1.__init__(19200, "Client 1")
    Connection1.update_byte_array(0x00, [0x09, 0xFF])
    #Connection1.resume_shecule()