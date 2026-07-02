import streamlit as st
import pandas as pd
import plotly.graph_objects as _go
import numpy as np
import uuid
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="AI Crypto Investment Intelligence Hub",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- KHỞI TẠO STATE HỆ THỐNG MOCK ---
if "session_id" not in st.session_state: 
    st.session_state.session_id = str(uuid.uuid4())
if "investor_profile" not in st.session_state: 
    st.session_state.investor_profile = None 
if "survey_step" not in st.session_state: 
    st.session_state.survey_step = 1
if "survey_complete" not in st.session_state: 
    st.session_state.survey_complete = False
if "chat_history" not in st.session_state: 
    st.session_state.chat_history = []
if "latest_quantitative_data" not in st.session_state: 
    st.session_state.latest_quantitative_data = None

# --- STATE QUẢN LÝ KỊCH BẢN ĐỘNG ---
if "monitored_coin" not in st.session_state:
    st.session_state.monitored_coin = "BTCUSDT"
if "live_alerts" not in st.session_state:
    st.session_state.live_alerts = []
if "pending_ticker" not in st.session_state:
    st.session_state.pending_ticker = None  
if "show_dashboard_triggered" not in st.session_state:
    st.session_state.show_dashboard_triggered = False 

def refresh_live_alerts():
    coin_tag = st.session_state.monitored_coin.replace("USDT", "")
    st.session_state.live_alerts = [
        {"type": "Whale Flow Alert 📊", "content": f"Dòng tiền phái sinh (Open Interest) của {coin_tag} tăng vọt 4.2% trong 1 giờ qua. Các định chế lớn đang tích lũy vị thế.", "time": "Vừa xong"},
        {"type": "Volatility Alert 📉", "content": f"{coin_tag} sụt giảm nhanh 1.15% trong vòng 15 phút qua, chạm ngưỡng cảnh báo thuật toán vĩ mô.", "time": "2 phút trước"}
    ]

if not st.session_state.live_alerts:
    refresh_live_alerts()

def generate_mock_chart_data(ticker):
    now = datetime.now()
    records = []
    base_price = 65000.0 if "BTC" in ticker else (3400.0 if "ETH" in ticker else 140.0)
    for i in range(30):
        open_p = base_price + np.random.uniform(-base_price*0.02, base_price*0.02)
        close_p = open_p + np.random.uniform(-base_price*0.025, base_price*0.025)
        high_p = max(open_p, close_p) + np.random.uniform(0, base_price*0.01)
        low_p = min(open_p, close_p) - np.random.uniform(0, base_price*0.01)
        t = (now - timedelta(days=30-i)).strftime("%Y-%m-%d")
        
        records.append({
            "open_time": t, "open": open_p, "high": high_p, "low": low_p, "close": close_p,
            "ema_20": open_p * 0.995, "bb_high": high_p * 1.02, "bb_low": low_p * 0.98
        })
        base_price = close_p
    return records

