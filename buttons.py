import sys
import cwiid
import time


def callback(msgs, timestamp):
    for msg in msgs:
        print(msg)
        if msg[0] == cwiid.MESG_BTN:
            wiimote.led = msg[1] & 0b1111


print('Put Wiimote in discoverable mode now (press 1+2)...')
if len(sys.argv) > 1:
    wiimote = cwiid.Wiimote(sys.argv[1])
else:
    wiimote = cwiid.Wiimote()
try:
    print(wiimote.state)
    wiimote.mesg_callback = callback
    wiimote.rpt_mode = cwiid.RPT_BTN
    wiimote.enable(cwiid.FLAG_MESG_IFC)

    while True:
        time.sleep(10)
        print(wiimote.state)
finally:
    wiimote.close()
