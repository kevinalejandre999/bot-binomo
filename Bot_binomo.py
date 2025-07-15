
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException,TimeoutException
import time
import requests
import json
import pyperclip
from pathlib import Path
from datetime import datetime, timedelta

from pathlib import Path


import re
import requests
import os


driver = None
consola_callback_global = None  # Aquí guardaremos la referencia


# Ruta del perfil de Chrome para WhatsApp
perfil_usuario = perfil_usuario = os.path.join(os.getcwd(), "chrome_profile")
#r"C:\\Users\\Inpasa\\AppData\\Local\\Google\\Chrome\\User Data\\WhatsAppPerfil"
chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={perfil_usuario}")
#chrome_options.add_argument('--headless=new')  # Usá 'new' en lugar del antiguo headless
#chrome_options.add_argument('--disable-gpu')
#chrome_options.add_argument('--no-sandbox')
#chrome_options.add_argument('--disable-dev-shm-usage')

SIGNALS_FILE = "C:/Users/Administrator/Documents/Python/Telegram_Whats/senales_binomo.txt"
SIGNALS_PATH = SIGNALS_FILE

OP_FILE = "op_binomo.txt"
ES_FILE = "es_binomo.txt"
OP_PATH = Path(__file__).parent / OP_FILE
ES_PATH = Path(__file__).parent / ES_FILE

API_URL = "https://api-binomo.onrender.com/senal"  # Cambiá por la URL de tu API real

monto_inicial = 0
valor_invertido = 0
monto = 0
reiniciarV = True
ganancia = 0
montos= []
horarios= []
historico = []
guardar_historico = datetime.now()
wins = 0
losses = 0
mayor_entrada = 0
multiplicador= 0
horario_mentrada = datetime.now().strftime("%H:%M:%S")
losses_cons = 0
mayor_loss = 0
stopwin = 0
errocritico = False
stop = False
winers = 0
# Iniciar navegador

#driver.get("https://web.whatsapp.com")
#input("Escaneá el código QR si es necesario y presioná Enter para continuar...")

#driver.execute_script("window.open('https://binomo.com', '_blank');")
#time.sleep(5)  # Espera suficiente para que cargue
#driver.switch_to.window(driver.window_handles[1])  # Cambia a Binomo
#driver.get("https://binomo.com")  # Asegura la URL correcta









def iniciar_driver():
    global driver
    chrome_options = Options()
    chrome_options.add_argument(f"user-data-dir={perfil_usuario}")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_experimental_option("excludeSwitches", ["disable-background-timer-throttling", "disable-renderer-backgrounding"])

    #chrome_options.add_argument('--headless=new') 

    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_window_size(1200, 800)
        driver.get("https://binomo.com")
        #input("Enter luego de iniciar binomo")
        return True
    except Exception as e:
        consola_callback_global(f"❌ Error al iniciar Chrome: {e}")
        return False
    
    


# Función para filtrar caracteres fuera de BMP
def filtrar_bmp(texto):
    return ''.join(c for c in texto if ord(c) <= 0xFFFF)

# Función para enviar mensajes a WhatsApp  a
def enviar_mensaje_whatsapp(grupo, mensaje):
    try:
        driver.switch_to.window(driver.window_handles[0])

        # Buscar el grupo por nombre
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        search_box.click()
        search_box.clear()
        search_box.send_keys(grupo)
        time.sleep(2)
        search_box.send_keys(Keys.ENTER)
        time.sleep(1)

        # Campo de mensaje
        msg_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
        )

        mensaje_filtrado = mensaje
        

        # Enviar línea por línea con salto de línea
        for linea in mensaje_filtrado.strip().split('\n'):
            pyperclip.copy(linea)
            msg_box.send_keys(Keys.CONTROL, 'v')

        
            ActionChains(driver).key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
            time.sleep(0.2)

        msg_box.send_keys(Keys.ENTER)
        consola_callback_global(f"✅ Mensaje enviado:\n{mensaje_filtrado}")

    except Exception as e:
        consola_callback_global("❌ Error al enviar mensaje a WhatsApp:", e)


