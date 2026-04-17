# This script requires Python 3.13.9 and below packages:
#     pip install python-can can-isotp  #do NOT install zlgcan
#
#     as of 20260417, official python package zlgcan is of v0.0.27,
#     which doesn't compatible with new ZLG devices.
#
# This script is supposed to run on Win x64
# This script is verified with ZLG USBCANFD-200U V1.04
#
# Cable connections as below:
# +----+         +---------------+           +----------------+
# |    |         |               |---CAN_H---|                |
# | PC |---USB---| USBCANFD 200U |           | RK3588 Android |
# |    |         |               |---CAN_L---|                |
# +----+         +---------------+           +----------------+
#
# Author : huang_qi_di@hotmail.com
# Date   : 2026.04.17
#
# run command on Android:
#     cat canfdframes128.txt | isotpsend -s 123 -d 124 -L 72:64:5 -p 55:55 can0

import can
import isotp
import time
import logging
from zlgcan import * # zlgcan.py

# configure log format: time-level-content
#logging.basicConfig(
#    level=logging.DEBUG, 
#    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
#)

# turn on log printing of protocol.py if isotp
#logging.getLogger("isotp").setLevel(logging.DEBUG)

# adapter class
class ZLG_20251230_Adapter(can.BusABC):
    def __init__(self, channel=0, bitrate=500000, dbitrate=2000000):
        super().__init__(channel)
        self._protocol = can.CanProtocol.CAN_FD
        self.channel = channel
        self.zlg = ZCAN()
        
        self.d_handle = self.zlg.OpenDevice(ZCAN_USBCANFD_200U, 0, 0)
        if self.d_handle == INVALID_DEVICE_HANDLE:
            raise Exception("Failed opening device")
        print("Opened Device Handle: %d." % self.d_handle)
        
        # read device info
        info = self.zlg.GetDeviceInf(self.d_handle)
        print("Device Info: \n%s" % info)
        print("----------------------: %s" % info.fw_version)
        can_number = info.can_num
        print("Channel Count: %d" % can_number)
        
        ret = self.zlg.ZCAN_SetValue(self.d_handle, "0/set_cn", "A001".encode("utf-8"))
        if ret == ZCAN_STATUS_OK:
            t = self.zlg.ZCAN_GetValue(self.d_handle, "0/get_cn/1")
            print("Device Name: %s" % c_char_p(t).value.decode("utf-8"))

        # arbitration bitrate & data bitrate
        #ret = self.zlg.ZCAN_SetValue(self.d_handle, str(self.channel) + "/canfd_abit_baud_rate", "500000".encode("utf-8"))
        #ret = self.zlg.ZCAN_SetValue(self.d_handle, str(self.channel) + "/canfd_dbit_baud_rate", "2000000".encode("utf-8"))
        baud_str = "500Kbps(80%),2.0Mbps(80%),(80,07C00002,01C00002)".encode("utf-8")
        ret = self.zlg.ZCAN_SetValue(self.d_handle, f"{self.channel}/baud_rate_custom", baud_str)
        if ret != ZCAN_STATUS_OK:
            print("ERROR: set CH%d baud failed!" % self.channel)

        # enable internal resistance    0-disable 1-enable
        ret = self.zlg.ZCAN_SetValue(self.d_handle, str(self.channel) + "/initenal_resistance", "1".encode("utf-8"))
        if ret != ZCAN_STATUS_OK:
            print("ERROR: open CH%d resistance failed!" % self.channel)

        # initialize channel
        chn_init_cfg = ZCAN_CHANNEL_INIT_CONFIG()
        chn_init_cfg.can_type = ZCAN_TYPE_CANFD
        chn_init_cfg.config.canfd.mode = 0  # 0-normal(R/W) 1-listen
        self.c_handle = self.zlg.InitCAN(self.d_handle, self.channel, chn_init_cfg)
        if self.c_handle is None:
            print("ERROR: initCAN failed!" % self.channel)

        # disable merged receive (can only be applied before startCAN)    0-disable 1-enable
        ret = self.zlg.ZCAN_SetValue(self.d_handle, str(self.channel) + "/set_device_recv_merge", "0".encode("utf-8"))
        if ret != ZCAN_STATUS_OK:
            print("ERROR: disable CH%d recv merge failed!" % self.channel)

        # disable echo printing     0-disable 1-enable
        ret = self.zlg.ZCAN_SetValue(self.d_handle, str(self.channel)+"/set_device_tx_echo", "0".encode("utf-8"))
        if ret != ZCAN_STATUS_OK:
            print("ERROR: set CH%d  set_device_tx_echo failed!" %(self.channel))

        # start CAN channel
        ret = self.zlg.StartCAN(self.c_handle)
        if ret != ZCAN_STATUS_OK:
            print("ERROR: startCAN failed!" % self.channel)
        else:
            print(f"ZLG channel {self.channel} ready (CAN FD 500K/2M)")


    def _recv_internal(self, timeout):
        rcv_canfd_num = self.zlg.GetReceiveNum(self.c_handle, ZCAN_TYPE_CANFD)
        #print("rcv_canfd_num(%d)" % rcv_canfd_num)
        if rcv_canfd_num:
            msgs, rcv_canfd_num = self.zlg.ReceiveFD(self.c_handle, rcv_canfd_num, 10)
            if rcv_canfd_num > 0:
                frame = msgs[0].frame
                return can.Message(
                    arbitration_id=frame.can_id & 0x1FFFFFFF,
                    data=bytes(frame.data[:frame.len]),
                    is_extended_id=False,
                    is_fd=True,
                    bitrate_switch=True,
                    channel=self.channel
                ), False
        return None, False

    def send(self, msg, timeout=None):
        tx_obj = ZCAN_TransmitFD_Data()
        tx_obj.frame.can_id = msg.arbitration_id
        tx_obj.frame.len = len(msg.data)
        # convert bytes to ctypes array
        for i, b in enumerate(msg.data):
            tx_obj.frame.data[i] = b
            
        tx_obj.frame.flags = 0x01 # enable BRS sending
        tx_obj.transmit_type = 0
        self.zlg.TransmitFD(self.c_handle, tx_obj, 1)

    def shutdown(self):
        self.zlg.ResetCAN(self.c_handle)
        self.zlg.CloseDevice(self.d_handle)


def main():
    try:
        bus = ZLG_20251230_Adapter(channel=0)
        addr = isotp.Address(rxid=0x123, txid=0x124)
        stack = isotp.CanStack(bus, address=addr, params={'tx_data_length': 64, 'stmin': 10, 'blocksize': 4})

        print(">>> Listening for ISOTP CAN messages...")
        while True:
            stack.process()
            if stack.available():
                payload = stack.recv()
                print(f"[{time.strftime('%H:%M:%S')}] Successfully received ({len(payload)} bytes): {payload.hex().upper()}")
            time.sleep(0.001)
    except KeyboardInterrupt:
        bus.shutdown()
    except Exception as e:
        print(f"Runtime Error: {e}")

if __name__ == "__main__":
    main()