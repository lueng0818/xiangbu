import streamlit as st
import pandas as pd
import time
import os
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
from rules import (generate_random_gua, generate_full_life_gua, check_exemption, 
                   calculate_score_by_mode, analyze_health_and_luck, is_all_same_color, 
                   get_marketing_strategy, get_past_life_reading, get_advanced_piece_analysis,
                   calculate_net_gain_from_gua, analyze_trinity_detailed, analyze_holistic_health,
                   analyze_coordinate_map, analyze_body_hologram, check_career_pattern, check_consumption_at_1_or_5)

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

st.set_page_config(page_title="專業象棋占卜系統 - 全盤流年版", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
h1 {color: #B22222; font-family: 'serif'; text-shadow: 1px 1px 2px #000000;}
h2, h3 {color: #C0C0C0; border-left: 5px solid #8B0000; padding-left: 15px; margin-top: 20px;}
.stage-box {border: 1px solid #444; padding: 10px; margin-bottom: 20px; border-radius: 5px; background-color: #262730;}
.sop-box {background-color: #2b303b; padding: 15px; border-left: 4px solid #ff4b4b; margin-top: 15px; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

st.title("🔮 專業象棋占卜系統：洞悉棋局，掌握人生格局")
st.markdown("---")

if 'reroll_count' not in st.session_state: st.session_state.reroll_count = 0
if 'final_result_status' not in st.session_state: st.session_state.final_result_status = "INIT"
if 'current_mode' not in st.session_state: st.session_state.current_mode = "SINGLE"
if 'sub_query' not in st.session_state: st.session_state.sub_query = "問運勢"
if 'message' not in st.session_state: st.session_state.message = ""
if 'current_gua' not in st.session_state: st.session_state.current_gua = []

with st.sidebar:
    st.header("天機奧秘，誠心求卜")
    st.warning("**1. 態度為先**：請保持尊重及恭敬。\n**2. 不成卦**：兩次全黑/全紅，暗示不可為。\n**3. 醫療免責**：僅供養生參考，不取代醫療。")
    gender = st.selectbox("1. 詢問性別", ["男", "女"])
    
    st.header("2. 選擇占卜模式")
    with st.container():
        st.subheader("🅰️ 全盤流年 (一生大運)")
        if st.button("🚀 排布全盤流年", type="primary"):
            st.session_state.current_mode = "FULL"
            with st.spinner('正在洗牌、切牌、排布全盤流年...'):
                time.sleep(1.5)
                st.session_state.full_life_gua = generate_full_life_gua()
                st.session_state.final_result_status = "VALID"
            st.rerun()

    st.markdown("---")
    with st.container():
        st.subheader("🅱️ 單卦問事 (特定問題)")
        current_sub_query_selection = st.selectbox("選擇問題類別", ["問運勢", "事業查詢", "前世格局", "健康分析", "投資/財運", "感情/關係", "離婚議題"])
        if current_sub_query_selection == "投資/財運": st.date_input("預計獲利時間點", value=None)
        if st.button("🔮 開始單卦占卜"):
            st.session_state.current_mode = "SINGLE"
            st.session_state.sub_query = current_sub_query_selection
            new_gua = generate_random_gua()
            if is_all_same_color(new_gua):
                st.session_state.reroll_count += 1
                if st.session_state.reroll_count == 1:
                    with st.spinner('不成卦，系統自動重抽中...'): time.sleep(1); new_gua = generate_random_gua()
                    if is_all_same_color(new_gua):
                        st.session_state.current_gua = new_gua; st.session_state.message = "❌ 兩次不成卦。"; st.session_state.final_result_status = "REJECTED"
                    else:
                        st.session_state.current_gua = new_gua; st.session_state.message = "🚨 重抽成功。"; st.session_state.final_result_status = "VALID"
                else: st.session_state.final_result_status = "REJECTED" 
            else:
                st.session_state.current_gua = new_gua; st.session_state.reroll_count = 0; st.session_state.final_result_status = "VALID"
            st.rerun()

if st.session_state.final_result_status == "INIT": st.info("👈 請在左側側邊欄選擇模式開始。"); st.stop()
if st.session_state.final_result_status == "REJECTED": st.error(st.session_state.message); st.stop() 
if st.session_state.current_mode == "SINGLE" and st.session_state.sub_query == "離婚議題" and gender == "男": st.error("⚠️ 規則限制：離婚議題僅限女性。"); st.stop()

if st.session_state.current_mode == "FULL":
    full_data = st.session_state.full_life_gua
    st.header("📜 象棋數理 - 全盤流年表")
    life_stages = ["11~20歲", "21~30歲", "31~40歲", "41~50歲", "51~60歲", "61~70歲"]
    for stage in life_stages:
        gua = full_data[stage]
        analysis = calculate_score_by_mode(gua, "general")
        st.markdown(f"<div class='stage-box'>", unsafe_allow_html=True)
        st.markdown(f"### 🗓️ {stage} 運勢")
        c1, c2, c3 = st.columns([1, 1, 1]); 
        with c2: display_piece(gua, 4)
        c4, c5, c6 = st.columns([1, 1, 1]); 
        with c4: display_piece(gua, 2); with c5: display_piece(gua, 1); with c6: display_piece(gua, 3)
        c7, c8, c9 = st.columns([1, 1, 1]); 
        with c8: display_piece(gua, 5)
        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        col_res1.metric("能量淨分", f"{analysis['net_score']}", analysis['interpretation'])
        exemption = check_exemption(gua)
        if exemption: col_res2.warning(f"特殊格局：{exemption[0]}") 
        else: col_res2.info("格局：平穩發展")
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.current_mode == "SINGLE":
    current_gua = st.session_state.current_gua
    sub_query = st.session_state.sub_query
    
    mode_map = {"問運勢":"general","事業查詢":"career","前世格局":"karma","健康分析":"health","投資/財運":"investment","感情/關係":"love","離婚議題":"divorce"}
    score_report = calculate_score_by_mode(current_gua, mode=mode_map.get(sub_query,"general"))
    piece_analysis = get_advanced_piece_analysis(current_gua)
    health_analysis = analyze_health_and_luck(current_gua)
    trinity_detailed = analyze_trinity_detailed(current_gua)
    holistic_report = analyze_holistic_health(current_gua)
    body_diagnosis = analyze_body_hologram(current_gua)

    st.header(f"✅ 單卦解析：{sub_query}")
    col_u1, col_u2, col_u3 = st.columns([1, 1, 1]); 
    with col_u2: display_piece(current_gua, 4)
    col_m1, col_m2, col_m3 = st.columns([1, 1, 1]); 
    with col_m1: display_piece(current_gua, 2); with col_m2: display_piece(current_gua, 1); with col_m3: display_piece(current_gua, 3)
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1]); 
    with col_d2: display_piece(current_gua, 5)

    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["📊 能量分析", "✨ 格局與建議", "🧬 深度解讀"])
    
    with tab1:
        st.subheader("💰 能量量化計分")
        c1, c2, c3 = st.columns(3)
        c1.metric(score_report["label_A"], f"{score_report['score_A']}"); c2.metric(score_report["label_B"], f"{score_report['score_B']}"); c3.metric(score_report["label_Net"], f"{score_report['net_score']}", delta_color="normal")
        st.info(score_report["interpretation"])
        if sub_query == "健康分析" and score_report['health_status']: st.write(score_report['health_status'])
        with st.expander("詳細計算過程"):
            st.write(f"➕ {score_report['label_A']}:", score_report['details_A'])
            st.write(f"➖ {score_report['label_B']}:", score_report['details_B'])

    with tab2:
        st.markdown("<div class='sop-box'>", unsafe_allow_html=True)
        if sub_query == "事業查詢":
            st.markdown("#### 💡 事業成交 SOP")
            st.write(get_marketing_strategy(current_gua))
            st.markdown(f"**棋子特質：** {piece_analysis['career_desc']}")
        elif sub_query == "投資/財運":
            st.markdown("#### 💡 投資 SOP")
            if check_consumption_at_1_or_5(current_gua): st.error("⚠️ 下格不穩，錢留不住。")
            else: st.success("下格穩固。")
        elif sub_query == "健康分析":
            st.markdown("#### 💡 養生 SOP")
            remedy = health_analysis['remedy']
            st.write(f"**調理建議：** {remedy['method']} ({remedy['advice']})")
        else:
            st.markdown("#### 💡 通用建議")
            st.write(f"**當下狀態：** {piece_analysis['self_desc']}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        exemption = check_exemption(current_gua)
        if exemption: st.success(f"特殊格局：{exemption[0]}")

    with tab3:
        if sub_query == "前世格局":
            karma = get_past_life_reading(current_gua)
            st.subheader("📜 前世今生解讀")
            st.markdown(f"**前世身分：** {karma['role']}")
            for rel in karma['relations']: st.write(f"- {rel}")
        elif sub_query == "健康分析":
            st.error("⚠️ **醫療免責：** 僅供養生參考。")
            st.subheader("全息身體診斷")
            if body_diagnosis:
                for d in body_diagnosis: st.write(f"- {d}")
            else: st.success("無明顯病灶訊號。")
            with st.expander("深度身心分析"):
                core = holistic_report["core"]
                if core: st.markdown(f"**核心：** {core['name']} ({core['element']})\n{core['psycho']}")
        else:
            st.subheader("🔍 三才缺失檢測")
            if trinity_detailed['missing_heaven']: st.error("❌ 缺天"); st.caption(trinity_detailed['missing_heaven']['reason'])
            else: st.success("✅ 天格穩固")
            if trinity_detailed['missing_human']: st.error("❌ 缺人"); st.caption(trinity_detailed['missing_human']['reason'])
            else: st.success("✅ 人格穩固")
            if trinity_detailed['missing_earth']: st.error("❌ 缺地"); st.caption(trinity_detailed['missing_earth']['reason'])
            else: st.success("✅ 地格穩固")