def obtener_senal_desde_api(api_url):
    try:
        #consola_callback_global('Aguardando Senal')
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if "senal" in data:
                direccion, hora, resu = data["senal"].strip().lower().split(",")
                return direccion, hora, resu
        else:
            consola_callback_global(f"⚠️ Error al consultar la API. Código: {response.status_code}")
    except Exception as e:
        consola_callback_global(f"❌ Error al obtener señal desde API: {e}")
    return 'Err', 'Err', 'Err'


def esperar_popout_y_determinar_resultado():
    global valor_invertido
    global ganancia
    global guardar_historico, mayor_loss, losses_cons
    global montos, wins, losses, horarios, mayor_entrada, horario_mentrada

    try:
        time.sleep(0.5)
        popout = None

        for intento in range(6):
            try:
                popout = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.option"))
                )
                if popout and popout.text.strip() != "":
                    consola_callback_global(f"✅ Popout detectado en intento {intento + 1}")
                    break  # Salir si fue encontrado y tiene texto
                else:
                    consola_callback_global(f"⚠️ Popout vacío en intento {intento + 1}, reintentando...")
            except TimeoutException:
                consola_callback_global(f"⚠️ Intento {intento + 1} fallido. Reintentando...")
            time.sleep(0.3)

        if not popout or popout.text.strip() == "":
            consola_callback_global("❌ Popout no detectado tras varios intentos.")
            consola_callback_global("⚠️ Verificando resultado en historial")
            return verificar_resultad_hist()

        texto = popout.text
        partes = texto.split()

        if len(partes) < 4:
            consola_callback_global(f"❌ Formato inesperado del popout: '{texto}'")
            return verificar_resultad_hist()

        numero_str = partes[3]
        numero_str = numero_str.replace(',', '').replace('.', '').replace('₲', '')
        consola_callback_global(f"📊 Valor bruto del resultado: {numero_str}")

        numero_entero = int(numero_str)
        ganancia += (numero_entero - valor_invertido)

        guardar_operacion(valor_invertido, numero_entero - valor_invertido, ganancia,
                          datetime.now().strftime("%Y/%m/%d %H:%M"))

        # Guardado periódico de estadísticas
        if guardar_historico <= datetime.now():
            guardar_historico = datetime.now() + timedelta(minutes=20)
            montos.append(ganancia)
            horarios.append(datetime.now().strftime("%H:%M"))
            guardar_estatistica(montos, horarios, wins, losses, mayor_entrada, horario_mentrada, mayor_loss)

        consola_callback_global(f"📈 Resultado Acumulado: {ganancia}", ganancia=ganancia)

        if numero_entero > 0:
            consola_callback_global("✅ Operación ganadora (win)")
            consola_callback_global(f"Resultado: {numero_entero - valor_invertido}")
            wins += 1
            losses_cons = 0
            return True
        else:
            consola_callback_global("❌ Operación perdida (loss)")
            losses += 1
            if losses_cons > mayor_loss:
                mayor_loss = losses_cons
            losses_cons += 1
            consola_callback_global(f"Losses consecutivos: {losses_cons}")
            return False

    except Exception as e:
        consola_callback_global(f"⚠️ Excepción durante análisis del popout: {e}")
        consola_callback_global("⚠️ Verificando resultado en historial")
        return verificar_resultad_hist()


# Obtener el reloj de Binomo
def obtener_hora_binomo():
    try:
        clock_elem = driver.find_element(By.CSS_SELECTOR, "trading-clock p.clock")
        texto = clock_elem.text.strip()
        match = re.search(r"(\d{2}:\d{2}:\d{2})", texto)
        if match:
            return match.group(1)
    except:
        pass
    return None

