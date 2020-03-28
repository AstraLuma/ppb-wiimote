import sys
import cwiid
import time

SEQUENCE = [
    cwiid.LED1_ON,
    cwiid.LED2_ON,
    cwiid.LED3_ON,
    cwiid.LED4_ON,
    cwiid.LED3_ON,
    cwiid.LED2_ON,
]

print('Put Wiimote in discoverable mode now (press 1+2)...')
if len(sys.argv) > 1:
    wiimote = cwiid.Wiimote(sys.argv[1])
else:
    wiimote = cwiid.Wiimote()
try:
    print(wiimote.state)
    wiimote.mesg_callback = print
    while True:
        for led in SEQUENCE:
            print(led)
            wiimote.led = led
            time.sleep(0.5)
finally:
    wiimote.close()
