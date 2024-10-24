import os
from openai import OpenAI
from dotenv import load_dotenv
import tkinter as tk

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la clave de API desde las variables de entorno
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("Clave API cargada correctamente")
else:
    print("Error al cargar la clave API")

# Crear una instancia del cliente OpenAI
if api_key:
    client = OpenAI(api_key=api_key)

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(pregunta):
    try:
        # Hacer una solicitud a la API de OpenAI usando el modelo GPT-3.5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pregunta}]
        )
        # Acceder al contenido de la respuesta de manera correcta
        return response.choices[0].message.content  # Acceso mediante atributos
    except Exception as e:
        return f"Error al obtener respuesta de ChatGPT: {e}"

# Función para enviar mensajes desde la interfaz
def enviar_mensaje(event=None):  # El parámetro 'event' permite que funcione con Enter y con el botón
    pregunta = entrada_usuario.get()  # Obtener la pregunta escrita por el usuario
    if pregunta:
        ventana_chat.insert(tk.END, "usuario: " + pregunta + "\n")
        respuesta = obtener_respuesta_chatgpt(pregunta)
        ventana_chat.insert(tk.END, "AHG: " + respuesta + "\n\n")
        entrada_usuario.delete(0, tk.END)  # Limpiar el campo de entrada de texto

# Crear la ventana principal de la interfaz gráfica
app = tk.Tk()
app.title("chatbot de prueba")

# Crear el área de chat (para mostrar la conversación)
ventana_chat = tk.Text(app, height=20, width=80)
ventana_chat.pack()

# Crear un campo de entrada de texto para que el usuario escriba sus preguntas
entrada_usuario = tk.Entry(app, width=80)
entrada_usuario.pack()
entrada_usuario.bind("<Return>", enviar_mensaje)  # Detectar la tecla Enter para enviar

# Crear un botón para enviar las preguntas
boton_enviar = tk.Button(app, text="Enviar", command=enviar_mensaje)
boton_enviar.pack()

# Iniciar la aplicación gráfica
app.mainloop()
