# Search and Sample Return Project

[//]: # (Image References)

[image_0]: ./misc/rover_image.jpg
[image_1]: ./misc/pic_1.png
[image_2]: ./misc/pic_2.png
[image_3]: ./misc/pic_3.png
[image_4]: ./misc/pic_4.png
[image_5]: ./misc/pic_5.png
[image_6]: ./misc/pic_6.png
[image_7]: ./misc/pic_7.png
[image_8]: ./misc/pic_8.png
[image_9]: ./misc/pic_9.png
[image_10]: ./misc/pic_10.png
[image_11]: ./misc/pic_11.png
[image_12]: ./misc/pic_12.png
[image_13]: ./misc/pic_13.png
[image_14]: ./misc/pic_14.png
[image_15]: ./misc/pic_15.png

This project is about the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) but I've only finished the part specified for Udacity RoboND Project, to detect the entire environment and find rocks. 

## The Simulator
You can download the simulator in [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).    
The simulator looks as below:

![alt text][image_0]

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Recording Data
In the training mode of simulator, you can record some data. The data includes images and logs. Logs is the state of the Rover in every image. 

## Identify the environment(perception_step)
The environment in the simulator includes 3 parts which are the navigable road, the obstacle and sampleRocks. The navigable road should be identified with blue color by Rover's camera. The obstacle is the mountain and some black rocks. SampleRocks are the yellow objects that the Rover needs to find and pick up. The aim of this step is to seperate these three kind of objects.

### Perspect Transform
The eye of the Rover is the camera, this view can be called as rover view. 

![alt text][image_1]

But we also have another "camera" called top-down view. The map needs Rover to percept usually in top-down view.

![alt text][image_2]

And if the Rover is in top-down view, It will be easy to know the place and the direction of Rover. An example of top-down view is as below.

![alt text][image_3]

So get the range of rover view in top-down view is very useful to map two datas in next step, rover's positon and rover's img. This means "Where the rover and what it is looking now!"  
Now we'll get "what it is looking now" from top-down view(I'll call this view as map-view).
* First press 'G' to display grids in the simulator.

![alt text][image_4]

* Then get rover view image(Don't move the Rover).
* Define 4 source points(maybe the grid cell in rover view) and also 4 destination points(fit for the size of top-down view) * Use cv2.getPerspectiveTransform and cv2.warpPerspective to get image of map-view. You can get help [here](https://docs.opencv.org/trunk/da/d6e/tutorial_py_geometric_transformations.html)

![alt text][image_5]

### Color Thresholding
With color thresholding the Rover can identify the navigable road, the obstacle and sampleRocks. So this work focus on color of images. Color thresholding is set a threshold of each RGB channels. But it is useful to set a threshold of HSV channels to identify small object in images as like the sampleRocks, more information [here](http://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_colorspaces/py_colorspaces.html)  
So use cv2.cvtColor and add param cv2.COLOR_RGB2HSV to transform image into HSV channels before doing color thresholding to sampleRocks.  
The effect of color thresholding as bellow:

![alt text][image_6]

The result of Color Thresholding to map-view is like this.

![alt text][image_7]

There is a little issue, the original point(the 0 point)is not the place of Rover. So use rover_coords function in my code to tranform it. Then the final result of Color Thresholding as below.

![alt text][image_8]

### Map to World Coordinates
The position information can be gotten from the simulator when the program connected to it. Also it is exist in a .csv file when Recording Data step.

![alt text][image_9]

Then the map of simulator as below.

![alt text][image_10]

With position and map-view we can map the Rover into the map.

![alt text][image_11]

Next tell some detail.  
Rover has its own Rover-Coordinate and it's different from World-Coordinate most of time. It is import to keep the only coordinate system when we deal with object's location. So use [Rotation Matrix](https://en.wikipedia.org/wiki/Rotation_matrix) to transform the Rover-Coordinate. In my code, function rotate_pix will apply the rotation and function translate_pix will perform the translation to the map. Then function pix_to_world will call them to finish this job.

![alt text][image_12]

### Code of perception_step function
Here is some points of my perception_step function.  
* I use three var obstacle_disp, navigable_disp, sampleRocks_disp to display non-warped images into the bottom left window in the simulator. I think it is comfortable to look.
* I set a decision about if the Rover pitch too much.
* I set a decision about if the sampleRocks in sight, and if a sampleRock has been found, self.samples_located in drive_rover.py will be True.

## Decision(decision_step)
When the simulator is working in Autonomous Mode, some states of Rover will be display here.

![alt text][image_13]

All of parameters of Rover will be transport between the simulator and the file "driver_rover.py" as a class RoverState.

![alt text][image_14]

Make a instance of this class can control the Rover by all of these parameters. But firstly caculator the angle for Rover to rotate the direction and caculator the distance of main direction in the Color Thresholding Image is very useful to control the Rover.

![alt text][image_15]

The to_polar_coords will do this job in my code.
### Modify the logic of decision
The "perception.py" is the eye of the Rover and also the "decision.py" file is the control center of the Rover. They are called in the "driver_rover.py" to complate once step of Rover Moving. We can get one image from RoverState.img in only one step. Then deal with this image will make a decision about next moving.  
It's really hard for me to modify "decision.py". I tried several kind of strategy, but it is always get worse. So in this submit I only change Rover.nav_dists**2 to be len(Rover.nav_angles). Because the value of Rover.stop_forward is 50, but Rover.nav_dists is just an array. They can't be caculated together with '>' or '<'.
## Future Enhancement
I'll work on this project. I'm trying the A* algorithm to make route planning.

