import os
import pathlib

CACHE_DIR = pathlib.Path('.cache')
CACHE_FILE = CACHE_DIR / 'latest.csv'

OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434/api/chat')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')

BAR_COLOR = '#00c2ff'
BG_COLOR = '#0c2144'

HIGHCHARTS_CDN = 'https://code.highcharts.com/highcharts.js'
HIGHCHARTS_INTEGRITY = 'sha384-GuZpdtcxzvZAKIlclU0on1Zsa1+lZeI7IuP89xDSHLVYRIlnJr2dIovnHgwlHGaw'
