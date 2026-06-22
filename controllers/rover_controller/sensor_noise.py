import numpy as np

def apply_sunlight_interference(depth_image, light_intensity, max_range, threshold=800, max_light=2500):
    """
    Simulates sunlight interference on active IR depth sensors (like RealSense).
    When sunlight hits the sensor, it washes out the IR pattern, causing noisy
    depth readings and "blind spots" (invalid pixels).
    
    Args:
        depth_image (np.ndarray): 2D array of depth values.
        light_intensity (float): Current light intensity from LightSensor.
        max_range (float): Max range of the depth sensor.
        threshold (float): Light intensity above which interference starts.
        max_light (float): Light intensity at which interference is maximum.
        
    Returns:
        np.ndarray: Modified depth image with interference.
    """
    if light_intensity < threshold:
        return depth_image # No interference, perfect depth
        
    # Calculate noise level (0.0 to 1.0)
    noise_factor = np.clip((light_intensity - threshold) / (max_light - threshold), 0.0, 1.0)
    
    noisy_depth = depth_image.copy()
    
    # 1. Add random Gaussian noise that scales with light
    # In extreme light, noise fluctuates up to 15% of max_range
    noise = np.random.normal(0, noise_factor * max_range * 0.15, depth_image.shape)
    noisy_depth += noise
    
    # 2. Add "blind spots" (dropouts where depth is lost)
    # The brighter the light, the more pixels drop out.
    dropout_prob = noise_factor * 0.6 # Up to 60% dropout in extreme glare
    dropouts = np.random.rand(*depth_image.shape) < dropout_prob
    noisy_depth[dropouts] = max_range # Webots uses max_range for "no return"
    
    # Ensure values are within bounds
    noisy_depth = np.clip(noisy_depth, 0.0, max_range)
    
    return noisy_depth
