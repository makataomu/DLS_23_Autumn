from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dummy.db'
dummy_db = SQLAlchemy(app)


class DummyFoodAdditive(dummy_db.Model):
    # Same column definitions as the original FoodAdditive model
    id = dummy_db.Column(dummy_db.Integer, primary_key=True)
    e_code = dummy_db.Column(dummy_db.String(10))
    name_ru = dummy_db.Column(dummy_db.String(100))
    description = dummy_db.Column(dummy_db.String(500))
    synonyms = dummy_db.relationship('DummySynonym', backref='food_additive', lazy=True)


class DummySynonym(dummy_db.Model):
    # Same column definitions as the original Synonym model
    id = dummy_db.Column(dummy_db.Integer, primary_key=True)
    food_additive_id = dummy_db.Column(dummy_db.Integer, dummy_db.ForeignKey('dummy_food_additive.id'), nullable=False)
    synonym = dummy_db.Column(dummy_db.String(100))

def clear_data():
    dummy_db.session.query(DummyFoodAdditive).delete()
    dummy_db.session.query(DummySynonym).delete()
    dummy_db.session.commit()

def parse_text_and_insert_data(text):
    lines = text.strip().split('\n')
    parsed_data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split('\t')
        synonyms = []
        e_code = None
        
        if (parts[0][0] == 'E' or parts[0][0] == 'E') and (len(parts) > 1):
            # if it's not a synonym
            e_code = parts[0].strip()
            name_ru = parts[1].strip()
            if '(' in name_ru:
                start_index = name_ru.find('(')
                end_index = name_ru.find(')')
                synonyms.append(name_ru[start_index+1:end_index])
                name_ru = name_ru[:start_index] + name_ru[end_index+1:]
                
            description = None

            if len(parts) > 2:
                description = parts[2].strip()
        else:
            # it's a synonym
            start_index = parts[0].find(')')+1
            if parts[0][-1] == ')':
                # (ii) Малат натрия (?)
                syn = parts[0][start_index:-4]
            elif '?' in parts[0]:
                end_index = parts[0].find('?')
                syn = parts[0][start_index:end_index]
            else:
                syn = parts[0][start_index:].strip()
            synonyms.append(syn)

        if e_code:
            additive = DummyFoodAdditive(e_code=e_code, name_ru=name_ru, description=description)
            dummy_db.session.add(additive)
            dummy_db.session.commit()

        for synonym in synonyms:
            synonym_entry = DummySynonym(food_additive=additive, synonym=synonym)
            dummy_db.session.add(synonym_entry)
        dummy_db.session.commit()


