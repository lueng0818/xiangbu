import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION, FIVE_ELEMENTS_DETAILS, ENERGY_REMEDIES, PIECE_SYMBOLISM, SYMBOL_KEY_MAP, PAST_LIFE_ARCHETYPES

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
    life_stages = ["11~20歲 (青少年)", "21~30歲 (青年)", "31~40歲 (壯年)", "41~50歲 (中年)", "51~60歲 (熟齡)", "61~70歲 (退休)"]
    full_gua = {}
    full_gua["raw_flow"] = full_deck 
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

# --- 新增全盤分析函數 ---
def analyze_total_fate(full_gua_data):
    first_stage = "11~20歲 (青少年)"
    gua = full_gua_data.get(first_stage, [])
    if not gua: return {"type": "未知", "desc": "數據錯誤"}
    center = next(p for p in gua if p[0] == 1)
    name = center[1]
    if name in ['將', '帥']: return {"type": "👑 領袖格 (將帥命)", "desc": "天生具有領導風範，主觀意識強。"}
    elif name in ['車', '俥', '馬', '傌']: return {"type": "🏎️ 開創格 (車馬命)", "desc": "行動力強，一生奔波勞碌但能成大事。"}
    elif name in ['士', '仕', '象', '相', '包', '炮']: return {"type": "📜 幕僚/策士格", "desc": "靠智慧、口才或專業技能取勝。"}
    else: return {"type": "🧱 實幹格 (兵卒命)", "desc": "腳踏實地，大器晚成。"}

def get_decade_advice(stage, gua):
    p1 = next(p for p in gua if p[0] == 1)
    p4 = next(p for p in gua if p[0] == 4)
    p5 = next(p for p in gua if p[0] == 5)
    if "11~20" in stage:
        if can_eat(4, 1, gua): return {"focus":"學業", "advice":"⚠️ 上格剋中：長輩壓力大，叛逆期需溝通。"}
        return {"focus":"學業", "advice":"平穩發展，適合探索興趣。"}
    elif "21~30" in stage:
        if check_career_pattern(gua): return {"focus":"事業起步", "advice":"🏆 事業格：衝勁十足，適合打江山。"}
        return {"focus":"事業起步", "advice":"累積經驗，多方嘗試。"}
    elif "31~40" in stage:
        if can_eat(2, 1, gua) or can_eat(3, 1, gua): return {"focus":"婚姻/成家", "advice":"💔 左右相剋：婚姻面臨考驗。"}
        return {"focus":"婚姻/成家", "advice":"家庭與事業需平衡。"}
    elif "41~50" in stage:
        if p1[1] in ['將', '帥']: return {"focus":"事業巔峰", "advice":"👑 掌權期：事業達巔峰。"}
        return {"focus":"事業巔峰", "advice":"穩中求進，注意身心保養。"}
    elif "51~60" in stage:
        if can_eat(5, 1, gua): return {"focus":"資產/子女", "advice":"💸 下格剋中：留意錢財流失。"}
        return {"focus":"資產/子女", "advice":"規劃退休生活。"}
    else:
        return {"focus":"健康/晚年", "advice":"保重身體，保持心情愉快。"}

def analyze_color_flow(full_deck):
    streaks = []; current_color = full_deck[0][1]; current_count = 1; start_idx = 0
    for i in range(1, len(full_deck)):
        color = full_deck[i][1]
        if color == current_color: current_count += 1
        else:
            if current_count >= 5: streaks.append(f"第 {start_idx+1}~{i} 支：連續 {current_count} 支{current_color}棋")
            current_color = color; current_count = 1; start_idx = i
    if current_count >= 5: streaks.append(f"第 {start_idx+1}~{len(full_deck)} 支：連續 {current_count} 支{current_color}棋")
    if streaks: return "🌊 **氣場流動異常：** " + "、".join(streaks)
    return "✅ 氣場流動正常。"

# --- 基礎與應用函數 (保持不變) ---
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
    elif eater_name in ['包', '炮']: is_valid = (geometry == "縱隔山") and any(p[0]==1 for p in current_gua)
    elif eater_name in ['兵', '卒']: is_valid = (geometry == "十字") 
    elif geometry == "十字": is_valid = True
    if not is_valid: return False

    rank_group = ['將', '帥', '士', '仕', '象', '相']
    if eater_name in ['兵', '卒'] and target_name in ['將', '帥']: return True
    if eater_name in rank_group:
        if target_name in rank_group: return VALUE_MAP[eater_name] >= VALUE_MAP[target_name]
        return True
    if eater_name in ['車', '俥'] and target_name in rank_group: return False
    return True

