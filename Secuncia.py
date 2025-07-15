import random
import requests
import time
from datetime import datetime,timedelta


decision = random.randint(0, 1)



def enviar_actualizacion(color: str, hora: str, res: str):
    """
    Envía una solicitud POST a la API con el color y la hora.
    
    Args:
        color (str): Color a enviar (por ejemplo: "verde").
        hora (str): Hora en formato HH:MM:SS.
    
    Returns:
        dict: Respuesta JSON de la API o error.
    """
    global horaant
    print(f"COr: {color}")
    if color == None:
       url = f"https://api-binomo.onrender.com/update/{color}/{horaant}/{res}"
    else: 
       url = f"https://api-binomo.onrender.com/update/{color}/{hora}/{res}" 
       horaant = hora  

    try:
        response = requests.post(url)
        response.raise_for_status()  # Lanza excepción si hubo error HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al hacer POST: {e}")
        return {"error": str(e)}



while True:
    decision = random.randint(0, 1)
    dirreccion = ("verde" if decision == 0 else "rojo")
    hora_actual = f"{(datetime.now()+timedelta(minutes=1)).strftime("%H:%M")}:59"
    print(f"{dirreccion} {hora_actual}")
    enviar_actualizacion(dirreccion,hora_actual,"win")
    time.sleep(120)









