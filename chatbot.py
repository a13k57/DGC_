import os
from openai import OpenAI
from dotenv import load_dotenv
import tkinter as tk
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuración de rutas y credenciales
CREDENTIALS_PATH = r'C:\Users\acastellanos\OneDrive - Alpha Hardin\Documentos\1\DGC\credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# IDs de documentos específicos en Google Drive
POLITICAS = {
    "capacitacion": "1F96z-c7CVnEoduQu-enIFnK6h67HX9lUxeBi0pQlZDk"
}

# Variables de control
seccion_seleccionada = False
seccion_actual = None

# Cargar variables de entorno
load_dotenv()

# Verificar la API key de OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Error: No se encontró la API key de OpenAI")
    exit()

client = OpenAI(api_key=api_key)

# Inicializar Google Drive API
try:
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS_PATH, scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=credentials)
except Exception as e:
    print(f"Error al conectar con Google Drive: {e}")
    exit()

# Función para obtener el contenido de un documento de Google Drive
def obtener_contenido_documento(doc_id):
    try:
        content = drive_service.files().export(
            fileId=doc_id,
            mimeType='text/plain'
        ).execute()
        return content.decode('utf-8')
    except Exception as e:
        print(f"Error al leer documento {doc_id}: {e}")
        return None

# Función para obtener un resumen de una sección específica
def obtener_resumen_seccion(seccion):
    try:
        contenido = obtener_contenido_documento(POLITICAS["capacitacion"])
        if contenido:
            # Generar un resumen usando ChatGPT
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Resume el siguiente texto en máximo 3 líneas, enfocándote en la sección {seccion}:"},
                    {"role": "user", "content": contenido}
                ]
            )
            return response.choices[0].message.content
        return "Sección no encontrada."
    except Exception as e:
        return f"Error al obtener el resumen: {str(e)}"

# Función para obtener respuesta de ChatGPT con un contexto específico
def obtener_respuesta_chatgpt(pregunta, contexto):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"Eres un asistente experto en políticas de capacitación. Responde la siguiente pregunta basándote únicamente en este contexto específico: {contexto}"},
                {"role": "user", "content": pregunta}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al obtener respuesta de ChatGPT: {e}"

# Flujo de preguntas
def flujo_preguntas(event=None):
    global seccion_seleccionada, seccion_actual
    entrada = entrada_usuario.get().strip()
    entrada_usuario.delete(0, tk.END)
    
    if entrada:
        ventana_chat.insert(tk.END, f"\nTú: {entrada}\n")

    if not seccion_seleccionada:
        ventana_chat.insert(tk.END, "\n¿Sobre qué tema quieres consultar?\n")
        ventana_chat.insert(tk.END, "1. Descripción general de la política\n")
        ventana_chat.insert(tk.END, "2. Tipos de capacitación\n")
        ventana_chat.insert(tk.END, "3. Modalidades de capacitación\n")
        ventana_chat.insert(tk.END, "4. Modelo de aprendizaje\n")
        ventana_chat.insert(tk.END, "5. Responsabilidades del colaborador\n")
        ventana_chat.insert(tk.END, "6. Responsabilidades de la empresa\n")
        ventana_chat.insert(tk.END, "7. Volver al menú principal\n")
        seccion_seleccionada = True
        return

    secciones = {
        "1": "descripcion_general",
        "2": "tipos_capacitacion",
        "3": "modalidades_capacitacion",
        "4": "modelo_aprendizaje",
        "5": "responsabilidades_colaborador",
        "6": "responsabilidades_empresa"
    }

    if entrada == "7":
        seccion_seleccionada = False
        seccion_actual = None
        flujo_preguntas()
        return

    if not seccion_actual:
        if entrada in secciones:
            seccion_actual = secciones[entrada]
            resumen = obtener_resumen_seccion(seccion_actual)
            ventana_chat.insert(tk.END, f"\nBot: Has seleccionado: {seccion_actual}\n")
            ventana_chat.insert(tk.END, f"Resumen:\n{resumen}\n")
            ventana_chat.insert(tk.END, "\n¿Tienes alguna pregunta específica sobre este tema? Puedes preguntar cualquier cosa o escribir '7' para volver al menú.\n")
        else:
            ventana_chat.insert(tk.END, "\nBot: Opción no válida. Por favor, selecciona un número del 1 al 7.\n")
            seccion_seleccionada = False
            flujo_preguntas()
    else:
        contexto_completo = obtener_contenido_documento(POLITICAS["capacitacion"])
        respuesta = obtener_respuesta_chatgpt(entrada, contexto_completo)
        ventana_chat.insert(tk.END, f"\nBot: {respuesta}\n")
        ventana_chat.insert(tk.END, "\nPuedes hacer otra pregunta específica o escribir '7' para volver al menú.\n")

    ventana_chat.see(tk.END)

def iniciar_chatbot():
    ventana_chat.insert(tk.END, "¡Bienvenido al Chatbot de Políticas de Capacitación!\n")
    flujo_preguntas()

# Crear la ventana principal
app = tk.Tk()
app.title("Chatbot de Políticas de Capacitación")

# Configuración de la ventana principal
app.geometry("800x600")
app.configure(bg='#f0f0f0')

# Crear y configurar la ventana de chat
ventana_chat = tk.Text(app, height=30, width=80, bg='white', fg='black')
ventana_chat.pack(pady=10, padx=10)

# Crear un frame para los elementos de entrada
input_frame = tk.Frame(app, bg='#f0f0f0')
input_frame.pack(fill=tk.X, padx=10, pady=5)

# Crear y configurar el campo de entrada
entrada_usuario = tk.Entry(input_frame, width=70)
entrada_usuario.pack(side=tk.LEFT, padx=5)
entrada_usuario.bind("<Return>", flujo_preguntas)

# Crear y configurar el botón de enviar
boton_enviar = tk.Button(input_frame, text="Enviar", command=flujo_preguntas, 
                        bg='#4CAF50', fg='white', padx=20)
boton_enviar.pack(side=tk.LEFT, padx=5)

# Iniciar el chatbot
iniciar_chatbot()

# Iniciar la aplicación
app.mainloop()
