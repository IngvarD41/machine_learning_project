# Machine Learning Project
Ingvar Drikkit, Jako Aimsalu, Laur Edvard Lindmaa, Mattias Avi
## P03 Intersection finder
Goal is to identify major roads (asphalt and gravel)
We must output a file in `.csv` format in the following format. The left-bottom corner is 0,0.
* `km-square-coord, offsetX-offsetY, offsetX-offsetY, offsetX-offsetY`
* `515000_6547000, 213-556, 452-889, 881-121`

## Data
* 1x1 km squares that contain 1000x1000 pixels. Each pixel is 1 meter.
* 3 layers: map, orto, black-white

Training data
* 6000 images
* 6000 list of intersection offsets (self-labeled)

Test data
* 1000 images (safeguarded until grading)

## TODO
1. Application to label training images
    - Web vs local app
1. Propose and compare possible algorithms
    - YOLO is too powerful for the task
    - Opencv might be capable.
1. Write chosen algorithm in Python
1. Train the model with training data
1. Validate the model
    - Improve hyperparameters and retrain
