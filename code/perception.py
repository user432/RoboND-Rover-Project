import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh=(160, 160, 160)):
    # Create an array of zeros same xy size as img, but single channel
    navigable_layer = np.zeros_like(img[:,:,0])
    obstacle_layer = np.zeros_like(img[:,:,0])
    sampleRocks_layer = np.zeros_like(img[:,:,0])
    # Threshold the image
    sampleRocks_thresh = (20,100,100)
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    navigable   = (img[:,:,0] > rgb_thresh[0]) \
                & (img[:,:,1] > rgb_thresh[1]) \
                & (img[:,:,2] > rgb_thresh[2])
    sampleRocks = (hsv[:,:,0] > sampleRocks_thresh[0]) \
                & (hsv[:,:,1] > sampleRocks_thresh[1]) \
                & (hsv[:,:,2] > sampleRocks_thresh[2])
    obstacle    = (img[:,:,0] <= rgb_thresh[0]) \
                & (img[:,:,1] <= rgb_thresh[1]) \
                & (img[:,:,2] <= rgb_thresh[2])
    # Return the binary images for ground, rock and obstacles.
    return navigable, obstacle, sampleRocks

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # NOTE: camera image is coming to you in Rover.img

    # 1) Define source and destination points for perspective transform
    # Set a bottom offset to account for the fact that the bottom of the image
    # is not the position of the rover but a bit in front of it
    # this is just a rough guess, feel free to change it!
    scale = 10
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[14, 140], [301, 140], [200, 96], [118, 96]])
    destination = np.float32([[Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - bottom_offset],
                              [Rover.img.shape[1] / 2 + dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              [Rover.img.shape[1] / 2 - dst_size, Rover.img.shape[0] - 2 * dst_size - bottom_offset],
                              ])

    # 2) Apply perspective transform
    warped = perspect_transform(Rover.img, source, destination)

    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    navigable, obstacle, sampleRocks = color_thresh(warped)
    navigable_disp, obstacle_disp, sampleRocks_disp = color_thresh(Rover.img)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
    Rover.vision_image[:,:,0] = obstacle_disp*255
    Rover.vision_image[:,:,1] = sampleRocks_disp*255
    Rover.vision_image[:,:,2] = navigable_disp*255
    # 5) Convert map image pixel values to rover-centric coords
    obstacle_x, obstacle_y = rover_coords(obstacle)
    sampleRocks_x, sampleRocks_y = rover_coords(sampleRocks)
    navigable_x, navigable_y = rover_coords(navigable)
    # 6) Convert rover-centric pixel values to world coordinates
    navigable_x_world, navigable_y_world = pix_to_world(navigable_x, navigable_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], scale)
    sampleRocks_x_world, sampleRocks_y_world = pix_to_world(sampleRocks_x, sampleRocks_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], scale)
    obstacle_x_world, obstacle_y_world = pix_to_world(obstacle_x, obstacle_y, Rover.pos[0], Rover.pos[1], Rover.yaw, Rover.worldmap.shape[0], scale)

    # 7) Update Rover worldmap (to be displayed on right side of screen)
    # Avoid rover pitch to accelerate
    if ((Rover.pitch > 359.5 or Rover.pitch < 0.5) and (Rover.roll > 359.5 or Rover.roll < 0.5)):
        Rover.worldmap[obstacle_y_world.astype(int), obstacle_x_world.astype(int), 0] += 1
        Rover.worldmap[sampleRocks_y_world.astype(int), sampleRocks_x_world.astype(int), 1] += 1
        Rover.worldmap[navigable_y_world.astype(int), navigable_x_world.astype(int), 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    # Identify if the sampleRocks in sight
    if len(sampleRocks_x_world) > 0:
        dist, angles = to_polar_coords(sampleRocks_x, sampleRocks_y)
        Rover.nav_dists = dist
        Rover.nav_angles = angles
        Rover.samples_located = True
    else:
        dist, angles = to_polar_coords(navigable_x, navigable_y)
        Rover.nav_dists = dist
        Rover.nav_angles = angles
        
    return Rover