from controller import Robot, Keyboard

robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())
keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP)

steer_right = robot.getDevice('steer1')
steer_left = robot.getDevice('steer2')

wheels = []
for name in ['wheel1', 'wheel2', 'wheel3', 'wheel4']:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))
    motor.setVelocity(0.0)
    wheels.append(motor)

# เปิดใช้งานกล้อง
rgb_cam = robot.getDevice('d435_rgb')
rgb_cam.enable(TIME_STEP)

MAX_SPEED = 6.0
MAX_STEER = 0.5

print("Rover is Ready! Click 3D view and use WASD.")

while robot.step(TIME_STEP) != -1:
    target_speed = 0.0
    target_steer = 0.0
    
    key = keyboard.getKey()
    while key != -1:
        if key == ord('W'):
            target_speed = MAX_SPEED
        elif key == ord('S'):
            target_speed = -MAX_SPEED
        elif key == ord('A'):
            target_steer = MAX_STEER
        elif key == ord('D'):
            target_steer = -MAX_STEER
        key = keyboard.getKey()
        
    for wheel in wheels:
        wheel.setVelocity(target_speed)
        
    steer_right.setPosition(target_steer)
    steer_left.setPosition(target_steer)