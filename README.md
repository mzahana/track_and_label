# track_and_label

A script to automate image dataset labeling. Images are asusmed to be extracted from a video. This code assumes you have a directory with images taken sequentially, which you would like to label with bounding boxes for object tracking. The images should be named in a way that allows them to be sorted in the correct order.

**NOTE** Currently the script supports single object tracking and labeling. The multi-object use case is planned for future release.

## Dependencies

* `Python >= 3.8`
* `OpenCV >= 4.2.0`
* `pip install opencv-contrib-python`
* `pip3 install Pillow`
* `sudo apt-get install python3-pil.imagetk`
* `sudo apt-get install python3-tk`

## Usage

### Image extraction form a video

You can use the `extract_frames_from_video.py` to extract images from a video.

* First download the video
* Run the script `python3 extract_frames_from_video.py`
* It will open a GUI in which you can select the input video, the output directory, the start/end time, frame/second and then you can  extract the image frames accordingly.

### Image renaming to desired ordering

If you find that the output directory contains filenames that you'd like to organize in a more meaningful way, you can utilize a Python script to achieve this. The script allows you to rename the files within the directory according to a desired order.

```python
python3 rename_files.py /path/to/your/folder
```

Remember to customize the file extension in the script if your images have a different extension, such as `.png` or `.jpeg`.

### Labeling

* First extract the set of ordered images from a video.
* Then, execute,

  ```python
  python3 track_and_label.py images_directory
  ```

There are instrucitons on the displayed window to show you how you can use the script

There should be 3 generated directories that shall be saved inside a directory named `output`

* `output/images` Images with `640x640` size
* `ouput/labels` Bounding boxes compatibe with Yolov5
* `output/imgs_with_bbx` images with bounding boxes for inspection

* The `output` directory will be in the same directory as the `track_and_label.py` script.
