import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION, FIVE_ELEMENTS_DETAILS, ENERGY_REMEDIES, PIECE_SYMBOLISM, SYMBOL_KEY_MAP, PAST_LIFE_ARCHETYPES, LIFE_STAGES

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
# 核心邏輯函數 (生成與基礎)
# ==============================================================================

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
    full_gua = {}
    full_gua["raw_flow"] = full_deck 
    start_index = 0
    for stage in LIFE_STAGES:
        stage_pieces_raw = full_deck[start_index : start_index + 5]
        start_index += 5
        stage_gua = []
        for i in range(5):
            name, color = stage_pieces_raw[i]
            stage_gua.append(((positions := [1, 2, 3, 4, 5])[i], name, color, VALUE_MAP.get(name, 0)))
        full_gua[stage] = stage_gua
    full_gua["餘棋"] = full_deck[30:]
    return full_gua

# --- 基礎判斷邏輯 ---
def is_same_type(name1, name2): return PIECE_TYPE_MAP.get(name1) == PIECE_TYPE_MAP.get(name2)

def check_good_friend(p1, p2): 
    """判斷好朋友 (同字不同色，含馬炮特殊位)"""
    base_check = is_same_type(p1[1], p2[1]) and p1[2] != p2[2]
    
    # 馬傌需斜對 (1與2345皆非斜對，但在五支棋盤面中，通常指互動關係)
    # 這裡簡化為：只要同字不同色即視為廣義好朋友，特殊位置由格局掃描處理
    
    # 特殊親密格 (黑士紅俥 / 紅仕黑車)
    special_intimacy = False
    n1, c1 = p1[1], p1[2]
    n2, c2 = p2[1], p2[2]
    if (n1 in ['士','仕'] and n2 in ['車','俥']) or (n1 in ['車','俥'] and n2 in ['士','仕']):
        if c1 != c2: special_intimacy = True

    return base_check or special_intimacy

def check_consumption(p1, p2):
    return is_same_type(p1[1], p2[1]) and p1[2] == p2[2]

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
    try:
        eater = next(p for p in current_gua if p[0] == eater_pos)
        target = next(p for p in current_gua if p[0] == target_pos)
    except StopIteration: return False
    eater_name, eater_color = eater[1], eater[2]
    target_name, target_color = target[1], target[2]
    if eater_color == target_color: return False 
    try: geometry = GEOMETRY_RELATION[eater_pos][target_pos]
    except KeyError: return False

    exemption = check_exemption(current_gua)
    if exemption:
        if exemption[0] == "眾星拱月" and target_pos == 1: return False
        if exemption[0] == "一枝獨秀" and target_pos == exemption[1]:
            if eater_name in ['馬', '傌', '包', '炮']: 
                if eater_name in ['馬', '傌'] and target_pos == 1 and target_name in ['車', '俥']: return False
                return True
            return False
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

