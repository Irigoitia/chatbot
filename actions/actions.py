import requests
from rasa_sdk.events import SlotSet #<-->
from typing import Any, Text, Dict, List
from thefuzz import process

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


class ActionConsultarDolar(Action):
    def name(self) -> Text:
        return "action_consultar_dolar"

    def normalizar_tipo_dolar(self, texto: str) -> str:
        if not texto:
            return ""

        texto = texto.lower().strip()

        equivalencias = {
            "mep": "bolsa",
            "dolar mep": "bolsa",
            "dólar mep": "bolsa",
            "dolar bolsa": "bolsa",
            "dólar bolsa": "bolsa",
            "contado con liqui": "contadoconliqui",
            "contado con liquidacion": "contadoconliqui",
            "contado con liquidación": "contadoconliqui",
            "ccl": "contadoconliqui",
            "dolar ccl": "contadoconliqui",
            "dólar ccl": "contadoconliqui",
            "todos": "todos",
            "todas": "todos"
        }

        return equivalencias.get(texto, texto)

    def obtener_tipo_dolar(self, tracker: Tracker, intent_name: Text) -> str:
        # 1. Primero intentamos con la entidad que detectó Rasa (NLU)
        entidad = next(tracker.get_latest_entity_values("tipo_dolar"), None)

        if entidad:
            return self.normalizar_tipo_dolar(entidad)

        texto = tracker.latest_message.get("text", "").lower()

        # 2. Detectar directamente tipos de dólar mencionados en la frase
        opciones_texto = ["oficial", "blue", "bolsa", "mep", "ccl", "contado con liqui", "contado con liquidacion", "contadoconliqui", "tarjeta", "mayorista", "cripto", "todos"]
        for opcion in opciones_texto:
            if opcion in texto:
                if opcion == "mep":
                    return "bolsa"
                if opcion in ["ccl", "contado con liqui", "contado con liquidacion", "contadoconliqui"]:
                    return "contadoconliqui"
                return opcion

        # 3. Si es una consulta genérica de cotización sin tipo específico, devolvemos todos
        if intent_name == "consultar_dolar":
            if any(palabra in texto for palabra in ["cotiz", "cotización", "cotizaciones", "cotizar", "cotizame", "mostrar cotiz", "mostrar cotizaciones"]):
                return "todos"

        # 4. Si no hay entidad ni coincidencia directa, usamos Fuzzy Matching sobre el texto completo
        opciones = ["oficial", "blue", "bolsa", "mep", "ccl", "contadoconliqui", "tarjeta", "mayorista", "cripto", "todos"]
        resultado = process.extractOne(texto, opciones)

        if resultado:
            palabra, puntaje = resultado
            if puntaje > 70:
                if palabra == "mep":
                    return "bolsa"
                if palabra == "ccl":
                    return "contadoconliqui"
                return palabra

        return ""

    def formatear_un_dolar(self, data: Dict[Text, Any]) -> str:
        nombre = data.get("nombre", "Sin nombre")
        compra = data.get("compra", "N/D")
        venta = data.get("venta", "N/D")
        fecha = data.get("fechaActualizacion", "N/D")

        return (
             f"Cotización del dólar {nombre}:\n"
             f"Compra: ${compra}\n"
             f"Venta: ${venta}\n"
             f"Actualizado: {fecha}"
        )

    def formatear_todos(self, lista, intent: Text = ""):
        if intent in ["comprar_dolar", "comprar_dolar_persona"]:
            lineas = ["Cotizaciones de venta del dólar:\n"]
            for dolar in lista:
                nombre = dolar.get("nombre", "Sin nombre")
                venta = dolar.get("venta", "N/D")
                lineas.append(f"- {nombre}: venta ${venta}")
            return "\n".join(lineas)

        if intent in ["vender_dolar", "vender_dolar_persona"]:
            lineas = ["Cotizaciones de compra del dólar:\n"]
            for dolar in lista:
                nombre = dolar.get("nombre", "Sin nombre")
                compra = dolar.get("compra", "N/D")
                lineas.append(f"- {nombre}: compra ${compra}")
            return "\n".join(lineas)

        lineas = ["Cotizaciones del dólar:\n"]
        for dolar in lista:
            nombre = dolar.get("nombre", "Sin nombre")
            compra = dolar.get("compra", "N/D")
            venta = dolar.get("venta", "N/D")
            lineas.append(f"- {nombre}: compra ${compra} | venta ${venta}")

        return "\n".join(lineas)

    def formatear_un_dolar_operacion(self, data: Dict[Text, Any], intent: Text) -> str:
        nombre = data.get("nombre", "Sin nombre")
        compra = data.get("compra", "N/D")
        venta = data.get("venta", "N/D")
        fecha = data.get("fechaActualizacion", "N/D")

        if intent in ["comprar_dolar", "comprar_dolar_persona"]:
            return (
                f"Precio de venta del dólar {nombre}: ${venta}\n"
                f"Actualizado: {fecha}"
            )

        if intent in ["vender_dolar", "vender_dolar_persona"]:
            return (
                f"Precio de compra del dólar {nombre}: ${compra}\n"
                f"Actualizado: {fecha}"
            )

        return (
             f"Cotización del dólar {nombre}:\n"
             f"Compra: ${compra}\n"
             f"Venta: ${venta}\n"
             f"Actualizado: {fecha}"
        )

    #ACA ES DONDE SE EJECUTA LA ACCION, SE OBTIENE EL TIPO DE DOLAR QUE EL USUARIO QUIERE CONSULTAR, SE HACE LA CONSULTA A LA API
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        intent_name = tracker.latest_message.get("intent", {}).get("name", "")
        tipo_dolar = self.obtener_tipo_dolar(tracker, intent_name)
        #ACA LLAMA A LA API PARA OBTENER LOS DATOS DE CADA DOLAR, DEPENDIENDO DEL TIPO QUE EL USUARIO QUIERA CONSULTAR
        endpoints = {
            "oficial": "https://dolarapi.com/v1/dolares/oficial",
            "blue": "https://dolarapi.com/v1/dolares/blue",
            "bolsa": "https://dolarapi.com/v1/dolares/bolsa",
            "mep": "https://dolarapi.com/v1/dolares/bolsa",
            "contadoconliqui": "https://dolarapi.com/v1/dolares/contadoconliqui",
            "tarjeta": "https://dolarapi.com/v1/dolares/tarjeta",
            "mayorista": "https://dolarapi.com/v1/dolares/mayorista",
            "cripto": "https://dolarapi.com/v1/dolares/cripto",
            "todos": "https://dolarapi.com/v1/dolares"
        }

        if not tipo_dolar:
            dispatcher.utter_message(
                text="[BotDolar] Para ayudarte necesito saber qué tipo de dólar querés consultar. Podés pedirme información del dólar oficial, blue, bolsa (MEP), CCL, tarjeta, mayorista o cripto.\n\n" +
                     "Si preferís, escribí algo como:\n" +
                     "- 'cotización del dólar blue'\n" +
                     "- 'precio del dólar oficial'\n" +
                     "- 'quiero saber el dólar tarjeta'\n" +
                     "- 'mostrar cotizaciones'"
            )
            return []

        url = endpoints.get(tipo_dolar)

        if not url:
            dispatcher.utter_message(
                text="[BotDolar] Ese tipo de dólar no lo reconozco todavía."
            )
            return []

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            intent_name = tracker.latest_message.get("intent", {}).get("name", "")

            if tipo_dolar == "todos":
                mensaje = self.formatear_todos(data, intent_name)
            else:
                mensaje = self.formatear_un_dolar_operacion(data, intent_name)

            dispatcher.utter_message(text=f"[BotDolar] {mensaje}")
            #Errores relacionados con la API o la conexión a internet
        except requests.exceptions.RequestException:
            dispatcher.utter_message(
                text="[BotDolar] No pude consultar la cotización en este momento. Probá de nuevo en un rato."
            )
            #Errores relaciones con la pregunta del usuario o el procesamiento de la respuesta
        except Exception:
            dispatcher.utter_message(
                text="[BotDolar] No pude consultar la cotización en este momento. Probá de nuevo en un rato."
            )

        return [ SlotSet("modo_chat", "bot_dolar"),
    SlotSet("contador_fuera_contexto", 0)]
    



    #===========================================================
