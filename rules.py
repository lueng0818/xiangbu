import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION

# ==============================================================================
# 輔助：棋子類型映射 (用於判斷同類棋子)
# ==============================================================================
PIECE_TYPE_MAP = {
    '帥': '將', '將': '將',
    '仕': '士', '士': '士',
    '相': '象', '象': '象',
    '俥': '車', '車': '車',
    '傌': '馬', '馬': '馬',
    '炮': '包', '包': '包',
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
    """單次占卜：從完整32支棋中隨機抽出5支 (允許重複棋子，如雙紅兵)"""
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
    """判斷兩隻棋是否屬於同一類 (例如 仕 vs 士)"""
    return PIECE_TYPE_MAP.get(name1) == PIECE_TYPE_MAP.get(name2)

def check_good_friend(p1, p2):
    """判斷是否為好朋友 (同類不同色)"""
    return is_same_type(p1[1], p2[1]) and p1[2] != p2[2]

def check_consumption(p1, p2):
    """判斷是否為消耗 (同類同色)"""
    return is_same_type(p1[1], p2[1]) and p1[2] == p2[2]

def analyze_trinity_detailed(current_gua):
    """
    【新增】詳細的三才缺失分析 (天地人)
    根據邏輯：消耗/相剋/被吃/孤立
    """
    p1 = next(p for p in current_gua if p[0] == 1) # 中
    p4 = next(p for p in current_gua if p[0] == 4) # 上
    p5 = next(p for p in current_gua if p[0] == 5) # 下
    
    result = {
        "missing_heaven": None, # 缺天
        "missing_human": None,  # 缺人
        "missing_earth": None   # 缺地
    }
    
    # 1. 缺天判斷 (4 vs 1)
    is_heaven_consuming = check_consumption(p4, p1)
    is_heaven_eating_human = can_eat(4, 1, current_gua)
    
    if is_heaven_consuming or is_heaven_eating_human:
        reason = "消耗關係 (長輩固執)" if is_heaven_consuming else "相剋/被吃 (長輩給壓力)"
        result["missing_heaven"] = {
            "status": True,
            "reason": reason,
            "desc": "缺乏長輩緣、天助運差。個性易鐵齒、傲慢叛逆，不信無形力量。",
            "advice": "1. 謙卑：練習對長輩恭敬。\n2. 連結大自然：爬山、曬太陽補磁場。\n3. 佈施：捐血或捐款補福報。"
        }

    # 2. 缺地判斷 (5 vs 1)
    is_earth_consuming = check_consumption(p5, p1)
    is_earth_eating_human = can_eat(5, 1, current_gua)
    
    if is_earth_consuming or is_earth_eating_human:
        reason = "消耗關係" if is_earth_consuming else "相剋/被吃 (根基被毀)"
        result["missing_earth"] = {
            "status": True,
            "reason": reason,
            "desc": "缺乏根基、財庫不穩。做事虎頭蛇尾，錢財左手進右手出。",
            "advice": "1. 強迫儲蓄：錢放信任親友戶頭。\n2. 實體資產：買房或黃金，將流動轉為穩固。\n3. 保守投資：避免高風險投機。"
        }

    # 3. 缺人判斷 (1 vs 四周)
    neighbors = [2, 3, 4, 5]
    has_friend = False
    for pos in neighbors:
        pn = next(p for p in current_gua if p[0] == pos)
        if check_good_friend(p1, pn):
            has_friend = True
            break
            
    if not has_friend:
        result["missing_human"] = {
            "status": True,
            "reason": "孤立無援 (四周無好朋友)",
            "desc": "缺乏人和、自我中心。易目中無人，聽不進意見，孤軍奮戰。",
            "advice": "1. 修身養性：多聽少說，換位思考。\n2. 尋求合作：強制自己融入團隊，勿單打獨鬥。"
        }
        
    return result

# --- 既有函數 (保持不變) ---

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
            is_eater_chariot_at_1 = (eater_name in ['車', '俥'] and eater_pos == 1)
            is_target_horse = (target_name in ['馬', '傌'])
            if is_target_horse and is_eater_chariot_at_1: return True
            if eater_name in ['馬', '傌']: return False 

    if eater_name in ['馬', '傌']: return geometry == "斜位"
    elif eater_name in ['包', '炮']: return geometry == "縱隔山"
    elif eater_name in ['兵', '卒']: return (eater_pos == 5 and target_pos == 1) or (eater_pos == 1 and target_pos == 4)
    elif geometry == "十字":
        if eater_name in ['將', '帥', '士', '仕', '象', '相'] and target_name in ['將', '帥', '士', '仕', '象', '相']:
            return VALUE_MAP[eater_name] >= VALUE_MAP[target_name]
        return True
    return False

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

def analyze_health_and_luck(current_gua):
    analysis = {'red_count': 0, 'black_count': 0, 'missing_elements': {'木': True, '火': True, '土': True, '金': True, '水': True}, 'health_warnings': []}
    for pos, name, color, val in current_gua:
        analysis['red_count'] += (color == '紅')
        analysis['black_count'] += (color == '黑')
        element = ATTRIBUTES.get(name, {}).get('五行', 'N/A')[0]
        if element != 'N': analysis['missing_elements'][element] = False
    if analysis['red_count'] > analysis['black_count']: analysis['health_warnings'].append("紅多 (缺血氣旺)：建議多踩草地強化磁場。")
    elif analysis['black_count'] > analysis['red_count']: analysis['health_warnings'].append("黑多 (缺氣血旺)：建議多曬太陽、捐血佈施。")
    return analysis

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
    interactions = []
    for pos_a, name_a, color_a, val_a in current_gua:
        for pos_b, name_b, color_b, val_b in current_gua:
            if pos_a == pos_b: continue
            if can_eat(pos_a, pos_b, current_gua):
                gain_value = val_b * 0.5
                is_full_eat = False
                if name_a in ['兵', '卒'] and name_b in ['將', '帥']:
                    gain_value = val_b * 1.0
                    is_full_eat = True
                elif VALUE_MAP[name_a] > VALUE_MAP[name_b]: 
                    is_full_eat = True
                    gain_value = val_b * 1.0
                
                if name_a in ['象', '相'] and name_b in ['車', '俥']:
                    gain_value = val_b * 0.5
                    is_full_eat = False

                interactions.append({
                    "eater_pos": pos_a, "target_pos": pos_b, "eater_name": name_a, "target_name": name_b, 
                    "value": gain_value, "is_full_eat": is_full_eat, "target_initial_value": val_b
                })
    total_gain = 0.0
    interactions_by_eater = {}
    for i in interactions:
        pos = i['eater_pos']
        interactions_by_eater.setdefault(pos, []).append(i)
    for eater_pos, interactions_list in interactions_by_eater.items():
        if eater_pos == 1:
            total_gain += sum(i['value'] for i in interactions_list)
            continue
        interactions_list.sort(key=lambda x: x['value'], reverse=True)
        if not interactions_list: continue
        first_interaction = interactions_list[0]
        if first_interaction['is_full_eat']:
            counter_attack_found = any(i['eater_pos'] == first_interaction['target_pos'] and i['target_pos'] == eater_pos for i in interactions)
            if not counter_attack_found: total_gain += sum(i['value'] for i in interactions_list[:3])
        else: total_gain += first_interaction['value']
    total_cost = sum(p[3] for p in current_gua) * 0.1 
    return {"gain": round(total_gain, 2), "cost": round(total_cost, 2), "net_gain": round(total_gain - total_cost, 2), "interactions": interactions}
