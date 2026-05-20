# -*- coding: utf-8 -*-
"""
npcdata 转换: KMS 合集格式 → GMS 独立文件 + 嵌套目录
KMS: npcdata/XXX.xml (合集, <ms2><npc id="X"><environment>...</environment></npc></ms2>)
GMS: npc/AA/BB/AAAAAAA.xml (独立, <ms2><environment><basic>...</basic>...</environment></ms2>)
"""

import os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
import xml.etree.ElementTree as ET

BASE = r'K:\SynologyDrive\RedMxdserver\Maple2_KC_Convert_to_Gms'
KMS_DIR = os.path.join(BASE, '2KMSXml', 'npcdata')
OUT_DIR = os.path.join(BASE, '5NewGMS', 'npc')

# KMS <environment> 中需要迁移到 GMS <basic> 的属性
ENV_TO_BASIC = [
    'friendly', 'npcAttackGroup', 'npcDefenseGroup', 'nametag', 'hitImmune',
    'abnormalImmune', 'level', 'class', 'carePathToEnemy', 'gender',
    'illust', 'emotionID', 'portrait'
]

# GMS <basic> 全部属性默认值
BASIC_DEFAULTS = {
    'friendly': '2',
    'npcAttackGroup': '2',
    'npcDefenseGroup': '1',
    'kind': '0',
    'iconName': '',
    'minimapIconName': '',
    'shopId': '0',
    'nametag': '1',
    'nametagSize': '18',
    'local': '0',
    'minimap': '1',
    'attackDamage': '0',
    'hpBar': '0',
    'defenceMaterial': '0',
    'hitImmune': '1',
    'abnormalImmune': '1',
    'level': '1',
    'class': '5',
    'rankIcon': '',
    'rotationDisabled': '0',
    'carePathToEnemy': '1',
    'npcSoundStart': '',
    'npcSoundEnd': '',
    'npcSoundCombatStart': '',
    'npcSoundCombatEnd': '',
    'npcSoundDead': '',
    'maxSpawnCount': '0',
    'groupSpawnCount': '0',
    'rareDegree': '0',
    'difficulty': '0',
    'propertyTags': '',
    'raceString': '',
    'bossNotify': '0',
    'gender': '0',
    'illust': '',
    'emotionID': '0',
    'mainTags': '',
    'subTags': '',
    'portrait': '',
    'talkAni': '0',
    'damagedColorScale': '2',
    'damagedVibrateDuration': '0',
    'damagedVibrateAmp': '0',
    'regenEffect': '',
    'deadEffect': '',
    'damageEffect': '',
    'createEffect': '',
    'keepEffect': '',
    'skipFrame': '1',
    'checkCameraDistance': '0',
    'extraCameraDistance': '0',
    'bossSoundDistance': '2000',
    'bossSoundEndDistance': '3000',
}

# GMS <stat> 属性默认值（KMS 的 stat 属性名不同，需要映射或跳过）
STAT_DEFAULTS = {
    'str': '0', 'dex': '0', 'int': '0', 'luk': '0',
    'hp': '0', 'hp_rgp': '0', 'hp_inv': '0',
    'sp': '0', 'sp_rgp': '0', 'sp_inv': '0',
    'ep': '0', 'ep_rgp': '0', 'ep_inv': '0',
    'asp': '0', 'msp': '100', 'atp': '0', 'evp': '0',
    'cap': '0', 'cad': '0', 'car': '0', 'ndd': '0',
    'abp': '0', 'jmp': '0', 'pap': '0', 'map': '100',
    'par': '0', 'mar': '0', 'wapmin': '0', 'wapmax': '0',
    'dmg': '0', 'pen': '0', 'rmsp': '0', 'bap': '0', 'bap_pet': '0',
}

