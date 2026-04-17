# isotp-debug-tools-zlg-usbcanfd-200u

Python scripts running on Windows x64 for sending/receiving ISOTP CANFD messages, via ZLG USBCANFD 200U device.
A zlgcan library, of version 251230, is also packed with scripts for ease of use.

File/Directory description:

`androidTools`		: Executables including *isotpsend* and *isotprecv* for Android.

`canfdTestFrames`	: Text files filling with long CANFD messages.

`kerneldlls`		: ZLG device management libraries.

`zlgcan.dll`		: ZLG CAN/CANFD library.

`zlgcan.py`			: ZLG user level python API package.

`zlg_isotp_send.py`	: Python script for sending ISOTP CANFD messages.

`zlg_isotp_recv.py`	: Python script for receiving ISOTP CANFD messages.

---
## 1. Verification Environment

Softwares:
+ `Windows x64`
+ `Python 3.13.9` [[download]](https://www.python.org/downloads/windows/)
+ `python-can`
	``` python
	pip install python-can
	```
+ `can-isotp`
	``` python
	pip install can-isotp
	```

Hardwares:
+ `USBCANFD 200U (v1.04)`
+ `RK3588`

---
## 2. Usages

### 2.1. Receive ISOTP CANFD messages:

Run command on Windows PC:
``` shell
D:\isotp-debug-tools-zlg-usbcanfd-200u>python zlg_isotp_recv.py
```

Run command on Android:
``` shell
rk3588_s:/sdcard $cat canfdframes128.txt | isotpsend -s 123 -d 124 -L 72:64:5 -p 55:55 can0
```

Expected output on Windows PC:
``` txt
Opened Device Handle: 2686976.
Device Info:
Hardware Version:V3.01
Firmware Version:V2.45
Driver Interface:V1.00
Interface Interface:V0.00
Interrupt Number:0
CAN Number:2
Serial:40A72B0410AE0E6492A0
Hardware Type:USBCANFD-200U

----------------------: V2.45
Channel Count: 2
Device Name: A001
ZLG channel 0 ready (CAN FD 500K/2M)
>>> Listening for ISOTP CAN messages...
python-can received msg_arbitration_id 291
python-can received msg_arbitration_id 291
python-can received msg_arbitration_id 291
[14:23:28] Successfully received (128 bytes): 1112131415161718191A1B1C1D1E1F202122232425262728292A2B2C2D2E2F303132333435363738393A3B3C3D3E3F404142434445464748494A4B4C4D4E4F505152535455565758595A5B5C5D5E5F606162636465666768696A6B6C6D6E6F707172737475767778797A7B7C7D7E7F808182838485868788898A8B8C8D8E8F90
```

### 2.2. Send ISOTP CANFD messages:

Run command on Android:
``` shell
rk3588_s:/sdcard $isotprecv -s 124 -d 123 -L 72:64:5 -l -p 55:55 can0
```

Run command on Windows PC:
``` shell
D:\isotp-debug-tools-zlg-usbcanfd-200u>python zlg_isotp_send.py canfdTestFrames\canfdframes256.txt
```

Expected output on Windows PC:
``` txt
Opened Device Handle: 2686976.
Device Info:
Hardware Version:V3.01
Firmware Version:V2.45
Driver Interface:V1.00
Interface Interface:V0.00
Interrupt Number:0
CAN Number:2
Serial:40A72B0410AE0E6492A0
Hardware Type:USBCANFD-200U

----------------------: V2.45
Channel Count: 2
Device Name: A001
ZLG channel 0 ready (CAN FD 500K/2M)
>>> Sending canfdTestFrames\canfdframes256.txt and exiting on completion...
>>> File loaded: canfdTestFrames\canfdframes256.txt (256 bytes)
python-can received msg_arbitration_id 292
>>> Transmission complete
>>> Task finished. Shutting down.
ZLG_20251230_Adapter was not properly shut down
```

Expected output on Android:
``` txt
11 12 13 14 15 16 17 18 19 1A 1B 1C 1D 1E 1F 20 21 22 23 24 25 26 27 28 29 2A 2B 2C 2D 2E 2F 30 31 32 33 34 35 36 37 38 39 3A 3B 3C 3D 3E 3F 40 41 42 43 44 45 46 47 48 49 4A 4B 4C 4D 4E 4F 50 51 52 53 54 55 56 57 58 59 5A 5B 5C 5D 5E 5F 60 61 62 63 64 65 66 67 68 69 6A 6B 6C 6D 6E 6F 70 71 72 73 74 75 76 77 78 79 7A 7B 7C 7D 7E 7F 80 81 82 83 84 85 86 87 88 89 8A 8B 8C 8D 8E 8F 90 91 92 93 94 95 96 97 98 99 9A 9B 9C 9D 9E 9F A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD AE AF B0 B1 B2 B3 B4 B5 B6 B7 B8 B9 BA BB BC BD BE BF C0 C1 C2 C3 C4 C5 C6 C7 C8 C9 CA CB CC CD CE CF D0 D1 D2 D3 D4 D5 D6 D7 D8 D9 DA DB DC DD DE DF E0 E1 E2 E3 E4 E5 E6 E7 E8 E9 EA EB EC ED EE EF F0 F1 F2 F3 F4 F5 F6 F7 F8 F9 FA FB FC FD FE FF 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10
```
