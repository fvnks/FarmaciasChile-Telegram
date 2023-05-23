import logging
import ssl
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler

TOKEN = 'tu_token'

# Configurar el nivel de registro para obtener información detallada
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Desactivar el uso de SSLv3 y forzar TLSv1.2
ssl._DEFAULT_CIPHERS += ':!SSLv3'
ssl._DEFAULT_CIPHERS += ':!SSLv2'
ssl._DEFAULT_CIPHERS += ':!TLSv1'
ssl._DEFAULT_CIPHERS += ':!TLSv1.1'

# Función para manejar el comando /farmacia
def get_farmacias(update: Update, context):
    # Obtener el nombre de la comuna ingresada por el usuario
    comuna = ' '.join(context.args).upper()  # Unir todos los argumentos en caso de que la comuna tenga espacios

    # Realizar la solicitud a la API de la farmacia con el parámetro de la comuna
    api_url = f'https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php?comuna_nombre={comuna}'
    response = requests.get(api_url)

    # Verificar el código de respuesta HTTP
    if response.status_code == 200:
        # Decodificar la respuesta JSON
        try:
            data = response.json()
            # Filtrar los datos para mostrar solo la información de la comuna consultada
            filtered_data = [farmacia for farmacia in data if farmacia['comuna_nombre'] == comuna]

            if filtered_data:
                # Mostrar la información de las farmacias encontradas en la comuna consultada
                for farmacia in filtered_data:
                 nombre = farmacia['local_nombre']
                direccion = farmacia['local_direccion']
                func_apertura = farmacia['funcionamiento_hora_apertura']
                func_cierre = farmacia['funcionamiento_hora_cierre']
                telefono = farmacia['local_telefono']
                id_local = farmacia['local_id']
                last_update = farmacia['fecha']
                dia_turno = farmacia['funcionamiento_dia'] 
                message = f'Farmacia: {nombre}\nDirección: {direccion}\nHora Apertura: {func_apertura}\nHora Cierre: {func_cierre}\nTelefono: {telefono}\nID Local: {id_local}\nDia Turno: {dia_turno}'
                update.message.reply_text(message)
            else:
                # No se encontraron farmacias en la comuna consultada
                update.message.reply_text(f'No se encontraron farmacias abiertas en la comuna {comuna}')
        except json.JSONDecodeError as e:
            logging.error(f'Error al decodificar la respuesta JSON: {str(e)}')
    else:
        logging.error(f'Error al realizar la solicitud a la API: {response.status_code}')

# Función principal
def main():
    # Crear una instancia de Updater con tu token de bot de Telegram
    updater = Updater(TOKEN, use_context=True)

    # Obtener el despachador para registrar los controladores de comandos
    dispatcher = updater.dispatcher

    # Registrar el controlador para el comando /farmacia
    dispatcher.add_handler(CommandHandler("farmacia", get_farmacias))

    # Iniciar el bot
    updater.start_polling()

    # Mantener el bot en ejecución hasta que se presione Ctrl + C
    updater.idle()

if __name__ == '__main__':
    main()
