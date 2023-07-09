import cv2
import easyocr
import os

reader = easyocr.Reader(['ru'], gpu=False)

def ocr_model_demo(image_path,  dec='greedy', beamW=5):
    img = cv2.imread(image_path)
    out = reader.readtext(img, decoder=dec, beamWidth=beamW, paragraph=True, y_ths = -0.1, x_ths=-0.1)
    # out в виде листа из листов вида [bbox, text, score] 
    for bbox, text in out:
      print(text)


def check_images_in_folder(folder_path, dec='greedy', beamW=5):
    
    file_list = os.listdir(folder_path)
    image_files = [file for file in file_list]

    # Rename the image files
    i = 1
    for image_file in image_files:
        print(i, 'IMAGE!!!')
        # Get the full path of the image file
        image_path = os.path.join(folder_path, image_file)
        ocr_model_demo(image_path)
        i += 1

# Usage example
folder_path = r"minitest"

check_images_in_folder(folder_path)