text = """E300 	Аскорбиновая кислота (Витамин C) 	
E301 	Аскорбат натрия (Натриевая соль аскорбиновой кислоты) 	
E302 	Аскорбат кальция 	
E303 	Аскорбат калия 	
E304 	Сложный эфир жирной кислоты аскорбиновой кислоты 	
	(i) Аскорбилпальмитат 	
E305 	(ii) Аскорбилстеарат 	
E306 	Концентрат смеси Токоферолов 	
E307 	Альфа-токоферол синтетический 	
E308 	Гамма-токоферол синтетический 	
E309 	Дельта-токоферол синтетический 	
E310 	Пропилгаллат 	Вреден для кожи, вызывает сыпь
E311 	Октилгаллат 	Вреден для кожи, вызывает сыпь
E312 	Додецилгаллат 	Вреден для кожи, вызывает сыпь
E313 	Этилгаллат 	
E314 	Гваяковая смола 	
E315 	Эриторбовая кислота (Изоаскорбиновая кислота?) 	
E316 	Эриторбат натрия (Изоаскорбат натрия?) 	
E317 	Эриторбат калия (Изоаскорбат калия?) 	
E318 	Эритробат кальция (Изоаскорбат кальция?) 	
E319 	Трет-бутилгидрохинон 	
E320 	Бутилгидроксианизол 	Холестерин
E321 	Бутилгидрокситолуол 	Холестерин
E322 	Лецитины 	
E323 	Аноксомер 	
E324 	Этоксихин 	
E325 	Лактат натрия 	
E326 	Лактат калия 	
E327 	Лактат кальция 	
E328 	Лактат аммония 	
E329 	Лактат магния 	
E330 	Лимонная кислота 	Может вызвать рак
E331 	Цитраты натрия: 	
	(i) Цитрат натрия однозамещенный 	
	(ii) Цитрат натрия двузамещенный 	
	(iii) Цитрат натрия трехзамещенный 	
E332 	Цитраты калия: 	
	(i) Цитрат калия двузамещенный 	
	(ii) Цитрат калия трехзамещенный 	
E333 	Цитраты кальция 	
E334 	Винная кислота (L(+)-) 	
E335 	Тартраты натрия: 	
	(i) Тартрат натрия однозамещенный 	
	(ii) Тартрат натрия двузамещенный 	
E336 	Тартраты калия: 	
	(i) Тартрат калия однозамещенный 	
	(ii) Тартрат калия двузамещенный 	
E337 	Тартрат калия-натрия 	
E338 	Ортофосфорная кислота 	Вызывает расстройство желудка
E339 	Ортофосфаты натрия: 	Вызывает расстройство желудка
	(i) Ортофосфат натрия однозамещенный 	Вызывает расстройство желудка
	(ii) Ортофосфат натрия двузамещенный 	Вызывает расстройство желудка
	(iii) Ортофосфат натрия трехзамещенный 	Вызывает расстройство желудка
E340 	Ортофосфаты калия: 	Вызывает расстройство желудка
	(i) Ортофосфат калия однозамещенный 	Вызывает расстройство желудка
	(ii) Ортофосфат калия двузамещенный 	Вызывает расстройство желудка
	(iii) Ортофосфат калия трехзамещенный 	Вызывает расстройство желудка
E341 	Ортофосфаты кальция: 	Вызывает расстройство желудка
	(i) Ортофосфат кальция однозамещенный 	Вызывает расстройство желудка
	(ii) Ортофосфат кальция двузамещенный 	Вызывает расстройство желудка
	(iii) Ортофосфат кальция трехзамещенный 	Вызывает расстройство желудка
E342 	Ортофосфаты аммония: 	
	(i) Ортофосфат аммония однозамещенный 	
	(ii) Ортофосфат аммония двузамещенный 	
E343 	Ортофосфаты магния: 	Вызывает кишечные расстройства
	(i) Ортофосфат магния однозамещенный 	Вызывает кишечные расстройства
	(ii) Ортофосфат магния двузамещенный 	Вызывает кишечные расстройства
	(iii) Ортофосфат магния трехзамещенный 	Вызывает кишечные расстройства
E344 	Цитрат лецитина 	
E345 	Цитрат магния 	
E349 	Малат аммония 	
E350 	Малаты натрия: 	
	(i) Малат натрия однозамещенный 	
	(ii) Малат натрия (?) 	
E351 	Малаты калия: 	
	(i) Малат калия однозамещенный 	
	(ii) Малат калия (?) 	
E352 	Малаты кальция: 	
	(i) Малат кальция однозамещенный 	
	(ii) Малат кальция (?) 	
E353 	Мета-винная кислота 	
E354 	Тартрат кальция 	
E355 	Адипиновая кислота 	
E356 	Адипат натрия 	
E357 	Адипат калия 	
E359 	Адипат аммония 	
E363 	Янтарная кислота 	
E365 	Фумарат натрия 	
E366 	Фумарат калия 	
E367 	Фумарат кальция 	
E368 	Фумарат аммония 	
E370 	Гептонолактон 	
E375 	Никотиновая кислота (ниацин) 	
E380 	Цитраты аммония 	
E381 	Цитраты аммония железа 	
E383 	Глицерофосфат кальция 	
E384 	Изопропилцитратная смесь 	
E385 	Кальция динатриевая соль этилендиаминтетрауксусной кислоты (CaNa2 ЭДТА) 	
E386 	Динатриевая соль этилендиаминтетрауксусной кислоты 	
E387 	Оксистеарин 	
E388 	Тиопропионовая кислота 	
E389 	Дилаурил тиодипропионат 	
E390 	Дистеарил тиодипропионат 	
E391 	Фитиновая кислота 	
E399 	Лактобионат кальция 	"""

if __name__ == '__main__':
    with app.app_context():
        #clear_data()
        dummy_db.create_all()
        parse_text_and_insert_data(text)
