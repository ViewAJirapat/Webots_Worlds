from controller import Robot, Keyboard
import numpy as np
import cv2

# 1. เริ่มต้นการเชื่อมต่อ
robot = Robot()
TIME_STEP = int(robot.getBasicTimeStep())

# 2. เปิดใช้งาน Keyboard
keyboard = robot.getKeyboard()
keyboard.enable(TIME_STEP)

# 3. ตั้งค่ามอเตอร์บังคับเลี้ยว (Steering)
steer_right = robot.getDevice('steer1')
steer_left = robot.getDevice('steer2')

# 4. ตั้งค่ามอเตอร์ขับเคลื่อน (Driving Wheels)
wheels = []
wheel_names = ['wheel1', 'wheel2', 'wheel3', 'wheel4']
for name in wheel_names:
    motor = robot.getDevice(name)
    motor.setPosition(float('inf'))  # ตั้งค่าเป็นโหมดหมุนต่อเนื่อง
    motor.setVelocity(0.0)
    wheels.append(motor)

# 5. เปิดใช้งานกล้อง RGB
rgb_cam = robot.getDevice('d435_rgb')
rgb_cam.enable(TIME_STEP)

# ตั้งค่าพารามิเตอร์การขับขี่
MAX_SPEED = 6.0         # ความเร็วสูงสุด (เรเดียน/วินาที)
MAX_STEER = 0.5         # องศาเลี้ยวสูงสุด (เรเดียน) ~ 28 องศา

print("Rover Controller Started!")
print("==========================")
print("คลิกที่หน้าต่าง 3D ของ Webots เพื่อเริ่มควบคุม")
print("W : เดินหน้า")
print("S : ถอยหลัง")
print("A : เลี้ยวซ้าย")
print("D : เลี้ยวขวา")
print("==========================")

# 6. Main Loop
while robot.step(TIME_STEP) != -1:
    # รีเซ็ตค่าความเร็วและองศาเลี้ยวในทุกๆ Time step
    target_speed = 0.0
    target_steer = 0.0
    
    # อ่านค่าปุ่มที่ถูกกด
    key = keyboard.getKey()
    
    # ตรวจสอบว่าปุ่มใดถูกกดค้างไว้ (สามารถกด W+A พร้อมกันเพื่อเลี้ยวขณะเดินหน้าได้)
    while key != -1:
        if key == ord('W'):
            target_speed = MAX_SPEED
        elif key == ord('S'):
            target_speed = -MAX_SPEED
        elif key == ord('A'):
            target_steer = MAX_STEER
        elif key == ord('D'):
            target_steer = -MAX_STEER
            
        key = keyboard.getKey() # อ่านค่าปุ่มถัดไปเผื่อกดหลายปุ่ม
        
    # สั่งงานมอเตอร์ขับเคลื่อน
    for wheel in wheels:
        wheel.setVelocity(target_speed)
        
    # สั่งงานมอเตอร์เลี้ยว
    steer_right.setPosition(target_steer)
    steer_left.setPosition(target_steer)
    
    # 7. ดึงภาพจากกล้องและแสดงผลด้วย OpenCV
    raw_image = rgb_cam.getImage()
    if raw_image is not None:
        # Webots ส่งข้อมูลภาพมาในรูปแบบ 1D Array (BGRA format)
        # เราต้องแปลงเป็น 3D Numpy Array เพื่อให้ OpenCV อ่านได้
        image = np.frombuffer(raw_image, np.uint8).reshape((rgb_cam.getHeight(), rgb_cam.getWidth(), 4))
        
        # แสดงผลภาพ
        cv2.imshow("Almondmatcha - D435 RGB Feed", image)
        
        # จำเป็นต้องมี waitKey เล็กน้อยเพื่อให้ OpenCV อัปเดตหน้าต่าง GUI
        cv2.waitKey(1)