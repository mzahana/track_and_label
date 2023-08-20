# track_and_label
A script to automate image dataset labeling. Images are asusmed to be extracted from a video. This code assumes you have a directory with images taken sequentially, which you would like to label with bounding boxes for object tracking. The images should be named in a way that allows them to be sorted in the correct order.

**NOTE** Currently the sctit supports single object tracking and labeling. Multi-object is planned for future release.

# Dependencies
* OpenCV
* `pip install opencv-contrib-python`
# Usage
* First extract the set of ordered images from a video.
* Then, execute,
  ```
  python3 track_and_label.py images_directory
  ```
There are instrucitons on the displayed window to show you how you can use the script

There should be 3 generated directories that shall be saved inside a directory named `output`
* `output/images` Images with `640x640` size
* `ouput/labels` Bounding boxes compatibe with Yolov5
* `output/imgs_with_bbx` images with bounding boxes for inspection

* The `output` directory will be in the same directory as the `track_and_label.py` script.