# ==============================================================================
# 【核心升級】特殊格局掃描引擎 (Rules 1-11)
# ==============================================================================
def check_special_patterns(current_gua):
    patterns = []
    p_map = {p[0]: p for p in current_gua}
    colors = {pos: p[2] for pos, p in p_map.items()}
    names = {pos: p[1] for pos, p in p_map.items()}
    all_names = [p[1] for p in current_gua]
    center = p_map[1]

    # 1. 好朋友格 (Good Friends)
    # 掃描與中心(1)的好朋友關係
    for pos in [2,3,4,5]:
        if check_good_friend(center, p_map[pos]):
            friend_type = ""
            n = center[1]
            if n in ['士','仕']: friend_type = " (最佳/心靈契合)"
            elif n in ['象','相']: friend_type = " (次之/穩重)"
            elif n in ['車','俥']: friend_type = " (各持己見)"
            elif n in ['兵','卒']: friend_type = " (踏實)"
            elif n in ['馬','傌','包','炮']: friend_type = " (曖昧/桃花)"
            
            # 特殊親密格檢查
            n_other = p_map[pos][1]
            if (n in ['士','仕'] and n_other in ['車','俥']) or (n in ['車','俥'] and n_other in ['士','仕']):
                patterns.append({"name": f"💞 親密格 (位{pos})", "desc": "互相欣賞，非關感情的特殊好感。"})
            else:
                patterns.append({"name": f"🤝 好朋友格 (位{pos})", "desc": f"互利互惠{friend_type}。"})

    # 2. 消耗格 (Consumption) - 同字同色
    for pos in [2,3,4,5]:
        if check_consumption(center, p_map[pos]):
            n = center[1]
            desc = ""
            if n in ['士','仕']: desc = "自以為是、憂慮 (傷肺/大腸)。"
            elif n in ['象','相']: desc = "情緒火氣大 (傷心)。"
            elif n in ['車','俥']: desc = "太衝、太激進、管太多 (傷肝)。"
            elif n in ['馬','傌']: desc = "意念紛飛、心太軟 (傷肝)。"
            elif n in ['包','炮']: desc = "恐懼、取巧 (傷腎)。"
            elif n in ['兵','卒']: desc = "想太多、行動力弱 (傷脾胃)。"
            elif n in ['將','帥']: desc = "固執、唯我獨尊。"
            patterns.append({"name": f"📉 消耗格 (位{pos})", "desc": desc})

    # 3. 破壞格 (Destruction)
    # 同字一黑二紅 或 一紅二黑
    # 統計各棋種的顏色數量
    type_counts = {}
    for p in current_gua:
        t = PIECE_TYPE_MAP.get(p[1])
        if t not in type_counts: type_counts[t] = {'紅':0, '黑':0}
        type_counts[t][p[2]] += 1
    
    for t, counts in type_counts.items():
        total = counts['紅'] + counts['黑']
        if total == 3:
            if (counts['紅']==1 and counts['黑']==2) or (counts['紅']==2 and counts['黑']==1):
                 patterns.append({"name": f"⚡ 破壞格 ({t})", "desc": "人際、決策受到干擾，留意小人壞話。"})

    # 4. 通吃格 (All-kill)
    # 兵象包象仕混雜，無保護被吃
    # 簡化判斷：若中心被 >=3 方吃，且無好朋友
    be_eaten_count = sum(1 for pos in [2,3,4,5] if can_eat(pos, 1, current_gua))
    has_friend = any(check_good_friend(center, p_map[pos]) for pos in [2,3,4,5])
    if be_eaten_count >= 3 and not has_friend:
         patterns.append({"name": "☠️ 通吃格", "desc": "孤立無援，需留餘地，全盤皆輸風險大。"})

    # 5. 富貴格 (Wealth) - 將士相
    has_gen = any(n in ['將', '帥'] for n in all_names)
    has_adv = any(n in ['士', '仕'] for n in all_names)
    has_ele = any(n in ['象', '相'] for n in all_names)
    if has_gen and has_adv and has_ele:
        trend = "往上愈好" if p_map[4][1] in ['將','帥','士','仕','象','相'] else "後段加強"
        patterns.append({"name": "💰 富貴格", "desc": f"有人幫做事，行動力弱。{trend}。"})

    # 6. 事業格 (Career) - 車馬包
    has_car = any(n in ['車', '俥'] for n in all_names)
    has_hor = any(n in ['馬', '傌'] for n in all_names)
    has_can = any(n in ['包', '炮'] for n in all_names)
    if has_car and has_hor and has_can:
        trend = "往上愈好" if p_map[4][1] in ['車','俥','馬','傌','包','炮'] else "後段加強"
        patterns.append({"name": "🏆 事業格", "desc": f"氣勢強、敢衝，不利感情。{trend}。"})

    # 7. 困擾格 (Dilemma) - 兩對好朋友
    friend_pairs = 0
    checked = []
    for i in range(1, 6):
        for j in range(i+1, 6):
            if i in checked or j in checked: continue
            if check_good_friend(p_map[i], p_map[j]):
                friend_pairs += 1
                checked.extend([i, j])
    if friend_pairs >= 2:
        patterns.append({"name": "😵 困擾格", "desc": "兩對好朋友，人際與決定上的困擾 (桃花或選擇多)。"})
        
    # 8. 三人同心格 (Unity)
    if sum(1 for n in all_names if n in ['兵', '卒']) >= 3:
        patterns.append({"name": "🤝 三人同心格", "desc": "三支兵卒，志同道合，氣勢如車。"})

    # 9. 勝利格 (Victory) - V型 (2,3,5)
    if colors[2] == colors[3] == colors[5]: # 假設同色即構成V
        winner = "自己勝利" if any(check_good_friend(center, p_map[n]) for n in [2,3,5]) else "他人勝利"
        patterns.append({"name": f"✌️ 勝利格 ({winner})", "desc": "V型同色。"})

    # 10. 雨傘格 (Umbrella) - 2,3,4 同色
    if colors[2] == colors[3] == colors[4]:
        u_type = "紅傘 (外界看好)" if colors[4] == "紅" else "黑傘 (外界不看好)"
        patterns.append({"name": f"☔ 雨傘格 ({u_type})", "desc": "有天助保護，但視野受限(悶)。"})

    # 11. 十字天助格 (Cross)
    if (colors[1] == colors[4] == colors[5]) or (colors[1] == colors[2] == colors[3]):
         patterns.append({"name": "✝️ 十字天助格", "desc": "有天助，逢凶化吉。"})

    # 補充：鬱卒/眾星/一枝獨秀 (依賴 check_exemption 判斷)
    exemp = check_exemption(current_gua)
    if exemp:
        p_name, _, _ = exemp
        if p_name == "眾星拱月": patterns.append({"name": f"🌟 {p_name}", "desc": "外人看好，內心有壓力。"})
        if p_name == "一枝獨秀": patterns.append({"name": f"🌲 {p_name}", "desc": "情緒起伏大，易犯小人(若非馬炮)。"})

    return patterns

