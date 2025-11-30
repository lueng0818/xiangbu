import streamlit as st
import pandas as pd
import time
import os
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
from rules import generate_random_gua, check_exemption, calculate_net_gain_from_gua, analyze_health_and_luck, is_all_same_color, check_career_pattern, check_wealth_pattern, check_consumption_at_1_or_5, check_interference

# ----------------------------------------------
# 輔助函數
# ----------------------------------------------
def display_piece(gua_data, pos_num):
    """輔助函數：用於顯示單個棋子的圖片和位置信息"""
    piece = next(p for p in gua_data if p[0] == pos_num)
    name, color = piece[1], piece[2]
    image_path = get_image_path(name, color) 
    
    st.markdown(f"<p style='text-align: center; font-size: 14px; margin-bottom: 0;'>{POSITION_MAP[pos_num]['名稱']} ({pos_num})</p>", unsafe_allow_html=True)
    
    # 檢查圖片是否存在，防止報錯
    if image_path and os.path.exists(image_path):
        st.image(image_path, caption=f"{color}{name}", width=90) 
    else:
        st.warning(f"圖缺: {color}{name}")

    st.markdown(f"<p style='text-align: center; font-size: 10px;'>{POSITION_MAP[pos_num]['關係']}</p>", unsafe_allow_html=True)

