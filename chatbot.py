import pymongo
import os
from openai import OpenAI
from dotenv import load_dotenv
import tkinter as tk

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Conectar a MongoDB Atlas
cliente = pymongo.MongoClient("mongodb+srv://castelite:8voG6EjCeXybD56o@cluster0.knltx.mongodb.net/?retryWrites=true&w=majority")
db = cliente["AHG"]  # Base de datos
coleccion = db["politicas_de_capacitacion"]  # Colección

# Obtener la clave de API de OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("Clave API cargada correctamente")
    client = OpenAI(api_key=api_key)
else:
    print("Error al cargar la clave API")

# Función para obtener todo el documento desde MongoDB
def obtener_documento_completo():
    resultado = coleccion.find_one()
    if resultado:
        return resultado.get("contenido", "No se encontró contenido en MongoDB.")
    return None

# Función para obtener la respuesta de ChatGPT
def obtener_respuesta_chatgpt(pregunta, documento_completo):
    try:
        # Enviar la pregunta y el documento completo a ChatGPT
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Este es el documento base:"},
                {"role": "system", "content": documento_completo},
                {"role": "user", "content": pregunta}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al obtener respuesta de ChatGPT: {e}"

# Función para manejar el envío de preguntas
def enviar_mensaje(event=None):
    pregunta = entrada_usuario.get()
    if pregunta:
        ventana_chat.insert(tk.END, "usuario: " + pregunta + "\n")
        
        # Obtener todo el documento desde MongoDB
        documento_completo = obtener_documento_completo()
        
        if documento_completo:
            # Consultar ChatGPT con el documento completo y la pregunta
            respuesta = obtener_respuesta_chatgpt(pregunta, documento_completo)
        else:
            respuesta = "No se encontró el documento en MongoDB."
        
        ventana_chat.insert(tk.END, "AHG: " + respuesta + "\n\n")
        entrada_usuario.delete(0, tk.END)

# Interfaz gráfica
app = tk.Tk()
app.title("Chatbot de Políticas")

ventana_chat = tk.Text(app, height=20, width=80)
ventana_chat.pack()

entrada_usuario = tk.Entry(app, width=80)
entrada_usuario.pack()
entrada_usuario.bind("<Return>", enviar_mensaje)

boton_enviar = tk.Button(app, text="Enviar", command=enviar_mensaje)
boton_enviar.pack()

app.mainloop()
