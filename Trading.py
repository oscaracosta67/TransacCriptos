import requests
import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
import telegram

# CONFIGURACIÓN
TOKEN = 'TU_TOKEN_DE_TELEGRAM'
CHAT_ID = 'TU_CHAT_ID'
SYMBOL = 'BTCUSDT'
INTERVAL = '5m'
LIMIT = 100

# Crear bot de Telegram
bot = telegram.Bot(token=TOKEN)

def get_klines(symbol, interval, limit):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        'time','open','high','low','close','volume','close_time','quote_asset_volume','num_trades','taker_buy_base','taker_buy_quote','ignore'
    ])
    df['close'] = df['close'].astype(float)
    return df

def analizar_y_alertar():
    df = get_klines(SYMBOL, INTERVAL, LIMIT)
    df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
    df['ema5'] = EMAIndicator(df['close'], window=5).ema_indicator()
    df['ema20'] = EMAIndicator(df['close'], window=20).ema_indicator()

    rsi = df['rsi'].iloc[-1]
    ema5 = df['ema5'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    precio = df['close'].iloc[-1]

    mensaje = f"{SYMBOL} - Precio: {precio:.2f}\nRSI: {rsi:.2f}\nEMA5: {ema5:.2f} | EMA20: {ema20:.2f}"

    if rsi < 30 and ema5 > ema20:
        bot.send_message(chat_id=CHAT_ID, text="🟢 Señal de COMPRA detectada\n" + mensaje)
    elif rsi > 70 and ema5 < ema20:
        bot.send_message(chat_id=CHAT_ID, text="🔴 Señal de VENTA detectada\n" + mensaje)
    else:
        print("Sin señal clara")

# Ejecutar solo una vez al día o por cronjob
analizar_y_alertar()
