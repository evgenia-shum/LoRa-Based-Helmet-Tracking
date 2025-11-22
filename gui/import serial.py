import serial.tools.list_ports
import serial
import time
ports = serial.tools.list_ports.comports()

for port in ports:
    print(port.device)
r = serial.Serial('com5', 9600)
f = open('text.txt', 'w')
while True:

    t = int(r.readline ())
    e = time.clock ()
    l = round(e, 2)
    print(t)
    f = open('text.txt','a')
    f.write(str(t)+ ' '+ str(1) + ' секунды' + '\n')
    time.sleep(0.1)
f.close()