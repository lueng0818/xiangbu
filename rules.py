import random
# 修正導入：從同級檔案 data.py 導入
from data import VALUE_MAP, ATTRIBUTES, PIECE_NAMES, GEOMETRY_RELATION

# ==============================================================================
# 核心邏輯函數
# ==============================================================================

def generate_random_gua():
    """
    隨機生成五支棋。
    模擬真實抽棋：建立一副完整的 32 支象棋，洗牌後抽出 5 支。
    """
    # 建立一副完整的象棋 (32支)
    full_deck = []
    # 紅方
    full_deck.extend([('帥', '紅'), ('仕', '紅'), ('仕', '紅'), ('相', '紅'), ('相', '紅'), 
                      ('俥', '紅'), ('俥', '紅'), ('傌', '紅'), ('傌', '紅'), ('炮', '紅'), ('炮', '紅')])
    full_deck.extend([('兵', '紅')] * 5)
    # 黑方
    full_deck.extend([('將', '黑'), ('士', '黑'), ('士', '黑'), ('象', '黑'), ('象', '黑'), 
                      ('車', '黑'), ('車', '黑'), ('馬', '黑'), ('馬', '黑'), ('包', '黑'), ('包', '黑')])
    full_deck.extend([('卒', '黑')] * 5)
    
    # 隨機抽出 5 支
    selected_pieces = random.sample(full_deck, 5)
    
    gua = []
    positions = [1, 2, 3, 4, 5]
    for i in range(5):
        name, color = selected_pieces[i]
        gua.append((
            positions[i],
            name,
            color,
            VALUE_MAP.get(name, 0)
        ))
    return gua

def is_all_same_color(current_gua):
    """檢查卦象是否為「全黑全紅格」（不成卦）。"""
    if not current_gua:
        return True
    first_color = current_gua[0][2]
    for pos, name, color, val in current_gua:
        if color != first_color:
            return False
    return True

def check_exemption(current_gua):
    """檢查是否符合眾星拱月或一枝獨秀，並返回豁免信息。"""
    color_counts = {'紅': 0, '黑': 0}
    for pos, name, color, val in current_gua:
        color_counts[color] += 1

    unique_color = None
    if color_counts['紅'] == 4 and color_counts['黑'] == 1:
        unique_color = '黑'
    elif color_counts['黑'] == 4 and color_counts['紅'] == 1:
        unique_color = '紅'
    
    if unique_color:
        unique_piece = next(p for p in current_gua if p[2] == unique_color)
        unique_pos, unique_name = unique_piece[0], unique_piece[1]
        
        if unique_pos == 1:
            return ("眾星拱月", unique_pos, unique_name)
        else:
            return ("一枝獨秀", unique_pos, unique_name)
    return None

def can_eat(eater_pos, target_pos, current_gua):
    """
    判斷攻擊方 (eater) 是否可以吃掉目標方 (target)。
    (包含移動規則、位階和特殊格局豁免)
    """
    
    eater = next(p for p in current_gua if p[0] == eater_pos)
    target = next(p for p in current_gua if p[0] == target_pos)
    
    eater_name, eater_color = eater[1], eater[2]
    target_name, target_color = target[1], target[2]
    
    if eater_color == target_color: return False
    
    try:
        geometry = GEOMETRY_RELATION[eater_pos][target_pos]
    except KeyError:
        return False

    # 1. 特殊格局豁免規則檢查
    exemption_info = check_exemption(current_gua)
    if exemption_info:
        pattern_type, unique_pos, unique_name = exemption_info
        if pattern_type == "眾星拱月" and target_pos == 1: return False # 中心不能被吃
        if pattern_type == "一枝獨秀" and target_pos == unique_pos:
            if eater_name not in ['馬', '傌', '包', '炮']: return False # 正門攻擊失敗
            
            is_eater_chariot_at_1 = (eater_name in ['車', '俥'] and eater_pos == 1)
            is_target_horse = (target_name in ['馬', '傌'])
            # 特例：我方1唯車俥可吃馬傌
            if is_target_horse and is_eater_chariot_at_1: return True
            # 特例：攻擊者也是馬傌，通常很難攻入獨秀，這裡保守返回 False
            if eater_name in ['馬', '傌']: return False 

    # 2. 正常移動規則判斷
    if eater_name in ['馬', '傌']: return geometry == "斜位"
    elif eater_name in ['包', '炮']: return geometry == "縱隔山"
    elif eater_name in ['兵', '卒']: 
        return (eater_pos == 5 and target_pos == 1) or (eater_pos == 1 and target_pos == 4)
            
    # 3. 其他皆吃十字 (將帥、士仕、象相、車俥)
    elif geometry == "十字":
        if eater_name in ['將', '帥', '士', '仕', '象', '相'] and target_name in ['將', '帥', '士', '仕', '象', '相']:
            return VALUE_MAP[eater_name] >= VALUE_MAP[target_name] # 位階大小
        return True # 其他棋子 (車) 只要十字對了就可以吃
            
    return False

