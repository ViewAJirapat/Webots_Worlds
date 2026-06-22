from controller import Robot, Keyboard
import cv2
import numpy as np
import sensor_noise

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

# เปิดใช้งานกล้อง RGB และ Depth
rgb_cam = robot.getDevice('d415_rgb')
rgb_cam.enable(TIME_STEP)

depth_cam = robot.getDevice('d415_depth')
depth_cam.enable(TIME_STEP)

# เปิดใช้งาน Light Sensor สำหรับเช็คแสงอาทิตย์
light_sensor = robot.getDevice('sunlight_sensor')
if light_sensor is not None:
    light_sensor.enable(TIME_STEP)

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
    # ส่วนแสดงภาพจากกล้อง RGB และ Depth
    # ==========================================
    raw_rgb = rgb_cam.getImage()
    
    # ดึงค่า depth
    # Webots RangeFinder จะให้ข้อมูลแบบ float array กลับมา
    raw_depth = depth_cam.getRangeImage()
    
    if raw_rgb is not None and raw_depth is not None:
        # 1. แสดงผล RGB
        image_rgb = np.frombuffer(raw_rgb, np.uint8).reshape((rgb_cam.getHeight(), rgb_cam.getWidth(), 4))
        
        # 2. แสดงผล Depth (RangeFinder)
        # ลองใช้ frombuffer ก่อนเพื่อความเร็ว ถ้าไม่ได้ให้ใช้ np.array ธรรมดา (รองรับ Webots ทุกเวอร์ชัน)
        try:
            image_depth = np.frombuffer(raw_depth, dtype=np.float32).reshape((depth_cam.getHeight(), depth_cam.getWidth()))
        except (AttributeError, TypeError):
            image_depth = np.array(raw_depth, dtype=np.float32).reshape((depth_cam.getHeight(), depth_cam.getWidth()))
        
        # จัดการค่าอนันต์ (inf) กรณีที่มองไม่เห็นวัตถุ (อยู่ไกลกว่า maxRange)
        max_range = depth_cam.getMaxRange()
        image_depth = np.nan_to_num(image_depth, posinf=max_range, neginf=0.0)
        
        # === เพิ่ม Noise จำลองแสงแดดกวนเซ็นเซอร์ IR ===
        if light_sensor is not None:
            light_val = light_sensor.getValue()
            image_depth = sensor_noise.apply_sunlight_interference(
                image_depth, light_val, max_range, threshold=800, max_light=2500
            )
        # ===============================================
        
        # Normalize ข้อมูล Depth ให้เป็นช่วง 0-255 เพื่อการมองเห็น (ภาพขาวดำ)
        depth_normalized = np.clip((image_depth / max_range) * 255, 0, 255).astype(np.uint8)
        
        # นำมาใส่ Color Map จะทำให้ดูค่าความลึกง่ายขึ้น (ใกล้จะร้อน(แดง) ไกลจะเย็น(น้ำเงิน))
        # ต้องกลับค่าก่อนเพื่อให้ของที่ใกล้กว่า (ค่าน้อย) มีสีโทนร้อน
        depth_colormap = cv2.applyColorMap(255 - depth_normalized, cv2.COLORMAP_JET)
        
        # แสดงหน้าต่างวิดีโอ
        cv2.imshow("RealSense D415 - RGB", image_rgb)
        cv2.imshow("RealSense D415 - Depth", depth_colormap)
        cv2.waitKey(1)