# --- 其他功能函數 (保持不變) ---
def calculate_score_by_mode(current_gua, mode="general"):
    center = next(p for p in current_gua if p[0] == 1)
    neighbors = [p for p in current_gua if p[0] != 1]
    report = {"score_A": 0.0, "score_B": 0.0, "net_score": 0.0, "label_A": "", "label_B": "", "label_Net": "", "details_A": [], "details_B": [], "interpretation": "", "health_status": []}
    config = {
        "general": ("助力 (+)", "壓力 (-)", "運勢損益"), "career": ("掌控權 (+)", "被剝奪感 (-)", "權力指數"),
        "karma": ("索取/討債 (+)", "虧欠/償債 (-)", "因果餘額"), "health": ("吸收力", "修復力", "療癒效能"),
        "investment": ("收穫 (+)", "成本 (-)", "投資淨利"), "love": ("對方愛我", "我愛對方", "情感權重"),
        "divorce": ("自由度 (+)", "損耗度 (-)", "離異指數"), "transaction": ("成交機率", "阻力成本", "成交指數")
    }
    lbl_A, lbl_B, lbl_Net = config.get(mode, config["general"])
    report["label_A"], report["label_B"], report["label_Net"] = lbl_A, lbl_B, lbl_Net

    for nb in neighbors:
        pos_n, name_n, val_n = nb[0], nb[1], VALUE_MAP.get(nb[1], 0)
        pos_c, name_c, val_c = center[0], center[1], VALUE_MAP.get(center[1], 0)
        gain = 0
        if can_eat(pos_c, pos_n, current_gua):
            if name_c in ['象','相'] and name_n in ['車','俥']: gain = val_n * 0.5
            elif name_c in ['兵','卒'] and name_n in ['將','帥']: gain = val_n * 1.0
            else: gain = val_n
        elif check_good_friend(center, nb) and mode not in ['health', 'love', 'transaction']: gain = val_n * 0.5

        cost = 0
        if can_eat(pos_n, pos_c, current_gua):
            if name_n in ['象','相'] and name_c in ['車','俥']: cost = val_c * 0.5
            elif name_n in ['兵','卒'] and name_c in ['將','帥']: cost = val_c * 1.0
            else: cost = val_c
        elif check_good_friend(center, nb) and mode not in ['health', 'love', 'transaction']: cost = val_c * 0.5

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
        elif mode == 'transaction':
            if check_good_friend(center, nb): report["score_A"] += 20; report["details_A"].append(f"{name_n}: 好朋友 (+20)")
            elif gain > 0: report["score_A"] += gain; report["details_A"].append(f"吃 {name_n}: +{gain}")
            if cost > 0: report["score_B"] += cost; report["details_B"].append(f"被 {name_n} 吃: -{cost}")
        else:
            if gain > 0: report["score_A"] += gain; report["details_A"].append(f"吃 {name_n}: +{gain}")
            if cost > 0: report["score_B"] += cost; report["details_B"].append(f"被 {name_n} 吃: -{cost}")

    if mode == 'health':
        if report["score_A"]>0 and report["score_B"]>0: report["interpretation"] = "🌟 完美適配"
        elif report["score_A"]>0: report["interpretation"] = "⚠️ 吃心安"
        elif report["score_B"]>0: report["interpretation"] = "⚠️ 虛不受補"
        else: report["interpretation"] = "⭕ 無明顯互動"
    elif mode == 'transaction':
        net = report["score_A"] - report["score_B"]; report["net_score"] = net
        if net > 15: report["interpretation"] = "🤝 高成交率"
        elif net > 0: report["interpretation"] = "🗣️ 需說服"
        else: report["interpretation"] = "🧱 阻力大"
    elif mode == 'love':
        diff = report["score_A"] - report["score_B"]; report["net_score"] = diff
        if diff > 5: report["interpretation"] = "❤️ 他愛你較多"
        elif diff < -5: report["interpretation"] = "💔 你愛他較多"
        else: report["interpretation"] = "⚖️ 關係對等"
    else:
        report["net_score"] = report["score_A"] - report["score_B"]; net = report["net_score"]
        if mode == 'investment': report["interpretation"] = "📈 可行" if net > 0 else "💸 不可行"
        elif mode == 'general': report["interpretation"] = "🚀 運勢上揚" if net > 0 else "🛡️ 運勢低迷"
    return report

