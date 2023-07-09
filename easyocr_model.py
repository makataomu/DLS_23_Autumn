import cv2
import easyocr
from fuzzywuzzy import fuzz
#import matplotlib.pyplot as plt

'''reader = easyocr.Reader(['en'], gpu=False)

image_path = 'uploads\image_en_5.jpg'

def bbox_text(image_path,  dec='greedy', beamW=5):
    img = cv2.imread(image_path)
    out = reader.readtext(img, decoder=dec, beamWidth=beamW, paragraph=True, y_ths = -0.1, x_ths=-0.1)
    #out = reader.readtext(img)
    return out

print(bbox_text(image_path))
'''
output = 'NlGRED1ENIS'
#output = 'COCIIB'
output =  '(Состав:'

start_word_en = 'ingridients'
start_word_ru_1 = 'состав'
start_word_ru_2 = 'coctab'

# make a list with variations or exclude all sneaky letters

out_lower = output.lower()
out_lower = out_lower.replace(':', '').strip()

def find_start_word(out_lower, threshold=62):
    out_lower = output.lower().replace(':', '').strip()  
    length = len(out_lower)

    if length > 7:
        # it can be 'ingridients'
        similarity = fuzz.ratio(out_lower, start_word_en)
        #print(similarity)
        if similarity > threshold:
            return True
    elif length > 4:
        similarity = fuzz.ratio(out_lower, start_word_ru_1)
        #print(similarity)
        if similarity > threshold:
            return True
        similarity = fuzz.ratio(out_lower, start_word_ru_2)
        #print(similarity)
        if similarity > threshold:
            return True
    return False

print(find_start_word(out_lower))

# exclude sneaky letters

output = 'NlGRED1ENIS'
output = 'COCIIB'

def find_start_word_ex(output):
    translation_table = output.maketrans('', '', 'IoO1lT')
    new_output = output.translate(translation_table)
    start_words = ['ngrdens', 'ccab', 'ссав']

    for word in start_words:
        similarity = fuzz.ratio(new_output.lower(), word.lower())
        if similarity > 80:
            return True
    return False

def grand_finale(out):
    # input: output from OCR
    # output: list with all found ingridients
    
    start_word_found = False
    final_output = []

    # Step 1: Find the start word
    len_out = len(out)

    for i in range(len_out):
        words = out[i][1].lower().split()
        for j in range(len(words)):
            if find_start_word(words[j]):
                start_word_found = True
            break
    
    # Step 2:
    if start_word_found:
        # start where start word is located, which is out[i][1]
        for x in range(i, len_out):
            words = out[x][1].lower().split()
            # start after start word, which is words[j]
            for y in range(j+1, len(words)):
                final_output.append(search_word(words[y]))

    return final_output
