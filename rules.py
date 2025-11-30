import random
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION

# ==============================================================================
# 核心邏輯函數
# ==============================================================================

def generate_random_gua():
    """單次占卜：隨機生成五支棋。"""
    all_pieces = [
        ('帥', '紅'), ('將', '黑'), 
        ('仕', '紅'), ('象', '黑'), 
        ('傌', '紅'), ('包', '黑'), 
        ('俥', '紅'), ('卒', '黑')  
    ]
    selected_pieces = random.sample(all_pieces, 5)
    
    gua = []
    positions = [1, 2, 3, 4, 5]
    for i in range(5):
        name, color = selected_pieces[i]
        gua.append((positions[i], name, color, VALUE_MAP.get(name, 0)))
    return gua

def generate_full_life_gua():
    """全盤流年：生成一副完整的32支棋。"""
    full_deck = []
    # 紅方
    full_deck.append(('帥', '紅'))
    full_deck.extend([('仕', '紅')] * 2); full_deck.extend([('相', '紅')] * 2)
    full_deck.extend([('俥', '紅')] * 2); full_deck.extend([('傌', '紅')] * 2); full_deck.extend([('炮', '紅')] * 2)
    full_deck.extend([('兵', '紅')] * 5)
    # 黑方
    full_deck.append(('將', '黑'))
    full_deck.extend([('士', '黑')] * 2); full_deck.extend([('象', '黑')] * 2)
    full_deck.extend([('車', '黑')] * 2); full_deck.extend([('馬', '黑')] * 2); full_deck.extend([('包', '黑')] * 2)
    full_deck.extend([('卒', '黑')] * 5)
    
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
    """
    判斷吃子規則 (依據指南第五章)。
    """
    eater = next(p for p in current_gua if p[0] == eater_pos)
    target = next(p for p in current_gua if p[0] == target_pos)
    eater_name, eater_color = eater[1], eater[2]
    target_name, target_color = target[1], target[2]
    
    if eater_color == target_color: return False # 同色不吃
    try: geometry = GEOMETRY_RELATION[eater_pos][target_pos]
    except KeyError: return False

    # 1. 特殊格局豁免 (眾星拱月/一枝獨秀)
    exemption_info = check_exemption(current_gua)
    if exemption_info:
        pattern_type, unique_pos, unique_name = exemption_info
        if pattern_type == "眾星拱月" and target_pos == 1: return False 
        if pattern_type == "一枝獨秀" and target_pos == unique_pos:
            # 除非是馬炮，否則正門攻不進
            if eater_name not in ['馬', '傌', '包', '炮']: return False
            # 簡化判斷：若為馬炮攻擊獨秀，暫定可攻入
            return True

    # 2. 移動規則驗證
    is_move_valid = False
    if eater_name in ['馬', '傌']: is_move_valid = (geometry == "斜位")
    elif eater_name in ['包', '炮']: is_move_valid = (geometry == "縱隔山")
    elif eater_name in ['兵', '卒']: is_move_valid = ((eater_pos == 5 and target_pos == 1) or (eater_pos == 1 and target_pos == 4))
    elif geometry == "十字": is_move_valid = True # 車、將、士、象走十字
    
    if not is_move_valid: return False

    # 3. 位階大小驗證 (指南 5.2: 只有將士象有位階問題，其他位子對了就吃)
    rank_group = ['將', '帥', '士', '仕', '象', '相']
    
    # 情況 A: 攻擊者是位階組 (將士象)
    if eater_name in rank_group:
        if target_name in rank_group:
            # 必須大吃小或平級
            return VALUE_MAP[eater_name] >= VALUE_MAP[target_name]
        else:
            # 將士象 吃 車馬包兵 -> 可以吃 (位階高)
            return True
            
    # 情況 B: 攻擊者是功能組 (車馬包兵) -> 位子對了就吃，忽略位階
    # (例外處理會在 calculate_net_gain 中計算分數係數，如象吃車半支)
    return True

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
    if analysis['red_count'] > analysis['black_count']: analysis['health_warnings'].append("紅多 (缺血氣旺)：易發炎急躁，建議多赤腳踩草地。")
    elif analysis['black_count'] > analysis['red_count']: analysis['health_warnings'].append("黑多 (缺氣血旺)：易氣滯陰沉，建議多曬太陽補陽。")
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
    """
    計算總收穫 (Gain) 與付出 (Cost)。
    依據指南第五章：能量互動法則。
    """
    interactions = []
    
    # 1. 識別所有可能的單次攻擊
    for pos_a, name_a, color_a, val_a in current_gua: # A 是攻擊者
        for pos_b, name_b, color_b, val_b in current_gua: # B 是被吃者
            if pos_a == pos_b: continue
            
            if can_eat(pos_a, pos_b, current_gua):
                # 基礎收穫：吃對方的分數 (吃一半預設為 0.5)
                modifier = 0.5 
                is_full_eat = False
                
                # 特殊全吃規則 (Guide 5.2)
                # 兵卒吃將帥 -> 全吃
                if name_a in ['兵', '卒'] and name_b in ['將', '帥']:
                    modifier = 1.0
                    is_full_eat = True
                # 位階大吃小 (將吃士, 士吃象...) 通常視為全吃? 
                # 指南提到 "只有將帥...有位階大小...兵卒吃全將帥...其他都只能吃一半"?
                # 修正：指南說 "象相吃半車俥...兵卒吃全將帥...其他都只能吃一半"。
                # 這意味著標準的大吃小也只是吃一半 (能量互動非毀滅性)
                # 但為了符合 "第一支吃全支才能續攻"，必須有更多全吃條件。
                # 假設：位階高吃位階低 = 全吃 (邏輯推斷，否則將帥太弱)
                elif VALUE_MAP[name_a] > VALUE_MAP[name_b]: 
                    modifier = 1.0
                    is_full_eat = True
                
                # 特殊半吃規則
                if name_a in ['象', '相'] and name_b in ['車', '俥']:
                    modifier = 0.5 # 象吃半車 (特定規則)
                    is_full_eat = False
                
                # 計算單次收穫與付出
                # 收穫 = 對方價值 * 係數
                # 付出 = 我方價值 (投入成本)
                gain = val_b * modifier
                cost = val_a 
                
                interactions.append({
                    "eater_pos": pos_a, "target_pos": pos_b, 
                    "eater_name": name_a, "target_name": name_b, 
                    "gain": gain, "cost": cost,
                    "is_full_eat": is_full_eat
                })
    
    # 2. 計算總分 (考慮續攻)
    total_gain = 0.0
    total_cost = 0.0
    
    interactions_by_eater = {}
    for i in interactions:
        pos = i['eater_pos']
        interactions_by_eater.setdefault(pos, []).append(i)
        
    for eater_pos, interactions_list in interactions_by_eater.items():
        # 排序：優先吃最有價值的
        interactions_list.sort(key=lambda x: x['gain'], reverse=True)
        
        # 判斷能否得分 (續攻規則)
        valid_attacks = []
        
        # 規則：位置 1 (中心) 四邊得分
        if eater_pos == 1:
            valid_attacks = interactions_list
        else:
            # 其他位置：第一支必須全吃才能續攻
            first_attack = interactions_list[0]
            if first_attack['is_full_eat']:
                # 檢查是否被擋 (對方是否反吃我)
                is_blocked = False
                for other_i in interactions:
                    if other_i['eater_pos'] == first_attack['target_pos'] and other_i['target_pos'] == eater_pos:
                        is_blocked = True
                        break
                
                if not is_blocked:
                    valid_attacks = interactions_list[:3] # 最多續攻3次
            else:
                # 只吃半支，無法續攻，只算這一次
                valid_attacks = [first_attack]
        
        # 累加分數
        for attack in valid_attacks:
            total_gain += attack['gain']
            # 付出只算一次 (啟動成本)，還是每次攻擊都算? 
            # 假設：同一隻棋子發動一輪攻擊，成本只算一次 (它的價值)
        
        if valid_attacks:
            # 加上發動攻擊這隻棋子的成本
            # 注意：如果同一隻棋子在多個 valid_attacks 中，這裡只加一次
            total_cost += interactions_list[0]['cost'] 

    return {
        "gain": round(total_gain, 1), 
        "cost": round(total_cost, 1), 
        "net_gain": round(total_gain - total_cost, 1), 
        "interactions": interactions
    }