# KMS <stat> 到 GMS 的属性映射（部分无法直接映射，用默认值）
# KMS: hp, msp, atp, evp, ndd, pap, map
# GMS: hp, msp, atp, evp, ndd, pap->pap, map->map (部分相同)
KMS_STAT_MAP = {
    'hp': 'hp',
    'msp': 'msp',
    'atp': 'atp',
    'evp': 'evp',
    'ndd': 'ndd',
    'pap': 'pap',
    'map': 'map',
}

# GMS 其他子节点默认值
OTHER_DEFAULTS = {
    'model': {'kfm': '', 'scale': '1.000000', 'anispeed': '1', 'anispeedfix': 'false', 'spawnAlphaAnimation': '0', 'offset': '0.000000,0.000000,0.000000'},
    'speed': {'rotation': '190', 'walk': '120', 'run': '0'},
    'distance': {'avoid': '0', 'sight': '0', 'sightHeightUP': '200', 'sightHeightDown': '50', 'customLastSightRadius': '0', 'customLastSightHeightUp': '0', 'customLastSightHeightDown': '0'},
    'skill': {'ids': '', 'levels': '', 'priorities': '', 'probs': '', 'coolDown': '0'},
    'additionalEffect': {'codes': '', 'levels': '', 'group': ''},
    'interact': {'interactFunction': '', 'interactCastingAnimation': '', 'interactCastingTime': '0', 'interactCoolTime': '0', 'interactIsShowCastingBar': 'true'},
    'combat': {'combatAbandonTick': '0', 'impossibleCombatAbandonTick': '0', 'ignoreExtendLifeTime': 'false', 'canShowHideTarget': 'false'},
    'assist': {'assistType1SkillCount': '0', 'assistType2SkillCount': '0', 'assistType2CheckTick': '0'},
    'aiInfo': {'path': ''},
    'collision': {'shape': '', 'width': '0', 'height': '0', 'depth': '0', 'widthOffset': '0', 'depthOffset': '0', 'heightOffset': '0'},
    'corpse': {'width': '0', 'height': '0', 'depth': '0', 'added': '0', 'offsetNametag': '0', 'corpseEffect': '', 'hitAble': '0', 'rotation': ''},
    'capsule': {'radius': '0', 'height': '0', 'ignore': '0'},
    'validBattleCylinder': {'radius': '0', 'height': '0'},
    'dead': {'time': '0', 'defaultaction': '', 'upaction': '', 'revival': '0', 'count': '0', 'lifeTime': '0', 'slowLastHit': '0', 'extendRoomTime': '0'},
    'push': {'back': '0', 'up': '0', 'knockback': '0'},
    'exp': {'customExp': '-1'},
    'shadow': {'scale': '250', 'bias': '1'},
    'normal': {'action': 'Idle_A', 'prob': '10000', 'movearea': '50', 'maidExpired': 'Idle_A'},
    'dropiteminfo': {'dropHeight': '0', 'dropDistanceBase': '50', 'dropDistanceRandom': '100', 'fireVelocity': '100', 'globalDropBoxId': '', 'globalDeadDropBoxId': '', 'individualDropBoxId': '', 'globalHitDropBoxId': '', 'individualHitDropBoxId': ''},
    'lookattarget': {'targetdummy': 'Bip01 Head', 'lookAtMyPCWhenTalking': '1', 'useTalkMotion': '1'},
}

def get_gms_path(npc_id):
    """计算 GMS 格式的路径: npc/AA/BB/AAAAAAAA.xml"""
    id_str = str(npc_id).zfill(8)
    aa = id_str[:2]
    bb = id_str[2:4]
    return os.path.join(OUT_DIR, aa, bb, f'{id_str}.xml')

