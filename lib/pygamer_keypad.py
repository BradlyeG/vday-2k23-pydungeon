### Simple joystick driver
### returns floating point X/Y values up to 1.0
### returns array of ints (0,1,2) for off, pressed, or released
### four buttons

import keypad
import analogio


class pygamerpad:

    def __init__(self, joyXPin, joyYPin, clk, dat, ltch, keyCount, valueWhenPressed, calFactorX=0, calFactorY=0, valueOffset=0.5):

        # Use the pin values passed in to set up the IO.
        self.btns = keypad.ShiftRegisterKeys(clock=clk, data=dat, latch=ltch, key_count=keyCount, value_when_pressed=valueWhenPressed)

        joyXIn = analogio.AnalogIn(joyXPin)
        joyYIn = analogio.AnalogIn(joyYPin)

        self.joystick = [joyXIn, joyYIn]

            #Modify this tuple to fit the key names used
            # Start = P, Select = M
        self.KEYNAMES = (
            "B"
            "A"
            "P"
            "M"
        )

        self.valueOffset = valueOffset
        self.calFactorX = calFactorX
        self.calFactorY = calFactorY


    def getJoyRaw(self):
        # This method takes no arguments, and returns an array
        # of the raw joystick x [0] and y [1] inuputs
        
        rawReading = [self.joystick[0].value, self.joystick[1].value]

        return rawReading

    def getJoy(self, deadzone:float=0.01):
        # This method takes no arguments, and returns an array
        # of the normalized joystick x [0] and y[1] inputs

        normX = ((self.joystick[0].value/65536) - self.valueOffset) - self.calFactorX
        normY = ((self.joystick[1].value/65536) - self.valueOffset) - self.calFactorY

        joyReading = []

        if abs(normX) > deadzone:
            joyReading.append(normX)
        else:
            joyReading.append(0)

        if abs(normY) > deadzone:    
            joyReading.append(normY)
        else:
            joyReading.append(0)

        return joyReading

    def getDigitalJoy(self, deadzone:float=0.1):
        # This method may take one argument, float(deadzone), and returns and array
        # of the status and direction of joystick activation
        # in the x [0] and y [1] axis as -1, 0, or, 1
        # The deadzone is used to adjust the sensitivity after getting the reading

        dX = 0 
        dY = 0

        tempX = ((self.joystick[0].value/65536) - self.valueOffset) - self.calFactorX
        tempY = ((self.joystick[1].value/65536) - self.valueOffset) - self.calFactorY

        if abs(tempX) > deadzone:
            if tempX < 0:
                dX = -1
            elif tempX > 0:
                dX = 1 
        if abs(tempY) > deadzone:
            if tempY < 0:
                dY = -1
            if tempY > 0:
                dY = 1

        joyReading = []

        joyReading.append(dX)
        joyReading.append(dY) 

        return joyReading

    def calibrateJoy(self, factor:int=10):
        # THIS IS BROKEN
        # This method may take one argument, factor, and will attempt to calibrate
        # the joystick. It does this by creating an array, sized from the factor,
        # and measuring the input int(factor) times then taking the average value
        # and setting that as the calibration factor (for x and y)

        calSumX = 0
        calSumY = 0

        for f in range(factor):
            calSumX += (self.joystick[0].value/65536) - self.valueOffset
            calSumY += (self.joystick[1].value/65536) - self.valueOffset

        self.calFactorX = calSumX/factor
        self.calFactorY = calSumY/factor

    def getButtons(self):
        # This method returns a string denoting which button and if it was (p)ressed or (r)eleased
        # The string will be empty if there is no press

        event = self.btns.events.get()
        
        if event:
            buttons = str(self.KEYNAMES[event.key_number]) + "p" if event.pressed else str(self.KEYNAMES[event.key_number]) + "r"
        else:
            buttons = ""

        return buttons