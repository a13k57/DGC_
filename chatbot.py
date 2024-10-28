import os
from anthropic import Anthropic
from dotenv import load_dotenv
import tkinter as tk
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configuración de rutas y credenciales
CREDENTIALS_PATH = r'C:\Users\acastellanos\OneDrive - Alpha Hardin\Documentos\1\DGC\credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# IDs de documentos específicos
POLITICAS = {
    "reembolsos": "1l7vc3LO5V4f7TrzTKuDryra0VQkMfS7wVXMzmTiZiH4",
    "capacitacion": "1F96z-c7CVnEoduQu-enIFnK6h67HX9lUxeBi0pQlZDk"
}

SECCIONES_CAPACITACION = {
    "1": "descripcion_general",
    "2": "tipos_capacitacion",
    "3": "modalidades_capacitacion",
    "4": "modelo_aprendizaje",
    "5": "responsabilidades_colaborador",
    "6": "responsabilidades_empresa"
}

# Variables de estado
politica_seleccionada = None
seccion_seleccionada = False
seccion_actual = None
en_capacitacion = False

def limpiar_respuesta(respuesta):
    """Limpia la respuesta de Claude de elementos no deseados"""
    if hasattr(respuesta, 'content'):
        # Si es un objeto de respuesta, obtener el contenido
        contenido = respuesta.content
    else:
        contenido = str(respuesta)
    
    # Limpiar elementos no deseados
    contenido = contenido.replace("[TextBlock(text='", "")
    contenido = contenido.replace("', type='text')]", "")
    contenido = contenido.replace("\\n", "\n")
    contenido = contenido.strip()
    
    return contenido

def verificar_configuracion():
    """Verifica la configuración inicial y muestra información de diagnóstico"""
    print("\n=== Verificación de Configuración ===")
    
    # Verificar archivo de credenciales
    print(f"\nVerificando archivo de credenciales en: {CREDENTIALS_PATH}")
    if os.path.exists(CREDENTIALS_PATH):
        print("✓ Archivo de credenciales encontrado")
    else:
        print("✗ Archivo de credenciales NO encontrado")
        return False

    # Verificar conexión a Drive
    try:
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_PATH, scopes=SCOPES
        )
        service = build('drive', 'v3', credentials=credentials)
        
        # Probar acceso a los documentos
        for nombre, doc_id in POLITICAS.items():
            try:
                doc = service.files().get(fileId=doc_id).execute()
                print(f"✓ Acceso exitoso a documento {nombre}: {doc['name']}")
            except Exception as e:
                print(f"✗ Error al acceder a documento {nombre}: {e}")
        
        return service
    except Exception as e:
        print(f"\n✗ Error al conectar con Google Drive: {e}")
        return False

def obtener_contenido_documento(service, doc_id):
    try:
        content = service.files().export(
            fileId=doc_id,
            mimeType='text/plain'
        ).execute()
        return content.decode('utf-8')
    except Exception as e:
        print(f"Error al leer documento {doc_id}: {e}")
        return None

def obtener_resumen_seccion(seccion):
    try:
        if en_capacitacion and seccion in SECCIONES_CAPACITACION.values():
            contenido = obtener_contenido_documento(drive_service, POLITICAS["capacitacion"])
            if contenido:
                message = anthropic.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=150,
                    messages=[
                        {
                            "role": "user",
                            "content": f"Resume el siguiente texto en máximo 3 líneas, enfocándote en la sección {seccion}: {contenido}"
                        }
                    ]
                )
                return limpiar_respuesta(message.content)
        return "Sección no encontrada."
    except Exception as e:
        return f"Error al obtener el resumen: {str(e)}"

def obtener_respuesta_claude(pregunta, politica):
    try:
        contenido = obtener_contenido_documento(drive_service, POLITICAS[politica])
        if contenido:
            message = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=f"Eres un asistente experto en políticas. Responde la siguiente pregunta basándote únicamente en este contexto específico: {contenido}",
                messages=[
                    {
                        "role": "user",
                        "content": pregunta
                    }
                ]
            )
            return limpiar_respuesta(message.content)
        return "No se pudo obtener el contenido del documento."
    except Exception as e:
        return f"Error al obtener respuesta de Claude: {e}"
