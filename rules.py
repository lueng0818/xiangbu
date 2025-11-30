import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION, FIVE_ELEMENTS_DETAILS, ENERGY_REMEDIES, PIECE_SYMBOLISM, SYMBOL_KEY_MAP

# ==============================================================================
# 輔助：棋子類型映射
# ==============================================================================
PIECE_TYPE_MAP = {
    '帥': '將', '將': '將', '仕': '士', '士': '士',
    '相': '象', '象': '象', '俥': '車', '車': '車',
    '傌': '馬', '馬': '馬', '炮': '包', '包': '包',
    '兵': '卒', '卒': '卒'
}

# ==============================================================================
# 核心邏輯函數
# ==============================================================================

def get_full_deck():
    """產生一副完整的32支象棋列表"""
    deck = []
    # 紅方
    deck.append(('帥', '紅')); deck.extend([('仕', '紅')] * 2); deck.extend([('相', '紅')] * 2)
    deck.extend([('俥', '紅')] * 2); deck.extend([('傌', '紅')] * 2); deck.extend([('炮', '紅')] * 2)
    deck.extend([('兵', '紅')] * 5)
    # 黑方
    deck.append(('將', '黑')); deck.extend([('士', '黑')] * 2); deck.extend([('象', '黑')] * 2)
    deck.extend([('車', '黑')] * 2); deck.extend([('馬', '黑')] * 2); deck.extend([('包', '黑')] * 2)
    deck.extend([('卒', '黑')] * 5)
    return deck

def generate_random_gua():
    """單次占卜：從完整32支棋中隨機抽出5支"""
    full_deck = get_full_deck()
    selected_pieces = random.sample(full_deck, 5)
    gua = []
    positions = [1, 2, 3, 4, 5]
    for i in range(5):
        name, color = selected_pieces[i]
        gua.append((positions[i], name, color, VALUE_MAP.get(name, 0)))
    return gua

def generate_full_life_gua():
    """全盤流年：完整32支棋洗牌分配"""
    full_deck = get_full_deck()
    random.shuffle(full_deck)
    life_stages = ["11~20歲", "21~30歲", "31~40歲", "41~50歲", "51~60歲", "61~70歲"]
    full_gua = {}
    start_index = 0
    positions = [1, 2, 3, 4, 5]
    for stage in life_stages:
        stage_pieces_raw = full_deck[start_index : start_index + 5]
        start_index += 5
        stage_gua = []
        for i in range(5):
            name, color = stage_pieces_raw[i]
            stage_gua.append((positions[i], name, color, VALUE_MAP.get(name, 0)))
        full_gua[stage] = stage_gua
    full_gua["餘棋"] = full_deck[30:]
    return full_gua

# --- 判斷邏輯 ---

def is_same_type(name1, name2):
    return PIECE_TYPE_MAP.get(name1) == PIECE_TYPE_MAP.get(name2)

def check_good_friend(p1, p2):
    return is_same_type(p1[1], p2[1]) and p1[2] != p2[2]

def check_consumption(p1, p2):
    return is_same_type(p1[1], p2[1]) and p1[2] == p2[2]

def is_all_same_color(current_gua):
    if not current_gua: return True
    first_color = current_gua[0][2]
    for pos, name, color, val in current_gua:
        if color != first_color: return False
    return True

def check_exemption(current_gua):
    color_counts = {'紅': 0, '黑': 0}
    for pos, name, color, val in current_gua:
        color_counts[color] += 1
    unique_color = None
    if color_counts['紅'] == 4 and color_counts['黑'] == 1: unique_color = '黑'
    elif color_counts['黑'] == 4 and color_counts['紅'] == 1: unique_color = '紅'
    if unique_color:
        unique_piece = next(p for p in current_gua if p[2] == unique_color)
        unique_pos, unique_name = unique_piece[0], unique_piece[1]
        if unique_pos == 1: return ("眾星拱月", unique_pos, unique_name)
        else: return ("一枝獨秀", unique_pos, unique_name)
    return None

