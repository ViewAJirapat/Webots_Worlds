from controller import Robot, Keyboard
import cv2
import numpy as np

# 1. เริ่มต้นการเชื่อมต่อ
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

# เปิดใช้งานกล้อง RGB
rgb_cam = robot.getDevice('d435_rgb')
rgb_cam.enable(TIME_STEP)

MAX_SPEED = 6.0
MAX_STEER = 0.5

print("Rover Ready! (ควบคุมด้วย WASD พร้อมแสดงภาพผ่าน OpenCV)")

while robot.step(TIME_STEP) != -1:
    target_speed = 0.0
    target_steer = 0.0
    
    key = keyboard.getKey()
    
    while key != -1:
        # สลับทิศทาง W/S ให้ถูกต้องตามหลักฟิสิกส์
        if key == ord('W') or key == ord('w') or key == Keyboard.UP:
            target_speed = -MAX_SPEED
        elif key == ord('S') or key == ord('s') or key == Keyboard.DOWN:
            target_speed = MAX_SPEED
        elif key == ord('A') or key == ord('a') or key == Keyboard.LEFT:
            target_steer = MAX_STEER
        elif key == ord('D') or key == ord('d') or key == Keyboard.RIGHT:
            target_steer = -MAX_STEER
            
        key = keyboard.getKey()
        
    for wheel in wheels:
        wheel.setVelocity(target_speed)
        
    steer_right.setPosition(target_steer)
    steer_left.setPosition(target_steer)

    # ==========================================
    # ส่วนแสดงภาพจากกล้อง
    # ==========================================
    raw_image = rgb_cam.getImage()
    if raw_image is not None:
        # แปลงข้อมูลภาพดิบให้เป็น Numpy Array 3 มิติ เพื่อให้ OpenCV อ่านได้
        image = np.frombuffer(raw_image, np.uint8).reshape((rgb_cam.getHeight(), rgb_cam.getWidth(), 4))
        
        # แสดงหน้าต่างวิดีโอ
        cv2.imshow("Almondmatcha - D435 RGB Feed", image)
        cv2.waitKey(1)