def flujo_preguntas(event=None):
    global politica_seleccionada, seccion_seleccionada, seccion_actual, en_capacitacion
    entrada = entrada_usuario.get().strip()
    entrada_usuario.delete(0, tk.END)
    
    if entrada:
        ventana_chat.insert(tk.END, f"\nTú: {entrada}\n")

    # Si no hay política seleccionada, mostrar menú principal
    if politica_seleccionada is None:
        ventana_chat.insert(tk.END, "\n¿Qué política deseas consultar?\n")
        ventana_chat.insert(tk.END, "1. Política de reembolsos y caja chica\n")
        ventana_chat.insert(tk.END, "2. Política de capacitación\n")
        politica_seleccionada = False
        return

    # Procesar selección inicial de política
    if politica_seleccionada is False:
        if entrada == "1":
            ventana_chat.insert(tk.END, "\nHas seleccionado Política de reembolsos y caja chica.\n")
            ventana_chat.insert(tk.END, "¿Qué deseas saber sobre esta política?\n")
            politica_seleccionada = True
            seccion_actual = "reembolsos"
            en_capacitacion = False
        elif entrada == "2":
            politica_seleccionada = True
            en_capacitacion = True
            ventana_chat.insert(tk.END, "\n¿Sobre qué tema de capacitación quieres consultar?\n")
            ventana_chat.insert(tk.END, "1. Descripción general de la política\n")
            ventana_chat.insert(tk.END, "2. Tipos de capacitación\n")
            ventana_chat.insert(tk.END, "3. Modalidades de capacitación\n")
            ventana_chat.insert(tk.END, "4. Modelo de aprendizaje\n")
            ventana_chat.insert(tk.END, "5. Responsabilidades del colaborador\n")
            ventana_chat.insert(tk.END, "6. Responsabilidades de la empresa\n")
            ventana_chat.insert(tk.END, "7. Volver al menú principal\n")
        else:
            ventana_chat.insert(tk.END, "\nOpción no válida. Por favor, selecciona 1 o 2.\n")
        return

    # Manejar preguntas sobre reembolsos
    if seccion_actual == "reembolsos":
        if entrada.lower() == "menu":
            politica_seleccionada = None
            seccion_actual = None
            en_capacitacion = False
            flujo_preguntas()
        else:
            respuesta = obtener_respuesta_claude(entrada, "reembolsos")
            ventana_chat.insert(tk.END, f"\nBot: {respuesta}\n")
            ventana_chat.insert(tk.END, "\nPuedes hacer otra pregunta o escribir 'menu' para volver al menú principal.\n")
        return

    # Manejar política de capacitación
    if en_capacitacion:
        if entrada == "7":
            politica_seleccionada = None
            seccion_actual = None
            en_capacitacion = False
            flujo_preguntas()
            return

        if not seccion_actual:
            if entrada in SECCIONES_CAPACITACION:
                seccion_actual = SECCIONES_CAPACITACION[entrada]
                resumen = obtener_resumen_seccion(seccion_actual)
                ventana_chat.insert(tk.END, f"\nBot: Has seleccionado: {seccion_actual}\n")
                ventana_chat.insert(tk.END, f"Resumen:\n{resumen}\n")
                ventana_chat.insert(tk.END, "\n¿Tienes alguna pregunta específica sobre este tema? Puedes preguntar cualquier cosa o escribir '7' para volver al menú.\n")
            else:
                ventana_chat.insert(tk.END, "\nBot: Opción no válida. Por favor, selecciona un número del 1 al 7.\n")
        else:
            respuesta = obtener_respuesta_claude(entrada, "capacitacion")
            ventana_chat.insert(tk.END, f"\nBot: {respuesta}\n")
            ventana_chat.insert(tk.END, "\nPuedes hacer otra pregunta específica o escribir '7' para volver al menú.\n")

    ventana_chat.see(tk.END)

def iniciar_chatbot():
    ventana_chat.insert(tk.END, "¡Bienvenido al Chatbot de Políticas!\n")
    flujo_preguntas()

# Inicializar servicios
load_dotenv()

# Verificar configuración y establecer conexión
print("Iniciando verificación de configuración...")
drive_service = verificar_configuracion()
if not drive_service:
    print("\nError: No se pudo inicializar el servicio de Google Drive")
    exit()

# Inicializar Anthropic
anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Create the main window
app = tk.Tk()
app.title("Chatbot de Políticas")

# Configure the main window
app.geometry("800x600")
app.configure(bg='#f0f0f0')

# Create and configure the chat window
ventana_chat = tk.Text(app, height=30, width=80, bg='white', fg='black')
ventana_chat.pack(pady=10, padx=10)

# Create a frame for input elements
input_frame = tk.Frame(app, bg='#f0f0f0')
input_frame.pack(fill=tk.X, padx=10, pady=5)

# Create and configure the input field
entrada_usuario = tk.Entry(input_frame, width=70)
entrada_usuario.pack(side=tk.LEFT, padx=5)
entrada_usuario.bind("<Return>", flujo_preguntas)

# Create and configure the send button
boton_enviar = tk.Button(input_frame, text="Enviar", command=flujo_preguntas, 
                        bg='#4CAF50', fg='white', padx=20)
boton_enviar.pack(side=tk.LEFT, padx=5)

# Start the chatbot
iniciar_chatbot()

# Start the application
app.mainloop()