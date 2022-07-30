import os
from dotenv import load_dotenv

def env(key):
    load_dotenv()
    result = os.getenv(key)
    return result