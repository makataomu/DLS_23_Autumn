from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory
from markupsafe import escape
import datetime
import os
import time

from werkzeug.utils import secure_filename
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SubmitField

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

import easyocr
import cv2

from search_demo import search_word_in_ecodes, search_word_in_additive_names_ru, search_similar_in_additive_names_ru
from search_demo import search_word_in_synonyms, search_similar_in_synonyms, search_word
from search_demo import find_start_word, grand_finale

# set FLASK_APP=app
# set FLASK_ENV=development
# flask run

# Accepted image for to upload for object detection model

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = '17a24934a1a3a47d6acfa7e5fbbb79940489637535cd0ab1'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads' 

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///names_en.db'
db = SQLAlchemy(app)

class FoodAdditive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    e_code = db.Column(db.String(10))
    name_ru = db.Column(db.String(100))
    description = db.Column(db.String(500))
    synonyms = db.relationship('Synonym', backref='food_additive', lazy=True)


class Synonym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_additive_id = db.Column(db.Integer, db.ForeignKey('food_additive.id'), nullable=False)
    synonym = db.Column(db.String(100))



class UploadForm(FlaskForm):
    photo = FileField(
        validators = [
            FileAllowed(photos, 'Only images are allowed'),
            FileRequired('File field should not be empty')
        ]
    )
    submit = SubmitField('Submit')

# инструкции - welcome screen
@app.route('/')
def welcome():
    return render_template('welcome.html')
# name of functon goes to <a href="{{ url_for('welcome') }}">FlaskApp</a>

# загрузить картинку и submit
@app.route('/uploads/<filename>')
def get_file(filename):
    return send_from_directory(app.config['UPLOADED_PHOTOS_DEST'], filename)
    

@app.route('/upload/', methods=('GET', 'POST'))
def upload():
    form = UploadForm()
    # will be True if submitted and valid form 
    if form.validate_on_submit():
        filename = photos.save(form.photo.data)
        file_url = url_for('get_file', filename=filename)
        return redirect(url_for('output', file_url=file_url))  # Pass file_url as a parameter to the output route
    else:
        file_url = None
    return render_template('image.html', form=form, file_url=file_url)
    
# загрузка - ожидание

# вывод списка 
@app.route('/output/')
def output():
    file_url = request.args.get('file_url')  # Retrieve the file_url parameter from the request
    # Get the absolute path of the uploaded file
    image_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_url)

    #print(image_path)
    start_time = time.time()
    # easyocr model 
    reader = easyocr.Reader(['ru'], gpu=False)

    def ocr_model(image_path,  dec='greedy', beamW=5):
        img = cv2.imread(image_path)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        out = reader.readtext(gray_image, decoder=dec, 
                              beamWidth=beamW, paragraph=True, 
                              y_ths = -0.1, x_ths=-0.1)
        print(out)
        return out

    ingrs = grand_finale(ocr_model(f'{image_path[1:]}'), FoodAdditive, Synonym)

    end_time = time.time()
    print('TIME:', start_time-end_time)
    return render_template('ingridients.html', file_url=file_url, items=ingrs)

# расписать миссию проекта
'''@app.route('/about/')
def about():
    return render_template('about.html')'''

if __name__ == "__main__":
    app.run(debug=True)