def esperar_fin_operacion():
    """Espera hasta que el temporizador desaparezca o llegue a 00:00:00"""
    try:
        consola_callback_global("⏳ Esperando fin de operación...")
        timeout = time.time() + 120  # Máximo 70 segundos
        while time.time() < timeout:
            try:
                # Selector mejorado para el temporizador
                timer = driver.find_element(
                    By.CSS_SELECTOR,
                    "div.deal-item.active platform-ui-timer vui-timer vui-label div.label_content__3c9Td div.timer_content__1pHjW"
                )
                timer_text = timer.text.lower()
                
                # Debug: Mostrar el texto actual del timer
                timer_text = timer_text.replace("\n","").replace(" ", "")
                #consola_callback_global(f"Tiempo actual: {timer_text}")
                
                if "00h00m03s" in timer_text:
                    consola_callback_global("✅ Temporizador en 00:00:03")
                    
                    return True
                    
                time.sleep(0.5)
                
            except NoSuchElementException:
                consola_callback_global("✅ Temporizador desaparecido (operación finalizada)")
                time.sleep(0.5)
                return True
                
        consola_callback_global("⚠️ Tiempo de espera excedido")
        return False
        
    except Exception as e:
        consola_callback_global(f"❌ Error inesperado: {e}")
        return False


def verificar_resultad_hist():
    global ganancia
    boton_historial = WebDriverWait(driver, 10).until(
      EC.element_to_be_clickable((By.ID, "qa_historyButton"))
    )
    boton_historial.click()
    time.sleep(1)

    
        # Esperar a que aparezca el resultado
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "trading-option-deal-item"))
    )
    

    p_tags = driver.find_elements(By.CSS_SELECTOR, "trading-option-deal-item p.font-regular-m")
    i_tag = driver.find_elements(By.CSS_SELECTOR, "trading-option-deal-item section.middle p.font-regular-s.text-primary")
    if len(p_tags) >= 2:
        resultado_ob = p_tags[1].text.strip().replace("+", "").replace("₲", "").replace(",", ".").replace(u'\xa0', '')
        consola_callback_global(f"🎯 Resultado detectado: {resultado_ob}")
        

    if len(i_tag) >= 2:
        monto_invertido = i_tag[1].text.strip().replace("+", "").replace("₲", "").replace(",", ".").replace(u'\xa0', '')
        consola_callback_global(f"🎯 Monto Inveritdo: {monto_invertido}")
        

        boton_historial.click()
        if int(resultado_ob.replace(".","")) > 0:
            ganancia = ganancia+int(resultado_ob.replace(".",""))
        else:
            ganancia = ganancia-int(monto_invertido.replace(".",""))

    consola_callback_global(f"📊 Ganancia total: {ganancia}",ganancia=ganancia)    
    return int(resultado_ob.replace(".","")) > 0