# ----------------------------------------------
# 頁面配置與自定義 CSS
# ----------------------------------------------
st.set_page_config(
    page_title="專業象棋占卜系統 - 象卜",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
#MainMenu {visibility: hidden;} footer {visibility: hidden;}
h1 {color: #B22222; font-family: 'serif'; text-shadow: 1px 1px 2px #000000;}
h2, h3 {color: #C0C0C0; border-left: 5px solid #8B0000; padding-left: 15px; margin-top: 20px;}
</style>
""", unsafe_allow_html=True)

st.title("🔮 專業象棋占卜系統：洞悉棋局，掌握人生格局")
st.markdown("---")

# ----------------------------------------------
# 側邊欄控制與輸入
# ----------------------------------------------
if 'reroll_count' not in st.session_state: st.session_state.reroll_count = 0
if 'final_result_status' not in st.session_state: st.session_state.final_result_status = "INIT"
if 'message' not in st.session_state: st.session_state.message = ""

with st.sidebar:
    st.header("天機奧秘，誠心求卜")
    
    st.markdown("### ⚠️ 占卜前重要須知")
    st.warning("""
        **1. 態度為先：** 象棋卜卦磁場強大，請在提問時保持**尊重及恭敬**。
        **2. 不成卦規則：** 卦象二次仍不成，暗示**「不會做也不會成」**。
    """)
    st.markdown("---")
    
    gender = st.selectbox("1. 詢問性別", ["男", "女"])
    
    query_type = st.selectbox(
        "2. 詢問類型", 
        [
            "解全盤 (11 步綜合解析)", 
            "問運勢", 
            "事業查詢", 
            "前世格局、關係", 
            "健康分析", 
            "投資/財運", 
            "感情/關係",
            "離婚議題"
        ]
    )
    
    if query_type == "投資/財運":
        st.info("💡 **重要：** 財運占卜必須有時間依據。")
        st.date_input("3. 請輸入預計**獲利或事件發生的時間點**", value=None)
    
    if st.button("開始占卜：擲出五支棋"):
        new_gua = generate_random_gua()
        if is_all_same_color(new_gua):
            st.session_state.reroll_count += 1
            if st.session_state.reroll_count == 1:
                with st.spinner('偵測到不成卦 (全黑/全紅)，正在進行第二次重抽...'): 
                    time.sleep(1)
                    new_gua = generate_random_gua()
                if is_all_same_color(new_gua):
                    st.session_state.current_gua = new_gua
                    st.session_state.message = "❌ **最終警示：** 卦象連續兩次為全黑/全紅，暗示**「不會做也不會成」**。本次分析已中止。"
                    st.session_state.final_result_status = "REJECTED"
                else:
                    st.session_state.current_gua = new_gua
                    st.session_state.message = "🚨 第一次卦象為全黑/全紅，已重抽成功並得到有效卦象。"
                    st.session_state.final_result_status = "VALID"
            else:
                 st.session_state.message = "請刷新頁面或清除緩存後，重新開始占卜。"
                 st.session_state.final_result_status = "REJECTED" 
        else:
            st.session_state.current_gua = new_gua
            st.session_state.reroll_count = 0
            st.session_state.message = "卦象已成功生成。"
            st.session_state.final_result_status = "VALID"

        st.success(st.session_state.message)
        # 【修正點】使用 st.rerun() 取代 st.experimental_rerun()
        st.rerun()


# ----------------------------------------------
# 主頁面流程控制與守衛
# ----------------------------------------------
if st.session_state.final_result_status == "INIT": st.info("請在左側邊欄輸入資訊，並點擊按鈕開始您的卦象解析。"); st.stop()
if st.session_state.final_result_status == "REJECTED": st.error(st.session_state.message); st.stop() 

if query_type == "離婚議題" and gender == "男":
    st.error("⚠️ **規則限制：** 根據象棋占卜秘笈，**離婚議題只能解析女性的命盤**。"); st.warning("請將左側的「詢問性別」選項改為**『女』**，或選擇其他相關的感情議題。"); st.stop()

# ----------------------------------------------
# 有效卦象分析 (VALID)
# ----------------------------------------------
current_gua = st.session_state.current_gua
analysis_results = calculate_net_gain_from_gua(current_gua) 
health_analysis = analyze_health_and_luck(current_gua)

st.header("✅ 當前卦象與核心能量場")
# 視覺化排布
col_u1, col_u2, col_u3 = st.columns([1, 1, 1])
with col_u2: display_piece(current_gua, 4)
col_m1, col_m2, col_m3 = st.columns([1, 1, 1])
with col_m1: display_piece(current_gua, 2)
with col_m2: display_piece(current_gua, 1)
with col_m3: display_piece(current_gua, 3)
col_d1, col_d2, col_d3 = st.columns([1, 1, 1])
with col_d2: display_piece(current_gua, 5)

st.markdown("---")

# ----------------------------------------------
# 數據分頁呈現 (Tabs)
# ----------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 總收穫與付出", "✨ 格局與特質分析", "🧬 健康與關係"])

# Tab 1: 總收穫與付出
with tab1:
    st.header(f"⚖️ {query_type} 總結：收穫與付出")
    col_g, col_c, col_n = st.columns(3)
    col_g.metric("總收穫 (Gain)", f"{analysis_results['gain']}", "棋力價值")
    col_c.metric("總付出 (Cost)", f"{analysis_results['cost']}", "行動與運作成本")
    col_n.metric("最終淨盈餘/虧損", f"{analysis_results['net_gain']}", 
                 delta="獲利" if analysis_results['net_gain'] > 0 else "虧損")
    
    if query_type == "投資/財運":
        if analysis_results['net_gain'] > 0: st.success("🎉 **恭喜！** 收穫大於付出，投資獲利機會高。")
        else: st.error("⚠️ **提醒！** 付出大於收穫，建議謹慎。")
    
    with st.expander("🛠️ 詳細吃子與續攻計算"):
        interactions_df = pd.DataFrame(analysis_results['interactions'])
        if not interactions_df.empty:
            interactions_df['結果'] = interactions_df.apply(lambda row: "全吃" if row['is_full_eat'] else "半吃", axis=1)
            interactions_df['eater_pos_name'] = interactions_df['eater_pos'].apply(lambda x: POSITION_MAP[x]['名稱'])
            interactions_df['target_pos_name'] = interactions_df['target_pos'].apply(lambda x: POSITION_MAP[x]['名稱'])
            st.dataframe(interactions_df[['eater_name', 'eater_pos_name', 'target_name', 'target_pos_name', '結果', 'value']], use_container_width=True)
        else:
            st.info("棋子間無有效的吃子或能量流動。")


# Tab 2: 格局與特質分析
with tab2:
    st.header("✨ 特殊格局解析")
    
    # I. 問運勢專項解析
    if query_type == "問運勢":
        st.subheader("☀️ 當前運勢總結與分析")
        red_count = health_analysis['red_count']
        black_count = health_analysis['black_count']
        st.markdown("**1. 氣血與情緒狀態 (@運勢解法)**")
        if (red_count == 2 and black_count == 3) or (red_count == 3 and black_count == 2): st.success("🎉 **二三配/三二配：** 情緒穩定，快樂指數高！")
        elif (red_count == 1 and black_count == 4) or (red_count == 4 and black_count == 1): st.warning("🚨 **一四配/四一配：** 情緒起伏較大，需留意心境調整。")
        else: st.info("棋色比例中等，情緒穩定度中等。")

        net_gain = analysis_results['net_gain']
        st.markdown("**2. 能量流動與總 Outlook**")
        if net_gain > 5.0: st.success(f"🚀 **運勢強勁：** 淨收穫 {net_gain}，能量磁場強大，可大膽前進！")
        elif net_gain < -5.0: st.error(f"📉 **運勢低迷：** 淨虧損 {abs(net_gain)}，需保守行事，防範消耗格影響。")
        else: st.info("運勢平穩，重點在於人際關係與特定格局。")
             
        st.markdown("---")
        st.subheader("⚠️ 運勢中的潛在格局")
        exemption = check_exemption(current_gua)
        if exemption: st.error(f"主要干擾/助力格局：{exemption[0]}")
        
        if check_career_pattern(current_gua): st.success("運勢中帶有事業衝勁 (車傌包)。")
        if check_wealth_pattern(current_gua): st.success("運勢中帶有貴人相助 (將士相)。")

    # II. 事業查詢專項解析
    elif query_type == "事業查詢":
        st.subheader("💼 核心事業格局分析")
        is_career = check_career_pattern(current_gua)
        if is_career: st.success("🎉 **恭喜！** 卦象偵測到**事業格 (車傌包)**！"); st.markdown("👉 **結論：** 具有做事業的氣勢，敢衝、能量磁場強。但需注意，此格局**不利感情卦**。")
        else: st.info("卦象未偵測到事業格。")
        is_wealth = check_wealth_pattern(current_gua)
        if is_wealth: st.success("💰 **富貴格 (將士相)：** 有人幫做事，自己行動力弱。");
        else: st.info("未偵測到富貴格。")

    # III. 通用格局檢查
    else:
        exemption = check_exemption(current_gua)
        if exemption: st.success(f"**🎉 偵測到重要格局：** {exemption[0]}！")
        else: st.info("未偵測到特殊格局。")
        
        st.markdown("---")
        st.subheader("💡 棋子特質與運勢建議")
        gua_data = [(p[2], p[1], ATTRIBUTES.get(p[1], {}).get('特質', '')) for p in current_gua]
        gua_df = pd.DataFrame(gua_data, columns=['顏色', '棋子', '特質解析'])
        st.table(gua_df)

# Tab 3: 健康與關係
with tab3:
    st.header("🧬 健康與關係總評")
    
    # I. 天地人三才與貴人運
    st.subheader("🍀 天地人三才與貴人運")
    trinity_cols = st.columns(3)
    if not any(p[0] == 4 for p in current_gua): trinity_cols[0].error("缺天 (長輩)：較鐵齒，需多與長輩維持好關係。")
    else: trinity_cols[0].success("天格穩固")
    if not any(p[0] in [1, 2, 3] for p in current_gua): trinity_cols[1].error("缺人 (平輩)：易目中無人，人和較弱。")
    else: trinity_cols[1].success("人格穩固")
    if not any(p[0] == 5 for p in current_gua): trinity_cols[2].error("缺地 (晚輩/踏實感)：缺乏踏實感，錢留不住，建議穩定投資。")
    else: trinity_cols[2].success("地格穩固")
        
    st.markdown("---")

    # II. 離婚格局解析 (僅限女性/離婚議題)
    if query_type == "離婚議題" and gender == "女":
        st.subheader("💔 離婚格局專項檢查 (女性命盤)")
        piece_1_name = next(p[1] for p in current_gua if p[0] == 1)
        divorce_pieces = ['將', '帥', '黑士', '黑車']
        if piece_1_name in divorce_pieces or any(p[1] in ['將', '帥'] for p in current_gua):
            st.error(f"⚠️ **高風險警示：** 中間 ({piece_1_name}) 或總格出現將帥/黑士/黑車，易導致關係強勢或出現問題。")
        else: st.success("核心棋子穩定，無明顯離婚高風險特質。")
        st.write("👉 **好朋友格在 2-3 或 4-5：** 需留意關係的過度平淡或聚少離多。")

    # III. 感情/關係格局解析 (通用情感)
    elif query_type == "感情/關係":
        st.subheader("💖 感情與關係格局解析")
        pao_bao_pieces = [p for p in current_gua if p[1] in ['炮', '包']]
        if pao_bao_pieces:
            pao_bao_info = [f"{p[2]}{p[1]} (位: {POSITION_MAP[p[0]]['名稱']})" for p in pao_bao_pieces]
            st.success(f"🎉 **桃花/人緣旺：** 卦象中出現 {len(pao_bao_pieces)} 支炮/包棋子 ({', '.join(pao_bao_info)})。")
        else: st.info("桃花/人緣能量較為平穩。")
        
        piece_2 = next(p for p in current_gua if p[0] == 2); piece_3 = next(p for p in current_gua if p[0] == 3)
        is_friend_2_3 = (piece_2[1] in ['炮', '包'] and piece_3[1] in ['炮', '包'])
        if is_friend_2_3: st.warning(f"⚠️ **好朋友格 (2-3)：** 關係可能過於平淡，像朋友多過像情人。")
        else: st.success("情感關係互動正常。")

    # IV. 前世格局、關係解析
    elif query_type == "前世格局、關係":
        st.subheader("📜 前世格局與今生關係解讀")
        piece_1 = next(p for p in current_gua if p[0] == 1); name_1 = piece_1[1]
        identity_map = {'將': '將軍', '帥': '領兵作戰將領', '士': '當官', '象': '修行人', '相': '修行人', '包': '美麗帥氣', '炮': '美麗帥氣', '兵': '生意人', '卒': '生意人'}
        st.write(f"👉 您前世的可能身份是：**{identity_map.get(name_1, '不明確')}**。")
        st.caption("斜對、平行、隔開關係需查閱秘笈細則。")

    # V. 解全盤進階項目 (專家優化)
    elif query_type == "解全盤 (11 步綜合解析)":
        st.subheader("🌟 解全盤 (11 步) - 終極解析")
        with st.expander("詳細解析項目"):
            is_consumption_1_5 = check_consumption_at_1_or_5(current_gua) 
            piece_1 = next(p for p in current_gua if p[0] == 1); piece_5 = next(p for p in current_gua if p[0] == 5)
            st.markdown("**1. 總格 1 和 5 (子女/不孕機會)**")
            if is_consumption_1_5: st.error("🚨 **高風險警告：** 總格 1 和 5 處於**消耗格**，**不孕機會高**！")
            else: st.success("總格 1 和 5 無明顯消耗格，不孕風險低。")
            
            st.markdown("**3. 干擾磁場確認 (小人、卡陰)**")
            interference_events = check_interference(current_gua) 
            if interference_events:
                st.error("⚠️ **干擾磁場警示！** 偵測到核心位置被攻擊：")
                for event in interference_events: st.write(f"  - **{event['attacker']}** 攻擊 **{event['target']}**，類型：*{event['type']}*")
            else: st.success("磁場穩定，核心位置未受到外部棋子干擾。")
    
    # VI. 通用健康與人際關係 (適用於所有主題的基礎分析)
    st.markdown("---")
    st.subheader("通用健康與人際關係基礎分析")
    st.write("請參考上方五行與氣血警示。")