# ====================================================================================================
# [ SIDEBAR - THÔNG TIN TRẠNG THÁI ]
# ====================================================================================================
with st.sidebar:
    st.title("👤 HỒ SƠ NHÀ ĐẦU TƯ")
    
    if st.session_state.survey_complete and st.session_state.investor_profile:
        st.write("🌐 Trạng thái: **✅ ACTIVE**")
        prof = st.session_state.investor_profile
        st.write(f"▪️ Mức rủi ro: `{str(prof.get('risk_profile')).upper()}`")
        st.write(f"▪️ Phong cách: `{str(prof.get('investment_behavior')).upper()}`")
    elif st.session_state.survey_step > 1:
        st.write(f"🌐 Trạng thái: **⏳ ĐANG PHÂN TÍCH** (Bước: {st.session_state.survey_step}/2)")
        st.warning("📊 Hệ thống đang cấu hình ma trận rủi ro...")
    else:
        st.write("🌐 Trạng thái: **🛑 CHƯA KHỞI TẠO**")
        st.info("Vui lòng chia sẻ tình trạng đầu tư ở màn hình chính để mở khóa hệ thống nghiên cứu chuyên sâu.")
        
    if st.button("Làm mới Session & Khảo sát 🔄", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.investor_profile = None
        st.session_state.survey_step = 1
        st.session_state.survey_complete = False
        st.session_state.chat_history = []
        st.session_state.latest_quantitative_data = None
        st.session_state.live_alerts = []
        st.session_state.pending_ticker = None
        st.session_state.show_dashboard_triggered = False
        st.rerun()
        
    st.markdown("---")
    st.title("🎯 MỤC TIÊU GIÁM SÁT")
    selected_coin = st.selectbox(
        "Chọn tài sản ưu tiên:",
        ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"],
        index=0,
        key="coin_selector_stream"
    )
    
    if selected_coin != st.session_state.monitored_coin:
        st.session_state.monitored_coin = selected_coin
        refresh_live_alerts()
        st.rerun()
        
    st.markdown("---")
    st.title("🔔 ALERTS STREAM")
    
    if st.session_state.show_dashboard_triggered:
        for alert in st.session_state.live_alerts:
            with st.expander(f"{alert['type']} ({alert['time']})", expanded=True):
                st.write(f" `{alert['content']}`")
    else:
        st.info("Cảnh báo ngầm đang chạy. Hãy yêu cầu xuất Dashboard từ AI Chatbot để đồng bộ hiển thị.")

# ====================================================================================================
# [ MAIN HUB - KHU VỰC TƯƠNG TÁC CHAT ]
# ====================================================================================================
st.title("🦅 AI CRYPTO INVESTMENT INTELLIGENCE HUB")
st.caption("Chế độ Offline Toàn Phần")
st.markdown("---")

chat_container = st.container(height=380, border=True)

with chat_container:
    if not st.session_state.chat_history:
        st.chat_message("assistant").write(
            "Xin chào! Tôi là Trợ lý phân tích trí tuệ nhân tạo cấp cao. "
            "Rất vinh hạnh được đồng hành cùng quý nhà đầu tư trên thị trường tài sản số.\n\n"
            "Để mình có thể tối ưu hóa thuật toán và đưa ra các bộ lọc phù hợp nhất, "
            "bạn có thể chia sẻ một chút về **kinh nghiệm tham gia thị trường hoặc mục tiêu đầu tư hiện tại** của bạn không?"
        )
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["text"])

uploaded_file = st.file_uploader("📂 Gửi kèm tài liệu PDF / Whitepaper nghiên cứu", type=["pdf"], label_visibility="collapsed")

if uploaded_file and not st.session_state.get(f"processed_{uploaded_file.name}", False):
    with st.spinner("AI Agent đang trích xuất cấu trúc và mô hình toán học của dự án..."):
        time.sleep(2) 
        ans_pdf = f"📝 **BÁO CÁO THẨM ĐỊNH TÀI LIỆU SÂU (`{uploaded_file.name}`):**\n\n" \
                f"Hệ thống đã phân tích xong cấu trúc tệp tin. Phát hiện mô hình tokenomics của dự án áp dụng thuật toán giảm phát tốt kèm cơ chế phi tập trung vững chắc. " \
                f"Điểm số an toàn cấu trúc mã nguồn đạt **88/100**. Phù hợp đưa vào danh mục theo dõi phân bổ trung hạn."
        st.session_state.chat_history.append({"role": "assistant", "text": ans_pdf})
        st.session_state[f"processed_{uploaded_file.name}"] = True
    st.rerun()

user_input = st.chat_input("Nhập nội dung trao đổi tại đây...")

