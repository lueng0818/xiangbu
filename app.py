import streamlit as st
import pandas as pd
import time
import os
from data import ATTRIBUTES, POSITION_MAP, get_image_path, GEOMETRY_RELATION
from rules import generate_random_gua, generate_full_life_gua, check_exemption, calculate_net_gain_from_gua, analyze_health_and_luck, is_all_same_color, check_career_pattern, check_wealth_pattern, check_consumption_at_1_or_5, check_interference, analyze_trinity_detailed, analyze_holistic_health

# ... (輔助函數與頁面配置保持不變) ...

# ... (側邊欄代碼保持不變) ...

# ... (主頁面 INIT/REJECTED 檢查保持不變) ...

# ----------------------------------------------
# 有效卦象分析 (VALID)
# ----------------------------------------------
# ... (Full 模式代碼保持不變) ...

# ==============================================================================
# 模式 B: 單卦問事 (Tab 3 核心更新)
# ==============================================================================
elif st.session_state.current_mode == "SINGLE":
    current_gua = st.session_state.current_gua
    sub_query = st.session_state.sub_query
    
    analysis_results = calculate_net_gain_from_gua(current_gua) 
    health_analysis = analyze_health_and_luck(current_gua)
    trinity_detailed = analyze_trinity_detailed(current_gua)
    # 【新增】呼叫深度身心診斷
    holistic_report = analyze_holistic_health(current_gua)

    # ... (卦象視覺化代碼保持不變) ...

    # ... (Tab 1, Tab 2 保持不變) ...
            
    with tab3:
        # 如果是健康分析，顯示詳細的身心診斷報告
        if sub_query == "健康分析":
            st.subheader("🏥 中醫五行身心深度診斷")
            st.info("本分析結合中醫五行與心理情緒，找出運勢與健康的『病灶』。")
            
            # 1. 核心體質 (Layer 1)
            core = holistic_report["core"]
            if core:
                with st.expander(f"1. 核心狀態 ({core['name']} - 五行屬{core['element']})", expanded=True):
                    st.markdown(f"**❤️ 當下情緒：** {core['psycho']}")
                    st.markdown(f"**🩺 身體隱疾：** {core['physio']}")
                    st.success(f"**🍀 調理建議：** {core['advice']}")
            
            # 2. 能量平衡 (Layer 2)
            st.markdown("**2. 盤面能量平衡 (五行偏頗)**")
            if holistic_report["balance"]["excess"]:
                for msg in holistic_report["balance"]["excess"]:
                    st.warning(msg)
            if holistic_report["balance"]["lack"]:
                for msg in holistic_report["balance"]["lack"]:
                    st.error(msg)
            if not holistic_report["balance"]["excess"] and not holistic_report["balance"]["lack"]:
                st.success("五行能量分布平均，身心相對平衡。")
                
            # 3. 致病原因 (Layer 3)
            st.markdown("**3. 壓力源與致病原因 (剋應與消耗)**")
            if holistic_report["interaction"]:
                for msg in holistic_report["interaction"]:
                    st.error(f"⚠️ {msg}")
            else:
                st.success("核心位置未受到明顯的剋制或消耗，自我修復能力良好。")
                
            st.markdown("---")
            # 顯示原本的氣血建議
            st.subheader("🩸 氣血循環建議")
            for warn in health_analysis['health_warnings']: st.warning(warn)

        # 其他主題顯示原有的三才分析
        else:
            st.subheader("🔍 天地人三才缺失檢測")
            # ... (原本的三才分析代碼保持不變) ...
            
            # 如果是前世或離婚，顯示特定內容 (保持不變)
