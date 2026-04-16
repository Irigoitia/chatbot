Instalación

Clonar el repositorio:

git clone https://github.com/Irigoitia/chatbot.git
cd chatbot_tp

Crear entorno virtual:
"""Sobre el entorno virtual (venv)

El entorno virtual (venv) crea un espacio aislado de Python para el proyecto.

Esto permite:

Evitar conflictos de versiones
Usar las mismas librerías que el resto del equipo
Mantener el proyecto organizado

Es necesario activarlo antes de trabajar con el chatbot."""

py -3.8 -m venv venv
venv\Scripts\activate

Instalar dependencias:

pip install -r requirements.txt
