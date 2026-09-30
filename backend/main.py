"""
Punto de entrada, igual que en Apolo-Avalian y Claudia: se corre con
`python main.py` desde esta misma carpeta (backend), para que la app
encuentre bien su archivo .env (la ruta está escrita como relativa en
app/config.py) y los imports de "app.algo" funcionen.
"""
import sys

# La consola de Windows no entiende los emojis que usan los mensajes de
# arranque (🚀, etc.) con la codificación por defecto — sin esto, el sistema
# no llega a levantar en Windows.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8040)
