import os
from openai import OpenAI
from dotenv import load_dotenv

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
        print(f"Error al obtener respuesta de ChatGPT: {e}")
        return None

if __name__ == "__main__":
    while True:
        user_input = input("Tú: ")  # Input del usuario
        if user_input.lower() == "salir":
            break

        # Obtener respuesta de ChatGPT
        respuesta = obtener_respuesta_chatgpt(user_input)
        if respuesta:
            print("ChatGPT:", respuesta)  # Solo imprime la respuesta ahora
        else:
            print("Error al obtener respuesta.")