def can_eat(eater_pos, target_pos, current_gua):
    eater = next(p for p in current_gua if p[0] == eater_pos)
    target = next(p for p in current_gua if p[0] == target_pos)
    eater_name, eater_color = eater[1], eater[2]
    target_name, target_color = target[1], target[2]
    
    if eater_color == target_color: return False 
    try: geometry = GEOMETRY_RELATION[eater_pos][target_pos]
    except KeyError: return False

    exemption_info = check_exemption(current_gua)
    if exemption_info:
        pattern_type, unique_pos, unique_name = exemption_info
        if pattern_type == "眾星拱月" and target_pos == 1: return False 
        if pattern_type == "一枝獨秀" and target_pos == unique_pos:
            if eater_name not in ['馬', '傌', '包', '炮']: return False
            return True 

    is_move_valid = False
    if eater_name in ['馬', '傌']: is_move_valid = (geometry == "斜位")
    elif eater_name in ['包', '炮']: is_move_valid = (geometry == "縱隔山")
    elif eater_name in ['兵', '卒']: is_move_valid = ((eater_pos == 5 and target_pos == 1) or (eater_pos == 1 and target_pos == 4))
    elif geometry == "十字": is_move_valid = True 
    if not is_move_valid: return False

    rank_group = ['將', '帥', '士', '仕', '象', '相']
    if eater_name in rank_group:
        if target_name in rank_group: return VALUE_MAP[eater_name] >= VALUE_MAP[target_name]
        else: return True
    return True

# --- 深度分析函數 ---

def analyze_trinity_detailed(current_gua):
    p1 = next(p for p in current_gua if p[0] == 1)
    p4 = next(p for p in current_gua if p[0] == 4)
    p5 = next(p for p in current_gua if p[0] == 5)
    result = {"missing_heaven": None, "missing_human": None, "missing_earth": None}
    
    is_heaven_consuming = check_consumption(p4, p1)
    is_heaven_eating_human = can_eat(4, 1, current_gua)
    if is_heaven_consuming or is_heaven_eating_human:
        reason = "消耗關係 (長輩固執)" if is_heaven_consuming else "相剋/被吃 (長輩給壓力)"
        result["missing_heaven"] = {"status": True, "reason": reason, "desc": "缺乏長輩緣、天助運差。個性易鐵齒、傲慢。", "advice": "1. 謙卑：練習對長輩恭敬。\n2. 連結大自然：爬山、曬太陽。\n3. 佈施：捐血或捐款。"}

    is_earth_consuming = check_consumption(p5, p1)
    is_earth_eating_human = can_eat(5, 1, current_gua)
    if is_earth_consuming or is_earth_eating_human:
        reason = "消耗關係" if is_earth_consuming else "相剋/被吃 (根基被毀)"
        result["missing_earth"] = {"status": True, "reason": reason, "desc": "缺乏根基、財庫不穩。做事虎頭蛇尾。", "advice": "1. 強迫儲蓄：錢放信任親友戶頭。\n2. 實體資產：買房或黃金。\n3. 保守投資：避免投機。"}

    neighbors = [2, 3, 4, 5]
    has_friend = False
    for pos in neighbors:
        pn = next(p for p in current_gua if p[0] == pos)
        if check_good_friend(p1, pn): has_friend = True; break
    if not has_friend:
        result["missing_human"] = {"status": True, "reason": "孤立無援", "desc": "缺乏人和、自我中心。易目中無人，孤軍奮戰。", "advice": "1. 修身養性：多聽少說，換位思考。\n2. 尋求合作：強制自己融入團隊。"}
    return result

