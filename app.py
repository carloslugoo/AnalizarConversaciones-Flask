from flask import Flask, request, jsonify, render_template, redirect, url_for
import zipfile
import emoji 
import pandas as pd
import re
import json
from unidecode import unidecode
# Crea una instancia de la aplicación Flask
app = Flask(__name__)

global estadisticas_generales
estadisticas_generales = {}
global estadisticas_emisores
estadisticas_emisores = {}
# Define una ruta y una función para manejar la solicitud
@app.route('/')
def index ():
    return render_template('index.html')

# Define una ruta y una función para manejar la solicitud
@app.route('/chats/recibir', methods=['POST'])
def recibir_archivo():
    if 'file' not in request.files:
        return jsonify({'error': 'No se adjuntó ningún archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400
    
    # Verificar si es un archivo ZIP
    if not file.filename.endswith('.zip'):
        return jsonify({'error': 'Formato de archivo no válido. Por favor, selecciona un archivo ZIP.'}), 400


    try: 
        #Leer el contenido del archivo ZIP sin extraerlo
        with zipfile.ZipFile(file, 'r') as zip_file:
            with zip_file.open('_chat.txt') as f:
        #-------------------Procesa el chat-------------------#
                chat_crudo = f.read().decode('utf-8')
                #print(chat_crudo)
                patron = re.compile(r'\[(\d+\/\d+\/\d+, \d+:\d+:\d+)\] (.+?): (.+)')
                coincidencias = patron.findall(chat_crudo)
                #print(coincidencias)
    except Exception as e:
        return jsonify({'error': 'El zip no contiene una conversación'}), 400
    

    chat_procesado = pd.DataFrame(coincidencias, columns = ['Fecha y Hora', 'Emisor', 'Mensaje'])
    #-------------------Procesa el chat-------------------#
    #-------------------Procesa los datos generales del chat-------------------#
    # Obtiene la lista de personas que participan en el chat
    personas_en_el_chat = chat_procesado['Emisor'].unique().tolist()
    personas_en_el_chat_filtrado = [unidecode(persona) for persona in personas_en_el_chat]
    # Obtiene la fecha del primer mensaje y del último mensaje
    fecha_inicio = chat_procesado['Fecha y Hora'].min()
    fecha_final = chat_procesado['Fecha y Hora'].max()

    # Obtiene la cantidad de mensajes encontrados
    cantidad_mensajes = len(chat_procesado)

    # Agrupa los mensajes por emisor y cuenta la cantidad de mensajes por emisor
    conteo_mensajes_por_emisor = chat_procesado['Emisor'].value_counts()
    # Obtén el conteo de mensajes por emisor como un diccionario
    conteo_mensajes_por_emisor_dict = conteo_mensajes_por_emisor.to_dict()

    # Itera a través del diccionario e imprime el emisor y la cantidad de mensajes
    #for emisor, cantidad_mensajes in conteo_mensajes_por_emisor_dict.items():
    #   print(f"{emisor}: {cantidad_mensajes}")
    # Imprime el conteo de mensajes por emisor
    
    # Obtener una lista de todos los emojis en el DataFrame
    def extract_emojis(text):
        return ''.join(c for c in text if c in emoji.EMOJI_DATA)

    chat_procesado['Emojis'] = chat_procesado['Mensaje'].apply(extract_emojis)
    print(chat_procesado)
    # Conteo exclusivo de la palabra 'imagen'
    imagen_count = chat_procesado['Mensaje'].str.lower().str.count('imagen').sum()
    # Conteo exclusivo de la palabra 'audio'
    audio_count = chat_procesado['Mensaje'].str.lower().str.count('audio').sum()
    # Conteo exclusivo de la palabra 'sticker'
    sticker_count = chat_procesado['Mensaje'].str.lower().str.count('sticker').sum()
    # Conteo exclusivo de la palabra 'sticker'
    videos_count = chat_procesado['Mensaje'].str.lower().str.count('video').sum()
    # Conteo exclusivo de la palabra 'documento'
    documento_count = chat_procesado['Mensaje'].str.lower().str.count('documento').sum()
    # Conteo exclusivo de la palabra 'llamada'
    llamada_count = chat_procesado['Mensaje'].str.lower().str.count('llamada').sum()
    ## Eliminar las columnas 'imagen_count' y 'audio_count' del DataFrame
    chat_procesado = chat_procesado.drop(['imagen_count', 'audio_count'], axis=1, errors='ignore')
    # Conteo de emojis
    emojis_count = chat_procesado['Emojis'].apply(lambda x: pd.Series(list(x))).stack().value_counts().head(5).to_dict()
    # Encontrar índices de filas que contienen palabras específicas y eliminar esas filas
    words_to_remove = ['omitido', 'omitida', 'audio', 'imagen', 'sticker', 'video', 'documento', 'a', 'al', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'del', 'desde',
                    'durante', 'e', 'el', 'ella', 'en', 'entre', 'eso', 'esta', 'está', 'ha','llamada',
                    'hacia', 'hasta', 'le', 'les', 'lo', 'los', 'me', 'mi', 'mis', 'mucho',
                    'más', 'ni', 'o', 'para', 'pero', 'por', 'que', 'se', 'si', 'sin', 'sobre',
                    'soy', 'su', 'sus', 'tal', 'te', 'tú', 'un', 'una', 'unas', 'uno', 'unos',
                    'y', 'ya', 'yo', 'él', 'ésta', 'éstas', 'éste', 'éstos', 'último', 'últimos']
    # Limpiar el texto de emojis y caracteres especiales utilizando expresiones regulares
    chat_procesado['Mensaje_Limpio'] = chat_procesado['Mensaje'].apply(lambda x: re.sub(r'[^\w\s]', '', x))  # Elimina caracteres no alfanuméricos
    chat_procesado['Mensaje_Limpio'] = chat_procesado['Mensaje_Limpio'].apply(lambda x: re.sub(r'\b\w{1,2}\b', '', x))  # Elimina palabras de uno o dos caracteres
    # Conteo de palabras más usadas por emisor
    word_counts = (
    chat_procesado.groupby('Emisor')['Mensaje_Limpio']
    .apply(lambda x: ' '.join(x))
    .apply(lambda x: pd.Series(re.findall(r'\b\w+\b', x.lower())))  # Encuentra palabras y convierte a minúsculas
    .apply(lambda x: x[~x.isin(words_to_remove)])  # Elimina palabras no deseadas
    .apply(pd.Series).stack().value_counts().head(5).to_dict()
    )
    global estadisticas_generales
    #Convierte los datos generales a json
    estadisticas_generales = {'PersonasGeneral': personas_en_el_chat_filtrado,
        'CantidadMensajesGeneral': int(cantidad_mensajes),
        'FInicio': fecha_inicio,
        'FFinal': fecha_final,
        'EmojisGeneral': emojis_count,
        'PalabrasGeneral': word_counts,
        'ImagenGeneral': int(imagen_count),
        'AudioGeneral': int(audio_count),
        'StickerGeneral': int(sticker_count),
        'VideosGeneral': int(videos_count),
        'DocumentosGeneral': int(documento_count),
        'LlamadasGeneral': int(llamada_count)
        }
    #print(estadisticas_generales)
    # Convertir el diccionario a JSON
    json_estadisticas = json.dumps(estadisticas_generales, indent=2)
    print(json_estadisticas)
    #-------------------Procesa los datos generales del chat-------------------#

    #-------------------Procesa los datos individuales del chat-------------------#
    # Lista para almacenar estadísticas individuales por emisor
    estadisticas_por_emisor = []
    aux = 0
    for emisor in personas_en_el_chat:

        # Filtrar el DataFrame por emisor
        mensajes_emisor = chat_procesado[chat_procesado['Emisor'] == emisor]

        # Conteo de emojis del emisor
        emojis_emisor = mensajes_emisor['Emojis'].apply(extract_emojis)
        emojis_count_emisor = pd.Series([emoji for sublist in emojis_emisor for emoji in sublist]).value_counts().head(5).to_dict()
        # Conteo exclusivo de la palabra 'imagen'
        imagen_count = mensajes_emisor['Mensaje'].str.lower().str.count('imagen').sum()
        # Conteo exclusivo de la palabra 'audio'
        audio_count = mensajes_emisor['Mensaje'].str.lower().str.count('audio').sum()
        # Conteo exclusivo de la palabra 'sticker'
        sticker_count = mensajes_emisor['Mensaje'].str.lower().str.count('sticker').sum()
        # Conteo exclusivo de la palabra 'sticker'
        videos_count = mensajes_emisor['Mensaje'].str.lower().str.count('video').sum()
        # Conteo exclusivo de la palabra 'documento'
        documento_count = mensajes_emisor['Mensaje'].str.lower().str.count('documento').sum()
        # Conteo exclusivo de la palabra 'llamada'
        llamada_count = mensajes_emisor['Mensaje'].str.lower().str.count('llamada').sum()
         # Conteo de palabras más usadas por emisor
        palabras_emisor = (
        mensajes_emisor['Mensaje_Limpio']
        .apply(lambda x: re.findall(r'\b\w+\b', x.lower()))
        .apply(lambda x: [word for word in x if word not in words_to_remove])
        )
        palabras_flat_emisor = [word for sublist in palabras_emisor for word in sublist]
        palabras_count_emisor = pd.Series(palabras_flat_emisor).value_counts().head(5).to_dict()

        # Crear un diccionario con las estadísticas del emisor actual
        estadisticas_emisor = {
            'Emisor': personas_en_el_chat_filtrado[aux],
            'CantidadMensajes': len(mensajes_emisor),
            'ConteoEmojis': emojis_count_emisor,
            'ConteoPalabras': palabras_count_emisor,
            'ImagenEmisor': int(imagen_count),
            'AudioEmisor': int(audio_count),
            'StickerEmisor': int(sticker_count),
            'VideosEmisor': int(videos_count),
            'DocumentosEmisor': int(documento_count),
            'LlamadasEmisor': int(llamada_count)
        }

        # Agregar el diccionario al listado de estadísticas por emisor
        aux += 1
        estadisticas_por_emisor.append(estadisticas_emisor)
    global estadisticas_emisores
    estadisticas_emisores = estadisticas_por_emisor
    #print(estadisticas_por_emisor)
    # Convertir la lista de estadísticas por emisor a JSON
    json_estadisticas_por_emisor = json.dumps(estadisticas_por_emisor, indent=2)
    print(json_estadisticas_por_emisor)
    #-------------------Procesa los datos individuales del chat-------------------#
    nueva_url = url_for('estadisticas')
    return jsonify({'redirect': True, 'url': nueva_url})


@app.route('/estadisticas', methods=['GET'])
def estadisticas():
    global estadisticas_generales
    global estadisticas_emisores
    if not estadisticas_emisores and not estadisticas_generales:
        return redirect(url_for('index'))
    else:
        print(estadisticas_generales)
        print(estadisticas_emisores)
        return render_template('estadisticas.html', generales = estadisticas_generales, emisores = estadisticas_emisores)

# Punto de entrada para la aplicación
if __name__ == '__main__':
     app.run(debug = True, port= 8000)