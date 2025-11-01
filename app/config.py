from dotenv import load_dotenv
import os

load_dotenv()  # Carga variables de entorno desde .env al entorno OS

SECRET_KEY = os.getenv("SECRET_KEY")