def check_consumption_at_1_or_5(current_gua):
    """
    專家優化：檢查總格 1 或 5 是否出現「消耗格」（兩支同色同字）。
    用於判斷不孕風險。
    """
    pieces_at_1_and_5 = [p for p in current_gua if p[0] in [1, 5]]
    
    name_color_counts = {}
    for pos, name, color, val in pieces_at_1_and_5:
        key = (name, color)
        name_color_counts[key] = name_color_counts.get(key, 0) + 1
        
    for (name, color), count in name_color_counts.items():
        if count >= 2:
            return True
    return False

def check_interference(current_gua):
    """
    專家優化：檢查是否有馬傌包炮成功攻擊到核心位置 (1, 2, 3)。
    返回干擾事件列表。
    """
    interference_events = []
    core_targets = [1, 2, 3] # 中、左、右 為核心目標
    
    for pos_a, name_a, color_a, val_a in current_gua:
        if name_a not in ['馬', '傌', '包', '炮']:
            continue
            
        for pos_b in core_targets:
            if pos_a == pos_b: continue 
            
            if can_eat(pos_a, pos_b, current_gua):
                target_piece = next(p for p in current_gua if p[0] == pos_b)
                
                if name_a in ['馬', '傌']:
                    inter_type = "犯小人/卡陰"
                else:
                    inter_type = "投資虧損/時機不佳" 
                
                interference_events.append({
                    "attacker": f"{color_a}{name_a} (位{pos_a})",
                    "target": f"{target_piece[2]}{target_piece[1]} (位{pos_b})",
                    "type": inter_type
                })
    return interference_events

def analyze_health_and_luck(current_gua):
    """分析卦象中的紅黑比例、五行所缺和天地人三才。"""
    analysis = {
        'red_count': 0, 'black_count': 0,
        'missing_elements': {'木': True, '火': True, '土': True, '金': True, '水': True},
        'health_warnings': []
    }
    for pos, name, color, val in current_gua:
        analysis['red_count'] += (color == '紅')
        analysis['black_count'] += (color == '黑')
        element = ATTRIBUTES.get(name, {}).get('五行', 'N/A')[0]
        if element != 'N': analysis['missing_elements'][element] = False
    
    if analysis['red_count'] > analysis['black_count']:
        analysis['health_warnings'].append("紅多 (缺血氣旺)：建議多踩草地強化磁場。")
    elif analysis['black_count'] > analysis['red_count']:
        analysis['health_warnings'].append("黑多 (缺氣血旺)：建議多曬太陽、捐血佈施。")
    return analysis

def check_career_pattern(current_gua):
    """檢查是否符合事業格 (車俥、馬傌、包炮混色皆可)。"""
    names = [p[1] for p in current_gua]
    has_chariot = any(n in ['車', '俥'] for n in names)
    has_horse = any(n in ['馬', '傌'] for n in names)
    has_cannon = any(n in ['包', '炮'] for n in names)
    if has_chariot and has_horse and has_cannon: return True
    return False

def check_wealth_pattern(current_gua):
    """檢查是否符合富貴格 (將帥、士仕、象相混色皆可)。"""
    names = [p[1] for p in current_gua]
    has_general = any(n in ['將', '帥'] for n in names)
    has_minister = any(n in ['士', '仕'] for n in names)
    has_elephant = any(n in ['象', '相'] for n in names)
    if has_general and has_minister and has_elephant: return True
    return False

def calculate_net_gain_from_gua(current_gua):
    """計算總收穫 (Gain) 和總付出 (Cost)，包含續攻邏輯。"""
    interactions = []
    
    # 1. 識別所有可能的攻擊互動
    for pos_a, name_a, color_a, val_a in current_gua:
        for pos_b, name_b, color_b, val_b in current_gua:
            if pos_a == pos_b: continue
            if can_eat(pos_a, pos_b, current_gua):
                gain_value = val_b * 0.5
                is_full_eat = False
                if name_a in ['兵', '卒'] and name_b in ['將', '帥']:
                    gain_value = val_b * 1.0
                    is_full_eat = True
                interactions.append({
                    "eater_pos": pos_a, "target_pos": pos_b, "eater_name": name_a, "target_name": name_b, 
                    "value": gain_value, "is_full_eat": is_full_eat, "target_initial_value": val_b
                })
    
    # 2. 執行續攻與總得分計算
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
            if not counter_attack_found:
                # 若未被擋，前三高分累計
                total_gain += sum(i['value'] for i in interactions_list[:3])
        else:
            # 半吃只能算一次
            total_gain += first_interaction['value']
            
    total_cost = sum(p[3] for p in current_gua) * 0.1 

    return {
        "gain": round(total_gain, 2), "cost": round(total_cost, 2), 
        "net_gain": round(total_gain - total_cost, 2), "interactions": interactions
    }
