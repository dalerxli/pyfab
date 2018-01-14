import serial
from serial.tools.list_ports import comports
import io
import fcntl


class SerialDevice(object):

    def __init__(self,
                 eol='\r',
                 manufacturer='Prolific',
                 baudrate=9600,
                 bytesize=serial.EIGHTBITS,
                 parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE,
                 timeout=0.1):
        self.eol = eol
        self.manufacturer = manufacturer
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.timeout = timeout
        if not self.find():
            raise ValueError('Could not find device')

    def find(self):
        ports = list(comports())
        if len(ports) <= 0:
            print 'No serial ports found'
            return
        for port in ports:
            if port.manufacturer is None:
                continue
            if self.manufacturer not in port.manufacturer:
                continue
            try:
                self.ser = serial.Serial(port.device,
                                         baudrate=self.baudrate,
                                         bytesize=self.bytesize,
                                         parity=self.parity,
                                         stopbits=self.stopbits,
                                         timeout=self.timeout)
                if self.ser.isOpen():
                    try:
                        fcntl.flock(self.ser.fileno(),
                                    fcntl.LOCK_EX | fcntl.LOCK_NB)
                    except IOError:
                        print 'Port {0} is busy'.format(self.ser.port)
                        self.ser.close()
                        continue
                else:
                    print 'Could not open {0}'.format(self.ser.port)
                    continue
            except serial.SerialException as ex:
                print 'Port {0} is unavailable: {1}'.format(port, ex)
                continue
            buffer = io.BufferedRWPair(self.ser, self.ser, 1)
            self.sio = io.TextIOWrapper(buffer, newline=self.eol,
                                        line_buffering=True)
            if self.identify():
                return True
            self.ser.close()
        return False

    def identify(self):
        return False

    def close(self):
        self.ser.close()

    def write(self, str):
        self.sio.write(unicode(str + self.eol))

    def readln(self):
        return self.sio.readline().decode().strip()