def analyze_body_hologram(current_gua):
    diagnosis = []
    for pos, name, color, val in current_gua:
        element = ATTRIBUTES.get(name, {}).get('五行', '')
        color_nature = "發炎/急性/燥熱" if color == "紅" else "氣滯/慢性/寒濕"
        if pos == 4:
            if name in ['炮', '包']: diagnosis.append(f"🔴 **頭部 ({color}{name})**：可能**頭痛、失眠**或神經衰弱。({color_nature})")
            elif name in ['車', '俥'] and color == '紅': diagnosis.append(f"🔴 **頭部 ({color}{name})**：紅車衝撞，留意**血壓高**或頭部脹痛。")
            elif element == "金" and color == "黑": diagnosis.append(f"🔵 **頭部 ({color}{name})**：悲觀思慮重，頭昏沉感。")
        elif pos == 5:
            if name in ['馬', '傌']: 
                symptom = "關節炎" if color == "紅" else "舊傷痠痛"
                diagnosis.append(f"🦵 **下肢/膝蓋 ({color}{name})**：留意膝蓋卡卡或無力。{symptom}。")
            elif name in ['包', '炮']: diagnosis.append(f"💧 **下肢/泌尿 ({color}{name})**：留意**水腫**、婦科或泌尿系統。")
            elif element == "土": diagnosis.append(f"🦵 **下肢 ({color}{name})**：腿部肌肉容易乏力。")
        elif pos in [2, 3]:
            side = "👉 右側" if pos == 2 else "👈 左側"
            if name in ['卒', '兵']: diagnosis.append(f"💪 **{side} 肩頸/手臂 ({color}{name})**：僵硬如石，氣血卡住。")
            elif name in ['車', '俥']: diagnosis.append(f"💪 **{side} 手部 ({color}{name})**：可能曾扭傷或過度使用痠痛。")
        elif pos == 1:
            if element == "木" and color == "黑": diagnosis.append(f"❤️ **胸腹核心 ({color}{name})**：肝氣鬱結，胸悶氣不順。")
            elif element == "土" and color == "紅": diagnosis.append(f"🌭 **腸胃核心 ({color}{name})**：胃火旺，易有胃食道逆流。")
    return diagnosis

def analyze_holistic_health(current_gua):
    report = {"core": {}, "balance": {"excess": [], "lack": []}, "interaction": []}
    center_piece = next(p for p in current_gua if p[0] == 1)
    center_name = center_piece[1]
    center_elm = ATTRIBUTES.get(center_name, {}).get("五行")
    if center_elm:
        details = FIVE_ELEMENTS_DETAILS.get(center_elm)
        report["core"] = {"name": f"{center_piece[2]}{center_name}", "element": center_elm, "psycho": details["psycho_msg"], "physio": details["physio_msg"], "advice": details["advice"]}

    element_counts = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for pos, name, color, val in current_gua:
        elm = ATTRIBUTES.get(name, {}).get("五行")
        if elm: element_counts[elm] += 1
    
    for elm, count in element_counts.items():
        if count >= 3:
            details = FIVE_ELEMENTS_DETAILS.get(elm)
            msg = f"**{elm}行過多 ({count}支)：** {details['emotion']}氣過重。"
            report["balance"]["excess"].append(msg)
    for elm, count in element_counts.items():
        if count == 0:
            msg = f"**缺{elm}：** 需留意相關臟腑功能。"
            report["balance"]["lack"].append(msg)

    center_pos = 1
    neighbors = [2, 3, 4, 5]
    for neighbor_pos in neighbors:
        neighbor = next(p for p in current_gua if p[0] == neighbor_pos)
        neighbor_name = neighbor[1]
        neighbor_elm = ATTRIBUTES.get(neighbor_name, {}).get("五行")
        neighbor_str = f"{neighbor[2]}{neighbor_name}"
        if can_eat(neighbor_pos, center_pos, current_gua):
            msg = f"受到 **{neighbor_str} ({neighbor_elm})** 的攻擊 (剋應)。"
            report["interaction"].append(msg)
        elif neighbor[2] == center_piece[2] and neighbor_elm == center_elm:
            msg = f"與 **{neighbor_str}** 形成消耗。"
            report["interaction"].append(msg)
    return report

