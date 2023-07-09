from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import re
from fuzzywuzzy import fuzz

import cv2
import easyocr



def search_word_in_ecodes(word, FoodAdditive):
    if 'e' in word or 'E' in word or 'е' in word or 'Е' in word:
        word = word.upper().replace('Е', 'E')
        start_index = word.find('E')
        word = word[start_index:start_index+4]
        #print(word)
        additive = FoodAdditive.query.filter(FoodAdditive.e_code == word).first()
        if additive is not None:
            return [additive.e_code, additive.name_ru, additive.description]
        return None
    else:
        return None


def search_word_in_additive_names_ru(word, FoodAdditive):
    additive = FoodAdditive.query.filter(FoodAdditive.name_ru == word).first()
    if additive is not None:
        return [additive.name_ru, additive.description]
    return None


def search_similar_in_additive_names_ru(word, FoodAdditive):
    additives = FoodAdditive.query.all()
    max_similarity = 0
    best_match = None

    for additive in additives:
        name_ru = additive.name_ru
        similarity = fuzz.ratio(word, name_ru)
        
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = additive

    if best_match is not None:
        return [max_similarity, best_match.name_ru, best_match.description]
    return None


def search_word_in_synonyms(word, Synonym):
    synonym = Synonym.query.filter(Synonym.synonym == word).first()
    if synonym:
        additive = synonym.food_additive
        return [synonym.synonym, additive.name_ru, additive.description] 
    return None


def search_similar_in_synonyms(word, Synonym):
    synonyms = Synonym.query.all()
    max_similarity = 0
    best_match = None
    sim_synych = None

    for synonym in synonyms:
        synonym_word = synonym.synonym
        similarity = fuzz.ratio(word, synonym_word)

        if similarity > max_similarity:
            max_similarity = similarity
            best_match = synonym.food_additive
            sim_synych = synonym.synonym

    if best_match is not None:
        return [max_similarity, sim_synych, best_match.name_ru, best_match.description]
    return None


def search_word(word, FoodAdditive, Synonym):
    #print(word)
    # Step 1: Search among E-codes
    result = search_word_in_ecodes(word, FoodAdditive)
    if result is not None:
        print('ecode', result)
        return result

    # Step 2: Search among additive names
    result = search_word_in_additive_names_ru(word, FoodAdditive)
    if result is not None:
        print('real name', result)
        return result

    # Step 3: Search among synonyms
    result = search_word_in_synonyms(word, Synonym)
    if result is not None:
        print('synonym', result)
        return result
    
    # Step 4: Search similar among additive names
    similar_name = search_similar_in_additive_names_ru(word, FoodAdditive)

    # Step 5: Search similar among synonyms
    similar_syn = search_similar_in_synonyms(word, Synonym)

    threshold = 73 # найдено ручками
    if similar_name is not None and similar_syn is not None:
        similarity_name = similar_name[0]
        similarity_syn = similar_syn[0]
        if similarity_name >= similarity_syn:
            if similarity_name > threshold:
                print('symname', similar_name)
                return similar_name
            else:
                return None
        else:
            if similarity_syn > threshold:
                print('symsyn', similar_syn)
                return similar_syn
            else:
                return None
    
    # Word not found
    return None


def find_start_word(word, threshold = 62, 
                    start_word_en = 'ingridients', 
                    start_word_ru_1= 'состав', 
                    start_word_ru_2= 'coctab'):
    start_word_en 
    out_lower = word.lower().replace(':', '').strip()  
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


def grand_finale(out, FoodAdditive, Synonym):
    # input: output from OCR
    # output: list with all found ingredients

    final_output = []

    # Step 1: Find the start word
    len_out = len(out)
    
    # Go through all words
    for x in range(len_out):
        words = out[x][1].lower().split()
        for y in range(len(words)):
            final_output.append(search_word(words[y], FoodAdditive, Synonym))

    final_output = [x for x in final_output if x is not None]
    return final_output

'''
def update_e_codes():
    additives = FoodAdditive.query.all()
    
    for additive in additives:
        old_e_code = additive.e_code
        new_e_code = old_e_code.replace('Е-', 'E') # eng E-
        new_e_code = old_e_code.replace('E-', 'E') # rus Е-
        print(new_e_code)
        additive.e_code = new_e_code

    db.session.commit()'''


word = 'E120'
word = 'Азорубин'
word = 'пввпаыпв'

'''
if __name__ == '__main__':
    with app.app_context():
        print(search_word(word))'''