def verificar_resultado():
    global valor_invertido
    global ganancia
    global guardar_historico,mayor_loss, losses_cons
    global montos,wins,losses,horarios,mayor_entrada,horario_mentrada,winers
    try:
        # Primero esperar a que termine el tiempo de la operación
        
            
        # Luego proceder con la verificación normal
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)
        
        boton_historial = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "qa_historyButton"))
        )
        #boton_historial.click()
        time.sleep(1)

        tiempo = ""
        while True:
            try:
                contador = driver.find_element(By.CSS_SELECTOR, "div.text")
                tiempo = contador.text.strip()
                consola_callback_global(f"Aguardando finalizar: {tiempo}", replace_last=True)
                if tiempo in ["00:01", "0:01", "00.01"]:
                    consola_callback_global(f"Iniciando verificacion en {tiempo}")
                    break
            except:
                pass
            time.sleep(0.6)
        consola_callback_global(f"Iniciando verificacnion en popuot")  
        return esperar_popout_y_determinar_resultado()    
        
        time.sleep(0.3)    
        try:
            resultado_div = driver.find_element(By.CSS_SELECTOR, "div.profit")
        except:
            resultado_div = driver.find_element(By.CSS_SELECTOR, "div.profit.lost")

        texto = resultado_div.text.strip()
        numero = int(re.sub(r"[^\d]", "", texto))  # Quita ₲, puntos y comas

        resultado = numero - valor_invertido
        
      
        # Evaluar si fue win o loss
        if "lost" in resultado_div.get_attribute("class"):
            consola_callback_global("❌ Operación perdida (loss)")
            losses += 1 
            ganancia -= valor_invertido
            if losses_cons > mayor_loss:
                mayor_loss = losses_cons
            losses_cons += 1
            winers = 0
        else:
            consola_callback_global("✅ Operación ganadora (win)")
            wins += 1
            losses_cons = 0
            ganancia += resultado
            winers = winers + 1 if 'winers' in globals() else 1

        consola_callback_global(f"💰 Resultado: {resultado}")
        consola_callback_global(f"📊 Ganancia total: {ganancia}",ganancia=ganancia)
        consola_callback_global(f"📉 Losses consecutivos: {losses_cons}")

        return True if "lost" not in resultado_div.get_attribute("class") else False

    except Exception as e:
        consola_callback_global(f"⚠️ Error al verificar operación en pantalla {e}")
        return verificar_resultad_hist()



        if not esperar_fin_operacion():
            return False
        
        return esperar_popout_y_determinar_resultado()
           
        
            # Esperar a que aparezca el resultado
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "trading-option-deal-item"))
        )
        

        p_tags = driver.find_elements(By.CSS_SELECTOR, "trading-option-deal-item p.font-regular-m")
        i_tag = driver.find_elements(By.CSS_SELECTOR, "trading-option-deal-item section.middle p.font-regular-s.text-primary")
        if len(p_tags) >= 2:
            resultado_ob = p_tags[1].text.strip().replace("+", "").replace("₲", "").replace(" ", "").replace(u'\xa0', '')
            consola_callback_global(f"🎯 Resultado detectado: {resultado_ob}")
           

        if len(i_tag) >= 2:
            monto_invertido = i_tag[1].text.strip().replace("+", "").replace("₲", "").replace(" ", "").replace(u'\xa0', '')
            consola_callback_global(f"🎯 Monto Inveritdo: {monto_invertido}")
           

            boton_historial.click()
            return int(resultado_ob.replace(".","")) > 0
            
def cargar_historico_por_lineas(ruta_archivo):
    global historico
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            if linea:
                try:
                    historico.append(json.loads(linea))
                except json.JSONDecodeError as e:
                    consola_callback_global("❌ Línea con error JSON:", linea)
    return historico