def analyze_health_and_luck(current_gua):
    analysis = {'red_count': 0, 'black_count': 0, 'missing_elements': {'木': True, '火': True, '土': True, '金': True, '水': True}, 'health_warnings': [], 'remedy': {}}
    for pos, name, color, val in current_gua:
        analysis['red_count'] += (color == '紅')
        analysis['black_count'] += (color == '黑')
        element = ATTRIBUTES.get(name, {}).get('五行', 'N/A')[0]
        if element != 'N': analysis['missing_elements'][element] = False
    
    if analysis['red_count'] > analysis['black_count']:
        remedy = ENERGY_REMEDIES["Red"]
        analysis['remedy'] = remedy
        analysis['health_warnings'].append(f"🔥 **{remedy['status']}**：{remedy['advice']}")
    elif analysis['black_count'] > analysis['red_count']:
        remedy = ENERGY_REMEDIES["Black"]
        analysis['remedy'] = remedy
        analysis['health_warnings'].append(f"💧 **{remedy['status']}**：{remedy['advice']}")
    else:
        analysis['remedy'] = {"status": "⚖️ 氣血平衡", "method": "維持現狀", "principle": "陰陽調和。", "advice": "目前氣血比例適中。"}
    return analysis

def analyze_coordinate_map(current_gua, gender):
    p1 = next(p for p in current_gua if p[0] == 1)
    p4 = next(p for p in current_gua if p[0] == 4)
    p5 = next(p for p in current_gua if p[0] == 5)
    p2 = next(p for p in current_gua if p[0] == 2)
    p3 = next(p for p in current_gua if p[0] == 3)
    
    report = {"center_status": "", "top_support": "", "bottom_foundation": "", "love_relationship": "", "peer_relationship": ""}
    p1_attr = ATTRIBUTES.get(p1[1], {})
    report["center_status"] = f"核心是 **{p1[2]}{p1[1]}** ({p1_attr.get('特質')})。處於{p1_attr.get('五行')}行能量狀態。"
    
    if check_good_friend(p1, p4): report["top_support"] = "🌟 **貴人提拔：** 長官/長輩疼愛，資源豐富。"
    elif can_eat(4, 1, current_gua): report["top_support"] = "⚡ **上司施壓：** 主管給壓力，或長輩身體欠安。"
    elif check_consumption(p1, p4): report["top_support"] = "🌀 **溝通消耗：** 與長輩/主管觀念不合。"
    else: report["top_support"] = "☁️ **關係平淡：** 凡事多靠自己。"

    if can_eat(5, 1, current_gua): report["bottom_foundation"] = "⚠️ **根基受損：** 下屬造反或錢財留不住。"
    elif can_eat(1, 5, current_gua): report["bottom_foundation"] = "✊ **掌控大局：** 能掌握資源，結局主導。"
    elif check_good_friend(p1, p5): report["bottom_foundation"] = "🌲 **根基穩固：** 基礎紮實，晚運佳。"
    else: report["bottom_foundation"] = "🍂 **漂泊無根：** 地格連結弱，適合保守。"

    target_love_pos = 2 if gender == "男" else 3
    target_peer_pos = 3 if gender == "男" else 2
    p_love = p2 if gender == "男" else p3
    p_peer = p3 if gender == "男" else p2
    
    love_role = "妻/女友" if gender == "男" else "夫/男友"
    if check_good_friend(p1, p_love): report["love_relationship"] = f"💕 **感情甜蜜：** {love_role}位是好朋友，關係融洽。"
    elif can_eat(target_love_pos, 1, current_gua): report["love_relationship"] = f"💔 **感情壓力：** {love_role}位剋制您，對方強勢。"
    elif check_consumption(p1, p_love): report["love_relationship"] = f"🗣️ **爭執消耗：** 與{love_role}容易吵架或冷戰。"
    else: report["love_relationship"] = f"😐 **緣分平平：** 與{love_role}互動較少。"

    peer_role = "兄弟/男同事" if gender == "男" else "姊妹/女同事"
    if can_eat(target_peer_pos, 1, current_gua): report["peer_relationship"] = f"🔪 **犯小人：** 留意{peer_role}扯後腿。"
    elif check_good_friend(p1, p_peer): report["peer_relationship"] = f"🤝 **得力夥伴：** {peer_role}是貴人，適合合作。"
    else: report["peer_relationship"] = f"Run **各自努力：** {peer_role}影響不大。"
    return report

