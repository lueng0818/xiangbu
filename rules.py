import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION, FIVE_ELEMENTS_DETAILS, ENERGY_REMEDIES, PIECE_SYMBOLISM, SYMBOL_KEY_MAP, PAST_LIFE_ARCHETYPES

# PIECE_TYPE_MAP, get_full_deck, generate_random_gua, generate_full_life_gua 
# ... (為節省篇幅，此處省略標準生成函數，請保留您原有的或參考前次版本) ...
# 請確保包含基本的生成函數

PIECE_TYPE_MAP = {
    '帥': '將', '將': '將', '仕': '士', '士': '士', '相': '象', '象': '象', 
    '俥': '車', '車': '車', '傌': '馬', '馬': '馬', '炮': '包', '包': '包', '兵': '卒', '卒': '卒'
}

def get_full_deck():
    deck = []
    deck.append(('帥', '紅')); deck.extend([('仕', '紅')] * 2); deck.extend([('相', '紅')] * 2)
    deck.extend([('俥', '紅')] * 2); deck.extend([('傌', '紅')] * 2); deck.extend([('炮', '紅')] * 2)
    deck.extend([('兵', '紅')] * 5)
    deck.append(('將', '黑')); deck.extend([('士', '黑')] * 2); deck.extend([('象', '黑')] * 2)
    deck.extend([('車', '黑')] * 2); deck.extend([('馬', '黑')] * 2); deck.extend([('包', '黑')] * 2)
    deck.extend([('卒', '黑')] * 5)
    return deck

def generate_random_gua():
    full_deck = get_full_deck()
    selected_pieces = random.sample(full_deck, 5)
    gua = []
    positions = [1, 2, 3, 4, 5]
    for i in range(5):
        name, color = selected_pieces[i]
        gua.append((positions[i], name, color, VALUE_MAP.get(name, 0)))
    return gua

def generate_full_life_gua():
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

# --- 基礎判斷邏輯 ---
def is_same_type(name1, name2): return PIECE_TYPE_MAP.get(name1) == PIECE_TYPE_MAP.get(name2)
def check_good_friend(p1, p2): return is_same_type(p1[1], p2[1]) and p1[2] != p2[2]
def check_consumption(p1, p2): return is_same_type(p1[1], p2[1]) and p1[2] == p2[2]
def is_all_same_color(current_gua):
    if not current_gua: return True
    first_color = current_gua[0][2]
    return all(p[2] == first_color for p in current_gua)

def check_exemption(current_gua):
    color_counts = {'紅': 0, '黑': 0}
    for p in current_gua: color_counts[p[2]] += 1
    unique_color = None
    if color_counts['紅'] == 4 and color_counts['黑'] == 1: unique_color = '黑'
    elif color_counts['黑'] == 4 and color_counts['紅'] == 1: unique_color = '紅'
    if unique_color:
        unique_piece = next(p for p in current_gua if p[2] == unique_color)
        if unique_piece[0] == 1: return ("眾星拱月", 1, unique_piece[1])
        else: return ("一枝獨秀", unique_piece[0], unique_piece[1])
    return None

def can_eat(eater_pos, target_pos, current_gua):
    eater = next(p for p in current_gua if p[0] == eater_pos)
    target = next(p for p in current_gua if p[0] == target_pos)
    eater_name, eater_color = eater[1], eater[2]
    target_name, target_color = target[1], target[2]
    if eater_color == target_color: return False
    try: geometry = GEOMETRY_RELATION[eater_pos][target_pos]
    except KeyError: return False

    exemption = check_exemption(current_gua)
    if exemption:
        if exemption[0] == "眾星拱月" and target_pos == 1: return False
        if exemption[0] == "一枝獨秀" and target_pos == exemption[1]:
            if eater_name not in ['馬', '傌', '包', '炮']: return False
            return True

    is_valid = False
    if eater_name in ['馬', '傌']: is_valid = (geometry == "斜位")
    elif eater_name in ['包', '炮']: 
        is_valid = (geometry == "縱隔山") and any(p[0]==1 for p in current_gua) # 需有砲架(中)
    elif eater_name in ['兵', '卒']: is_valid = (geometry == "十字") # 簡化: 兵卒近身十字皆可
    elif geometry == "十字": is_valid = True
    
    if not is_valid: return False

    rank_group = ['將', '帥', '士', '仕', '象', '相']
    if eater_name in ['兵', '卒'] and target_name in ['將', '帥']: return True # 兵吃將
    if eater_name in rank_group:
        if target_name in rank_group: return VALUE_MAP[eater_name] >= VALUE_MAP[target_name]
        return True
    if eater_name in ['車', '俥'] and target_name in rank_group: return False
    return True

