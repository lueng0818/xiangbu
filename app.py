import streamlit as st
import pandas as pd
import time
import os
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
# 導入所有邏輯函數
from rules import generate_random_gua, generate_full_life_gua, check_exemption, calculate_net_gain_from_gua, analyze_health_and_luck, is_all_same_color, check_career_pattern, check_wealth_pattern, check_consumption_at_1_or_5, check_interference, analyze_trinity_detailed, analyze_holistic_health, analyze_coordinate_map, analyze_body_hologram, calculate_score_by_mode, get_advanced_piece_analysis, get_marketing_strategy, get_past_life_reading

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
.sop-box {background-color: #2b303b; padding: 15px; border-left: 4px solid #ff4b4b; margin-top: 15px; border-radius: 4px;}
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
    st.markdown("### ⚠️ 占卜前重要須知")
    st.warning("""
        **1. 態度為先**：請保持尊重及恭敬。
        **2. 不成卦**：兩次全黑/全紅，暗示不可為。
        **3. 醫療免責**：本分析僅供養生參考，不可取代醫療診斷。
    """)
    
    st.markdown("---")
    st.header("1. 基本資料")
    gender = st.selectbox("詢問性別", ["男", "女"])
    
    st.markdown("---")
    
    # === 雙模式並列顯示 ===
    st.header("2. 選擇占卜模式")
    
    with st.container():
        st.subheader("🅰️ 全盤流年 (一生大運)")
        st.info("使用完整32支棋，排布11~80歲人生架構。")
        if st.button("🚀 排布全盤流年", type="primary"):
            st.session_state.current_mode = "FULL"
            with st.spinner('正在洗牌、切牌、排布全盤流年...'):
                time.sleep(1.5)
                st.session_state.full_life_gua = generate_full_life_gua()
                st.session_state.final_result_status = "VALID"
                st.session_state.message = "全盤流年排佈完成！"
            st.rerun()

    st.markdown("---")

    with st.container():
        st.subheader("🅱️ 單卦問事 (特定問題)")
        current_sub_query_selection = st.selectbox(
            "選擇問題類別", 
            ["問運勢", "事業查詢", "前世格局", "健康分析", "投資/財運", "感情/關係", "離婚議題"]
        )
        if current_sub_query_selection == "投資/財運":
            st.date_input("預計獲利時間點", value=None)
            
        if st.button("🔮 開始單卦占卜"):
            st.session_state.current_mode = "SINGLE"
            st.session_state.sub_query = current_sub_query_selection
            new_gua = generate_random_gua()
            if is_all_same_color(new_gua):
                st.session_state.reroll_count += 1
                if st.session_state.reroll_count == 1:
                    with st.spinner('不成卦，系統自動重抽中...'): 
                        time.sleep(1)
                        new_gua = generate_random_gua()
                    if is_all_same_color(new_gua):
                        st.session_state.current_gua = new_gua; st.session_state.message = "❌ 兩次不成卦，暗示「不會做也不會成」。"; st.session_state.final_result_status = "REJECTED"
                    else:
                        st.session_state.current_gua = new_gua; st.session_state.message = "🚨 第一次不成卦，已自動重抽並成功。"; st.session_state.final_result_status = "VALID"
                else:
                     st.session_state.message = "請刷新頁面重試。"; st.session_state.final_result_status = "REJECTED" 
            else:
                st.session_state.current_gua = new_gua; st.session_state.reroll_count = 0; st.session_state.message = "卦象生成成功。"; st.session_state.final_result_status = "VALID"
            st.rerun()

# ----------------------------------------------
# 主頁面顯示邏輯
# ----------------------------------------------
if st.session_state.final_result_status == "INIT": st.info("👈 請在左側側邊欄選擇 **「全盤流年」** 或 **「單卦問事」** 開始。"); st.stop()
if st.session_state.final_result_status == "REJECTED": st.error(st.session_state.message); st.stop() 

if st.session_state.current_mode == "SINGLE" and st.session_state.sub_query == "離婚議題" and gender == "男":
    st.error("⚠️ **規則限制：** 根據象棋占卜秘笈，**離婚議題只能解析女性的命盤**。"); 
    st.warning("請將左側的「詢問性別」選項改為**『女』**，或選擇其他相關的感情議題。"); 
    st.stop()

# ==============================================================================
# 模式 A: 全盤流年顯示 (修復排版錯誤)
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
        coord_report = analyze_coordinate_map(gua, gender)
        st.markdown(f"<div class='stage-box'>", unsafe_allow_html=True)
        st.markdown(f"### 🗓️ {stage} 運勢")
        
        # --- 修正後的排版 (正確分行) ---
        c1, c2, c3 = st.columns([1, 1, 1])
        with c2: 
            display_piece(gua, 4)
            
        c4, c5, c6 = st.columns([1, 1, 1])
        with c4: 
            display_piece(gua, 2)
        with c5: 
            display_piece(gua, 1)
        with c6: 
            display_piece(gua, 3)
            
        c7, c8, c9 = st.columns([1, 1, 1])
        with c8: 
            display_piece(gua, 5)
        # -------------------------------

        st.markdown("---")
        col_res1, col_res2 = st.columns(2)
        net_gain = analysis['net_gain']
        status = "運勢強勁 🚀" if net_gain > 0 else "需保守沈潛 🛡️"
        col_res1.metric("能量淨分 (Score)", f"{net_gain}", status)
        
        exemption = check_exemption(gua)
        if exemption: 
            col_res2.warning(f"特殊格局：{exemption[0]} (影響{POSITION_MAP[exemption[1]]['名稱']})") 
        else: 
            col_res2.info("格局：平穩發展")
            
        trinity = analyze_trinity_detailed(gua)
        if trinity['missing_heaven']: st.error(f"❌ 缺天：{trinity['missing_heaven']['reason']}")
        if trinity['missing_human']: st.error(f"❌ 缺人：{trinity['missing_human']['reason']}")
        if trinity['missing_earth']: st.error(f"❌ 缺地：{trinity['missing_earth']['reason']}")
        st.markdown("</div>", unsafe_allow_html=True)
    st.warning("⚠️ **71~80歲及晚年：** 需參照餘棋或重新起卦進行專項健康分析。")

# ==============================================================================
# 模式 B: 單卦問事 (修復排版錯誤)
# ==============================================================================
elif st.session_state.current_mode == "SINGLE":
    current_gua = st.session_state.current_gua
    sub_query = st.session_state.sub_query
    
    # 執行所有分析
    analysis_results = calculate_net_gain_from_gua(current_gua) 
    health_analysis = analyze_health_and_luck(current_gua)
    trinity_detailed = analyze_trinity_detailed(current_gua)
    holistic_report = analyze_holistic_health(current_gua)
    coord_report = analyze_coordinate_map(current_gua, gender)
    body_diagnosis = analyze_body_hologram(current_gua)
    
    mode_map = {"問運勢":"general","事業查詢":"career","前世格局":"karma","健康分析":"health","投資/財運":"investment","感情/關係":"love","離婚議題":"divorce"}
    score_report = calculate_score_by_mode(current_gua, mode=mode_map.get(sub_query,"general"))
    piece_analysis = get_advanced_piece_analysis(current_gua)

    st.header(f"✅ 單卦解析：{sub_query}")
    
    # --- 修正後的排版 (正確分行) ---
    col_u1, col_u2, col_u3 = st.columns([1, 1, 1])
    with col_u2: 
        display_piece(current_gua, 4)
        
    col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
    with col_m1: 
        display_piece(current_gua, 2)
    with col_m2: 
        display_piece(current_gua, 1)
    with col_m3: 
        display_piece(current_gua, 3)
        
    col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
    with col_d2: 
        display_piece(current_gua, 5)
    # -------------------------------

    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 能量分數", "✨ 格局與建議", "🧬 深度解讀", "📍 座標定位"])
    
    # Tab 1
    with tab1:
        st.subheader("💰 能量量化計分")
        c1, c2, c3 = st.columns(3)
        c1.metric(score_report["label_A"], f"{score_report['score_A']} 分")
        c2.metric(score_report["label_B"], f"{score_report['score_B']} 分")
        c3.metric(score_report["label_Net"], f"{score_report['net_score']} 分", delta_color="normal")
        
        if score_report["net_score"] > 0: st.success(score_report["interpretation"])
        elif score_report["net_score"] < 0: st.error(score_report["interpretation"])
        else: st.info(score_report["interpretation"])
            
        with st.expander("查看詳細計分過程"):
            c_left, c_right = st.columns(2)
            with c_left:
                st.markdown(f"**➕ {score_report['label_A']}**"); 
                for d in score_report["details_A"]: st.write(f"- {d}")
            with c_right:
                st.markdown(f"**➖ {score_report['label_B']}**"); 
                for d in score_report["details_B"]: st.write(f"- {d}")

    # Tab 2
    with tab2:
        st.subheader(f"🎭 您的當下角色：{piece_analysis['role_title']}")
        st.info(f"**狀態解析：** {piece_analysis['self_desc']}")
        for warn in piece_analysis["special_warnings"]: st.warning(warn)
        st.markdown("---")
        exemption = check_exemption(current_gua)
        if exemption: st.success(f"特殊格局：{exemption[0]}")
        else: st.info("無特殊格局")
        
        st.markdown("<div class='sop-box'>", unsafe_allow_html=True)
        if sub_query == "問運勢":
            st.markdown("#### 💡 運勢諮詢 SOP")
            red_c = health_analysis['red_count']; black_c = health_analysis['black_count']
            if (red_c==2 and black_c==3) or (red_c==3 and black_c==2): st.success("✅ **二三配：** 情緒最穩。")
            else: st.warning("⚠️ **一四配/全色：** 情緒起伏大。")
        elif sub_query == "事業查詢":
            st.markdown("#### 💡 事業諮詢 SOP")
            st.write(get_marketing_strategy(current_gua))
            st.markdown(f"**棋子特質：** {piece_analysis['career_desc']}")
            if check_career_pattern(current_gua): st.success("🏆 **事業格 (車馬包)**")
        elif sub_query == "投資/財運":
            st.markdown("#### 💡 投資 SOP")
            if check_consumption_at_1_or_5(current_gua): st.error("⚠️ 下格不穩，錢留不住。")
            else: st.success("下格穩固。")
        elif sub_query == "感情/關係":
            st.markdown("#### 💡 感情諮詢 SOP")
            st.markdown(f"**棋子特質建議：** {piece_analysis['love_desc']}")
        elif sub_query == "健康分析":
            st.markdown("#### 💡 養生 SOP")
            remedy = health_analysis['remedy']
            st.write(f"**調理建議：** {remedy['method']} ({remedy['advice']})")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        for warn in health_analysis['health_warnings']: st.warning(warn)

    # Tab 3
    with tab3:
        if sub_query == "健康分析":
            st.error("⚠️ **醫療免責：** 僅供養生參考。")
            st.subheader("全息身體診斷")
            if body_diagnosis:
                for d in body_diagnosis: st.write(f"- {d}")
            else: st.success("無明顯病灶訊號。")
            with st.expander("深度身心分析"):
                core = holistic_report["core"]
                if core: st.markdown(f"**核心：** {core['name']} ({core['element']})\n{core['psycho']}")
        elif sub_query == "前世格局":
            karma = get_past_life_reading(current_gua)
            st.subheader("📜 前世今生解讀")
            st.markdown(f"**前世身分：** {karma['role']}")
            for rel in karma['relations']: st.write(f"- {rel}")
        else:
            st.subheader("🔍 三才缺失檢測")
            cols = st.columns(3)
            if trinity_detailed['missing_heaven']:
                with cols[0]: st.error("❌ 缺天"); st.caption(trinity_detailed['missing_heaven']['reason'])
            else: cols[0].success("✅ 天格穩固")
            if trinity_detailed['missing_human']:
                with cols[1]: st.error("❌ 缺人"); st.caption(trinity_detailed['missing_human']['reason'])
            else: cols[1].success("✅ 人格穩固")
            if trinity_detailed['missing_earth']:
                with cols[2]: st.error("❌ 缺地"); st.caption(trinity_detailed['missing_earth']['reason'])
            else: cols[2].success("✅ 地格穩固")
            
            if sub_query == "離婚議題" and gender == "女":
                 st.warning("請留意好朋友格在2-3或4-5的影響。")

    # Tab 4
    with tab4:
        st.subheader("🗺️ 五支棋座標地圖")
        col_v1, col_v2, col_v3 = st.columns(3)
        with col_v1: st.markdown("**☁️ 上格**"); st.write(coord_report["top_support"])
        with col_v2: st.markdown("**👤 中格**"); st.write(coord_report["center_status"])
        with col_v3: st.markdown("**⛰️ 下格**"); st.write(coord_report["bottom_foundation"])
        st.markdown("---")
        col_h1, col_h2 = st.columns(2)
        with col_h1: st.markdown("**👈 左格**"); st.write(coord_report["love_relationship"] if gender == "男" else coord_report["peer_relationship"])
        with col_h2: st.markdown("**👉 右格**"); st.write(coord_report["peer_relationship"] if gender == "男" else coord_report["love_relationship"])
