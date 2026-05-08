import requests
import threading
import os

RASA_URL = "http://localhost:5005/webhooks/rest/webhook"

timer = None


def cerrar_por_timeout():
    print("\n⏰ La sesión expiró por inactividad.")
    os._exit(0)


def iniciar_timer():
    global timer
    timer = threading.Timer(60, cerrar_por_timeout)
    timer.start()


def cancelar_timer():
    global timer
    if timer is not None:
        timer.cancel()
        timer = None


print("🤖 Chat iniciado (escribí 'salir' para terminar)\n")

while True:

    iniciar_timer()

    mensaje = input("Vos: ")

    cancelar_timer()

    if mensaje.lower() == "salir":
        print("👋 Conversación finalizada.")
        break

    response = requests.post(
        RASA_URL,
        json={
            "sender": "usuario",
            "message": mensaje
        }
    )

    respuestas = response.json()

    if respuestas:

        for r in respuestas:

            if "text" in r:

                texto = r["text"]

                if "[SESSION_END]" in texto:

                    texto = texto.replace("[SESSION_END]", "").strip()

                    print(f"\n{texto}")
                    print("⛔ Sesión cerrada.\n")

                    exit()

                if texto.startswith("[BotDolar]"):

                    texto = texto.replace("[BotDolar]", "").strip()
                    print(f"BotDolar: {texto}")

                elif texto.startswith("[BotOperador]"):

                    texto = texto.replace("[BotOperador]", "").strip()
                    print(f"BotOperador: {texto}")

                elif texto.startswith("[ChitChat]"):

                    texto = texto.replace("[ChitChat]", "").strip()
                    print(f"ChitChat: {texto}")

                else:
                    print(f"Bot: {texto}")

    else:
        print("Bot: No respondió.")