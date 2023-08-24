"""
BSD 3-Clause License

Copyright (c) 2023, Mohamed Abdelkader Zahana

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import cv2
import os
import sys

def resize_image(image, target_size=(640, 640)):
    height, width = image.shape[:2]
    scale_x = target_size[0] / width
    scale_y = target_size[1] / height
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
    return resized, scale_x, scale_y

def save_bbox_to_file(image, bbox, file_path, class_id=0):
    height, width = image.shape[:2]
    x_center = (bbox[0] + bbox[2] / 2) / width
    y_center = (bbox[1] + bbox[3] / 2) / height
    w = bbox[2] / width
    h = bbox[3] / height
    with open(file_path, 'w') as f:
        f.write(f"{class_id} {x_center} {y_center} {w} {h}")

def overlay_text(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.6, color=(0, 255, 0), thickness=2):
    cv2.putText(image, text, position, font, font_scale, color, thickness)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python script_name.py path_to_original_images")
        sys.exit(1)

    image_dir = sys.argv[1]
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith('.jpg')])
    image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))  # Sort images based on numeric filename

    output_dir = 'output'
    output_image_dir = os.path.join(output_dir, "images")
    output_label_dir = os.path.join(output_dir, "labels")
    output_bbox_dir = os.path.join(output_dir, "imgs_with_bbx") 
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)
    os.makedirs(output_bbox_dir, exist_ok=True)

    image_index = 0
    first_image_path = os.path.join(image_dir, image_files[image_index])
    first_image = cv2.imread(first_image_path)
    resized_first_image, scale_x, scale_y = resize_image(first_image)
    overlayed_img = resized_first_image.copy()
    height, width = overlayed_img.shape[:2]
    overlay_text(overlayed_img, "PAUSED", (width//2 - 40, 30), color=(0, 0, 255))
    overlay_text(overlayed_img, "First, Select bounding box and press ENTER", (width//2 - 150, 50))
    overlay_text(overlayed_img, "Press 'p' to pause/unpause", (width//2 - 150, 70))
    overlay_text(overlayed_img, "Use left/right arrow keys to navigate frames", (width//2 - 150, 90))
    overlay_text(overlayed_img, "Press 'q' or 'c' to quit", (width//2 - 50, 110), color=(0, 0, 255))
    roi = cv2.selectROI("Tracking", overlayed_img, False, False)
    cv2.destroyAllWindows()

    tracker = cv2.TrackerCSRT_create()
    tracker.init(resized_first_image, roi)
    prev_bbox = roi

    paused = False
    FPS = 30
    DELAY = int(1000 / FPS) # millisecond

    while image_index < len(image_files):
        image_path = os.path.join(image_dir, image_files[image_index])
        image = cv2.imread(image_path)
        resized_image, _, _ = resize_image(image)

        ok = False
        if not paused:
            ok, bbox = tracker.update(resized_image)
            if ok:
                prev_bbox = bbox
                file_name = os.path.splitext(os.path.basename(image_path))[0]
                txt_file_path = os.path.join(output_label_dir, file_name + '.txt')
                save_bbox_to_file(resized_image, bbox, txt_file_path)
                scaled_image_path = os.path.join(output_image_dir, file_name + '.jpg')
                cv2.imwrite(scaled_image_path, resized_image)
            else:
                print(f"Tracking failed for image: {image_files[image_index]}")
                paused = True

        # Always display the current image with bounding box (if tracking is successful)
        overlayed_img = resized_image.copy()
        if ok:
            overlayed_img = cv2.rectangle(overlayed_img, (int(bbox[0]), int(bbox[1])), (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3])), (0, 255, 0), 2)
            overlayed_img_path = os.path.join(output_bbox_dir, file_name + '.jpg')
            cv2.imwrite(overlayed_img_path, overlayed_img)
            
        else:
            if not ok and not paused:
                overlay_text(overlayed_img, "FAIL", (width//2 - 40, 30), color=(0, 0, 255))
            overlay_text(overlayed_img, "Press 'r' to initialize", (width//2 - 100, 50), )
            overlay_text(overlayed_img, "Use left/right arrow keys to navigate frames", (width//2 - 150, 70))
        
        cv2.imshow("Tracking", overlayed_img)

        key = cv2.waitKey(DELAY) & 0xFF
        if key == ord('p'):
            paused = not paused
        elif key == ord('r'):
            overlayed_img = resized_image.copy()
            overlay_text(overlayed_img, "Select bounding box and press ENTER", (width//2 - 150, 30))
            roi = cv2.selectROI("Tracking", overlayed_img, False, False)
            tracker = cv2.TrackerCSRT_create() # Reset the tracker
            tracker.init(resized_image, roi)
            prev_bbox = roi
            paused = False
        elif key == ord('l'): # Right key
            paused = True
            image_index += 1
        elif key == ord('j'): # Left key
            paused = True
            image_index -= 1
            if image_index < 0:
                image_index=0
        elif key == ord('q') or key == ord('Q'):
            break

        if not paused:
            image_index += 1

cv2.destroyAllWindows()