if user_input:
    with chat_container:
        st.chat_message("user").write(user_input)
    st.session_state.chat_history.append({"role": "user", "text": user_input})
    
    input_lower = user_input.lower()

    # ------------------------------------------------------------------------------------------------
    # LƯU CHẤT: LOGIC CHAT KYC HOÀN TOÀN TỰ NHIÊN
    # ------------------------------------------------------------------------------------------------
    if not st.session_state.survey_complete:
        with st.spinner("AI đang phân tích cấu trúc hành vi rủi ro..."):
            time.sleep(1)
            
            if st.session_state.survey_step == 1:
                ans = "Dạ vâng, thời gian **3-6 tháng** là giai đoạn cực kỳ quan trọng vì bạn đã bắt đầu nắm được nhịp của sàn nhưng rất dễ bị tâm lý đám đông chi phối. " \
                    "Thường ở giai đoạn này, điều cốt lõi không phải là tìm mọi cách tối ưu vốn bằng đòn bẩy lớn, mà là kiểm soát được mức độ sụt giảm tài sản khi thị trường rung lắc mạnh.\n\n" \
                    "Cho mình hỏi một chút để cấu hình bộ lọc rủi ro: Nếu chẳng may đồng coin bạn vừa mua bị **sụt giảm đột ngột 20-25%** do biến động vĩ mô xấu, " \
                    "hành động ưu tiên của bạn là cắt lỗ ngay lập tức để bảo toàn số vốn còn lại, hay có sẵn nguồn vốn dự phòng để mua tích lũy thêm (DCA)?"
                st.session_state.survey_step = 2
                
            elif st.session_state.survey_step == 2:
                ans = "Hiểu được tâm lý này của bạn, việc xót vốn và muốn trung bình giá (DCA) là phản ứng rất phổ biến của các nhà đầu tư mới tham gia. " \
                    "Tuy nhiên, chiến lược này đòi hỏi bạn phải có một kỷ luật phân bổ tỷ lệ vốn cực kỳ nghiêm ngặt để không bị chôn vốn sâu.\n\n" \
                    "Dựa trên những chia sẻ thực tế vừa rồi, hệ thống định lượng của mình đã tự động phân loại cấu trúc hồ sơ cho bạn: " \
                    "**SWING TRADER (Hành vi giao dịch ngắn-trung hạn với mức độ chịu rủi ro trung bình)**.\n\n" \
                    "Mô-đun Phân tích Thị trường Chuyên sâu (Function 2) đã được mở khóa! Bạn đang quan tâm đến đồng coin nào, ví dụ như BTC hay ETH để mình tiến hành quét dữ liệu?"
                st.session_state.investor_profile = {"risk_profile": "BALANCED RISK", "investment_behavior": "SWING TRADER"}
                st.session_state.survey_complete = True
            
            st.session_state.chat_history.append({"role": "assistant", "text": ans})
        st.rerun()
        
    # ------------------------------------------------------------------------------------------------
    # LƯU CHẤT: LOGIC NGHIÊN CỨU COIN & BUNG DASHBOARD THÔNG MINH
    # ------------------------------------------------------------------------------------------------
    else:
        if st.session_state.pending_ticker and any(word in input_lower for word in ["có", "ok", "đồng ý", "xuất", "hiển thị", "xem đi", "yes"]):
            with st.spinner("AI Agent đang liên kết luồng dữ liệu Alerts và dựng Dashboard định lượng..."):
                time.sleep(1.2)
                ticker = st.session_state.pending_ticker
                ans = f"📊 **Đồng bộ hệ thống định chế hoàn tất!** Mình đã liên kết và kích hoạt luồng quét **ALERTS ENGINE** trực tiếp tại thanh Sidebar bên trái cho cặp **{ticker}USDT**.\n\n" \
                      f"Toàn bộ ma trận chỉ báo kỹ thuật bóc tách thành phần, đồ thị dòng chảy tâm lý thị trường, và Báo cáo đề xuất quản trị vốn chuyên sâu của **{ticker}** đã xuất bản đầy đủ ở khu vực Dashboard phía dưới!"
                
                st.session_state.chat_history.append({"role": "assistant", "text": ans})
                st.session_state.monitored_coin = f"{ticker}USDT"
                refresh_live_alerts()
                
                st.session_state.latest_quantitative_data = {
                    "coin": ticker, "chart_data": generate_mock_chart_data(ticker)
                }
                st.session_state.show_dashboard_triggered = True
                st.session_state.pending_ticker = None 
            st.rerun()
            
        else:
            with st.spinner("AI Agent đang quét dòng chảy dữ liệu vĩ mô..."):
                time.sleep(1)
                detected_ticker = "BTC"
                if "eth" in input_lower: detected_ticker = "ETH"
                elif "sol" in input_lower: detected_ticker = "SOL"
                elif "bnb" in input_lower: detected_ticker = "BNB"
                
                st.session_state.pending_ticker = detected_ticker
                
                ans = f"Hệ thống định lượng đã ghi nhận mã tài sản mục tiêu bạn quan tâm: **{detected_ticker}**.\n\n" \
                    f"Đúng lúc lắm, dựa trên dữ liệu On-chain và dòng tiền phái sinh hiện tại, mình phát hiện dòng tiền của các quỹ lớn đang có sự cơ cấu lại và xuất hiện các dấu hiệu phân kỳ kỹ thuật khá mạnh ở khung thời gian lớn.\n\n" \
                    f"❓ **Bạn có muốn mình xuất toàn bộ hệ thống Institutional Dashboard chuyên sâu ở phía dưới để chúng ta nhìn rõ toàn cảnh xu hướng hiện tại và nhận mô hình quản trị vốn riêng cho đồng {detected_ticker} này không?**"
                
                st.session_state.chat_history.append({"role": "assistant", "text": ans})
            st.rerun()