# --- 應用邏輯函數 ---

def calculate_score_by_mode(current_gua, mode="general"):
    """【核心】多模式計分引擎 (含健康四象限、感情天平)"""
    center = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    
    report = {"score_A": 0.0, "score_B": 0.0, "net_score": 0.0, "details_A": [], "details_B": [], "interpretation": "", "health_status": []}
    
    # 模式標籤配置
    config = {
        "general": ("助力 (+)", "壓力 (-)"), "career": ("掌控權 (+)", "被剝奪感 (-)"),
        "karma": ("索取/討債 (+)", "虧欠/償債 (-)"), "health": ("吸收力 (身吃藥)", "修復力 (藥修身)"),
        "investment": ("收穫 (+)", "成本 (-)"), "love": ("對方愛我 (他吃我)", "我愛對方 (我吃他)"),
        "divorce": ("自由度 (+)", "損耗度 (-)")
    }
    lbl_A, lbl_B = config.get(mode, config["general"])
    report["label_A"], report["label_B"] = lbl_A, lbl_B

    for nb in neighbors:
        pos_n, name_n, val_n = nb[0], nb[1], VALUE_MAP.get(nb[1], 0)
        pos_c, name_c, val_c = center[0], center[1], VALUE_MAP.get(center[1], 0)
        
        # Action A: 我吃人 (Gain/Active)
        gain = 0
        if can_eat(pos_c, pos_n, current_gua):
            if name_c in ['象','相'] and name_n in ['車','俥']: gain = val_n * 0.5
            elif name_c in ['兵','卒'] and name_n in ['將','帥']: gain = val_n * 1.0
            else: gain = val_n
        elif check_good_friend(center, nb) and mode not in ['health', 'love']: gain = val_n * 0.5

        # Action B: 人吃我 (Cost/Passive)
        cost = 0
        if can_eat(pos_n, pos_c, current_gua):
            if name_n in ['象','相'] and name_c in ['車','俥']: cost = val_c * 0.5
            elif name_n in ['兵','卒'] and name_c in ['將','帥']: cost = val_c * 1.0
            else: cost = val_c
        elif check_good_friend(center, nb) and mode not in ['health', 'love']: cost = val_c * 0.5

        # 分數歸戶 & 健康特殊邏輯
        if mode == 'health':
            status = "無感"
            if gain > 0 and cost > 0: status = "完美適配 (互吃)"; report["score_A"]+=gain; report["score_B"]+=cost
            elif gain > 0: status = "吃心安 (只吸收)"; report["score_A"]+=gain
            elif cost > 0: status = "虛不受補 (只修復)"; report["score_B"]+=cost
            else: status = "路人關係 (無效)"
            report["health_status"].append(f"{nb[2]}{name_n}: {status}")
            
        elif mode == 'love':
            if cost > 0: report["score_A"] += cost; report["details_A"].append(f"被 {name_n} 吃: 對方主導 {cost}")
            if gain > 0: report["score_B"] += gain; report["details_B"].append(f"吃 {name_n}: 我方付出 {gain}")
        else:
            if gain > 0: report["score_A"] += gain; report["details_A"].append(f"吃 {name_n}: +{gain}")
            if cost > 0: report["score_B"] += cost; report["details_B"].append(f"被 {name_n} 吃: -{cost}")

    # 最終結算
    if mode == 'health':
        if report["score_A"]>0 and report["score_B"]>0: report["interpretation"] = "🌟 完美適配：吸收與修復兼具。"
        elif report["score_A"]>0: report["interpretation"] = "⚠️ 吃心安：可吸收但無對症療效。"
        elif report["score_B"]>0: report["interpretation"] = "⚠️ 虛不受補：藥效強但身體吸收不了。"
        else: report["interpretation"] = "⭕ 無明顯互動：建議更換療法。"
    elif mode == 'love':
        diff = report["score_A"] - report["score_B"]; report["net_score"] = diff
        if diff > 5: report["interpretation"] = "❤️ 他愛你較多 / 他主導。"
        elif diff < -5: report["interpretation"] = "💔 你愛他較多 / 你付出。"
        else: report["interpretation"] = "⚖️ 關係對等 / 勢均力敵。"
    else:
        report["net_score"] = report["score_A"] - report["score_B"]; net = report["net_score"]
        if mode == 'investment': report["interpretation"] = "📈 可行 (獲利)" if net > 0 else "💸 不可行 (虧損)"
        else: report["interpretation"] = "🚀 運勢上揚" if net > 0 else "🛡️ 運勢低迷"
        
    return report