def check_consumption_at_1_or_5(current_gua):
    pieces_at_1_and_5 = [p for p in current_gua if p[0] in [1, 5]]
    name_color_counts = {}
    for pos, name, color, val in pieces_at_1_and_5:
        key = (name, color)
        name_color_counts[key] = name_color_counts.get(key, 0) + 1
    for (name, color), count in name_color_counts.items():
        if count >= 2: return True
    return False

def check_interference(current_gua):
    interference_events = []
    core_targets = [1, 2, 3]
    for pos_a, name_a, color_a, val_a in current_gua:
        if name_a not in ['馬', '傌', '包', '炮']: continue
        for pos_b in core_targets:
            if pos_a == pos_b: continue 
            if can_eat(pos_a, pos_b, current_gua):
                target_piece = next(p for p in current_gua if p[0] == pos_b)
                if name_a in ['馬', '傌']: inter_type = "犯小人/卡陰"
                else: inter_type = "投資虧損/時機不佳" 
                interference_events.append({
                    "attacker": f"{color_a}{name_a} (位{pos_a})",
                    "target": f"{target_piece[2]}{target_piece[1]} (位{pos_b})",
                    "type": inter_type
                })
    return interference_events

def check_career_pattern(current_gua):
    names = [p[1] for p in current_gua]
    has_chariot = any(n in ['車', '俥'] for n in names)
    has_horse = any(n in ['馬', '傌'] for n in names)
    has_cannon = any(n in ['包', '炮'] for n in names)
    if has_chariot and has_horse and has_cannon: return True
    return False

def check_wealth_pattern(current_gua):
    names = [p[1] for p in current_gua]
    has_general = any(n in ['將', '帥'] for n in names)
    has_minister = any(n in ['士', '仕'] for n in names)
    has_elephant = any(n in ['象', '相'] for n in names)
    if has_general and has_minister and has_elephant: return True
    return False

def calculate_net_gain_from_gua(current_gua):
    """(舊版相容用，實際上會呼叫 calculate_score_by_mode)"""
    res = calculate_score_by_mode(current_gua, mode="investment")
    return {"gain": res["score_A"], "cost": res["score_B"], "net_gain": res["net_score"], "interactions": []}