# ====================================================================================================
# [ KHU VỰC HIỂN THỊ DASHBOARD QUÂN SỰ / ĐỊNH CHẾ CAO CẤP ]
# ====================================================================================================
if st.session_state.latest_quantitative_data and st.session_state.show_dashboard_triggered:
    data = st.session_state.latest_quantitative_data
    ticker = data.get("coin")
    
    st.markdown("---")
    st.header(f"🏛️ INSTITUTIONAL QUANTITATIVE DASHBOARD HUB: {ticker}")
    st.caption("Cơ sở dữ liệu tính toán thời gian thực từ các Pool thanh khoản và sàn Phái sinh Định chế")
    
    # 1. THẺ ĐIỂM SỐ CHÍNH (TOP METRICS)
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("📈 TECHNICAL MATRIX CORE", "85 / 100", help="Tổng điểm cấu trúc thuật toán xu hướng & dòng chảy lệnh")
    with m2: st.metric("📰 SENTIMENT FLUID INDEX", "72 / 100", help="Chỉ số tổng hợp tâm lý mạng xã hội, tin tức vĩ mô và tỷ lệ Long/Short")
    with m3: st.metric("🚨 SYSTEMIC RISK ASSESSMENT", "LOW TO MEDIUM", help="Mức độ rủi ro hệ thống dựa trên biến động Volatility")
        
    # 2. KHU VỰC ĐỒ THỊ CHÍNH & GIẢI THÍCH CHẤM ĐIỂM LOGIC
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.write("### 📊 1. Price Action Cấu trúc & Volatility Bands Daily")
        chart_records = data.get("chart_data", [])
        if chart_records:
            df_chart = pd.DataFrame(chart_records)
            fig = _go.Figure()
            fig.add_trace(_go.Candlestick(
                x=df_chart['open_time'], open=df_chart['open'], high=df_chart['high'], low=df_chart['low'], close=df_chart['close'], name='Nến Giá'
            ))
            fig.add_trace(_go.Scatter(x=df_chart['open_time'], y=df_chart['ema_20'], line=dict(color='orange', width=1.5), name='Hỗ trợ động EMA 20'))
            fig.update_layout(height=380, xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.write("### 🔍 2. Biểu đồ cấu trúc Technical (85/100)")
        # Biểu đồ cột bóc tách thành phần kỹ thuật
        tech_components = ['Trend (EMA)', 'RSI Oscillator', 'Volume Profile', 'Order Book Depth']
        tech_scores = [90, 80, 88, 82] # Tổng trung bình ~ 85
        
        fig_tech = _go.Figure(data=[_go.Bar(
            x=tech_scores, y=tech_components, orientation='h',
            marker_color=['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78']
        )])
        fig_tech.update_layout(height=380, template="plotly_dark", xaxis=dict(range=[0,100]), margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_tech, use_container_width=True)

    # 3. KHU VỰC ĐỒ THỊ SENTIMENT & ĐÁNH GIÁ NGUYÊN NHÂN RỦI RO
    c3, c4 = st.columns([1, 1])
    
    with c3:
        st.write("### 📰 3. Biểu đồ diễn biến dòng chảy tâm lý - Sentiment Flux (72/100)")
        # Biểu đồ vùng mô phỏng biến động tâm lý 7 ngày qua
        days = [(datetime.now() - timedelta(days=i)).strftime("%m-%d") for i in range(7)][::-1]
        sentiment_trend = [65, 68, 70, 67, 74, 71, 72]
        
        fig_sent = _go.Figure()
        fig_sent.add_trace(_go.Scatter(x=days, y=sentiment_trend, fill='tozeroy', line_color='cyan', name='Sentiment Score'))
        fig_sent.update_layout(height=280, template="plotly_dark", yaxis=dict(range=[50,100]), margin=dict(l=10,r=10,t=10,b=10))
        st.plotly_chart(fig_sent, use_container_width=True)
        
    with c4:
        st.write("### 🚨 4. Ma trận Chấm điểm & Rủi ro Hệ thống")
        # Bản diễn giải logic cấu trúc chặt chẽ thay thế cho việc ghi điểm suông
        st.markdown(f"""
        * **Cơ sở điểm Kỹ thuật (85/100):** Cấu trúc nến duy trì vững chắc trên đường trung bình trượt lũy tiến **EMA 20**. Bản đồ nhiệt *Volume Profile* xác nhận tích lũy khối lượng lớn tại vùng đáy cục bộ, lực bán yếu dần (Phân kỳ tăng giá ẩn).
        * **Cơ sở điểm Tâm lý (72/100):** Chỉ số quét tin tức vĩ mô ghi nhận mật độ thảo luận tích cực tăng 15% trên các kênh mạng xã hội đầu chế. Tuy nhiên, tỷ lệ đòn bẩy phái sinh (Funding Rate) đang hơi cao nên điểm số dừng lại ở mức 72 để cảnh báo rũ bỏ ngắn hạn.
        * **Đánh giá rủi ro (LOW TO MEDIUM):** Áp lực thanh lý phân bổ chủ yếu cách xa vùng giá hiện tại khoảng 8%. Biến động tài sản (`Volatility`) nằm trong biên độ kiểm soát an toàn của thuật toán Market Maker.
        """)

    # 4. BÁO CÁO PHÂN BỔ VÀ QUẢN TRỊ VỐN THAY THẾ JSON THÔ
    st.markdown("---")
    st.write(f"### 📋 BÁO CÁO KHUYẾN NGHỊ QUẢN TRỊ VỐN ĐỊNH CHẾ: ({ticker})")
    
    col_rep1, col_rep2 = st.columns(2)
    with col_rep1:
        st.info(f"""
        **🎯 VÙNG ENTRY CHIẾN LƯỢC ĐỀ XUẤT**
        * **Điểm mua tối ưu:** Tập trung giải ngân quanh vùng **Hỗ trợ động khung Daily (EMA 20)**. Đây là khu vực giao thoa của dòng tiền thuật toán, hạn chế tối đa rủi ro drawdown sâu cho tài khoản có kinh nghiệm dưới 6 tháng.
        * **Hành vi bổ trợ:** Không mua đuổi khi nến giá vượt quá dải trên Bollinger Band (BB High).
        """)
    with col_rep2:
        st.warning(f"""
        **💼 QUY MÔ PHÂN BỔ VÀ HÀNH ĐỘNG GIẢM THIỂU RỦI RO**
        * **Tỷ trọng phân bổ:** Giới hạn tối đa **25% tổng quy mô danh mục đầu tư hiện tại** cho mã tài sản này. Giữ 75% sức mua bằng Stablecoin để chuẩn bị kịch bản phòng vệ rủi ro.
        * **Kế hoạch phòng vệ:** Theo dõi sát luồng **Alerts Stream** ở thanh Sidebar trái. Nếu nổ cảnh báo biến động giá sụt giảm sâu đi kèm dòng tiền phái sinh (Open Interest) tháo chạy tháo cống, lập tức dừng kế hoạch DCA và chờ lệnh cấu trúc mới.
        """)