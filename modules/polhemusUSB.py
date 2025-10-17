"""
Created on Thu Jun 28 13:49:35 2018
@author: akruszew
"""

import usb1
import time

class PolhemusUSB:
    """
    Small Polhemus sensor library
    Gets the position (x,y,z) in 'mm' and the orientation (quaternion) of each sensors (up to 4)

    Made for linux with usb1 python library installed. """

    class sensor:
        """ The data structure that holds the last sensor informations"""
        def __init__(self):
            self._position=[0]*3
            self._quaternion=[0]*4
            self._time = 0
        def GetLastPosition(self):
            """ the last known position in cm since the last call of UpdateSensors"""
            return self._position

        def GetLastQuaterion(self):
            """ the last known quaternion since the last call of UpdateSensors"""
            return self._quaternion

        def GetLastUpdateTime(self):
            """ the local time of the last call of UpdateSensors"""
            return self._time

    def __init__(self):
        # USB access informations
        self._VENDOR_ID = 0x0F44
        self._PRODUCT_ID = 0xFF20
        self._InEP = 0x88
        self._OutEp = 0x4
        self._INTERFACE = 0
        self._CONFIGURATION = 1

        # Find the device
        self._handle = usb1.USBContext().openByVendorIDAndProductID(
            self._VENDOR_ID,
            self._PRODUCT_ID,
            skip_on_error=True,
            )
        if self._handle is None:
            print("Device not found")
        try:
            with self._handle.claimInterface(self._INTERFACE):
                # configuration of the Polhemus
                self._handle.bulkWrite(self._OutEp, b'U1\r',100) #config: in cm (1)
                self._handle.bulkWrite(self._OutEp, b'O*,2,7,1\r',100) #config: X, Y, Z Cartesian coordinates of position (2), quaternion (7) new line (1)
                # self._handle.bulkWrite(self._OutEp, b'0x12' ,100) #config: reset alignment frame to identity for station 1 (1) 
        except usb1.USBErrorTimeout:
            print('time Out while trying to configure the sensor')
            raise
        # init data structure (4 sensors)
        self.sensors=[]*4
        for i in range(4):
            self.sensors.append(PolhemusUSB.sensor())



    def UpdateSensors(self):
        """ Access the Polhemus device and updates the sensors informations"""
        with self._handle.claimInterface(self._INTERFACE):
            try:
                self._handle.bulkWrite(self._OutEp,b'p',100)
                try:
                    rawData = self._handle.bulkRead(self._InEP,400,100)
                    rawFrames = rawData.split(b'\r\n')
                    # at this point each line of rawFrames is a list of data for the i-th sensor. The last line is empty
                    # default data format = [ID+Err, x, y, z, Azimuth, Elevation, Roll]
                    for i in range(len(rawFrames)-1):
                        tempFrame = rawFrames[i].split()
                        self.sensors[i]._position=[float(x) for x in tempFrame[1:4]]
                        self.sensors[i]._quaternion=[float(x) for x in tempFrame[4:8]]
                        self.sensors[i]._time=time.time()

                        offset = [-(19.4-2.85), -0.45, 27.3-1.85-2.7]
                        calibratedPosition = [round((self.sensors[i]._position[j] + offset[j])*10.0, 3) for j in range(3)]
                        calibratedPosition = [ calibratedPosition[0], -calibratedPosition[2], calibratedPosition[1] ]
                        self.sensors[i]._position = calibratedPosition

                except usb1.USBErrorTimeout:
                    print('time Out while waiting frame datas')
                    pass
            except usb1.USBErrorTimeout:
                    print('time Out while sending the frame request')
                    pass


if __name__ == "__main__":
    polhemus = PolhemusUSB()
    positionAccumulator=[0]*3
    while True:
        polhemus.UpdateSensors()
        for i in range(1):
            print("Sensor ",i,": ",polhemus.sensors[i].GetLastPosition())
        time.sleep(0.1)