def get_marketing_strategy(current_gua):
    """【新增】業務成交策略：看有無好朋友"""
    center = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    has_friend = any(check_good_friend(center, n) for n in neighbors)
    
    if has_friend: return "❤️ **感性行銷**：頻率相同，多聊理念、搏感情，信任即成交。"
    else: return "📊 **理性行銷**：頻率不同，需拿數據、證明、CP值分析來打破隔閡。"

def get_past_life_reading(current_gua):
    """【新增】前世今生解讀：角色 + 空間"""
    center = next(p for p in current_gua if p[0] == 1)
    name = center[1]
    role = PAST_LIFE_ARCHETYPES.get(name, "平民")
    
    # 空間緣分
    relations = []
    for pos in [2, 3]: # 左右
        p = next(p for p in current_gua if p[0] == pos)
        relations.append(f"左右 ({p[1]}): **平行/淺緣** (前世同事/鄰居，今生平淡穩定)。")
    for pos in [4, 5]: # 上下
        p = next(p for p in current_gua if p[0] == pos)
        relations.append(f"上下 ({p[1]}): **隔開/深緣** (前世深刻羈絆，今生靈魂連結強)。")
        
    return {"role": role, "relations": relations}

# ... (check_career_pattern, check_wealth_pattern, analyze_health_and_luck 等保持不變，需包含在內) ...
# 為確保完整性，以下列出關鍵函數的簡化版
def check_career_pattern(current_gua):
    names = [p[1] for p in current_gua]
    return all(n in "".join(names) for n in ['車','馬','包']) or all(n in "".join(names) for n in ['俥','傌','炮']) # 簡化寫法，實際請用完整檢查

def analyze_health_and_luck(current_gua):
    analysis = {'red_count': 0, 'black_count': 0, 'health_warnings': [], 'remedy': {}}
    for p in current_gua: analysis['red_count'] += (p[2]=='紅'); analysis['black_count'] += (p[2]=='黑')
    if analysis['red_count'] > analysis['black_count']: analysis['remedy'] = ENERGY_REMEDIES["Red"]
    elif analysis['black_count'] > analysis['red_count']: analysis['remedy'] = ENERGY_REMEDIES["Black"]
    else: analysis['remedy'] = {"status": "氣血平衡", "advice": "維持現狀", "method": "規律作息", "principle": "陰陽調和"}
    analysis['health_warnings'].append(f"{analysis['remedy']['status']}: {analysis['remedy']['advice']}")
    return analysis

def get_advanced_piece_analysis(current_gua):
    center = next(p for p in current_gua if p[0] == 1)
    sym_key = SYMBOL_KEY_MAP.get(center[1], "兵卒")
    data = PIECE_SYMBOLISM.get(sym_key, {})
    return {"role_title": data.get("role",""), "self_desc": data.get("self",""), "special_warnings": []}

def check_consumption_at_1_or_5(current_gua):
    # 簡化：檢查 1, 5 是否同色同名
    p1 = next(p for p in current_gua if p[0] == 1)
    p5 = next(p for p in current_gua if p[0] == 5)
    return p1[1] == p5[1] and p1[2] == p5[2]

def check_interference(current_gua): return [] # 簡化，實際請用完整版
def analyze_trinity_detailed(current_gua): 
    return {"missing_heaven": None, "missing_human": None, "missing_earth": None} # 簡化
def analyze_holistic_health(current_gua): return {"core": {}, "balance": {"excess":[], "lack":[]}, "interaction": []} # 簡化
def analyze_coordinate_map(current_gua, gender): return {"top_support": "", "center_status": "", "bottom_foundation": "", "love_relationship": "", "peer_relationship": ""} # 簡化
def calculate_net_gain_from_gua(current_gua): return calculate_score_by_mode(current_gua, "investment")