def analyze_health_and_luck(current_gua):
    analysis = {'red_count': 0, 'black_count': 0, 'health_warnings': [], 'remedy': {}}
    for p in current_gua: analysis['red_count'] += (p[2]=='紅'); analysis['black_count'] += (p[2]=='黑')
    rc, bc = analysis['red_count'], analysis['black_count']
    if (rc==2 and bc==3) or (rc==3 and bc==2): analysis['balance_msg'] = "✅ **二三配：** 情緒穩定。"
    elif (rc==1 and bc==4) or (rc==4 and bc==1): analysis['balance_msg'] = "⚠️ **一四配：** 情緒起伏大。"
    else: analysis['balance_msg'] = "⚠️ **全色格：** 氣場偏頗。"
    if rc > bc: analysis['remedy'] = ENERGY_REMEDIES["Red"]
    elif bc > rc: analysis['remedy'] = ENERGY_REMEDIES["Black"]
    else: analysis['remedy'] = {"status": "氣血平衡", "advice": "維持現狀", "method": "規律作息", "principle": "陰陽調和"}
    analysis['health_warnings'].append(f"{analysis['remedy']['status']}: {analysis['remedy']['advice']}")
    return analysis

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
    for pos in [2, 3]: relations.append(f"左右: **平行/淺緣** (同事/鄰居)。")
    for pos in [4, 5]: relations.append(f"上下: **隔開/深緣** (深刻羈絆)。")
    return {"role": role, "relations": relations}

def calculate_net_gain_from_gua(current_gua):
    res = calculate_score_by_mode(current_gua, mode="investment")
    return {"gain": res["score_A"], "cost": res["score_B"], "net_gain": res["net_score"], "interactions": []}

def get_advanced_piece_analysis(current_gua):
    center = next(p for p in current_gua if p[0] == 1)
    sym_key = SYMBOL_KEY_MAP.get(center[1], "兵卒")
    data = PIECE_SYMBOLISM.get(sym_key, {})
    return {"role_title": data.get("role",""), "self_desc": data.get("self",""), "love_desc": data.get("love",""), "career_desc": data.get("career",""), "health_desc": data.get("health",""), "special_warnings": []}

def check_consumption_at_1_or_5(current_gua):
    p1 = next(p for p in current_gua if p[0] == 1); p5 = next(p for p in current_gua if p[0] == 5)
    return p1[1] == p5[1] and p1[2] == p5[2]

def check_interference(current_gua):
    events = []
    for pos_a, name_a, color_a, val_a in current_gua:
        if name_a in ['馬', '傌', '包', '炮']:
            if can_eat(pos_a, 1, current_gua):
                type_ = "犯小人/卡陰" if name_a in ['馬', '傌'] else "投資虧損"
                events.append(f"{color_a}{name_a} 剋入 ({type_})")
    return events

