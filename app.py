import streamlit as st
import pandas as pd
import time
import os
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
# 導入所有新增的分析函數
from rules import generate_random_gua, generate_full_life_gua, check_exemption, calculate_net_gain_from_gua, analyze_health_and_luck, is_all_same_color, check_career_pattern, check_wealth_pattern, check_consumption_at_1_or_5, check_interference, analyze_trinity_detailed, analyze_holistic_health, analyze_coordinate_map, analyze_body_hologram

# ----------------------------------------------
# 輔助函數
# ----------------------------------------------
def display_piece(gua_data, pos_num):
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
st.set_page_config(page_title="專業象棋占卜系統 - 全盤流年版", layout="wide", initial_sidebar_state="expanded")
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
    query_type = st.selectbox("2. 詢問類型", ["全盤流年 (11~80歲完整排盤)", "單卦問事 (運勢/財運/感情)"])
    
    current_sub_query_selection = "問運勢"
    if query_type == "單卦問事 (運勢/財運/感情)":
        current_sub_query_selection = st.selectbox("3. 詳細事項", ["問運勢", "事業查詢", "前世格局", "健康分析", "投資/財運", "感情/關係", "離婚議題"])
        if current_sub_query_selection == "投資/財運":
            st.date_input("4. 獲利時間點", value=None)
    
    if st.button("開始排盤 / 占卜"):
        if query_type == "全盤流年 (11~80歲完整排盤)":
            st.session_state.current_mode = "FULL"
            with st.spinner('排布全盤流年中...'):
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
                    with st.spinner('不成卦，重抽中...'): 
                        time.sleep(1)
                        new_gua = generate_random_gua()
                    if is_all_same_color(new_gua):
                        st.session_state.current_gua = new_gua; st.session_state.message = "❌ 兩次不成卦，暗示不可為。"; st.session_state.final_result_status = "REJECTED"
                    else:
                        st.session_state.current_gua = new_gua; st.session_state.message = "🚨 重抽成功。"; st.session_state.final_result_status = "VALID"
                else:
                     st.session_state.message = "請刷新重試。"; st.session_state.final_result_status = "REJECTED" 
            else:
                st.session_state.current_gua = new_gua; st.session_state.reroll_count = 0; st.session_state.message = "卦象生成成功。"; st.session_state.final_result_status = "VALID"
        st.success(st.session_state.message)
        st.rerun()

if st.session_state.final_result_status == "INIT": st.info("請點擊左側按鈕開始。"); st.stop()
if st.session_state.final_result_status == "REJECTED": st.error(st.session_state.message); st.stop() 

if query_type == "離婚議題" and gender == "男":
    st.error("⚠️ 規則限制：離婚議題僅限女性命盤。"); st.stop()

# ==============================================================================
# 模式 A: 全盤流年顯示
# ==============================================================================
if st.session_state.current_mode == "FULL":
    full_data = st.session_state.full_life_gua
    st.header("📜 象棋數理 - 全盤流年表")
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
        col_res1.metric("能量淨分 (Score)", f"{net_gain}", status)
        
        exemption = check_exemption(gua)
        if exemption: 
            col_res2.warning(f"特殊格局：{exemption[0]}") 
        else: 
            col_res2.info("格局：平穩發展")
            
        trinity = analyze_trinity_detailed(gua)
        if trinity['missing_heaven']: st.error(f"❌ 缺天：{trinity['missing_heaven']['reason']}")
        if trinity['missing_human']: st.error(f"❌ 缺人：{trinity['missing_human']['reason']}")
        if trinity['missing_earth']: st.error(f"❌ 缺地：{trinity['missing_earth']['reason']}")

        st.markdown("</div>", unsafe_allow_html=True)
    st.warning("⚠️ **71~80歲及晚年：** 需參照餘棋或重新起卦進行專項健康分析。")