def panel(): 
    global valor_invertido
    global ganancia
    global historico, mayor_loss, losses_cons
    global montos, wins, losses, horarios, mayor_entrada, horario_mentrada, winers

    url = "https://panel-binomo.onrender.com/api/data"

    # Aseguramos valores default si algo está vacío
    consola_callback_global("Iniciando carga")
    entrada_actual = f"{valor_invertido:,}".replace(",", ".") if valor_invertido else "No hay entrada"
    mayor_entrada_txt = f"{mayor_entrada:,} a las {horario_mentrada}".replace(",", ".") if mayor_entrada and horario_mentrada else "Sin datos"
    tiempo_operacion = "-"  # reemplazar por cálculo real si querés
    stop_win_buscado = "250.000"  # si es fijo o lo tomás de alguna variable
    gancia_p =f"{ganancia:,}".replace(",", ".")

    fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")
    consola_callback_global("Iniciando carga")
    # Preparar histórico si existe
    ganancias_dias = []
    if historico:
        for i in range(len(historico)):
            ganancias_dias.append({
                "fecha": historico[i]["fecha"],
                "ganancia": historico[i]["ganancia"],
                "mayor_entrada": historico[i]["mayor_entrada"]
            })

    # Armar el payload
    data = {
        "entrada_actual": entrada_actual,
        "ganancia_actual": gancia_p,
        "mayor_entrada": mayor_entrada_txt,
        "tiempo_operacion": tiempo_operacion,
        "stop_win_buscado": stop_win_buscado,
        "fecha_actualizacion": fecha_actualizacion,
        "ganancias_dias": ganancias_dias
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            consola_callback_global("✅ Datos enviados correctamente al panel")
        else:
            consola_callback_global("❌ Error al enviar datos:", response.status_code, response.text)
    except Exception as e:
        consola_callback_global("❌ Error de conexión:", str(e))




def obtener_proxima_hora_disponible():
    """Obtiene la hora de la próxima vela disponible inmediatamente después del tiempo actual"""
    hora_actual = obtener_hora_binomo()
    
    # Suponiendo que las velas son de 1 minuto (ajusta según tu estrategia)
    # Extraemos minutos y segundos
    partes = hora_actual.split(':')
    minutos = int(partes[1])
    segundos = int(partes[2]) if len(partes) > 2 else 0
    
    # Calculamos el próximo minuto completo
    proximo_minuto = minutos + 1
    hora_proxima = f"{partes[0]}:{proximo_minuto:02d}:00"
    
    hora_proxima = obtener_hora_binomo()

    return hora_proxima

def input_valor(valor):
    global errocritico
    intento = 0
    max_intento = 5

    while intento < max_intento:
        try: 
            input_monto = WebDriverWait(driver, 5).until(  # Timeout más corto
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.input-controls_input-lower__2ePca"))
            )
            #driver.execute_script(f"arguments[0].value = '{monto}';", input_monto)
            input_monto.click()
            input_monto.clear()
            input_monto.clear()
            input_monto.send_keys(str(valor))   
            time.sleep(0.5)
            monto_inputado = driver.find_element(By.CSS_SELECTOR, "input.input-controls_input-lower__2ePca").get_attribute("value").replace(",", ".").replace("₲","")
            if not driver.find_element(By.CSS_SELECTOR, "input.input-controls_input-lower__2ePca").get_attribute("value").replace(",", ".").replace("₲","") == str(valor):
                intento+=1
                consola_callback_global(f"Intento inputar {valor} intento {intento} valor recuperado {monto_inputado}")
            else:
                consola_callback_global(f"Valor Confirmado {valor}")
                break
        except ElementClickInterceptedException:   
            intento+=1
            consola_callback_global(f"Intento inputar {valor} intento {intento} Elemento no disponible")
    else:
        consola_callback_global("No se puedo inputar el valor luego de varios intentos")
        errocritico = True



def set_consola_callback(callback):
    global consola_callback_global
    consola_callback_global = callback

def guardar_operacion(valor, retorno,acumulado,hora):
    consola_callback_global("Iniciando guardado")
    with open(OP_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{valor},{retorno},{acumulado},{hora}\n")

def guardar_estatistica(valor, hora,win,loss,m_entrada,horam,mloss):
    consola_callback_global("Iniciando guardado estadistica")
    with open(ES_PATH, 'w', encoding='utf-8') as f:
        f.seek(0)  # Va al inicio del archivo
        f.truncate()  # Limpia el contenido
        
    with open(ES_PATH, 'a', encoding='utf-8') as f:
        f.write(f"{valor}\n")
        f.write(f"{hora}\n")
        f.write(f"{win}\n")
        f.write(f"{loss}\n")
        f.write(f"{m_entrada}|{horam}\n")
        f.write(f"{mloss}\n")
   




# Realizar operación en Binomo
def operar_en_binomo(direccion, hora_entrada,es_martingale=False, intento_martingale=0):
    #global driver
    global reiniciarV
    global monto_inicial
    global monto,valor_invertido
    global mayor_entrada
    global horario_mentrada,ganancia,stopwin,multiplicador, stop

    try:
        MAX_MARTINGALES = 1
        
        # Corrección del error de switch_to.to.window
        driver.switch_to.window(driver.window_handles[0])
        #time.sleep(0.5)
        if reiniciarV:
            monto = monto_inicial
            consola_callback_global("Monto Reiniciado")
            input_valor(monto)
            reiniciarV = False
            time.sleep(0.5)
        
        hora_correcta = datetime.strptime(hora_entrada,"%H:%M:%S")
        hora_entrada = (hora_correcta - timedelta(seconds=1)).strftime("%H:%M:%S") # para restar una (hora_correcta - timedelta(hours=1)).strftime("%H:%M:%S")
        #consola_callback_global(obtener_hora_binomo())
        minuto_segundo = ":".join(hora_entrada.split(":")[1:])  # Resultado: mm
        consola_callback_global(f"⏳ Esperando para entrada en Binomo a las {hora_entrada}...")
        # Espera optimizada con timeout
        #consola_callback_global(minuto_segundo)
        if not es_martingale:
              while True:
                formato = "%H:%M:%S"
                hora_binomo = obtener_hora_binomo()
                hora_binomo_dt = datetime.strptime(hora_binomo, formato).time()
                hora_entrada_dt = datetime.strptime(hora_entrada, formato).time()
                consola_callback_global(f"⏳ Hora de Binomo {obtener_hora_binomo()}...", replace_last=True)

                # Comparar las horas
                if hora_binomo_dt > hora_entrada_dt:
                        consola_callback_global("⏳ Tiempo perdido: La hora de Binomo es mayor que la hora de entrada.")
                        return False  # Opcional: Retorna True para manejar el corte externamente.
                elif hora_binomo_dt == hora_entrada_dt:
                        break
                time.sleep(0.05)

        
        if mayor_entrada <= monto:
            mayor_entrada = monto
            horario_mentrada = datetime.now().strftime("%H:%M:%S")
            consola_callback_global(f"Mayo entrada detectada. {mayor_entrada} a las {horario_mentrada}",mayor_entrada=mayor_entrada,horario_mentrada=horario_mentrada)



        # Selección de dirección optimizada
        boton_id = "qa_trading_dealUpButton" if direccion == "verde" else "qa_trading_dealDownButton"
        boton = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, boton_id))
        )
        # Click con JavaScript para mayor confiabilidad
        driver.execute_script("arguments[0].click();", boton)
        consola_callback_global(f"🚀 Entrada realizada: {direccion.upper()} | Monto: {monto} {'(Martingale #'+str(intento_martingale+1)+')' if es_martingale else ''}",valor_invertido=monto)
         

        # Verificación de resultado optimizada
        resultado = None
        valor_invertido = monto
        #prepara para martingale
        monto = round(monto * multiplicador)
        input_valor(monto)
        
        #input_monto.send_keys(str(nuevo_monto))
        consola_callback_global(f"Monto actualizado {monto}")
        time.sleep(3)

        panel()
       
        resultado = verificar_resultado()

         

        # Manejo del resultado
        if not resultado:
            if intento_martingale < MAX_MARTINGALES:
        
                proxima_hora = obtener_proxima_hora_disponible()
                consola_callback_global(f"🔴 Pérdida detectada. Preparando martingala para la proxima con {monto}...",valor_invertido=0)
               
                # Cierre rápido
                #driver.close()
                #driver.switch_to.window(driver.window_handles[0])
                
                # Entrar inmediatamente en la próxima vela
                consola_callback_global(intento_martingale)
                valor_invertido=0
                panel() 
                return operar_en_binomo(direccion, proxima_hora,True,intento_martingale+1)
            else:
                consola_callback_global("⛔ Máximo de martingales alcanzado. esperando proximo senal...",valor_invertido=0)
                #reiniciarV = True
                #driver.close()
                #driver.switch_to.window(driver.window_handles[0])

                valor_invertido=0
                panel()
                return False
        else:
            consola_callback_global("🏆 Operación exitosa!" + (" ¡Martingale completada!" if es_martingale else ""),valor_invertido=0)
            reiniciarV = True
            valor_invertido=0
            panel()

            #driver.close()
            #driver.switch_to.window(driver.window_handles[0])
            if  stopwin <= ganancia:
                consola_callback_global(f"Stop Win Alcanzado  {datetime.now().strftime("%H:%M:%S")} Ganancia de {ganancia}")
                stop = True
                panel()
                #os._exit(1)
                
                #input(f"Stop Win Alcanzado  {datetime.now().strftime("%H:%M:%S")}") 
            
            return True
   
    except Exception as e:
        consola_callback_global(f"❌ Error crítico en operacion: {str(e)}")
        return False

