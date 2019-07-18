from adafruit_servokit import ServoKit


class DriveControl:

    def __init__(self,servoControler, rightServo, leftServo):
        self._servos = servoControler
        self.right = rightServo
        self.left = leftServo
        self._speed = 1;



    '''
    SPEED
    This is a getter for the speed variable.
    '''
    @property
    def speed(self):
        return self._speed

    """
    SPEED
    This is a setter for the speed variable not allowing the ship to move faster than six pixels per frame 
    or go in reverse faster than three pixels per frame.
    """
    @speed.setter
    def speed(self, speed):
        # 100% speed
        if speed >= 100:
            self._speed = 1

        # 0% speed
        elif speed <= 0:
            self._speed = 0

        else:
            self._speed = speed * 0.01

    def turnRight(self):
        self._servos.continuous_servo[self.right].set_pulse_width_range(1000, 3000)
        self._servos.continuous_servo[self.left].set_pulse_width_range(1000, 3000)

        self._servos.continuous_servo[self.right].throttle = self.speed
        self._servos.continuous_servo[self.left].throttle = self.speed
        
    def turnLeft(self):
        self._servos.continuous_servo[self.right].set_pulse_width_range(1000, 3000)
        self._servos.continuous_servo[self.left].set_pulse_width_range(1000, 3000)

        self._servos.continuous_servo[self.right].throttle = -1 * self.speed
        self._servos.continuous_servo[self.left].throttle = -1 * self.speed
        
    def foreword(self):
        self._servos.continuous_servo[self.right].set_pulse_width_range(1000, 3000)
        self._servos.continuous_servo[self.left].set_pulse_width_range(1000, 3000)

        self._servos.continuous_servo[self.right].throttle = -1 * self.speed
        self._servos.continuous_servo[self.left].throttle = self.speed
        
    def reverse(self):
        self._servos.continuous_servo[self.right].set_pulse_width_range(1000, 3000)
        self._servos.continuous_servo[self.left].set_pulse_width_range(1000, 3000)

        self._servos.continuous_servo[self.right].throttle = self.speed
        self._servos.continuous_servo[self.left].throttle = -1 * self.speed
        
    def stop(self):
        self._servos.continuous_servo[self.right].set_pulse_width_range(0, 3000)
        self._servos.continuous_servo[self.left].set_pulse_width_range(0, 3000)

        self._servos.continuous_servo[self.right].throttle = -1
        self._servos.continuous_servo[self.left].throttle = -1
        