def calculate_score_by_mode(current_gua, mode="general"):
    center = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    report = {"score_A": 0.0, "score_B": 0.0, "net_score": 0.0, "label_A": "", "label_B": "", "label_Net": "", "details_A": [], "details_B": [], "interpretation": "", "health_status": []}
    
    config = {
        "general": ("助力 (+)", "壓力 (-)"), "career": ("掌控權 (+)", "被剝奪感 (-)"),
        "karma": ("索取/討債 (+)", "虧欠/償債 (-)"), "health": ("吸收力", "修復力"),
        "investment": ("收穫 (+)", "成本 (-)"), "love": ("對方愛我", "我愛對方"),
        "divorce": ("自由度 (+)", "損耗度 (-)")
    }
    lbl_A, lbl_B = config.get(mode, config["general"])
    report["label_A"], report["label_B"] = lbl_A, lbl_B

    for nb in neighbors:
        pos_n, name_n, val_n = nb[0], nb[1], VALUE_MAP.get(nb[1], 0)
        pos_c, name_c, val_c = center[0], center[1], VALUE_MAP.get(center[1], 0)
        
        gain = 0
        if can_eat(pos_c, pos_n, current_gua):
            if name_c in ['象','相'] and name_n in ['車','俥']: gain = val_n * 0.5
            elif name_c in ['兵','卒'] and name_n in ['將','帥']: gain = val_n * 1.0
            else: gain = val_n
        elif check_good_friend(center, nb) and mode not in ['health', 'love']: gain = val_n * 0.5

        cost = 0
        if can_eat(pos_n, pos_c, current_gua):
            if name_n in ['象','相'] and name_c in ['車','俥']: cost = val_c * 0.5
            elif name_n in ['兵','卒'] and name_c in ['將','帥']: cost = val_c * 1.0
            else: cost = val_c
        elif check_good_friend(center, nb) and mode not in ['health', 'love']: cost = val_c * 0.5

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

    if mode == 'health':
        if report["score_A"]>0 and report["score_B"]>0: report["interpretation"] = "🌟 完美適配"
        elif report["score_A"]>0: report["interpretation"] = "⚠️ 吃心安"
        elif report["score_B"]>0: report["interpretation"] = "⚠️ 虛不受補"
        else: report["interpretation"] = "⭕ 無明顯互動"
    elif mode == 'love':
        diff = report["score_A"] - report["score_B"]; report["net_score"] = diff
        if diff > 5: report["interpretation"] = "❤️ 他愛你較多"
        elif diff < -5: report["interpretation"] = "💔 你愛他較多"
        else: report["interpretation"] = "⚖️ 關係對等"
    else:
        report["net_score"] = report["score_A"] - report["score_B"]; net = report["net_score"]
        if mode == 'investment': report["interpretation"] = "📈 可行 (獲利)" if net > 0 else "💸 不可行 (虧損)"
        else: report["interpretation"] = "🚀 運勢上揚" if net > 0 else "🛡️ 運勢低迷"
    return report

def get_marketing_strategy(current_gua):
    center = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    has_friend = any(check_good_friend(center, n) for n in neighbors)
    if has_friend: return "❤️ **感性行銷**：頻率相同，多聊理念。"
    else: return "📊 **理性行銷**：頻率不同，需拿數據。"

def get_past_life_reading(current_gua):
    center = next(p for p in current_gua if p[0] == 1); name = center[1]
    role = PAST_LIFE_ARCHETYPES.get(name, "平民")
    relations = []
    for pos in [2, 3]:
        p = next(p for p in current_gua if p[0] == pos)
        relations.append(f"左右 ({p[1]}): **平行/淺緣**。")
    for pos in [4, 5]:
        p = next(p for p in current_gua if p[0] == pos)
        relations.append(f"上下 ({p[1]}): **隔開/深緣**。")
    return {"role": role, "relations": relations}

def calculate_net_gain_from_gua(current_gua):
    res = calculate_score_by_mode(current_gua, mode="investment")
    return {"gain": res["score_A"], "cost": res["score_B"], "net_gain": res["net_score"], "interactions": []}

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
    return {"role_title": data.get("role",""), "self_desc": data.get("self",""), "love_desc": data.get("love",""), "career_desc": data.get("career",""), "health_desc": data.get("health",""), "special_warnings": []}

def check_consumption_at_1_or_5(current_gua):
    p1 = next(p for p in current_gua if p[0] == 1); p5 = next(p for p in current_gua if p[0] == 5)
    return p1[1] == p5[1] and p1[2] == p5[2]

def check_interference(current_gua): return [] 

def analyze_trinity_detailed(current_gua): 
    p1 = next(p for p in current_gua if p[0] == 1); p4 = next(p for p in current_gua if p[0] == 4); p5 = next(p for p in current_gua if p[0] == 5)
    res = {"missing_heaven":None,"missing_human":None,"missing_earth":None}
    if check_consumption(p4,p1) or can_eat(4,1,current_gua): res["missing_heaven"]={"reason":"長輩壓力/消耗","desc":"缺長輩緣","advice":"謙卑，曬太陽"}
    if check_consumption(p5,p1) or can_eat(5,1,current_gua): res["missing_earth"]={"reason":"根基受損","desc":"財庫不穩","advice":"買房/定存"}
    neighbors = [2, 3, 4, 5]; has_friend = False
    for pos in neighbors:
        pn = next(p for p in current_gua if p[0] == pos)
        if check_good_friend(p1, pn): has_friend = True; break
    if not has_friend: res["missing_human"] = {"reason":"孤立無援","desc":"人和弱","advice":"修身養性"}
    return res
    
def analyze_holistic_health(current_gua):
    report = {"core": {}, "balance": {"excess":[], "lack":[]}, "interaction": []}
    center = next(p for p in current_gua if p[0] == 1)
    elm = ATTRIBUTES.get(center[1], {}).get("五行")
    if elm: 
        dt = FIVE_ELEMENTS_DETAILS.get(elm)
        report["core"] = {"name": center[1], "element": elm, "psycho": dt["psycho_msg"], "physio": dt["physio_msg"], "advice": dt["advice"]}
    return report

def analyze_coordinate_map(current_gua, gender):
    return {"top_support": "分析中", "center_status": "分析中", "bottom_foundation": "分析中", "love_relationship": "分析中", "peer_relationship": "分析中"}

def analyze_body_hologram(current_gua): return []
def check_career_pattern(current_gua):
    names = [p[1] for p in current_gua]
    return all(n in "".join(names) for n in ['車','馬','包']) or all(n in "".join(names) for n in ['俥','傌','炮'])
def check_wealth_pattern(current_gua): return False