def leer_y_borrar_senal():
    """Lee y borra la primera señal, devolviendo (direccion, hora)"""
    try:
        with open(SIGNALS_PATH, 'r+', encoding='utf-8') as f:
            lineas = f.readlines()
            
            if not lineas:
                return None, None
                
            primera_linea = lineas[0].strip()
            if ',' not in primera_linea:  # Validación básica
                consola_callback_global(f"⚠️ Formato inválido: {primera_linea}")
                return None, None
                
            direccion, hora_entrada = primera_linea.split(',', 1)  # Split en la primera coma
            
            # Eliminar la línea procesada
            f.seek(0)
            f.truncate()
            f.writelines(lineas[1:])

        return direccion, hora_entrada
        
    except Exception as e:
        consola_callback_global(f"❌ Error leyendo señales: {e}")
        return None, None



def ejecutar_senales(monto_inicial_p, stop_win_p, multiplicador_p,estado_ini, consola_callback=consola_callback_global):
    global monto_inicial, stopwin, multiplicador,losses_cons, stop, errocritico, ganancia, horario_mentrada, mayor_entrada,winers
    old_direccion= '0'
    old_hora_entrada='0'
    old_entrada = 0
  
    lossers = 0

    old_resultado_registrado = ""
    winers = 0
    

    #iniciar_driver()
    monto_inicial = monto_inicial_p
    stopwin = stop_win_p
    multiplicador = multiplicador_p
    set_consola_callback(consola_callback)
    cargar_historico_por_lineas(os.path.join(os.getcwd(), "resultados.txt"))
    #while True:
    #    direccion, hora = leer_y_borrar_senal()
    #    
    #    if not direccion or not hora:
    #        time.sleep(1)
    #        continue
    #        
    #    consola_callback_global(f"⚡ Señal a ejecutar: {direccion} @ {hora}")
    #    
    #    try:
    #       
    #        operar_en_binomo(direccion, hora)
    #        time.sleep(2)
    #        
    #    except Exception as e:
    #        consola_callback_global(f"❌ Error en ejecución: {e}")
    #        try:
    #            driver.quit()
    #        except:
    #            pass
    #        driver = None
    #        time.sleep(5)
    consola_callback_global(f'Bot Iniciado, estado  {stop},  {errocritico}')
    while True:
        if not stop and not errocritico:
            
            direccion, hora_entrada, resulant = obtener_senal_desde_api(API_URL)
            if direccion in ["verde", "rojo"]:
                # Verifica si es una nueva señal y cumple condiciones para operar
                if hora_entrada != old_hora_entrada and (losses_cons < 14 or winers >= 1):
                    consola_callback_global(f"📥 Senal autorizada: Losses: {losses_cons}, Winers: {winers}")
                    consola_callback_global(f"📥 Señal recibida: Dirección: {direccion}, Hora: {hora_entrada}")
                    operar_en_binomo(direccion, hora_entrada)
                    old_hora_entrada = hora_entrada
                    old_resultado_registrado = ""  # Se espera resultado
                else:
                    if hora_entrada == old_hora_entrada:
                        if losses_cons  > 3:
                          consola_callback_global(f"⏳ Se detectaron perdidas consecutivas, esperando el mercado estabilizar Actual: {winers} win, {losses_cons} loss consecutivos", replace_last=True)
                        else:
                          consola_callback_global(f"⏳ Esperando proxima entrada, anterior fue a las  {hora_entrada}", replace_last=True)
            
            elif direccion == "none" and resulant in ["win", "loss"]:
                # Registra el resultado si aún no fue registrado para esa hora
                if hora_entrada != old_resultado_registrado:
                    if resulant == "win":
                        winers += 1
                        #losses_cons = 0
                    else:
                        lossers += 1
                        winers = 0
                    old_resultado_registrado = hora_entrada

                    consola_callback_global(f"📊 Ultimo resultado: {resulant.upper()} Win segudido {winers}")

                else:
                    consola_callback_global(f"⏳ Esperando nuevo resultado... Último registrado: {old_resultado_registrado}")
            
            else:
                consola_callback_global(f"⏳ Señal no válida: {direccion}, {hora_entrada}, {resulant}")
            
            time.sleep(5)
        else:
            break
    consola_callback_global('En caso que quires operar nuevamente, clik en el boton')    
    ganancia,losses_cons,mayor_entrada = 0,0,0
    stop,errocritico = False,False
    horario_mentrada = 0

    estado_ini()
    #return True



if __name__ == "__main__":
    consola_callback_global("Iniciando ejecutor de señales...")
    
    #ejecutar_senales()
