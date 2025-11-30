import streamlit as st
import pandas as pd
import time
import os
# 修正導入：直接 import 模組名稱
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
from rules import generate_random_gua, generate_full_life_gua, check_exemption, calculate_net_gain_from_gua, analyze_health_and_luck, is_all_same_color, check_career_pattern, check_wealth_pattern, check_consumption_at_1_or_5, check_interference

# ----------------------------------------------
# 輔助函數
# ----------------------------------------------
def display_piece(gua_data, pos_num):
    """輔助函數：用於顯示單個棋子的圖片和位置信息"""
    try:
        piece = next(p for p in gua_data if p[0] == pos_num)
        name, color = piece[1], piece[2]
        image_path = get_image_path(name, color) 
        
        st.markdown(f"<div style='text-align: center; font-size: 14px; margin-bottom: 2px;'>{POSITION_MAP[pos_num]['名稱']}</div>", unsafe_allow_html=True)
        
        if image_path and os.path.exists(image_path):
            st.image(image_path, caption=f"{color}{name}", width=70)
        else:
            st.warning(f"{color}{name}")
            
        st.markdown(f"<div style='text-align: center; font-size: 10px; color: #888;'>{POSITION_MAP[pos_num]['關係']}</div>", unsafe_allow_html=True)
    except StopIteration:
        st.empty()