# ==============================================================================
# 模式 B: 單卦問事
# ==============================================================================
elif st.session_state.current_mode == "SINGLE":
    current_gua = st.session_state.current_gua
    sub_query = st.session_state.sub_query
    
    analysis_results = calculate_net_gain_from_gua(current_gua) 
    health_analysis = analyze_health_and_luck(current_gua)
    trinity_detailed = analyze_trinity_detailed(current_gua)
    holistic_report = analyze_holistic_health(current_gua)
    coord_report = analyze_coordinate_map(current_gua, gender)
    body_diagnosis = analyze_body_hologram(current_gua)

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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 能量分數", "✨ 格局建議", "🧬 身心診斷", "📍 座標定位"])
    
    with tab1:
        st.subheader("💰 能量互動法則計算 (Score)")
        gain = analysis_results['gain']
        cost = analysis_results['cost']
        net = analysis_results['net_gain']
        c1, c2, c3 = st.columns(3)
        c1.metric("收穫", f"{gain} 分"); c2.metric("付出", f"{cost} 分"); c3.metric("淨利", f"{net} 分", delta_color="normal")
        
        if sub_query == "投資/財運":
            if net > 0: st.success(f"🎉 **獲利判斷：** 淨利 {net} 分，投資可行，獲利機會高！")
            elif net < 0: st.error(f"📉 **風險判斷：** 虧損 {abs(net)} 分，建議觀望或保守。")
            else: st.info("⚖️ **平衡判斷：** 收支平衡。")
        else:
            st.info(f"能量淨值：{net} 分。正分代表運勢上揚，負分代表內耗或阻礙。")
        with st.expander("詳細計算"): st.dataframe(pd.DataFrame(analysis_results['interactions']))
        
    with tab2:
        exemption = check_exemption(current_gua)
        if exemption: st.success(f"特殊格局：{exemption[0]}")
        else: st.info("無特殊格局")
        
        if sub_query == "事業查詢":
            if check_career_pattern(current_gua): st.success("符合事業格！")
        
        for warn in health_analysis['health_warnings']: st.warning(warn)
            
    with tab3:
        if sub_query == "健康分析":
            st.subheader("🏥 中醫五行身心深度診斷")
            st.info("本分析結合中醫五行與心理情緒，找出運勢與健康的『病灶』。")
            
            remedy = health_analysis.get('remedy', {})
            st.markdown(f"#### 1. 整體氣血與調理建議")
            if "Red" in str(remedy) or "血氣旺" in str(remedy.get('status','')):
                st.warning(f"**{remedy['status']}**"); st.write(f"👉 **建議行動：{remedy['method']}**"); st.caption(f"原理：{remedy['principle']}")
            elif "Black" in str(remedy) or "氣血旺" in str(remedy.get('status','')):
                st.info(f"**{remedy['status']}**"); st.write(f"👉 **建議行動：{remedy['method']}**"); st.caption(f"原理：{remedy['principle']}")
            else:
                st.success(f"**{remedy['status']}**：{remedy['advice']}")

            st.markdown("---")
            st.markdown(f"#### 2. 身體部位全息掃描 (鏡像原理)")
            if body_diagnosis:
                st.write("根據卦象，請留意以下部位的不適訊號：")
                for diag in body_diagnosis: st.write(f"- {diag}")
            else: st.success("目前盤面上無顯著的病灶訊號，身體狀況相對平穩。")
            
            st.markdown("---")
            with st.expander("查看深度心理與五行分析"):
                core = holistic_report["core"]
                if core:
                    st.markdown(f"**核心 ({core['name']})：**"); st.write(f"❤️ 心：{core['psycho']}"); st.write(f"🩺 身：{core['physio']}")
                if holistic_report["balance"]["excess"]:
                    st.write("**能量過剩：**"); 
                    for msg in holistic_report["balance"]["excess"]: st.warning(msg)
                if holistic_report["interaction"]:
                    st.write("**致病壓力源：**"); 
                    for msg in holistic_report["interaction"]: st.error(msg)

        else:
            st.subheader("🔍 天地人三才缺失檢測")
            cols = st.columns(3)
            if trinity_detailed['missing_heaven']:
                with cols[0]:
                    st.error("❌ 缺天 (無上格)"); st.markdown(f"**特質：** {trinity_detailed['missing_heaven']['desc']}"); with st.expander("💡 化解建議"): st.write(trinity_detailed['missing_heaven']['advice'])
            else: cols[0].success("✅ 天格穩固")

            if trinity_detailed['missing_human']:
                with cols[1]:
                    st.error("❌ 缺人 (無中格)"); st.markdown(f"**特質：** {trinity_detailed['missing_human']['desc']}"); with st.expander("💡 化解建議"): st.write(trinity_detailed['missing_human']['advice'])
            else: cols[1].success("✅ 人格穩固")

            if trinity_detailed['missing_earth']:
                with cols[2]:
                    st.error("❌ 缺地 (無下格)"); st.markdown(f"**特質：** {trinity_detailed['missing_earth']['desc']}"); with st.expander("💡 化解建議"): st.write(trinity_detailed['missing_earth']['advice'])
            else: cols[2].success("✅ 地格穩固")

            if sub_query == "前世格局":
                 piece_1 = next(p for p in current_gua if p[0] == 1)
                 st.write(f"前世身分參考：{piece_1[1]}")
            elif sub_query == "離婚議題" and gender == "女":
                 st.warning("請留意好朋友格在2-3或4-5的影響。")

    with tab4:
        st.subheader("🗺️ 五支棋座標地圖 (位置決定角色)")
        st.info("此分析結合了「天地人」垂直軸線與「性別對應」水平軸線，精準定位問題來源。")
        st.markdown("#### 1. 垂直軸線：命運的承載力")
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1: st.markdown("**☁️ 上格 (天/長輩)**"); st.write(coord_report["top_support"])
        with col_v2: st.markdown("**👤 中格 (人/核心)**"); st.write(coord_report["center_status"])
        with col_v3: st.markdown("**⛰️ 下格 (地/結果)**"); st.write(coord_report["bottom_foundation"])
        st.markdown("---")
        st.markdown(f"#### 2. 水平軸線：人生的際遇力 (問卜者：{gender})")
        col_h1, col_h2 = st.columns(2)
        left_role = "妻/女友 (異性位)" if gender == "男" else "姊妹/女同事 (同性位)"
        with col_h1: st.markdown(f"**👈 左格 (2) - {left_role}**"); st.write(coord_report["love_relationship"] if gender == "男" else coord_report["peer_relationship"])
        right_role = "兄弟/男同事 (同性位)" if gender == "男" else "夫/男友 (異性位)"
        with col_h2: st.markdown(f"**👉 右格 (3) - {right_role}**"); st.write(coord_report["peer_relationship"] if gender == "男" else coord_report["love_relationship"])
        with st.expander("💡 諮詢師的實務應用 SOP"): st.markdown("1. 先看 **中格**，確認狀態與能力。\n2. 再看 **上格**，確認長官挺不挺。\n3. 接著看 **下格**，確認結果有沒有「根」。\n4. 最後看 **左右**，精準定位貴人與小人。")
