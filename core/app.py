import streamlit as st
import pandas as pd
import altair as alt

# ────────────── Page Config & CSS ──────────────
st.set_page_config(page_title="Tilandky 媽媽覺察陪伴室", layout="wide", page_icon="🧘‍♀️")

# 定義品牌色
COLOR_PRIMARY = "#073B4C"
COLOR_SECONDARY = "#118AB2"
COLOR_ACCENT_GREEN = "#06D6A0"
COLOR_ACCENT_YELLOW = "#FFD166"
COLOR_ACCENT_RED = "#FF6B6B"

st.markdown(
    f"""<style>
    /* 全局字體與背景 */
    .stApp {{
        background-color: #f8fafc;
        font-family: 'Inter', 'Noto Sans TC', sans-serif;
    }}
    
    /* Hero Section */
    .hero {{
        padding: 3rem 2rem;
        text-align: center;
        background-color: {COLOR_PRIMARY};
        color: white;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
    }}
    .hero h1 {{
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    .hero p {{
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }}
    
    /* 卡片樣式 */
    div[data-testid="stContainer"] {{
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }}
    
    /* 標題樣式 */
    h2 {{
        color: {COLOR_SECONDARY};
        font-weight: 700 !important;
        text-align: center;
        margin-bottom: 1.5rem !important;
    }}
    h3 {{
        color: {COLOR_PRIMARY};
        font-weight: 600 !important;
    }}
    
    /* CTA 按鈕 */
    .btn-cta {{
        display: inline-block;
        padding: 12px 30px;
        background-color: {COLOR_SECONDARY};
        color: white !important;
        text-decoration: none;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.1rem;
        margin-top: 20px;
        text-align: center;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(17, 138, 178, 0.3);
    }}
    .btn-cta:hover {{
        background-color: #0c6a8a;
        transform: translateY(-2px);
    }}
    
    /* 流程箭頭 */
    .flow-arrow {{
        text-align: center;
        font-size: 2rem;
        color: {COLOR_SECONDARY};
        margin: 10px 0;
        opacity: 0.6;
    }}
    
    /* Footer */
    .footer {{
        text-align: center;
        padding: 2rem;
        color: #64748b;
        font-size: 0.9rem;
        background-color: #f1f5f9;
        margin-top: 3rem;
        border-top: 1px solid #e2e8f0;
    }}
    </style>""",
    unsafe_allow_html=True,
)

# ────────────── Data Preparation ──────────────

# 1. 媽媽精力分配數據 (Donut Chart Data)
energy_data = pd.DataFrame({
    'Role': ['媽媽角色 (育兒/家務)', '伴侶角色 (夫妻關係)', '職場角色 (工作/事業)', '自我時間 (休息/成長)'],
    'Value': [40, 20, 30, 10],
    'Color': [COLOR_SECONDARY, COLOR_ACCENT_GREEN, COLOR_ACCENT_YELLOW, COLOR_ACCENT_RED]
})

# 2. 核心卡點數據 (Bar Chart Data)
pain_point_data = pd.DataFrame({
    'PainPoint': [
        '自我愧疚 (覺得自己不夠好)', 
        '伴侶衝突 (缺乏神隊友支援)', 
        '職涯焦慮 (失去自我價值)', 
        '原生家庭影響 (複製舊模式)', 
        '金錢匱乏感 (對未來不安)'
    ],
    'Percentage': [85, 78, 65, 60, 50]
})

# 3. TRUST 系統數據
trust_steps = [
    {
        "step": "T - Truth (真實/洞察)",
        "desc": "看清「系統藍圖」，停止自我攻擊。我們將診斷妳的真實卡點，而不是表層問題。",
        "items": ["📋 深度系統診斷報告書", "✨ 瑪雅圖騰 靈魂藍圖分析 (個人+合盤)"]
    },
    {
        "step": "R - Reframe (重塑/釋放)",
        "desc": "清除「潛意識病毒」，安裝「支持性信念」。透過日常覺察抓取舊模式，並用希塔療癒重塑。",
        "items": ["🧠 西塔療癒 潛意識除錯 (抓Bug/安裝新程式)", "🎧 Tilandky 每日覺察練功房 (情境SOP音檔)"]
    },
    {
        "step": "U - Union (合一/目標)",
        "desc": "從「我」的覺察，擴展到「我們」的家庭願景。釐清妳真正渴望的平衡狀態。",
        "items": ["🎯 家庭合一 願景目標書 (妳的北極星)"]
    },
    {
        "step": "S - Strategy (策略/行動)",
        "desc": "讓「覺察」不只是空想，而是「日常」的具體行動。提供客製化的溝通腳本與天賦引導策略。",
        "items": ["📝 客製化 親子/伴侶行動計劃書 (溝通腳本)", "💬 6次陪跑 專案檢核系統 (每週覺察回報)"]
    },
    {
        "step": "T - Transformation (轉化/成果)",
        "desc": "慶祝轉化，將「覺察」內化為妳的DNA。看見真實的改變，並獲得持續支持的藍圖。",
        "items": ["📈 個人轉化 成果報告 (Before/After 對比)", "🔄 未來藍圖 與 複訓計畫 (持續支持)"]
    }
]

# ────────────── Main Content ──────────────