def create_gms_environment(kms_npc):
    """从 KMS <npc> 创建 GMS <environment> 节点"""
    env = kms_npc.find('environment')
    if env is None:
        return None
    
    # 创建新的 <environment> (GMS 格式)
    new_env = ET.Element('environment')
    new_env.set('feature', env.get('feature', ''))
    new_env.set('locale', '')
    
    # 1. 创建 <basic> 子节点（从 KMS <environment> 属性迁移）
    basic = ET.SubElement(new_env, 'basic')
    for attr in ENV_TO_BASIC:
        val = env.get(attr)
        if val is not None:
            basic.set(attr, val)
    # 补充 <basic> 默认值（KMS 没有的属性）
    for attr, default in BASIC_DEFAULTS.items():
        if attr not in basic.attrib:
            basic.set(attr, default)
    
    # 2. 处理 <model>
    model = env.find('model')
    new_model = ET.SubElement(new_env, 'model')
    if model is not None:
        for k, v in model.attrib.items():
            new_model.set(k, v)
    # 补充 GMS <model> 独有属性
    for k, default in OTHER_DEFAULTS['model'].items():
        if k not in new_model.attrib:
            new_model.set(k, default)
    
    # 3. 处理 <stat>
    stat = env.find('stat')
    new_stat = ET.SubElement(new_env, 'stat')
    if stat is not None:
        # 映射 KMS stat 属性到 GMS
        for kms_attr, gms_attr in KMS_STAT_MAP.items():
            val = stat.get(kms_attr)
            if val is not None:
                new_stat.set(gms_attr, val)
    # 补充 GMS <stat> 默认值
    for k, default in STAT_DEFAULTS.items():
        if k not in new_stat.attrib:
            new_stat.set(k, default)
    
    # 4. 处理其他 GMS 子节点
    for tag, defaults in OTHER_DEFAULTS.items():
        if tag in ('model', 'stat'):  # 已处理
            continue
        node = env.find(tag)
        new_node = ET.SubElement(new_env, tag)
        if node is not None:
            for k, v in node.attrib.items():
                new_node.set(k, v)
        # 补充默认值
        for k, default in defaults.items():
            if k not in new_node.attrib:
                new_node.set(k, default)
    
    # 5. 保留 KMS 的 <effectdummy> (GMS 也有)
    effectdummy = env.find('effectdummy')
    if effectdummy is not None:
        new_env.append(effectdummy)
    
    return new_env

def process_npcdata_folder():
    """处理 npcdata 目录，转换所有文件"""
    if not os.path.exists(KMS_DIR):
        print(f'[!] KMS npcdata 目录不存在: {KMS_DIR}')
        return
    
    os.makedirs(OUT_DIR, exist_ok=True)
    
    files = sorted([f for f in os.listdir(KMS_DIR) if f.endswith('.xml')])
    print(f'找到 {len(files)} 个 KMS npcdata 文件')
    print()
    
    total_npcs = 0
    errors = []
    
    for fname in files:
        kms_path = os.path.join(KMS_DIR, fname)
        print(f'处理: {fname}')
        
        try:
            tree = ET.parse(kms_path)
            root = tree.getroot()
            
            npcs = root.findall('npc')
            print(f'  NPC 数量: {len(npcs)}')
            
            for npc in npcs:
                npc_id = npc.get('id')
                if not npc_id:
                    continue
                
                # 创建 GMS <environment>
                new_env = create_gms_environment(npc)
                if new_env is None:
                    errors.append(f'{fname}: NPC {npc_id} 缺少 <environment>')
                    continue
                
                # 创建输出文件
                out_path = get_gms_path(npc_id)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                # 写入文件
                new_root = ET.Element('ms2')
                new_root.append(new_env)
                new_tree = ET.ElementTree(new_root)
                ET.indent(new_tree, space='\t')
                new_tree.write(out_path, encoding='utf-8', xml_declaration=True)
                
                total_npcs += 1
            
            print(f'  ✓ 完成')
        
        except Exception as e:
            errors.append(f'{fname}: {e}')
            print(f'  ✗ 错误: {e}')
        
        print()
    
    print(f'=== 完成 ===')
    print(f'总 NPC 数: {total_npcs}')
    print(f'错误数: {len(errors)}')
    if errors:
        print('错误详情:')
        for e in errors[:10]:
            print(f'  {e}')

if __name__ == '__main__':
    process_npcdata_folder()
