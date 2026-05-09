# PROYECTO CHATBOT - DOLARIX

Este proyecto implementa un sistema de chatbot conversacional utilizando el framework **Rasa**, diseñado para procesar lenguaje natural (**NLU**) y gestionar el flujo de diálogos mediante aprendizaje automático.

---

## 1. Requisitos previos

- Python 3.8.x. Se recomienda la versión estable **3.8.10**.
- Administrador de paquetes `pip` actualizado.
- Conexión a Internet, solo para la primera ejecución y descarga de dependencias.
- Espacio en disco para modelos de lenguaje, aproximadamente entre **500 MB y 1 GB**.

---

## 2. Configuración del entorno

Los siguientes comandos se ejecutan desde la terminal de VS Code.

### A. Instalación

Clonar el repositorio:

```bash
git clone https://github.com/Irigoitia/chatbot.git
cd chatbot_tp
```

### B. Crear y activar el entorno virtual

Crear el entorno virtual con Python 3.8:

```bash
py -3.8 -m venv .venv
```

Activar el entorno virtual en Windows PowerShell:

```powershell
.\.venv\Scripts\activate
```

Activar el entorno virtual en Linux, Mac o Git Bash:

```bash
source .venv/bin/activate
```

### C. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 3. Ejecución

Para iniciar el sistema, se deben ejecutar los siguientes comandos en terminales independientes dentro del entorno virtual.

### Terminal 1: Servidor de acciones

```bash
rasa run actions
```

### Terminal 2: Motor del chatbot

```bash
rasa run --enable-api --cors "*"
```

Una vez ejecutadas ambas terminales, abrir el archivo:

```text
chat.html
```

El archivo `chat.html` se encuentra dentro del repositorio y funciona como interfaz web del chatbot.

---

## 4. Notas de uso

### Posibles errores

- **Error de compatibilidad:** si `pip` falla al instalar dependencias, asegurarse de que las **Build Tools de C++** estén instaladas en el sistema.

- **PowerShell bloquea el script:** si PowerShell no permite activar el entorno virtual, ejecutar antes:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

Luego volver a activar el entorno virtual:

```powershell
.\.venv\Scripts\activate
```

---

## 5. Resumen de comandos principales

```bash
rasa run actions
```

```bash
rasa run --enable-api --cors "*"
```

```bash
pip install -r requirements.txt
```
