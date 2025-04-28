# Warzone Loadouts Bot

Un bot de **Discord** para gestionar loadouts de Call of Duty: Warzone 🎮, usando **Slash Commands** `/`, **Firebase** para almacenar los loadouts por servidor, y **Flask** para mantenerse activo en **Render**.

---

## 🚀 Comandos Disponibles

| Comando | Descripción | Permisos |
|:--------|:------------|:---------|
| `/loadouts` | Ver los loadouts disponibles | Todos |
| `/add_load` | Agregar un nuevo loadout (con accesorios) | Admin |
| `/edit_load` | Editar un loadout existente | Admin |
| `/del_load` | Eliminar un loadout | Admin |
| `/offbot` | El owner expulsa el bot del servidor | Owner |
| `/setbot` | Restringe `/loadouts` a un solo canal | Admin |
| `/unsetbot` | Vuelve `/loadouts` global | Admin |

---

## 🛠️ Tecnologías Usadas

- **Discord.py** 2.3.2
- **Firebase Admin SDK**
- **Flask** (para keep alive)
- **Python-Dotenv**
- **Gunicorn** (para Render)

---

## 📋 Requisitos

- Python 3.10 o superior.
- Crear un proyecto en **Firebase** y descargar la `firebase-key.json`.
- Tener un servidor de Discord y crear una **aplicación/bot** en el [Developer Portal de Discord](https://discord.com/developers/applications).

---

## ⚙️ Configuración Inicial

1. Clonar este repositorio o copiar los archivos.
2. Instalar dependencias:
    ```bash
    pip install -r requirements.txt
    ```
3. Crear un archivo `.env` en la raíz con:

    ```
    TOKEN=tu_token_aqui
    OWNER_ID=tu_id_aqui
    ```
4. Poner tu archivo `firebase-key.json` en la raíz.
5. Editar en `firebase.py` la ruta correcta a tu `firebase-key.json`.

---

## 🔥 Deploy en Render

1. Crear una cuenta en [Render](https://render.com/).
2. Crear un nuevo Web Service.
3. Conectar tu repositorio.
4. Variables de entorno (`Environment Variables`):
    - `TOKEN`
    - `OWNER_ID`
5. Archivo `Start Command`:
    ```
    gunicorn bot:app
    ```
6. Agregar un archivo `Procfile`:

    ```
    web: python3 bot.py
    ```

(esto mantendrá tu bot vivo gracias a `keep_alive.py`)

---

## 🎨 Características Adicionales

- **Loadouts por servidor**: cada servidor tiene sus propios loadouts.
- **Embeds de color verde oscuro**.
- **Botones verdes** para mostrar configuraciones rápidas.
- **Comandos slash fáciles de usar**.
- **Restricciones de canal opcionales**.

---

## 📸 Vista previa

> ¡Aquí se mostraría una captura de cómo se ve el bot funcionando!

---

## 📣 Créditos

- Desarrollado por Jorge (@MyAkarii) 👨‍💻

---