# ----------------------------------------------
# 頁面配置
# ----------------------------------------------
st.set_page_config(
    page_title="專業象棋占卜系統 - 全盤流年版",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
h1 {color: #B22222; font-family: 'serif'; text-shadow: 1px 1px 2px #000000;}
h2, h3 {color: #C0C0C0; border-left: 5px solid #8B0000; padding-left: 15px; margin-top: 20px;}
.stage-box {border: 1px solid #444; padding: 10px; margin-bottom: 20px; border-radius: 5px; background-color: #262730;}
</style>
""", unsafe_allow_html=True)

st.title("🔮 專業象棋占卜系統：洞悉棋局，掌握人生格局")
st.markdown("---")

# ----------------------------------------------
# 側邊欄與狀態初始化
# ----------------------------------------------
if 'reroll_count' not in st.session_state: st.session_state.reroll_count = 0
if 'final_result_status' not in st.session_state: st.session_state.final_result_status = "INIT"
if 'current_mode' not in st.session_state: st.session_state.current_mode = "SINGLE"
if 'sub_query' not in st.session_state: st.session_state.sub_query = "問運勢"
if 'message' not in st.session_state: st.session_state.message = ""
if 'current_gua' not in st.session_state: st.session_state.current_gua = []

with st.sidebar:
    st.header("天機奧秘，誠心求卜")
    st.warning("**全盤流年**：將使用一副完整32支棋，排列出您的一生運勢架構。")
    
    gender = st.selectbox("1. 詢問性別", ["男", "女"])
    
    query_type = st.selectbox(
        "2. 詢問類型", 
        [
            "全盤流年 (11~80歲完整排盤)", 
            "單卦問事 (運勢/財運/感情)", 
        ]
    )
    
    current_sub_query_selection = "問運勢"
    
    if query_type == "單卦問事 (運勢/財運/感情)":
        current_sub_query_selection = st.selectbox("3. 詳細事項", ["問運勢", "事業查詢", "前世格局", "健康分析", "投資/財運", "感情/關係", "離婚議題"])
        if current_sub_query_selection == "投資/財運":
            st.date_input("4. 獲利時間點", value=None)
    
    if st.button("開始排盤 / 占卜"):
        if query_type == "全盤流年 (11~80歲完整排盤)":
            st.session_state.current_mode = "FULL"
            with st.spinner('正在洗牌、切牌、排布全盤流年...'):
                time.sleep(1.5)
                st.session_state.full_life_gua = generate_full_life_gua()
                st.session_state.final_result_status = "VALID"
                st.session_state.message = "全盤流年排佈完成！"
        else:
            st.session_state.current_mode = "SINGLE"
            st.session_state.sub_query = current_sub_query_selection
            
            new_gua = generate_random_gua()
            if is_all_same_color(new_gua):
                st.session_state.reroll_count += 1
                if st.session_state.reroll_count == 1:
                    with st.spinner('不成卦 (全黑/全紅)，重抽中...'): time.sleep(1); new_gua = generate_random_gua()
                    if is_all_same_color(new_gua):
                        st.session_state.current_gua = new_gua
                        st.session_state.message = "❌ 兩次不成卦，暗示「不會做也不會成」。"
                        st.session_state.final_result_status = "REJECTED"
                    else:
                        st.session_state.current_gua = new_gua
                        st.session_state.message = "🚨 重抽成功，卦象生成。"
                        st.session_state.final_result_status = "VALID"
                else:
                     st.session_state.message = "請刷新頁面重試。"
                     st.session_state.final_result_status = "REJECTED" 
            else:
                st.session_state.current_gua = new_gua
                st.session_state.reroll_count = 0
                st.session_state.message = "卦象生成成功。"
                st.session_state.final_result_status = "VALID"
        
        st.success(st.session_state.message)
        st.rerun()

# ----------------------------------------------
# 主頁面顯示邏輯
# ----------------------------------------------
if st.session_state.final_result_status == "INIT": st.info("請點擊左側按鈕開始。"); st.stop()
if st.session_state.final_result_status == "REJECTED": st.error(st.session_state.message); st.stop() 

# 模式 A: 全盤流年顯示
if st.session_state.current_mode == "FULL":
    full_data = st.session_state.full_life_gua
    
    st.header("📜 象棋數理 - 全盤流年表")
    st.info("本排盤使用完整 32 支象棋，依序對應您人生的不同十年大運。")
    
    st.subheader("🏁 總格 (整體命盤核心)")
    with st.expander("查看總格解析", expanded=True):
        st.write("此部分整合全盤能量，建議關注「11~20歲」及「31~40歲」的基礎奠定。")
    
    life_stages = ["11~20歲", "21~30歲", "31~40歲", "41~50歲", "51~60歲", "61~70歲"]
    
    for stage in life_stages:
        gua = full_data[stage]
        analysis = calculate_net_gain_from_gua(gua)
        
        st.markdown(f"<div class='stage-box'>", unsafe_allow_html=True)
        st.markdown(f"### 🗓️ {stage} 運勢")
        
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: display_piece(gua, 4)
        c4, c5, c6 = st.columns([1, 1, 1])
        with c4: display_piece(gua, 2)
        with c5: display_piece(gua, 1)
        with c6: display_piece(gua, 3)
        c7, c8, c9 = st.columns([1, 1, 1])
        with c8: display_piece(gua, 5)
        
        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        
        net_gain = analysis['net_gain']
        status = "運勢強勁 🚀" if net_gain > 0 else "需保守沈潛 🛡️"
        col_res1.metric("階段能量淨值", f"{net_gain}", status)
        
        exemption = check_exemption(gua)
        if exemption:
            col_res2.warning(f"特殊格局：{exemption[0]} (影響{POSITION_MAP[exemption[1]]['名稱']})")
        else:
            col_res2.info("格局：平穩發展")
            
        center_piece = next(p for p in gua if p[0] == 1)
        st.caption(f"**核心主導 ({stage})：** {center_piece[2]}{center_piece[1]} - {ATTRIBUTES.get(center_piece[1], {}).get('特質', '')}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.warning("⚠️ **71~80歲及晚年：** 需參照餘棋或重新起卦進行專項健康分析。")

# 模式 B: 單卦問事
elif st.session_state.current_mode == "SINGLE":
    current_gua = st.session_state.current_gua
    sub_query = st.session_state.sub_query
    
    analysis_results = calculate_net_gain_from_gua(current_gua) 
    health_analysis = analyze_health_and_luck(current_gua)

    st.header(f"✅ 單卦解析：{sub_query}")
    
    col_u1, col_u2, col_u3 = st.columns([1, 1, 1])
    with col_u2: display_piece(current_gua, 4)
    col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
    with col_m1: display_piece(current_gua, 2)
    with col_m2: display_piece(current_gua, 1)
    with col_m3: display_piece(current_gua, 3)
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d2: display_piece(current_gua, 5)

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 收穫與付出", "✨ 格局分析", "🧬 深入解讀"])
    
    with tab1:
        st.metric("淨盈餘/虧損", f"{analysis_results['net_gain']}", delta="獲利" if analysis_results['net_gain'] > 0 else "虧損")
        st.dataframe(pd.DataFrame(analysis_results['interactions']))
        
    with tab2:
        exemption = check_exemption(current_gua)
        if exemption: st.success(f"特殊格局：{exemption[0]}")
        else: st.info("無特殊格局")
        
        if sub_query == "事業查詢":
            if check_career_pattern(current_gua): st.success("符合事業格！")
            
    with tab3:
        if sub_query == "健康分析":
            st.write(health_analysis['health_warnings'])
            if check_consumption_at_1_or_5(current_gua): st.error("留意消耗格影響健康。")
        elif sub_query == "前世格局":
             piece_1 = next(p for p in current_gua if p[0] == 1)
             st.write(f"前世身分參考：{piece_1[1]}")
        elif sub_query == "離婚議題" and gender == "女":
             st.warning("請留意好朋友格在2-3或4-5的影響。")
        else:
            st.info("請參考通用運勢分析。")
