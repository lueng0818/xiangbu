import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION, FIVE_ELEMENTS_DETAILS

# ... (省略前面 get_full_deck, generate_random_gua, generate_full_life_gua 等函數，保持不變) ...
# 請保留原有的 can_eat, check_exemption 等函數

# ==============================================================================
# 【新增】核心身心診斷邏輯 (依據五行與中醫理論)
# ==============================================================================

def analyze_holistic_health(current_gua):
    """
    執行三個層次的深度身心診斷：
    1. 中間牌 (人格/核心病灶)
    2. 盤面多寡 (能量偏頗)
    3. 攻擊與消耗 (剋應/致病原因)
    """
    report = {
        "core": {},
        "balance": {"excess": [], "lack": []},
        "interaction": []
    }
    
    # --- 層次一：中間牌 (人格/核心) ---
    center_piece = next(p for p in current_gua if p[0] == 1)
    center_name = center_piece[1]
    center_attr = ATTRIBUTES.get(center_name, {})
    center_element = center_attr.get("五行")
    
    if center_element:
        details = FIVE_ELEMENTS_DETAILS.get(center_element)
        report["core"] = {
            "name": f"{center_piece[2]}{center_name}",
            "element": center_element,
            "psycho": details["psycho_msg"],
            "physio": details["physio_msg"],
            "advice": details["advice"]
        }

    # --- 層次二：盤面多寡 (五行偏頗) ---
    element_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pos, name, color, val in current_gua:
        elm = ATTRIBUTES.get(name, {}).get("五行")
        if elm: element_counts[elm] += 1
    
    # 判斷過多 (>=3支)
    for elm, count in element_counts.items():
        if count >= 3:
            details = FIVE_ELEMENTS_DETAILS.get(elm)
            msg = f"**{elm}行過多 (能量淤積)：** {count}支。{details['emotion']}氣過重。"
            if elm == "土": msg += " 思慮過多，動彈不得，胃氣不和。"
            if elm == "木": msg += " 壓抑憤怒，肝火旺，易抽筋。"
            if elm == "金": msg += " 悲觀固執，氣滯胸悶。"
            if elm == "水": msg += " 驚恐擔憂，腎氣耗損。"
            if elm == "火": msg += " 急躁亢奮，耗損心神。"
            report["balance"]["excess"].append(msg)
            
    # 判斷缺失 (0支)
    for elm, count in element_counts.items():
        if count == 0:
            msg = f"**缺{elm}：** "
            if elm == "土": msg += "缺乏誠信或安全感，脾胃吸收弱。"
            if elm == "木": msg += "缺乏衝勁，肝膽排毒功能較差。"
            if elm == "火": msg += "缺乏熱情，血液循環較慢。"
            if elm == "金": msg += "缺乏決斷力，呼吸系統較弱。"
            if elm == "水": msg += "缺乏智慧或靈活度，腎水不足。"
            report["balance"]["lack"].append(msg)

    # --- 層次三：攻擊與消耗 (剋應/致病原因) ---
    # 檢查誰在吃中間 (1號位)，或誰跟中間消耗
    center_pos = 1
    neighbors = [2, 3, 4, 5]
    
    for neighbor_pos in neighbors:
        neighbor = next(p for p in current_gua if p[0] == neighbor_pos)
        neighbor_name = neighbor[1]
        neighbor_elm = ATTRIBUTES.get(neighbor_name, {}).get("五行")
        neighbor_str = f"{neighbor[2]}{neighbor_name}"
        
        # 1. 檢查被吃 (受威脅/剋應)
        if can_eat(neighbor_pos, center_pos, current_gua):
            # 判斷剋應關係 (簡化版，根據五行生剋)
            # 木剋土, 土剋水, 水剋火, 火剋金, 金剋木
            relation_msg = f"{neighbor_elm}剋{center_element}"
            
            detail_msg = f"受到 **{POSITION_MAP[neighbor_pos]['名稱']} ({neighbor_str})** 的攻擊。"
            if neighbor_elm == "木" and center_element == "土":
                detail_msg += " (木剋土) 因憤怒衝動或強勢壓力，傷及脾胃，導致胃痛、自信受損。"
            elif neighbor_elm == "土" and center_element == "水":
                detail_msg += " (土剋水) 因思慮過度或現實壓力，抑制了你的靈活度，導致內分泌失調或恐懼。"
            elif neighbor_elm == "水" and center_element == "火":
                detail_msg += " (水剋火) 因恐懼擔憂，澆熄了熱情，導致心神不寧、血循變差。"
            elif neighbor_elm == "火" and center_element == "金":
                detail_msg += " (火剋金) 因急躁情緒，融化了原則，導致呼吸道發炎或皮膚問題。"
            elif neighbor_elm == "金" and center_element == "木":
                detail_msg += " (金剋木) 因悲觀固執或太講義氣，壓抑了生機，導致肝氣鬱結或筋骨痠痛。"
            else:
                detail_msg += " 外在壓力直接衝擊核心，造成身心負擔。"
                
            report["interaction"].append(detail_msg)
            
        # 2. 檢查消耗 (同類同色/自刑)
        # 這裡定義消耗：同五行且同色 (如 紅仕 vs 紅仕)
        # 或者 即使不同名但同五行同色 (如 紅車 vs 紅馬 都是木)
        elif neighbor[2] == center_piece[2] and neighbor_elm == center_element:
            # 自刑/消耗
            detail_msg = f"與 **{POSITION_MAP[neighbor_pos]['名稱']} ({neighbor_str})** 形成消耗。"
            if center_element == "金":
                detail_msg += " (金金自刑) 憂傷肺。因自以為是或過度悲觀鑽牛角尖，導致呼吸不順胸悶。"
            elif center_element == "木":
                detail_msg += " (木木消耗) 怒傷肝。因堅持己見或鬥氣，導致肝火過旺。"
            elif center_element == "土":
                detail_msg += " (土土消耗) 思傷胃。因固執己見或過度操煩，導致消化系統停滯。"
            elif center_element == "水":
                detail_msg += " (水水消耗) 恐傷腎。因過度驚疑或聰明反被聰明誤，耗損精神。"
            elif center_element == "火":
                detail_msg += " (火火消耗) 喜傷心。因情緒起伏過大或太過急躁，耗損心神。"
            
            report["interaction"].append(detail_msg)

    return report

# ... (請務必保留原本 rules.py 的所有其他函數，如 can_eat, analyze_trinity_detailed 等) ...
# 為了完整性，這裡不重複貼上所有舊函數，請將 analyze_holistic_health 加入到您現有的 rules.py 中。
