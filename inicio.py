import customtkinter as ctk
import threading
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from Bot_binomo import ejecutar_senales, iniciar_driver

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("🤖 Bot Binomo Super Invest")
app.geometry("800x700")
app.resizable(False, False)
app.iconbitmap("icon.ico")

ganancia_anterior = 0
rem = True
params_global = {}
linea_reemplazable = {"index": None}
bot = False
info_font = ctk.CTkFont(size=18)

# TÍTULO
titulo = ctk.CTkLabel(app, text="🤖 Bot Binomo Super Invest", font=ctk.CTkFont(size=22, weight="bold"))
titulo.pack(pady=(15, 10))

# FRAME SUPERIOR HORIZONTAL
frame_superior = ctk.CTkFrame(app)
frame_superior.pack(padx=20, pady=(0, 10), fill="x")

# FRAME IZQUIERDO – Inputs
frame_inputs = ctk.CTkFrame(master=frame_superior)
frame_inputs.grid(row=0, column=0, padx=20, pady=10, sticky="n")

entry_inicio = ctk.CTkEntry(frame_inputs, placeholder_text="Valor Inicio", width=180)
entry_inicio.grid(row=0, column=0, padx=10, pady=(10, 5))

entry_stop_win = ctk.CTkEntry(frame_inputs, placeholder_text="Stop Win", width=180)
entry_stop_win.grid(row=1, column=0, padx=10, pady=5)

entry_multiplicador = ctk.CTkEntry(frame_inputs, placeholder_text="Multiplicador", width=180)
entry_multiplicador.grid(row=2, column=0, padx=10, pady=5)

label_moneda = ctk.CTkLabel(frame_inputs, text="Seleccioná la moneda:")
label_moneda.grid(row=3, column=0, pady=(20, 5))

moneda_seleccionada = ctk.StringVar(value="PYG")
radio_usd = ctk.CTkRadioButton(frame_inputs, text="💵 Dólar (USD)", variable=moneda_seleccionada, value="USD")
radio_usd.grid(row=4, column=0, sticky="w", padx=10)

radio_guarani = ctk.CTkRadioButton(frame_inputs, text="🇵🇾 Guaraní (PYG)", variable=moneda_seleccionada, value="PYG")
radio_guarani.grid(row=5, column=0, sticky="w", padx=10)

radio_real = ctk.CTkRadioButton(frame_inputs, text="🇧🇷 Real (BRL)", variable=moneda_seleccionada, value="BRL")
radio_real.grid(row=6, column=0, sticky="w", padx=10)

# FRAME DERECHO – Informaciones en tiempo real
frame_info = ctk.CTkFrame(master=frame_superior, border_width=2)
frame_info.grid(row=0, column=1, padx=20, pady=10, sticky="n")

info_title = ctk.CTkLabel(frame_info, text="📊 Información en Tiempo Real", font=ctk.CTkFont(size=14, weight="bold"))
info_title.grid(row=0, column=0, padx=10, pady=(10, 5))

entrada_actual_var = ctk.StringVar(value="💰 Entrada actual: ₲0")
ganancia_actual_var = ctk.StringVar(value="📈 Ganancia actual: ₲0")
mayor_entrada_var = ctk.StringVar(value="🏆 Mayor entrada: ₲0 - 00:00")
tiempo_var = ctk.StringVar(value="⏳ Tiempo en mercado")

entrada_actual_label = ctk.CTkLabel(frame_info, textvariable=entrada_actual_var, anchor="w", width=300, font=info_font)
entrada_actual_label.grid(row=1, column=0, sticky="w", padx=10, pady=2)

ganancia_actual_label = ctk.CTkLabel(frame_info, textvariable=ganancia_actual_var, anchor="w", width=300, font=info_font)
ganancia_actual_label.grid(row=2, column=0, sticky="w", padx=10, pady=2)

mayor_entrada_label = ctk.CTkLabel(frame_info, textvariable=mayor_entrada_var, anchor="w", width=300, font=info_font)
mayor_entrada_label.grid(row=3, column=0, sticky="w", padx=10, pady=2)


# CONSOLA
consola = ScrolledText(app, height=15, width=90, font=("Courier New", 10))
consola.pack(padx=20, pady=15)

# BOTONES
boton_iniciar = ctk.CTkButton(app, text="🚀 Iniciar", command=lambda: iniciar())
boton_iniciar.pack(pady=(5, 0))

boton_confirmar = ctk.CTkButton(app, text="✅ Estoy listo (Binomo abierto)", command=lambda: confirmar_inicio())
# No lo mostramos todavía

def consola_callback(msg, replace_last=False, valor_invertido=None, ganancia=None, mayor_entrada=None, horario_mentrada=None):
    global rem, ganancia_anterior

    msg = str(msg)

    if valor_invertido is not None:
        entrada_actual_var.set(f"💰 Entrada actual: ₲{valor_invertido:,}".replace(",", "."))

    if ganancia is not None:
        ganancia_actual_var.set(f"📈 Ganancia actual: ₲{ganancia:,}".replace(",", ".")) 

        try:
            g_actual = float(str(ganancia).replace(",", "").replace("₲", ""))
            g_anterior = float(ganancia_anterior)

            if g_actual > g_anterior:
                ganancia_actual_label.configure(text_color="green")
            elif g_actual < g_anterior:
                ganancia_actual_label.configure(text_color="red")
            else:
                ganancia_actual_label.configure(text_color="white")

            ganancia_anterior = g_actual
        except:
            pass

    if mayor_entrada is not None and horario_mentrada is not None:
        mayor_entrada_var.set(f"🏆 Mayor entrada: ₲{mayor_entrada:,} - {horario_mentrada}".replace(",", "."))

    if replace_last:
        if rem:
            consola.insert("end", msg + "\n")
            rem = False
        else:
            last_index = consola.index("end-2l")
            consola.delete(last_index, "end-1c")
            consola.insert(last_index, msg + "\n")
    else:
        consola.insert("end", msg + "\n")
        rem = True

    consola.see("end")

def estado_ini():
    boton_confirmar.configure(state="enabled", text="Operar Nuevamente")
    boton_iniciar.configure(state="disabled", text="Bot iniciado")

def confirmar_inicio():
    try:
        vi = int(entry_inicio.get())
        sw = int(entry_stop_win.get())
        m = float(entry_multiplicador.get())
    except ValueError:
        messagebox.showerror("Error", "Todos los campos deben ser numéricos.")
        return

    global params_global
    moneda = moneda_seleccionada.get()
    params_global = {'vi': vi, 'sw': sw, 'm': m, 'moneda': moneda}

    consola_callback("⏳ Iniciando bot...")
    threading.Thread(target=lambda: ejecutar_senales(vi, sw, m, estado_ini, consola_callback), daemon=True).start()
    messagebox.showinfo("✅ Bot iniciado", "El bot se está ejecutando.")
    boton_confirmar.configure(state="disabled", text="Bot operando")
    boton_iniciar.configure(state="disabled", text="Bot iniciado")

def iniciar():
    try:
        vi = int(entry_inicio.get())
        sw = int(entry_stop_win.get())
        m = float(entry_multiplicador.get())
    except ValueError:
        messagebox.showerror("Error", "Todos los campos deben ser numéricos.")
        return

    global params_global
    moneda = moneda_seleccionada.get()
    params_global = {'vi': vi, 'sw': sw, 'm': m, 'moneda': moneda}

    iniciar_driver()
    consola_callback("⚠️ Abrí Binomo manualmente, luego presioná 'Estoy listo'.")
    boton_confirmar.pack(pady=10)

app.mainloop()
