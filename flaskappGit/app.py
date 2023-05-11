import os
from flask import (Flask, render_template, request,
                   session, url_for, redirect, send_file)
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from random import randint
from io import BytesIO
from os import urandom

from matplotlib.image import imread
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

# объект приложения
app = Flask(__name__)
# создадим ключ для сессий
app.secret_key = urandom(24)


# главная страница с капчей
@app.route("/", methods=['POST', 'GET'])
def start():
    error = False
    if request.method == "POST":
        # получаем данные формы
        input_captcha = request.values.get('input_captcha')
        # получаем данные сессии
        sess_captcha = session.get('code')
        # сравниваем данные сессии и формы
        if str(input_captcha).lower() == str(sess_captcha).lower():
            # при успехе перенаправляем на
            # страничку приветствия
            return redirect(url_for('image'))
        else:
            # при неправильном вводе кода
            # капчи - показываем надпись
            error = True
    return render_template('simple.html', error=error)


# генерация собственной капчи при помощи `Pillow`
@app.route('/captcha.png', methods=['GET'])
def captcha(width=300, height=100):
    # генерация кода капчи из 5 символов
    code = str(randint(10000, 99999))
    # сгенерированный код пишем в сессию
    session['code'] = code

    # создаем подложку
    img = Image.new('RGB', (width, height), (255, 255, 255))
    # получаем контекст рисования
    draw = ImageDraw.Draw(img)

    # Подключаем растровый шрифт (укажите свой)
    font = ImageFont.truetype('20421.ttf', size=50)
    # начальное положение символов кода
    x = 0
    # наносим код капчи
    for let in code:
        if x == 0:
            x = 5
        else:
            x = x + width / 5
        # случайное положение по высоте
        y = randint(3, 55)
        # наносим символ
        draw.text((x, y), let, font=font,
                  fill=(randint(100, 200), randint(100, 200), randint(100, 200), 128))

    # создаем шум капчи (в данном случае черточки)
    # можно создать шум точками (кому как нравиться)
    tolshina = 1
    for i in range(100):
        draw.line([(randint(0, width), randint(0, height)),
                   (randint(0, width), randint(0, height))],
                  (randint(0, 100), randint(0, 100), randint(0, 100)), tolshina)

    # создаем объект в буфере
    f = BytesIO()
    # сохраняем капчу в буфер
    img.save(f, "PNG")
    # возвращаем капчу как байтовый объект
    return f.getvalue()


# /////////////////////////////////////////////////////

UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def image_lightening(filename, forse):
    img = Image.open(UPLOAD_FOLDER + filename)
    if forse >= 0:
        forse = forse * 5
    power = 1 + forse / 100
    im_output = ImageEnhance.Brightness(img).enhance(power)
    im_output.save(UPLOAD_FOLDER + 'edit/' + filename)
    return


def image_color_plot(UPLOAD_FOLDER, filename):
    img = imread(UPLOAD_FOLDER + filename)
    # получение значений цветов
    r = img[:, :, 0].ravel()
    g = img[:, :, 1].ravel()
    b = img[:, :, 2].ravel()

    # создание гистограммы
    fig, ax = plt.subplots()
    ax.hist(r, bins=32, alpha=0.5, color='red')
    ax.hist(g, bins=32, alpha=0.5, color='green')
    ax.hist(b, bins=32, alpha=0.5, color='blue')

    plt.savefig(UPLOAD_FOLDER + 'graph/' + filename)
    return


@app.route('/ok', methods=['POST', 'GET'])
def image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('no filename')
            return redirect(request.url)
        else:
            forse = int(request.values['forse'])
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print("saved file successfully")

            image_lightening(filename, forse)
            image_color_plot(UPLOAD_FOLDER, filename)
            image_color_plot(UPLOAD_FOLDER + 'edit/', filename)

            # send file name as parameter to downlad
            return redirect('/ok/downloadfile/' + filename)
    return render_template('image.html')


# /////////////////////////////////////////////////////


@app.route("/ok/downloadfile/<filename>", methods=['GET'])
def download_file(filename):
    return render_template('download.html', value=filename)


@app.route('/input-files/<filename>')
def input_files_tut(filename):
    file_path = UPLOAD_FOLDER + filename
    return send_file(file_path, as_attachment=True)


@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = UPLOAD_FOLDER + "edit/" + filename
    return send_file(file_path, as_attachment=True)


@app.route('/graph1/<filename>')
def graph1_tut(filename):
    file_path = UPLOAD_FOLDER + "graph/" + filename
    return send_file(file_path, as_attachment=True)


@app.route('/graph2/<filename>')
def graph2_tut(filename):
    file_path = UPLOAD_FOLDER + "edit/" + "graph/" + filename
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
