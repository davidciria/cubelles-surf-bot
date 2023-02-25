import json
import requests
import boto3

########################################################################################################
# CONFIGURATION ########################################################################################
########################################################################################################
URL = "https://api.telegram.org/<bot_key>/" # Telegram bot URL.
########################################################################################################
########################################################################################################

def send_message(text, chat_id):
    final_text = text
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)

def lambda_handler(event, context):
    print(event)
    lambda_client = boto3.client('lambda')
    
    if event.get('body'):
        body = json.loads(event.get('body'))
        if body.get('message'):
            text = body.get('message').get('text')
            if text:
                chat_id = body.get('message').get('chat').get('id')
                username = body.get('message').get('from').get('username')
                type = body.get('message').get('chat').get('type')
                
                if "/predict" in text:
                    response = lambda_client.invoke(
                      FunctionName='cubesurf_bot',
                      Payload=json.dumps({"chat_id": chat_id}),
                      InvocationType="Event"
                    )
                else:
                    if username:
                        message = """Hola @{}! 🤖🌊
Mi función es predecir la altura de las olas de la localidad de Cubelles.
Pudes invocarme con las siguientes ordenes:
/predict -> Prediccion de los próximos 4 dias.

Para sugerencias y más información contactar con @davidciria""".format(username)
                    else:
                        message = """Hola! 🤖🌊
Mi función es predecir la altura de las olas de la localidad de Cubelles.
Pudes invocarme con las siguientes ordenes:
/predict -> Prediccion de los próximos 4 dias.

Para sugerencias y más información contactar con @davidciria""".format(username)

                    send_message(message, chat_id)
        
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
