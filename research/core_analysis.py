import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator, SMAIndicator
from ta.volatility import BollingerBands
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

try:
    TOKENIZER = AutoTokenizer.from_pretrained("ProsusAI/finbert")
    MODEL = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
except Exception as e:
    TOKENIZER, MODEL = None, None

def calculate_technical_score(klines: list) -> dict:
    if not klines or len(klines) < 20:
        return {"technical_score": 50, "indicators": {}, "df_clean": []}
        
    # Format dữ liệu nến Binance: Open Time, Open, High, Low, Close, Volume...
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'qav', 'num_trades', 'taker_base', 'taker_quote', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
        
    # 1. Tính các chỉ số nâng cao cho Biểu đồ Chuyên nghiệp
    df['rsi'] = RSIIndicator(close=df["close"], window=14).rsi()
    df['ema_20'] = EMAIndicator(close=df["close"], window=20).ema_indicator()
    df['sma_50'] = SMAIndicator(close=df["close"], window=50).sma_indicator()
    
    bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    df['bb_high'] = bb.bollinger_hband()
    df['bb_low'] = bb.bollinger_lband()
    
    macd_obj = MACD(close=df["close"])
    df['macd_hist'] = macd_obj.macd_diff()

    # Lấy các giá trị hiện tại ở cây nến mới nhất
    current_rsi = float(df["rsi"].iloc[-1]) if not np.isnan(df["rsi"].iloc[-1]) else 50.0
    current_macd = float(df["macd_hist"].iloc[-1]) if not np.isnan(df["macd_hist"].iloc[-1]) else 0.0
    current_close = float(df["close"].iloc[-1])
    current_bb_high = float(df["bb_high"].iloc[-1])
    current_bb_low = float(df["bb_low"].iloc[-1])

    # 2. Thuật toán chấm điểm định lượng đa yếu tố (Multi-factor Technical Scoring)
    score = 50.0
    # RSI Trigger
    if current_rsi < 30: score += 25
    elif current_rsi > 70: score -= 25
    else: score += (current_rsi - 50) * 0.4
    
    # MACD Trigger
    if current_macd > 0: score += 15
    else: score -= 15
        
    # Bollinger Bands Position Trigger
    if current_close > current_bb_high: score -= 10 # Quá nóng, chạm dải trên
    elif current_close < current_bb_low: score += 15 # Vùng mua kỹ thuật tốt

    final_score = int(max(0, min(100, score)))
    
    # Chuẩn hóa dữ liệu trả về để vẽ đồ thị bên Streamlit
    df_clean = df[['open_time', 'open', 'high', 'low', 'close', 'volume', 'ema_20', 'sma_50', 'bb_high', 'bb_low']].tail(30).to_dict(orient='records')
    
    return {
        "technical_score": final_score,
        "indicators": {
            "current_price": current_close,
            "rsi": round(current_rsi, 2),
            "macd_hist": round(current_macd, 6),
            "bb_width_pct": round(((current_bb_high - current_bb_low) / current_close) * 100, 2)
        },
        "chart_data": df_clean
    }

def calculate_sentiment_score(news_articles: list) -> dict:
    if not news_articles or not MODEL:
        return {"sentiment_score": 50, "label": "Neutral", "probabilities": {"positive": 0.33, "negative": 0.33}}
        
    titles = [a.get("title", "") for a in news_articles[:10]]
    if not titles:
        return {"sentiment_score": 50, "label": "Neutral", "probabilities": {"positive": 0.33, "negative": 0.33}}
        
    inputs = TOKENIZER(titles, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        outputs = MODEL(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
    mean_preds = predictions.mean(dim=0).tolist()
    pos_prob, neg_prob = mean_preds[0], mean_preds[1]
    
    sentiment_score = 50 + (pos_prob * 50) - (neg_prob * 50)
    final_score = int(max(0, min(100, sentiment_score)))
    
    return {
        "sentiment_score": final_score,
        "label": "Positive" if final_score > 60 else "Negative" if final_score < 40 else "Neutral",
        "probabilities": {"positive": round(pos_prob, 2), "negative": round(neg_prob, 2)}
    }

def evaluate_risk_level(coin: str, technical_score: int, sentiment_score: int) -> str:
    base_risk = "Low" if coin.upper() in ["BTC", "ETH"] else "Medium" if coin.upper() in ["SOL", "LINK", "AVAX"] else "High"
    if technical_score < 35 or sentiment_score < 35: return "High"
    return base_risk

def optimize_portfolio(investor_profile: dict, coin: str, technical_score: int, sentiment_score: int) -> dict:
    risk_tolerance = investor_profile.get("risk_profile", "Balanced") if investor_profile else "Balanced"
    market_strength = (technical_score * 0.6) + (sentiment_score * 0.4)
    
    allocated_asset = 0.0
    if risk_tolerance == "Conservative":
        allocated_asset = 40.0 if market_strength > 70 else 20.0 if market_strength > 45 else 5.0
    elif risk_tolerance == "Aggressive":
        allocated_asset = 80.0 if market_strength > 70 else 50.0 if market_strength > 45 else 20.0
    else:
        allocated_asset = 60.0 if market_strength > 70 else 35.0 if market_strength > 45 else 10.0
        
    return {
        "allocation_strategy": {f"{coin.upper()}": f"{allocated_asset}%", "USDT_Cash": f"{100.0 - allocated_asset}%"},
        "risk_management": {
            "suggested_stop_loss": "5% below entry" if market_strength > 60 else "3% below entry",
            "suggested_take_profit": "15% above entry" if market_strength > 60 else "10% above entry",
            "execution_style": "DCA" if market_strength < 50 else "Lump Sum"
        }
    }