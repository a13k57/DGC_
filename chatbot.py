import os
from anthropic import Anthropic
from dotenv import load_dotenv
import tkinter as tk
import pymongo

# Load environment variables
load_dotenv()

# Verificar variables de entorno
print("MONGO_URI presente:", bool(os.getenv("MONGO_URI")))
print("ANTHROPIC_API_KEY presente:", bool(os.getenv("ANTHROPIC_API_KEY")))

# Connect to MongoDB Atlas
try:
    cliente = pymongo.MongoClient(os.getenv("MONGO_URI"))
    cliente.admin.command('ping')
    print("Conexión exitosa a MongoDB")
    
    db = cliente["AHG"]
    coleccion = db["politicas_de_capacitacion"]
    
    # Verificar el contenido de la colección
    documento = coleccion.find_one()
    if documento:
        print("Estructura del documento:", documento.keys())
    else:
        print("No se encontraron documentos en la colección")
        
except Exception as e:
    print("Error de conexión a MongoDB:", e)

# Connect to Anthropic API
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key:
    anthropic = Anthropic(api_key=api_key)
else:
    print("Error: No se encontró la API key de Anthropic")

# Flag for controlling the question flow
seccion_seleccionada = False
seccion_actual = None

def obtener_resumen_seccion(seccion):
    try:
        documento = coleccion.find_one({})
        if documento and seccion in documento:
            # Generar un resumen usando Claude
            message = anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=150,
                messages=[
                    {
                        "role": "user",
                        "content": f"Resume el siguiente texto en máximo 3 líneas: {documento[seccion]}"
                    }
                ]
            )
            return message.content
        return "Sección no encontrada."
    except Exception as e:
        return f"Error al obtener el resumen: {str(e)}"

def obtener_seccion_completa(seccion):
    try:
        documento = coleccion.find_one({})
        if documento and seccion in documento:
            return documento[seccion]
        return "Sección no encontrada."
    except Exception as e:
        return f"Error al obtener la sección: {str(e)}"

def obtener_respuesta_claude(pregunta, contexto):
    try:
        message = anthropic.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1000,
            system=f"Eres un asistente experto en políticas de capacitación. Responde la siguiente pregunta basándote únicamente en este contexto específico: {contexto}",
            messages=[
                {
                    "role": "user",
                    "content": pregunta
                }
            ]
        )
        return message.content
    except Exception as e:
        return f"Error al obtener respuesta de Claude: {e}"

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
        # Procesar la pregunta del usuario usando el contexto completo
        contexto_completo = obtener_seccion_completa(seccion_actual)
        respuesta = obtener_respuesta_claude(entrada, contexto_completo)
        ventana_chat.insert(tk.END, f"\nBot: {respuesta}\n")
        ventana_chat.insert(tk.END, "\nPuedes hacer otra pregunta específica o escribir '7' para volver al menú.\n")

    ventana_chat.see(tk.END)

def iniciar_chatbot():
    ventana_chat.insert(tk.END, "¡Bienvenido al Chatbot de Políticas de Capacitación!\n")
    flujo_preguntas()

# Create the main window
app = tk.Tk()
app.title("Chatbot de Políticas de Capacitación")

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