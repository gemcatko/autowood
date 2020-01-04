import serial
import math
from multiprocessing import Process, Value, Queue



class Magneto(Process):    
    """
    Magneto A1332 CE odometer.
    Grab current and previous angle from sensor (sensor prints current angle to serial console in a loop)
    , calculate delta and maintain overall distance/mileage of degrees.
    """

    def __init__(self, shared_distance, serial_file='/dev/ttyUSB0', speed=115200, wheel_radius=1):
        Process.__init__(self)
        self.wheel_radius = wheel_radius
        self.serial_console = serial.Serial(serial_file, speed, timeout=1)
        self.distance = 0
        self.s_distance = shared_distance
        self.angle = 0
        self.delta = 0
        self.previous_angle = 0
        
        

    def __get_angle__(self):
        with self.serial_console as s:
            #read curr. angle from serial con
            current_angle = s.readline().decode('ascii')
            self.previous_angle = self.angle
            self.angle = math.ceil(float(current_angle))
            #self.angle = self.angle - 3 # simulate angle change

    def __get_delta__(self):
        self.delta = self.angle - self.previous_angle
        self.delta = (self.delta + 180) % 360 - 180
    
    def maintain_distance(self):
        self.__get_angle__()
        self.__get_delta__()
        self.distance += self.delta
        self.s_distance.value += self.delta
        print(s_distance.value)

    def get_distance(self):
        return self.distance

    def run(self):
        while True:
            self.maintain_distance()



if __name__ == '__main__':
#multiprocessing example
    #initialize shared var for distance
    s_distance = Value('l', 0)
    
    #create instance of Process subclass Magneto and pass shared value var
    sensor_process = Magneto(shared_distance=s_distance)
    sensor_process.start()


#non multiprocessing example
 #sensor = Magneto()
     #while True:
     #    sensor.maintain_distance()
     #    d = sensor.get_distance()
     #print(d)