def analyze_trinity_detailed(current_gua): 
    p1 = next(p for p in current_gua if p[0] == 1); p4 = next(p for p in current_gua if p[0] == 4); p5 = next(p for p in current_gua if p[0] == 5)
    res = {"missing_heaven":None,"missing_human":None,"missing_earth":None}
    if check_consumption(p4,p1) or can_eat(4,1,current_gua): res["missing_heaven"]={"reason":"長輩壓力","desc":"缺長輩緣","advice":"謙卑，曬太陽"}
    if check_consumption(p5,p1) or can_eat(5,1,current_gua): res["missing_earth"]={"reason":"根基受損","desc":"財庫不穩","advice":"買房/定存"}
    if not any(check_good_friend(p1, next(p for p in current_gua if p[0]==pos)) for pos in [2,3,4,5]):
        res["missing_human"] = {"reason":"孤立無援","desc":"人和弱","advice":"修身養性"}
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
    p1 = next(p for p in current_gua if p[0] == 1); p4 = next(p for p in current_gua if p[0] == 4); p5 = next(p for p in current_gua if p[0] == 5)
    p2 = next(p for p in current_gua if p[0] == 2); p3 = next(p for p in current_gua if p[0] == 3)
    report = {"center_status": "", "top_support": "", "bottom_foundation": "", "love_relationship": "", "peer_relationship": ""}
    p1_attr = ATTRIBUTES.get(p1[1], {})
    report["center_status"] = f"核心 **{p1[2]}{p1[1]}** ({p1_attr.get('特質')})。"
    report["top_support"] = "貴人提拔" if check_good_friend(p1, p4) else "關係平淡"
    report["bottom_foundation"] = "根基穩固" if check_good_friend(p1, p5) else "漂泊無根"
    love_pos = 2 if gender == "男" else 3; p_love = p2 if gender == "男" else p3
    report["love_relationship"] = "感情甜蜜" if check_good_friend(p1, p_love) else "緣分平平"
    peer_pos = 3 if gender == "男" else 2; p_peer = p3 if gender == "男" else p2
    report["peer_relationship"] = "得力夥伴" if check_good_friend(p1, p_peer) else "各自努力"
    return report

def analyze_body_hologram(current_gua):
    diagnosis = []
    for pos, name, color, val in current_gua:
        if pos == 4 and name in ['炮', '包']: diagnosis.append(f"🔴 頭部：**頭痛/失眠**")
        if pos == 5 and name in ['馬', '傌']: diagnosis.append(f"🦵 下肢：**關節/膝蓋**")
    return diagnosis

def check_career_pattern(current_gua):
    names = [p[1] for p in current_gua]
    return all(n in "".join(names) for n in ['車','馬','包']) or all(n in "".join(names) for n in ['俥','傌','炮'])
def check_wealth_pattern(current_gua):
    names = [p[1] for p in current_gua]
    return all(n in "".join(names) for n in ['將','士','象']) or all(n in "".join(names) for n in ['帥','仕','相'])

def analyze_total_fate(full_gua_data):
    first_stage = LIFE_STAGES[0]; gua = full_gua_data.get(first_stage, [])
    if not gua: return {"type": "未知", "desc": "數據錯誤"}
    center = next(p for p in gua if p[0] == 1); name = center[1]
    if name in ['將', '帥']: return {"type": "👑 領袖格", "desc": "天生領導風範。"}
    else: return {"type": "🧱 實幹格", "desc": "腳踏實地。"}

def get_decade_advice(stage, gua):
    if "11~20" in stage: return {"focus":"學業", "advice":"平穩發展。"}
    else: return {"focus":"運勢", "advice":"保重身體。"}

def analyze_color_flow(full_deck): return "✅ 氣場流動正常。"

def check_divorce_pattern(current_gua, gender):
    if gender != "女": return {"is_risk": False, "warnings": [], "advice": ""}
    p1 = next(p for p in current_gua if p[0] == 1); name = p1[1]
    if name in ['將', '帥']: return {"is_risk": True, "warnings": ["核心強勢"], "advice": "需尋回自我。"}
    return {"is_risk": False, "warnings": [], "advice": "結構尚穩。"}

def check_peach_blossom_detailed(current_gua):
    p_names = [p[1] for p in current_gua]
    if '包' in p_names or '炮' in p_names: return {"is_true_peach": True, "type": "桃花格", "desc": "人緣好。"}
    return {"is_true_peach": False, "type": "無", "desc": ""}

def check_safety_issues(current_gua):
    warnings = []
    for p in current_gua:
        if p[0] != 1 and can_eat(p[0], 1, current_gua):
            if p[1] in ['車', '俥']: warnings.append("🚗 車關警示")
            if p[1] in ['士', '仕']: warnings.append("🏥 血光警示")
    return warnings