# 1. Hero Section
st.markdown(
    """
    <div class="hero">
        <h1>Tilandky 日常覺察陪伴室</h1>
        <p>用「工程師邏輯」與「男性視角」，數據化妳的內在轉化</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# 2. 現狀分析 (Charts)
st.markdown("## 這是否是妳的日常？")
st.caption("身為 25-45 歲的媽媽，妳是否也常在「媽媽、伴侶、職場」等多重角色中掙扎？")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    with st.container(border=True):
        st.markdown("### 媽媽的精力分配")
        st.write("妳的精力與時間總是被各種角色佔據，留給「自我」的空間少之又少。")
        
        # Altair Donut Chart
        base = alt.Chart(energy_data).encode(
            theta=alt.Theta("Value", stack=True)
        )
        pie = base.mark_arc(innerRadius=60).encode(
            color=alt.Color("Role", scale=alt.Scale(domain=energy_data['Role'].tolist(), range=energy_data['Color'].tolist()), legend=dict(orient="bottom")),
            order=alt.Order("Value", sort="descending"),
            tooltip=["Role", "Value"]
        )
        st.altair_chart(pie, use_container_width=True)

with col_chart2:
    with st.container(border=True):
        st.markdown("### 核心卡點分析")
        st.write("根據 300+ 位媽媽的諮詢數據，這些是最常見的內在卡點：")
        
        # Altair Bar Chart
        bar = alt.Chart(pain_point_data).mark_bar(color=COLOR_SECONDARY, cornerRadiusEnd=4).encode(
            x=alt.X('Percentage', title='回報比例 (%)'),
            y=alt.Y('PainPoint', sort='-x', title=None),
            tooltip=['PainPoint', 'Percentage']
        ).properties(height=300)
        st.altair_chart(bar, use_container_width=True)

st.info("💡 **核心洞察**：所有外在的議題（親子、伴侶、金錢），其實都是妳與「自己」關係的延伸。")

# 3. 比較優勢 (Comparison)
st.divider()
st.markdown("## Tilandky 的獨特之處：理性與溫暖的結合")

col_comp1, col_comp2 = st.columns(2)

with col_comp1:
    with st.container(border=True):
        st.markdown("### 🌀 傳統身心靈")
        st.markdown("""
        * 🌫️ 觀點抽象，難以落地
        * 😢 容易陷入純粹的情緒宣洩
        * ❓ 缺乏系統，問題重複發生
        * ⚖️ 可能帶有隱藏的價值評斷
        """)

with col_comp2:
    # 使用 info 框來強調優勢，背景會有淡藍色
    st.info("### ⚙️ Tilandky 陪伴室 (冠龍)")
    st.markdown("""
    * **工程師邏輯**：提供可執行的 SOP 與行動清單
    * **男性視角**：理性分析，幫妳翻譯隊友的語言
    * **系統化除錯**：找出問題根源 (Bug) 而非只解症狀
    * **溫暖陪伴**：不帶評斷的傾聽樹洞
    """)

# 4. TRUST 系統 (Process)
st.divider()
st.markdown("## TRUST 系統：妳的 6 個月轉化藍圖")
st.markdown("<div style='text-align: center; margin-bottom: 30px; color: #666;'>這是一套被 300+ 媽媽驗證的系統化流程。核心引擎就是貫穿全程的「日常覺察」。</div>", unsafe_allow_html=True)

# 這裡使用一個垂直的佈局來呈現流程
col_center = st.columns([1, 2, 1]) # 讓內容集中在中間

with col_center[1]:
    for i, step in enumerate(trust_steps):
        with st.container(border=True):
            st.markdown(f"### {step['step']}")
            st.write(step['desc'])
            
            # 交付項目區塊
            st.markdown(
                """
                <div style="background-color: #f0f9ff; padding: 10px; border-radius: 5px; margin-top: 10px;">
                <strong>📦 交付項目：</strong>
                </div>
                """, 
                unsafe_allow_html=True
            )
            for item in step['items']:
                st.markdown(f"- {item}")
        
        # 除了最後一個步驟外，顯示箭頭
        if i < len(trust_steps) - 1:
            st.markdown('<div class="flow-arrow">⬇</div>', unsafe_allow_html=True)

# 5. 社會證明 (Social Proof)
st.divider()
st.markdown("## 真實的轉化，來自數據的驗證")
col_stat1, col_stat2, col_stat3 = st.columns([1, 2, 1])
with col_stat2:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <p style="font-size: 1.2rem; color: #666;">這不只是空談，這套系統已經成功協助...</p>
            <div style="font-size: 5rem; font-weight: 800; color: {COLOR_SECONDARY}; line-height: 1;">300+</div>
            <p style="font-size: 1.5rem; font-weight: 600; color: {COLOR_PRIMARY};">位媽媽找回內在的平靜與力量</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 6. CTA (Call to Action)
st.divider()
col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])

with col_cta2:
    with st.container(border=True):
        st.markdown("<h3 style='text-align: center;'>🚀 開始妳的轉化第一步</h3>", unsafe_allow_html=True)
        st.write("妳不需要立刻承諾 6 個月。從一個 20 分鐘的「工程師邏輯診斷」開始。我會用最高效率的方式，幫妳釐清妳的「真實卡點」。")
        
        st.markdown(
            f"""
            <div style="text-align: center; background-color: #f8fafc; padding: 20px; border-radius: 10px; margin-top: 20px;">
                <p style="font-size: 1.2rem; font-weight: 600; color: {COLOR_PRIMARY};">前導諮詢 (20分鐘 邏輯診斷)</p>
                <p style="font-size: 3rem; font-weight: 800; color: {COLOR_SECONDARY}; margin: 10px 0;">$200</p>
                <a href="https://line.me/R/ti/p/%40690ZLAGN" target="_blank" class="btn-cta">
                    點擊預約妳的 20 分鐘診斷
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

# ────────────── Footer ──────────────
st.markdown(
    """
    <div class="footer">
      <p>© 2025 Tilandky 陪你聊 | 親子關係陪伴室. All rights reserved.</p>
    </div>
    """,
    unsafe_allow_html=True
)