class ActionFallbackContador(Action):

    def name(self):
        return "action_fallback_contador"

    def run(self, dispatcher, tracker, domain):

        contador = tracker.get_slot("contador_fuera_contexto")
        modo = tracker.get_slot("modo_chat")

        if contador is None:
            contador = 0

        contador += 1

        # =========================
        # BOT DOLAR
        # =========================

        if modo == "bot_dolar":

            if contador == 1:

                dispatcher.utter_message(
                    text="[BotDolar] ⚠️ Eso no parece relacionado al dólar."
                )

                dispatcher.utter_message(
                    text="[BotDolar] 🔄 Volviendo al operador..."
                )

                return [
                    SlotSet("modo_chat", "operador"),
                    SlotSet("contador_fuera_contexto", contador)
                ]

            elif contador == 2:

                dispatcher.utter_message(
                    text="[BotDolar] 😄 Pasando al modo conversación casual."
                )

                return [
                    SlotSet("modo_chat", "chit_chat"),
                    SlotSet("contador_fuera_contexto", contador)
                ]

            else:

                dispatcher.utter_message(
                    text="[BotDolar] ❌ Conversación finalizada."
                )

                return [
                    SlotSet("modo_chat", "operador"),
                    SlotSet("contador_fuera_contexto", 0)
                ]

        # =========================
        # CHIT CHAT
        # =========================

        elif modo == "chit_chat":

            if contador >= 3:

                dispatcher.utter_message(
                    #text="[ChitChat] 👋 Finalizando sesión."
                    text="[SESSION_END] [ChitChat] 👋 Finalizando sesión."
                )

                return [
                    #SlotSet("modo_chat", "operador"),
                    SlotSet("contador_fuera_contexto", 0)
                ]

         
            dispatcher.utter_message(
                text="[ChitChat] 😄 Seguimos conversando..."
            )
            return [
                SlotSet("contador_fuera_contexto", contador)
            ]

        # =========================
        # OPERADOR
        # =========================

        elif modo == "operador":
            dispatcher.utter_message(text=f"[DEBUG] contador={contador}")
            # Primer y segundo fallback
            if contador < 3:

                dispatcher.utter_message(
                    text="[BotOperador] 🤖 No entendí eso."
                )

                return [
                    SlotSet("contador_fuera_contexto", contador)
                ]

            # Tercer fallback → pasar a chit chat
            elif contador == 3:

                dispatcher.utter_message(
                    text="[ChitChat] 😄 Pasando al modo conversación casual."
                )

                return [
                    SlotSet("modo_chat", "chit_chat"),
                    SlotSet("contador_fuera_contexto", contador)
                ]

            # Más de 5 → cerrar sesión
            elif contador >= 5:

                dispatcher.utter_message(
                    text="[BotOperador] Conversación finalizada."
                )

                return [
                    SlotSet("modo_chat", "operador"),
                    SlotSet("contador_fuera_contexto", 0)
                ]









    #============================================================
class ActionRouterConversacion(Action):

     def name(self):
        return "action_router_conversacion"

     def run(self, dispatcher, tracker, domain):

        ultimo_intent = tracker.latest_message['intent'].get('name')

        # Entrar al bot dólar
        if ultimo_intent == "consultar_dolar":

            return [
                SlotSet("modo_chat", "bot_dolar"),
                SlotSet("contador_fuera_contexto", 0)
            ]

        # Entrar al chit chat
        elif ultimo_intent == "chit_chat":

            return [
                SlotSet("modo_chat", "chit_chat")
            ]

        # Mantener modo actual
            return []