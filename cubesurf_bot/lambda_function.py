import requests
import datetime
import pytz
from bs4 import BeautifulSoup
import sys
import io
import json
import random
import os
import lxml
from matplotlib import pyplot
from matplotlib.ticker import FormatStrFormatter
import numpy as np

########################################################################################################
# CONFIGURATION ########################################################################################
########################################################################################################
URL = "https://api.telegram.org/<bot_key>/" # Telegram bot URL.
# Set environment variable "chat_id" (default chat id).
########################################################################################################
########################################################################################################

def main(chat_id):
    session = requests.session()
    
    def get_weather_dict_7_days():
        weather_response = session.get('https://www.aemet.es/xml/municipios/localidad_08074.xml')
        
        soup = BeautifulSoup(weather_response.content, features='html.parser')
        
        pred_dias = soup.find_all('dia')
        
        value_to_description = {}
        datetime_to_weather = {}
        
        tz = pytz.timezone('Europe/Madrid')
        
        for dia in pred_dias:
            fecha_dia = dia.get('fecha') # Format: 2022-09-05.
            estados_cielo = dia.find_all('estado_cielo')
            for ec in estados_cielo:
                value = ec.text
                description = ec.get('descripcion')
                hours = ec.get('periodo')
                if hours:
                    start = hours[0:2]
                    end = hours[3::]
                    if value == '':
                        continue
                    pred_datetime_start = datetime.datetime.strptime("{} {}:00:00".format(fecha_dia, start), '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
                    if end == '24':
                        pred_datetime_end = datetime.datetime.strptime("{} 23:59:00".format(fecha_dia), '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
                    else:
                        pred_datetime_end = datetime.datetime.strptime("{} {}:00:00".format(fecha_dia, end), '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
                    datetime_to_weather[pred_datetime_start] = description
                    while pred_datetime_start < pred_datetime_end:
                        datetime_to_weather[pred_datetime_start] = description
                        pred_datetime_start = pred_datetime_start + datetime.timedelta(hours=1)
                else:
                    for i in range(0, 24):
                        hour = str(i)
                        if len(hour) == 1: hour = '0' + hour
                        pred_datetime = datetime.datetime.strptime("{} {}:00:00".format(fecha_dia, hour), '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
                        datetime_to_weather[pred_datetime] = description
                
                value_to_description[value] = description
                
        return datetime_to_weather
    
    def get_weather_dict():
        weather_response = session.get('https://www.aemet.es/xml/municipios_h/localidad_h_08074.xml')
        
        soup = BeautifulSoup(weather_response.content, features='html.parser')
        
        pred_dias = soup.find_all('dia')
        
        value_to_description = {}
        datetime_to_weather = {}
        
        tz = pytz.timezone('Europe/Madrid')
        
        for dia in pred_dias:
            fecha_dia = dia.get('fecha') # Format: 2022-09-05.
            estados_cielo = dia.find_all('estado_cielo')
            for ec in estados_cielo:
                value = ec.text
                description = ec.get('descripcion')
                hour = ec.get('periodo')
                value_to_description[value] = description
                pred_datetime = datetime.datetime.strptime("{} {}:00:00".format(fecha_dia, hour), '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
                datetime_to_weather[pred_datetime] = description
        
        return datetime_to_weather
    
    def send_photo(chat_id, img_url, title, local = None, image = None):
            method = "sendPhoto"
            if local:
                params = {'chat_id': chat_id, 'caption': title}
                resp = requests.post(URL + method, params, files={'photo': image})
                return resp
                
            
            params = {'chat_id': chat_id, 'photo': img_url, 'caption': title}
            resp = requests.post(URL + method, params)
            return resp
    
    def sendWelcomeImage(chat_id):
        with open('images.json', 'r') as images_file:
            images_obj = json.loads(images_file.read())
            images_results = images_obj['results']
    
        index = random.randrange(0, len(images_results) - 1)
        send_photo(chat_id, images_results[index]['original'], images_results[index]['title'])
    
    def sendMessageToGroup(message, chat_id):
        method = "sendMessage"
        params = {'chat_id': chat_id, 'text': message, 'parse_mode': 'html'}
        response = session.get(URL + method, params=params)
    
        return response
    
    if not(chat_id):
        chat_id = os.environ.get('chat_id') # Group chat ID.
    
    old_stdout = sys.stdout
    aux_stdout = io.StringIO()
    sys.stdout = aux_stdout
    
    if not(chat_id):
        chat_id = os.environ.get('chat_id') # Group chat ID.
    
    welcome_message = "¡Buenos dias surfers 🏄‍♂️!"
    
    sendMessageToGroup(welcome_message,chat_id)
    
    sendWelcomeImage(chat_id)
    
    r = session.post('https://bancodatos.puertos.es/TablaAccesoSimplificado/util/get_wanadata.php', data={'point': os.environ.get('point'), 'name': 'Cubelles'})
    
    threshold = 0.8
    data = []
    
    soup = BeautifulSoup(r.content, features='html.parser')
    table = soup.find_all('table')[1]
    
    table_body = table.find('tbody')
    
    rows = table_body.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
    
    tz = pytz.timezone('Europe/Madrid')
    now_datetime = datetime.datetime.now(tz)
    
    day_preds = {}
    
    datetime_to_weather = get_weather_dict_7_days()
    
    for record in data:
        date = record[0]
        wave_height = record[4]
        period_tp = record[6]
        wind_speed = record[2]
        wind_dir = record[3]
    
        pred_datetime = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz).astimezone(tz)
        key = pred_datetime.strftime('%Y-%m-%d')
        key = datetime.datetime.strptime(key, '%Y-%m-%d').replace(tzinfo=tz).astimezone(tz)
    
        if key in day_preds: day_preds[key].append({'datetime': pred_datetime, 'wave_height': wave_height, 'weather': datetime_to_weather.get(pred_datetime), 'period_tp': period_tp, 'wind_dir': wind_dir, 'wind_speed': wind_speed})
        else: day_preds[key] = [{'datetime': pred_datetime, 'wave_height': wave_height, 'weather': datetime_to_weather.get(pred_datetime), 'period_tp': period_tp, 'wind_dir': wind_dir, 'wind_speed': wind_speed}]
    
    weekday_to_str = {
        0: 'Lunes',
        1: 'Martes',
        2: 'Miercoles',
        3: 'Jueves',
        4: 'Viernes',
        5: 'Sabado',
        6: 'Domingo'
    }
    
    sys.stdout = old_stdout
    print(day_preds)
    sys.stdout = aux_stdout
    
    for day in day_preds:
        print('<strong>···········································')
        print(weekday_to_str[day.weekday()], day.strftime('%d-%m-%Y'))
        print('···········································</strong>')
        max_height = [0.0, None] # Height, date.
        avg_height = 0.0
        good_waves = []
        for pred in day_preds[day]:
            pred_wave_height = float(pred['wave_height'])
            if pred_wave_height > max_height[0]:
                max_height = [pred_wave_height, pred['datetime'], pred['weather']]
            
            avg_height += pred_wave_height/len(day_preds[day])
    
            if (float(pred['period_tp']) > 7.0 and pred_wave_height > threshold) or (float(pred['period_tp']) > 7.0 and pred_wave_height > 0.6):
                good_waves.append(pred)
        buf = None
        if len(good_waves):
            print('<strong>¡Hay buenas olas 🌊!</strong>')
            
            print('''
    <pre>
|Hora |Altura |Tp  |Viento |
|-----|:-----:|:--:|:------|''')
    
            # print('---------------------------------')
            # print('Date                | Height (m)')
            # print('---------------------------------')
            for pred in good_waves:
                wind_dir_string = pred['wind_dir']
                for i in range(7 - len(pred['wind_dir'])): wind_dir_string += ' '
                print("|{}|:{}m:|{}|{}|".format(pred['datetime'].strftime('%H:%M'), pred['wave_height'], pred['period_tp'], wind_dir_string))
            
            hour_x = [pred['datetime'].strftime('%H') for pred in day_preds[day]]
            height_y = [float(pred['wave_height']) for pred in day_preds[day]]
            period_y = [float(pred['period_tp']) for pred in day_preds[day]]
            
            fig, ax = pyplot.subplots()
            pyplot.plot(hour_x, height_y, label="Altura")
            pyplot.plot(hour_x, period_y, label="Periodo")
            
            # Establecer el color de los ejes.
            pyplot.axhline(0, color="black")
            pyplot.axvline(0, color="black")
            
            pyplot.legend(loc="upper left")
            max_value = 0
            if np.max(height_y) > np.max(period_y):
                max_value = np.max(height_y)
            else:
                max_value = np.max(period_y)
            ax.yaxis.set_ticks(np.arange(0, max_value, 0.5))
            
            # Guardar gráfico como imágen PNG.
            buf = io.BytesIO()
            pyplot.savefig(buf, format='png')
            buf.seek(0)
            
            pyplot.clf()
    
            print("</pre>\n")
        
        print('Altura maxima: {:.2f} m ({} - {})'.format(max_height[0], max_height[1].strftime('%H:%M:%S'), max_height[2]))
        print('Altura media: {:.2f} m'.format(avg_height) )
        message = aux_stdout.getvalue()
        sendMessageToGroup(message, chat_id)
        if buf:
            send_photo(chat_id, None, weekday_to_str[day.weekday()] + ' ' + day.strftime('%d-%m-%Y'), True, buf)
        aux_stdout = io.StringIO()
        sys.stdout = aux_stdout
    
    send_photo(chat_id, 'https://bancodatos.puertos.es/TablaAccesoSimplificado/img/windrose.jpg', 'Leyenda direcciones viento (las direcciones indican dirección de procedencia)')
    
    sendMessageToGroup('<a href="https://bancodatos.puertos.es/TablaAccesoSimplificado/?p=2104134&name=Cubelles">Fuente de información</a>', chat_id)
    
    
    sys.stdout = old_stdout

def lambda_handler(event, context):
    chat_id = event.get('chat_id')
    main(chat_id)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