def calculate_score_by_mode(current_gua, mode="general"):
    """多模式量化計分引擎 (Universal Scoring Engine)"""
    center_piece = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    
    report = {"score_A": 0.0, "score_B": 0.0, "net_score": 0.0, "label_A": "", "label_B": "", "label_Net": "", "details_A": [], "details_B": [], "interpretation": ""}
    
    labels = {
        "general": ("環境助力 (+)", "環境壓力 (-)", "運勢損益"),
        "career": ("掌控權 (+)", "被剝奪感 (-)", "權力指數"),
        "karma": ("索取/討債 (+)", "虧欠/償債 (-)", "因果餘額"),
        "health": ("吸收力 (身吃藥)", "修復力 (藥修身)", "療癒效能"),
        "investment": ("收穫 (利潤)", "成本 (風險)", "投資淨利"),
        "love": ("對方愛我 (他吃我)", "我愛對方 (我吃他)", "情感權重"),
        "divorce": ("自由度 (反擊)", "損耗度 (被吃)", "離異指數")
    }
    lbl_A, lbl_B, lbl_Net = labels.get(mode, labels["general"])
    report["label_A"], report["label_B"], report["label_Net"] = lbl_A, lbl_B, lbl_Net

    for neighbor in neighbors:
        pos_n = neighbor[0]; name_n = neighbor[1]; val_n = VALUE_MAP.get(name_n, 0)
        pos_c = center_piece[0]; name_c = center_piece[1]; val_c = VALUE_MAP.get(name_c, 0)
        
        gain = 0
        if can_eat(pos_c, pos_n, current_gua):
            if name_c in ['象','相'] and name_n in ['車','俥']: gain = val_n * 0.5
            elif name_c in ['兵','卒'] and name_n in ['將','帥']: gain = val_n * 1.0
            else: gain = val_n
        elif check_good_friend(center_piece, neighbor):
            if mode not in ['love', 'health']: gain = val_n * 0.5

        cost = 0
        if can_eat(pos_n, pos_c, current_gua):
            if name_n in ['象','相'] and name_c in ['車','俥']: cost = val_c * 0.5
            elif name_n in ['兵','卒'] and name_c in ['將','帥']: cost = val_c * 1.0
            else: cost = val_c
        elif check_good_friend(center_piece, neighbor):
            if mode not in ['love', 'health']: cost = val_c * 0.5

        if mode == 'health':
            if gain > 0: report["score_A"] += gain; report["details_A"].append(f"吃 {name_n}: 吸收 {gain} 分")
            if cost > 0: report["score_B"] += cost; report["details_B"].append(f"被 {name_n} 吃: 修復 {cost} 分")
        elif mode == 'love':
            if cost > 0: report["score_A"] += cost; report["details_A"].append(f"被 {name_n} 吃: 對方主導 {cost} 分")
            if gain > 0: report["score_B"] += gain; report["details_B"].append(f"吃 {name_n}: 我方付出 {gain} 分")
        else:
            if gain > 0: report["score_A"] += gain; report["details_A"].append(f"吃 {name_n}: +{gain}")
            if cost > 0: report["score_B"] += cost; report["details_B"].append(f"被 {name_n} 吃: -{cost}")

    if mode == 'health':
        if report["score_A"] > 0 and report["score_B"] > 0: report["net_score"] = report["score_A"] + report["score_B"]; report["interpretation"] = "🌟 **完美互補：** 吸收與修復兼具。"
        elif report["score_A"] > 0: report["net_score"] = report["score_A"]; report["interpretation"] = "⚠️ **只吃不被吃：** 可吸收但無對症修復效果。"
        elif report["score_B"] > 0: report["net_score"] = report["score_B"]; report["interpretation"] = "⚠️ **被吃不可吃：** 有療效但身體虛不受補。"
        else: report["interpretation"] = "無明顯能量互動。"
    elif mode == 'love':
        diff = report["score_A"] - report["score_B"]; report["net_score"] = diff
        if diff > 5: report["interpretation"] = "❤️ **他愛你較多：** 對方主導或付出較多。"
        elif diff < -5: report["interpretation"] = "💔 **你愛他較多：** 您付出較多。"
        else: report["interpretation"] = "⚖️ **關係對等：** 勢均力敵。"
    else:
        report["net_score"] = report["score_A"] - report["score_B"]
        net = report["net_score"]
        if mode == 'investment': report["interpretation"] = "📈 **獲利：** 投資可行。" if net > 0 else "💸 **虧損：** 建議勿投。"
        elif mode == 'general': report["interpretation"] = "🚀 **運勢上揚：** 助力大。" if net > 0 else "🛡️ **運勢低迷：** 壓力大。"
        
    return report

def get_advanced_piece_analysis(current_gua):
    center_piece = next(p for p in current_gua if p[0] == 1)
    name = center_piece[1]
    symbol_key = SYMBOL_KEY_MAP.get(name, "兵卒")
    symbol_data = PIECE_SYMBOLISM.get(symbol_key, {})
    analysis = {"role_title": symbol_data.get("role", ""), "self_desc": symbol_data.get("self", ""), "love_desc": symbol_data.get("love", ""), "career_desc": symbol_data.get("career", ""), "health_desc": symbol_data.get("health", ""), "special_warnings": []}
    
    if name in ['馬', '傌']: analysis["special_warnings"].append("⚠️ **受困格局：** 馬在中間施展不開。")
    if name in ['兵', '卒']: analysis["special_warnings"].append("💰 **強迫儲蓄：** 兵卒是辛苦錢，建議定存。")
    if name in ['包', '炮']: analysis["special_warnings"].append("📏 **保持距離：** 感情或合作適合隔山打牛。")
    if name in ['車', '俥']: analysis["special_warnings"].append("🔥 **煞車提醒：** 做事多留三分餘地。")
    return analysis
