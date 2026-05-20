# -*- coding: utf-8 -*-
"""
CG to GMS Format Converter
用于4C&GXml achievefileConvertingto3GMSXmlformat
Converts 4C&GXml achieve files to 3GMSXml format
"""

import os
import re
import copy
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

def find_subfolders(source_dir):
    """查找Source directory下所有subfolder"""
    folders = []
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders

def convert_achieve_to_gms(content):
    """ConvertsCGFormat conversiontoGMSformat"""
    try:
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  XML Parse Error / XML Parse Error: {e}")
        return None
    
    achieves_list = root.findall('achieves')
    
    for achieves in achieves_list:
        current_attrs = achieves.attrib.copy()
        attr_order = ['id', 'account', 'icon', 'noticePercent', 'locking', 'categoryTag', 'feature', 'locale']
        
        new_attrs_list = []
        for attr in attr_order:
            if attr == 'locking':
                new_attrs_list.append(('locking', ''))
            elif attr == 'noticePercent':
                new_attrs_list.append(('noticePercent', current_attrs.get('noticePercent', '1')))
            elif attr in current_attrs:
                new_attrs_list.append((attr, current_attrs[attr]))
        
        for key in list(achieves.attrib.keys()):
            del achieves.attrib[key]
        for k, v in new_attrs_list:
            achieves.set(k, v)
        
        for grade in achieves.findall('grade'):
            conditions = grade.findall('condition')
            rewards = grade.findall('reward')
            for cond in conditions:
                if 'target' not in cond.attrib:
                    cond.set('target', '')
            if len(rewards) == 0:
                empty_reward = ET.SubElement(grade, 'reward')
                empty_reward.set('type', '')
                empty_reward.set('code', '0')
                empty_reward.set('value', '0')
                empty_reward.set('rank', '1')
            else:
                for reward in rewards:
                    if 'rank' not in reward.attrib:
                        reward.set('rank', '1')
    
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="utf-8"?>')
    
    if '<!--' in content and '-->' in content:
        comment_match = re.search(r'(<!--.*?-->)', content, re.DOTALL)
        if comment_match:
            xml_lines.append(comment_match.group(1))
    
    def elem_to_str(element, indent=1):
        spaces = '\t' * indent
        attrs = ' '.join([f'{k}="{v}"' for k, v in element.attrib.items()])
        if len(element) == 0 and element.text is None:
            tag_part = f'{element.tag} {attrs}' if attrs else element.tag
            return f'{spaces}<{tag_part} />'
        elif len(element) == 0:
            tag_part = f'{element.tag} {attrs}' if attrs else element.tag
            return f'{spaces}<{tag_part}>{element.text}</{element.tag}>'
        else:
            tag_part = f'{element.tag} {attrs}' if attrs else element.tag
            lines = [f'{spaces}<{tag_part}>']
            if element.text and element.text.strip():
                lines.append(f'{element.text}')
            for child in element:
                lines.append(elem_to_str(child, indent + 1))
            lines.append(f'{spaces}</{element.tag}>')
            return '\n'.join(lines)
    
    xml_lines.append(elem_to_str(root))
    return '\n'.join(xml_lines)

def process_achieve_folder(source_dir, output_dir):
    """Processingachievefolder"""
    source_achieve = os.path.join(source_dir, 'achieve')
    output_achieve = os.path.join(output_dir, 'achieve')
    
    if not os.path.exists(source_achieve):
        print(f"Error: Source directory does not exist: {source_achieve}")
        return
    
    os.makedirs(output_achieve, exist_ok=True)
    xml_files = [f for f in os.listdir(source_achieve) if f.endswith('.xml')]
    total = len(xml_files)
    
    print(f"\nFound {total} XML files")
    print("Starting conversion...\n")
    
    success = 0
    failed = 0
    
    for i, filename in enumerate(xml_files, 1):
        source_file = os.path.join(source_achieve, filename)
        output_file = os.path.join(output_achieve, filename)
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            converted = convert_achieve_to_gms(content)
            if converted:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(converted)
                success += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            failed += 1
        if i % 100 == 0 or i == total:
            print(f"Progress: {i}/{total}")
    
    print(f"\nConversion completed! Success: {success}, Failed: {failed}")
    print(f"Output directory: {output_achieve}")

def _count_items(folder_path):
    """递归计算directory中fileTotal"""
    count = 0
    for root, dirs, files in os.walk(folder_path):
        count += len(files)
    return count

def process_table_folder(source_dir, output_dir):
    """Processingtablefolder：让用户Please selectcnorkr，Copy到Output directory并renamed tona/"""
    import shutil
    source_table = os.path.join(source_dir, 'table')
    output_table = os.path.join(output_dir, 'table')
    
    if not os.path.exists(source_table):
        print(f"Error: Source directory does not exist: {source_table}")
        return
    
    cn_path = os.path.join(source_table, 'cn')
    kr_path = os.path.join(source_table, 'kr')
    default_path = os.path.join(source_table, 'default')
    
    if not os.path.exists(cn_path) and not os.path.exists(kr_path):
        print(f"Error: Source directory missing cn/ or kr/ subfolder")
        return
    
    print("\ntable conversion: Please select version to use:")
    if os.path.exists(cn_path):
        cn_count = _count_items(cn_path)
        print(f"  1. cn (CN server) - {cn_count} files")
    if os.path.exists(kr_path):
        kr_count = _count_items(kr_path)
        print(f"  2. kr (KR server) - {kr_count} files")
    print("  3. Both")
    
    choice = input("Please enter selection (1/2/3): ").strip()
    os.makedirs(output_table, exist_ok=True)
    copied = 0
    
    def copy_and_rename(src, dst_name):
        dst = os.path.join(output_table, dst_name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        count = _count_items(dst)
        print(f"  Copied: {src} -> {dst} ({count} files)")
        return count
    
    if choice == '1' and os.path.exists(cn_path):
        copied += copy_and_rename(cn_path, 'na')
    elif choice == '2' and os.path.exists(kr_path):
        copied += copy_and_rename(kr_path, 'na')
    elif choice == '3':
        print("  Note: cn will be output as na/")
        copied += copy_and_rename(cn_path, 'na')
        copied += copy_and_rename(kr_path, 'kr')
    else:
        print("Invalid selection，Default using cn")
        copied += copy_and_rename(cn_path, 'na')
    
    if os.path.exists(default_path):
        copied += copy_and_rename(default_path, 'default')
    
    print(f"\ntable Processing completed! ({copied} files)")

def process_direct_copy(source_dir, output_dir, folder_name):
    """Direct copyfolder（无Converting）"""
    import shutil
    source_folder = os.path.join(source_dir, folder_name)
    output_folder = os.path.join(output_dir, folder_name)
    
    if not os.path.exists(source_folder):
        print(f"Error: Source directory does not exist: {source_folder}")
        return
    
    total_files = _count_items(source_folder)
    print(f"Processing {total_files} files")
    
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    
    os.makedirs(output_folder, exist_ok=True)
    copied = 0
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        output_item = os.path.join(output_folder, item)
        if os.path.isfile(source_item):
            shutil.copy2(source_item, output_item)
            copied += 1
        elif os.path.isdir(source_item):
            for root, dirs, files in os.walk(source_item):
                rel_root = os.path.relpath(root, source_folder)
                dest_root = os.path.join(output_folder, rel_root)
                os.makedirs(dest_root, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(dest_root, f))
                    copied += 1
        pct = copied * 100 // total_files if total_files > 0 else 100
        print(f"\rProgress: {copied}/{total_files} ({pct}%)", end='', flush=True)
    
    print()
    print(f"Copy completed! {folder_name} ({copied} files)")

def process_anikeyinfo_folder(source_dir, output_dir):
    """Processinganikeyinfofolder，incrementalUpdatedanikeytext.xml"""
    source_anikeyinfo = os.path.join(source_dir, 'anikeyinfo')
    output_anikeytext = os.path.join(output_dir, 'anikeytext.xml')
    
    # 创建outputdirectory
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(source_anikeyinfo):
        print(f"Error: Source directory does not exist: {source_anikeyinfo}")
        return
    
    if not os.path.exists(output_anikeytext):
        print(f"Error: Output directorymissing anikeytext.xml")
        print(f"Please copy original GMS anikeytext.xml to: {output_dir}")
        return
    
    try:
        tree = ET.parse(output_anikeytext)
        root = tree.getroot()
    except Exception as e:
        print(f"Error: Cannot parse anikeytext.xml: {e}")
        return
    
    xml_files = [f for f in os.listdir(source_anikeyinfo) if f.endswith('.xml')]
    total = len(xml_files)
    print(f"Found {total} XML files in anikeyinfo")
    print("StartingincrementalUpdated...\n")
    
    replace_count = 0
    append_count = 0
    error_count = 0
    
    for i, filename in enumerate(xml_files, 1):
        kfm_name = os.path.splitext(filename)[0]
        source_file = os.path.join(source_anikeyinfo, filename)
        try:
            file_tree = ET.parse(source_file)
            file_root = file_tree.getroot()
            existing_kfm = root.find(f"kfm[@name='{kfm_name}']")
            
            if existing_kfm is not None:
                for child in list(existing_kfm):
                    existing_kfm.remove(child)
                for child in file_root:
                    existing_kfm.append(child)
                replace_count += 1
            else:
                new_kfm = ET.Element('kfm')
                new_kfm.set('name', kfm_name)
                for child in file_root:
                    new_kfm.append(child)
                root.append(new_kfm)
                append_count += 1
        except Exception as e:
            print(f"  Error processing {filename}: {e}")
            error_count += 1
        if i % 100 == 0 or i == total:
            print(f"Progress: {i}/{total}")
    
    try:
        tree.write(output_anikeytext, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"Error: Cannot write anikeytext.xml: {e}")
        return
    
    print(f"\nProcessing completed! Replaced: {replace_count}, Appended: {append_count}, Error: {error_count}")

# ============================================================
# ============================================================
# script directoryConverting
# ============================================================

def _add_gms_script_attrs(elem):
    """给 select/script/monologue Add feature locale attribute"""
    if elem.tag in ('select', 'script', 'monologue'):
        elem.set('feature', '')
        elem.set('locale', '')
    for child in elem:
        if child.tag == 'content':
            child.set('gotoFail', '')
        _add_gms_script_attrs(child)


def _convert_content_gotofail(elem):
    """给所有 distractor Add gotoFail空attribute"""
    for child in elem:
        if child.tag == 'distractor' and 'gotoFail' not in child.attrib:
            child.set('gotoFail', '')
        _convert_content_gotofail(child)


def process_script_folder(cg_dir, out_dir):
    """Converting script directory：npc and quest 子directory"""
    import os, xml.etree.ElementTree as ET
    from collections import defaultdict

    # script 数据在 2KMSXml（4C&GXml不含scriptdirectory）
    kms_script = os.path.join(os.path.dirname(cg_dir.rstrip(os.sep)), '2KMSXml', 'script')
    out_script = os.path.join(out_dir, 'script')

    # ---- NPC Converting ----
    npc_src = os.path.join(kms_script, 'npc', 'npcscript_final.xml')
    npc_out = os.path.join(out_script, 'npc')
    os.makedirs(npc_out, exist_ok=True)

    print(f'  Converting NPC scripts: {npc_src}')
    tree = ET.parse(npc_src)
    root = tree.getroot()

    npc_count = 0
    for npc in root.findall('npc'):
        npc_id = npc.get('id')
        ms2 = ET.Element('ms2')
        for child in list(npc):
            npc.remove(child)
            ms2.append(child)
        _add_gms_script_attrs(ms2)
        _convert_content_gotofail(ms2)

        out_file = os.path.join(npc_out, f'{npc_id}.xml')
        ET.indent(ms2, '\t')
        ET.ElementTree(ms2).write(out_file, encoding='utf-8', xml_declaration=True)
        npc_count += 1

    print(f'    NPC: {npc_count} files')

    # ---- Quest Converting ----
    # 建立 GMS ID -> file名 精确映射
    gms_ref = os.path.join(os.path.dirname(cg_dir), '3GMSXml', 'script', 'quest')
    gms_id_map = {}
    for gf in os.listdir(gms_ref):
        gfpath = os.path.join(gms_ref, gf)
        if gf.endswith('.xml') and os.path.isfile(gfpath):
            try:
                gt = ET.parse(gfpath)
                for q in gt.getroot().findall('quest'):
                    gms_id_map[int(q.get('id'))] = gf
            except:
                pass

    def classify_quest(qid):
        if qid in gms_id_map:
            return gms_id_map[qid]
        # KMS-only fallback by ID range
        if 10001000 <= qid <= 19999999:
            return 'questscript_epic.xml'
        if 30000340 <= qid <= 39999999:
            return 'questscript_eventcommon.xml'
        if 40001000 <= qid <= 49999999:
            return 'questscript_tutorial.xml'
        if 60001000 <= qid <= 69999999:
            return 'questscript_tutorial.xml'
        if 73000000 <= qid <= 73999999:
            return 'questscript_guild.xml'
        if 80000001 <= qid <= 80009999:
            return 'questscript_eventkr.xml'
        if 80010000 <= qid <= 80019999:
            return 'questscript_eventcn.xml'
        if 80020001 <= qid <= 80029999:
            return 'questscript_eventna.xml'
        if 80030000 <= qid <= 80039999:
            return 'questscript_eventjp.xml'
        if 90000000 <= qid <= 90999999:
            return 'questscript_guide.xml'
        if 91000000 <= qid <= 91999999:
            return 'questscript_famecontents.xml'
        if 92000000 <= qid <= 92999999:
            return 'questscript_famefield.xml'
        if 93000000 <= qid <= 94999999:
            return 'questscript_famemission.xml'
        if 95000000 <= qid <= 95999999:
            return 'questscript_item.xml'
        return 'questscript_world.xml'

    q_src = os.path.join(kms_script, 'quest', 'questscript_final.xml')
    q_out = os.path.join(out_script, 'quest')
    os.makedirs(q_out, exist_ok=True)

    print(f'  Converting Quest scripts: {q_src}')
    qt = ET.parse(q_src)
    qr = qt.getroot()

    groups = defaultdict(list)
    for quest in qr.findall('quest'):
        qid = int(quest.get('id'))
        fname = classify_quest(qid)
        groups[fname].append(quest)

    total_quests = 0
    for fname in sorted(groups.keys()):
        quests = groups[fname]
        ms2 = ET.Element('ms2')
        for q in quests:
            q_copy = ET.fromstring(ET.tostring(q, encoding='unicode'))
            _add_gms_script_attrs(q_copy)
            _convert_content_gotofail(q_copy)
            ms2.append(q_copy)

        out_file = os.path.join(q_out, fname)
        ET.indent(ms2, '\t')
        ET.ElementTree(ms2).write(out_file, encoding='utf-8', xml_declaration=True)
        print(f'    {fname}: {len(quests)} quests')
        total_quests += len(quests)

    print(f'    Quest: {total_quests} questwritten to {len(groups)} files')


# skilldata Converting相关函数
# ============================================================

def _skill_id_to_path(sid_str):
    """
    skillID映射toGMSfilepath（folder+file名）
    - 8位以内: 补零到8位 → 取前2位作folder → file名=补零8位
    - 9位:     Direct取前3位作folder → file名=原ID
    """
    sid = int(sid_str)
    if sid < 100000000:
        padded = str(sid).zfill(8)
        folder = padded[:2]
        fname = padded + '.xml'
    else:
        folder = str(sid)[:3]
        fname = str(sid) + '.xml'
    return folder, fname

def _format_range_add(value):
    """KMS rangeAdd "0,25,0" → GMS "0.000000,25.000000,0.000000" """
    try:
        parts = value.split(',')
        return ','.join([f'{float(p):.6f}' for p in parts])
    except (ValueError, AttributeError):
        return value

# attack 子node重命名映射

# KMS basic children that belong in level in GMS (not basic)
_LEVEL_ONLY_TAGS = {'autoTargeting', 'push'}

_ATTACK_CHILD_RENAME = {
    'range': 'rangeProperty',
    'sensor': 'sensorProperty',
    'pause': 'pauseProperty',
    'arrow': 'arrowProperty',
    'damage': 'damageProperty',
}

def _convert_attack_children(kms_attack, gms_attack):
    """
    Converting <attack>  子node: range→rangeProperty, sensor→sensorProperty, etc.
    gms_attack 已从模板深拷贝，包含完整默认attribute。
    策略：以模板to基础，KMS 有什么覆盖什么；KMS 没有 Preserving模板默认值。
    """
    for child in kms_attack:
        tag = child.tag

        if tag in _ATTACK_CHILD_RENAME:
            # 标签重命名，从模板找对应node，用 KMS 覆盖
            new_tag = _ATTACK_CHILD_RENAME[tag]
            new_elem = gms_attack.find(new_tag)
            if new_elem is None:
                new_elem = ET.SubElement(gms_attack, new_tag)
            for k, v in child.attrib.items():
                # rangeAdd / collision / collisionAdd requires整型→浮点format化
                if k in ('rangeAdd', 'collision', 'collisionAdd', 'rangeOffset'):
                    v = _format_range_add(v)
                new_elem.set(k, v)

        elif tag == 'actionAdditional':
            # actionAdditional → conditionSkill (additionalID → skillID)
            cond_skill = gms_attack.find('conditionSkill')
            if cond_skill is None:
                cond_skill = ET.SubElement(gms_attack, 'conditionSkill')
            for k, v in child.attrib.items():
                if k == 'additionalID':
                    cond_skill.set('skillID', v)
                else:
                    cond_skill.set(k, v)

        else:
            # 其他未知子node
            new_elem = gms_attack.find(child.tag)
            if new_elem is None:
                new_elem = ET.SubElement(gms_attack, child.tag)
            for k, v in child.attrib.items():
                new_elem.set(k, v)

def _convert_kms_skill_to_gms(skill_elem, template_tree):
    """
    一KMS <skill> nodeConvertingtoGMSformat <ms2 feature="">
    
    KMS 结构:
      <skill id="1">
        <basic mainType="1">
          <ui attackType="1"/>
          <kinds rangeType="1"/>
          <stateAttr .../>
          ...
        </basic>
        <level value="1" cooldown="600">
          <motion sequenceName="..." ...>
            <attack point="p0" ...>
              <range rangeType="box" .../>
              <arrow .../>
              <damage .../>
            </attack>
          </motion>
          <actionAdditional additionalID="..."/>
          <detectProperty .../>
        </level>
      </skill>
    
    GMS 结构:
      <ms2 feature="">
        <basic>
          <ui .../>
          <kinds .../>
          <stateAttr .../>
          ...
        </basic>
        <level value="1">
          <beginCondition level="1" gender="2" target="0" ... cooldownTime="0.6">
            <weapon index="0"/>
          </beginCondition>
          <motion>
            <motionProperty sequenceName="..." .../>
            <attack point="p0" ...>
              <pauseProperty .../>
              <rangeProperty .../>
              <arrowProperty .../>
              <damageProperty .../>
            </attack>
          </motion>
          <conditionSkill skillID="..."/>
          <detectProperty .../>
        </level>
      </ms2>
    """
    skill_id = skill_elem.attrib.get('id', '')
    if not skill_id:
        return None

    # 深拷贝模板
    new_root = copy.deepcopy(template_tree.getroot())
    new_root.set('feature', '')

    # ===== Processing basic node =====
    kms_basic = skill_elem.find('basic')
    if kms_basic is not None:
        gms_basic = new_root.find('basic')
        if gms_basic is not None:
            # mainType: KMS basic attribute，GMS basic 下不有此node，Skipping
            # (GMS 仅在特定职业skill中有 mainType，通用skill没有)

            # Copy basic  子nodeattribute到 GMS
            # Note: autoTargeting/push 在 KMS basic 下，但在 GMS 中属于 level
            # 不Copy到 basic，稍后用它们覆盖 level 模板默认值
            for child in kms_basic:
                if child.tag in _LEVEL_ONLY_TAGS:
                    continue  # 稍后在 level 层Processing
                gms_child = gms_basic.find(child.tag)
                if gms_child is None:
                    gms_child = ET.SubElement(gms_basic, child.tag)
                for k, v in child.attrib.items():
                    gms_child.set(k, v)

    # ===== Use KMS basic's autoTargeting/push to override level template defaults =====
    # These are in KMS basic but belong in GMS level
    kms_level_only_data = {}
    if kms_basic is not None:
        for child in kms_basic:
            if child.tag in _LEVEL_ONLY_TAGS:
                kms_level_only_data[child.tag] = dict(child.attrib)

    # ===== Processing每 level node =====
    kms_levels = skill_elem.findall('level')
    gms_level_template = new_root.find('level')

    if kms_levels and gms_level_template is not None:
        new_root.remove(gms_level_template)

    for lvl in kms_levels:
        lvl_value = lvl.attrib.get('value', '1')
        lvl_cooldown = lvl.attrib.get('cooldown', None)

        lvl_copy = copy.deepcopy(gms_level_template)
        lvl_copy.set('value', lvl_value)

        # Apply KMS basic autoTargeting/push data to level
        for tag_name, attrs in kms_level_only_data.items():
            level_elem = lvl_copy.find(tag_name)
            if level_elem is not None:
                for k, v in attrs.items():
                    level_elem.set(k, v)

        # cooldown: levelattribute(ms) → beginCondition.cooldownTime(s)
        begin_cond = lvl_copy.find('beginCondition')
        if begin_cond is not None and lvl_cooldown is not None:
            try:
                cooldown_sec = float(lvl_cooldown) / 1000.0
                # GMS整秒不带小数点: 1.0→"1", 0.6→"0.6"
                cooldown_str = str(int(cooldown_sec)) if cooldown_sec == int(cooldown_sec) else str(cooldown_sec)
                begin_cond.set('cooldownTime', cooldown_str)
            except ValueError:
                pass

        # 遍历 KMS level  Direct子node
        for child in lvl:
            tag = child.tag

            if tag == 'motion':
                # === <motion> Processing ===
                gms_motion = lvl_copy.find('motion')
                if gms_motion is None:
                    gms_motion = ET.SubElement(lvl_copy, 'motion')

                # motion attribute → motionProperty 子node
                motion_prop = gms_motion.find('motionProperty')
                if motion_prop is None:
                    motion_prop = ET.SubElement(gms_motion, 'motionProperty')
                for k, v in child.attrib.items():
                    motion_prop.set(k, v)

                # Remove template attacks first
                for tpl_atk in list(gms_motion.findall('attack')):
                    gms_motion.remove(tpl_atk)

                # motion 下  <attack> node
                for attack_child in child:
                    if attack_child.tag == 'attack':
                        # 从模板  level 获取模板 attack（模板 motion 下 已被删除）
                        tpl_motion = gms_level_template.find('motion') if gms_level_template is not None else None
                        tpl_attack = tpl_motion.find('attack') if tpl_motion is not None else None
                        if tpl_attack is not None:
                            gms_attack = copy.deepcopy(tpl_attack)
                        else:
                            gms_attack = ET.Element('attack')
                        gms_motion.append(gms_attack)
                        # 用 KMS attack attribute覆盖模板默认值
                        for k, v in attack_child.attrib.items():
                            gms_attack.set(k, v)
                        # Converting attack 子node（模板已有默认值，KMS 覆盖）
                        _convert_attack_children(attack_child, gms_attack)
                    else:
                        # motion 下 其他子nodeDirectCopy
                        new_elem = ET.SubElement(gms_motion, attack_child.tag)
                        for k, v in attack_child.attrib.items():
                            new_elem.set(k, v)

            elif tag == 'condition':
                # <condition><weapon> → <beginCondition><weapon>
                if begin_cond is not None:
                    for wc in child.findall('weapon'):
                        wc_copy = copy.deepcopy(wc)
                        begin_cond.append(wc_copy)

            elif tag == 'actionAdditional':
                # level Direct子node  actionAdditional → conditionSkill
                cond_skill = ET.SubElement(lvl_copy, 'conditionSkill')
                for k, v in child.attrib.items():
                    if k == 'additionalID':
                        cond_skill.set('skillID', v)
                    else:
                        cond_skill.set(k, v)

            elif tag == 'chain':
                # KMS 独有，GMS 没有，Skipping
                pass

            elif tag == 'detectProperty':
                # 同标签，Copy KMS 数据到 GMS detectProperty
                gms_detect = lvl_copy.find('detectProperty')
                if gms_detect is None:
                    gms_detect = ET.SubElement(lvl_copy, 'detectProperty')
                for k, v in child.attrib.items():
                    if k == 'rangeOffset':
                        v = _format_range_add(v)
                    gms_detect.set(k, v)

            else:
                # 其他 level Direct子nodeDirectCopy
                gms_child = lvl_copy.find(tag)
                if gms_child is None:
                    gms_child = ET.SubElement(lvl_copy, tag)
                for k, v in child.attrib.items():
                    gms_child.set(k, v)

        new_root.append(lvl_copy)

    return new_root

def _merge_additional_effect(kms_file, gms_root):
    """ConvertsKMS精简additional effectmerge到GMS完整模板"""
    kms_tree = ET.parse(kms_file)
    kms_root = kms_tree.getroot()
    kms_levels = kms_root.findall('level')
    if not kms_levels:
        return None
    kms_lvl = kms_levels[0]
    gms_levels = gms_root.findall('level')
    if not gms_levels:
        return None
    gms_lvl = gms_levels[0]
    for child in kms_lvl:
        tag = child.tag
        gms_child = gms_lvl.find(tag)
        if gms_child is None:
            gms_child = ET.SubElement(gms_lvl, tag)
        for k, v in child.attrib.items():
            gms_child.set(k, v)
    return gms_root


def process_additionaleffect(source_dir, output_dir):
    """Processingadditionaleffect：以GMSto基础Incremental mergeKMSattribute"""
    source_ae = os.path.join(source_dir, 'additionaleffect')
    output_ae = os.path.join(output_dir, 'additionaleffect')
    gms_ae = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), '3GMSXml', 'additionaleffect')

    if not os.path.exists(source_ae):
        print(f"Error: Source directory does not exist: {source_ae}")
        return

    # CopyGMS original作to基础
    if os.path.exists(gms_ae):
        import shutil
        if os.path.exists(output_ae):
            shutil.rmtree(output_ae)
        shutil.copytree(gms_ae, output_ae)
        print(f"Copied GMS original {len(os.listdir(output_ae))} files as base")
    else:
        os.makedirs(output_ae, exist_ok=True)
        print("Warning: GMS original directory does not exist, output will be empty")

    xml_files = sorted([f for f in os.listdir(source_ae) if f.endswith('.xml')])
    total = len(xml_files)
    updated = 0
    new_files = 0
    errors = 0

    print(f"\nFound {total} KMS additionaleffectfile")
    print("Starting incremental merge...\n")

    for fi, fname in enumerate(xml_files, 1):
        source_file = os.path.join(source_ae, fname)
        output_file = os.path.join(output_ae, fname)
        try:
            if os.path.exists(output_file):
                gms_tree = ET.parse(output_file)
                gms_root = gms_tree.getroot()
                result = _merge_additional_effect(source_file, gms_root)
                if result is not None:
                    ET.indent(result)
                    ET.ElementTree(result).write(output_file, encoding='utf-8', xml_declaration=True)
                    updated += 1
            else:
                # KMS独有file，DirectCopy
                import shutil
                shutil.copy2(source_file, output_file)
                new_files += 1
        except Exception as e:
            print(f"  Error {fname}: {e}")
            errors += 1

        if fi % 500 == 0 or fi == total:
            pct = fi * 100 // total
            print(f"\rProgress: {fi}/{total} ({pct}%)", end='', flush=True)

    print()
    print(f"\nadditionaleffect merge completed!")
    print(f"  Existing files updated: {updated}")
    print(f"  KMS-only new files: {new_files}")
    print(f"  Error: {errors}")


def process_skilldata_folder(source_dir, output_dir):
    """Processing skilldata folder: KMS format to GMS format"""
    import shutil

    source_skill = os.path.join(source_dir, 'skilldata')
    output_skill = os.path.join(output_dir, 'skill')

    if not os.path.exists(source_skill):
        print(f"Error: Source directory does not exist: {source_skill}")
        return

    # 读取模板
    template_path = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), 'skill_template.xml')
    if not os.path.exists(template_path):
        print(f"Error: Template file does not exist: {template_path}")
        return

    try:
        template_tree = ET.parse(template_path)
    except Exception as e:
        print(f"Error: Cannot parse template: {e}")
        return

    xml_files = sorted([f for f in os.listdir(source_skill) if f.endswith('.xml')])
    total_files = len(xml_files)
    total_skills = 0
    written = 0
    errors = 0

    print(f"\nFound {total_files} XML files in skilldata")
    print("Starting conversion...\n")

    os.makedirs(output_skill, exist_ok=True)

    for fi, fname in enumerate(xml_files, 1):
        source_file = os.path.join(source_skill, fname)
        try:
            tree = ET.parse(source_file)
            root = tree.getroot()
        except Exception as e:
            print(f"  Parse error {fname}: {e}")
            errors += 1
            continue

        skills = root.findall('skill')
        total_skills += len(skills)

        for sk in skills:
            sid = sk.attrib.get('id', '')
            if not sid:
                continue

            try:
                gms_root = _convert_kms_skill_to_gms(sk, template_tree)
                if gms_root is None:
                    errors += 1
                    continue

                folder, fname_out = _skill_id_to_path(sid)
                target_dir = os.path.join(output_skill, folder)
                os.makedirs(target_dir, exist_ok=True)
                out_path = os.path.join(target_dir, fname_out)

                ET.indent(gms_root)
                tree_out = ET.ElementTree(gms_root)
                tree_out.write(out_path, encoding='utf-8', xml_declaration=True)
                written += 1

            except Exception as e:
                print(f"  Converting skill {sid} error during: {e}")
                errors += 1

        if fi % 10 == 0 or fi == total_files:
            pct = fi * 100 // total_files
            print(f"\rProgress: {fi}/{total_files} ({pct}%)", end='', flush=True)

    print()
    print(f"\nConversion completed! Files: {total_files}, skill: {total_skills}")
    print(f"Success: {written}, Error: {errors}")
    print(f"Output directory: {output_skill}")


def main():
    print("=" * 50)
    print("KMS to GMS Format Converter")
    print("=" * 50)

    while True:
        source_dir = input("\nPleaseentersourcedirectorypath: ").strip().strip('"')
        if os.path.exists(source_dir):
            break
        print(f"Directory does not exist, please re-enter")

    subfolders = find_subfolders(source_dir)

    # itempreset: source是KMSitemmodeldirectory
    if 'itemmodel' in subfolders and 'itempreset' not in subfolders:
        subfolders.append('itempreset')

    # mapdirectory来自3GMSXml而非4C&G，requires额外检查
    gms_ref = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), '3GMSXml')
    gms_map_dir = os.path.join(gms_ref, 'map')
    if os.path.exists(gms_map_dir) and 'map' not in subfolders:
        subfolders.append('map')
    
    # exceldirectory来自3GMSXml而非4C&G，requires额外检查
    gms_excel_dir = os.path.join(gms_ref, 'excel')
    if os.path.exists(gms_excel_dir) and 'excel' not in subfolders:
        subfolders.append('excel')

    if not subfolders:
        print("No subdirectories in source directory")
        return

    supported = ['achieve', 'camera', 'ui', 'ugcmap', 'anikeyinfo', 'trigger', 'table', 'string', 'skilldata', 'script', 'riding', 'quest', 'pet', 'object', 'emotion', 'musicscore', 'masteryhomemade', 'npcdata', 'mapxblock', 'map', 'excel', 'itempreset', 'itemdata', 'groundeffect', 'additionaleffect', 'exportedugcmap', 'effect']

    # directory名映射: KMSdirectory名 → scriptProcessing名
    folder_alias = {'itemmodel': 'itempreset'}

    # 只显示支持 folder（映射后检查）
    display_folders = [f for f in subfolders if folder_alias.get(f, f) in supported]

    if not display_folders:
        print('No folders to process')
        return

    print(f'\nAvailable folders:')
    for i, folder in enumerate(display_folders, 1):
        alias = folder_alias.get(folder)
        label = folder + ' -> ' + alias if alias else folder
        print(f'  {i}. {label}')

    if 'anikeyinfo' in display_folders:
        print('\nNote: Processing anikeyinfo requires original anikeytext.xml in output directory')

    if 'skilldata' in display_folders or 'itemmodel' in display_folders:
        parent_dir = os.path.dirname(source_dir.rstrip(os.sep))
        tpl = os.path.join(parent_dir, 'skill_template.xml')
        print(f'\nNote: Processing skilldata requires template file skill_template.xml')
        print(f'  Template path: {tpl}')

    if 'itemdata' in display_folders:
        parent_dir = os.path.dirname(source_dir.rstrip(os.sep))
        tpl = os.path.join(parent_dir, 'item_template.xml')
        print(f'\nNote: Processing itemdata requires template file item_template.xml')
        print(f'  Template path: {tpl}')

    choice = input('\nPlease select folder numbers (comma-separated, Enter for all): ').strip()

    if not choice:
        selected = [folder_alias.get(f, f) for f in display_folders]
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = [folder_alias.get(display_folders[i-1], display_folders[i-1]) for i in indices]
        except:
            print('Invalid selection，Default selecting all')
            selected = [folder_alias.get(f, f) for f in display_folders]

    while True:
        output_dir = input("\nPleaseenteroutputdirectorypath: ").strip().strip('"')
        if output_dir:
            break
        print("Output directory cannot be empty")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 50)
    print("Conversion Info")
    print("=" * 50)
    print(f"Source directory: {source_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Processing: {', '.join(selected)}")

    print("\nConversion rules:")
    print("  achieve: Format conversion（locking、target attributes）")
    print("  camera/ui/ugcmap/trigger/string: Direct copy")
    print("  anikeyinfo: incrementalUpdated anikeytext.xml")
    print("  skilldata: KMS collection -> GMS individual files")
    print("  script: NPC/Quest collection -> GMS individual files")
    print("  riding: Riding files + passenger extraction")
    print("  quest: Add GMS-only nodes and attributes")
    print("  pet: Direct copy")
    print("  object: Direct copy")
    print("  npcdata: KMS collection -> GMS individual files")
    print("  mapxblock: KMSfull + GMS-only")
    print("  map: GMS-only directoryDirect copy")
    print("  itempreset: KMS itemmodel -> GMS individual itempreset files")
    print("  itemdata: KMS collection -> GMS individual files + option node conversion")
    print("  groundeffect: Direct copy")

    confirm = input("\nConfirm conversion start? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return

    for folder in selected:
        print(f"\n{'='*50}")
        print(f"Processingfolder: {folder}")
        print(f"{'='*50}")

        if folder == 'achieve':
            process_achieve_folder(source_dir, output_dir)
        elif folder == 'camera':
            process_direct_copy(source_dir, output_dir, 'camera')
        elif folder == 'ugcmap':
            process_direct_copy(source_dir, output_dir, 'ugcmap')
        elif folder == 'ui':
            process_direct_copy(source_dir, output_dir, 'ui')
        elif folder == 'anikeyinfo':
            process_anikeyinfo_folder(source_dir, output_dir)
        elif folder == 'trigger':
            process_direct_copy(source_dir, output_dir, 'trigger')
        elif folder == 'table':
            process_table_folder(source_dir, output_dir)
        elif folder == 'string':
            process_direct_copy(source_dir, output_dir, 'string')
        elif folder == 'skilldata':
            process_skilldata_folder(source_dir, output_dir)
        elif folder == 'script':
            process_script_folder(source_dir, output_dir)
        elif folder == 'riding':
            process_riding_folder(source_dir, output_dir)
        elif folder == 'quest':
            process_quest_folder(source_dir, output_dir)
        elif folder == 'pet':
            process_direct_copy(source_dir, output_dir, 'pet')
        elif folder == 'object':
            process_direct_copy(source_dir, output_dir, 'object')
        elif folder == 'emotion':
            process_direct_copy(source_dir, output_dir, 'emotion')
            # GMS-only file补入（KMS没有 ）
            import shutil
            kms_folder = os.path.join(source_dir, 'emotion')
            gms_folder = os.path.join(gms_ref, 'emotion')
            output_folder = os.path.join(output_dir, 'emotion')
            extra_count = 0
            for root, dirs, files in os.walk(gms_folder):
                for f in files:
                    gms_file = os.path.join(root, f)
                    rel = os.path.relpath(gms_file, gms_folder)
                    kms_file = os.path.join(kms_folder, rel)
                    if not os.path.exists(kms_file):
                        dest = os.path.join(output_folder, rel)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(gms_file, dest)
                        extra_count += 1
            if extra_count:
                print(f"  GMS-only files: {extra_count}")
        elif folder == 'musicscore':
            process_direct_copy(source_dir, output_dir, 'musicscore')
        elif folder == 'masteryhomemade':
            process_direct_copy(source_dir, output_dir, 'masteryhomemade')
        elif folder == 'npcdata':
            process_npcdata_folder(source_dir, output_dir)
        elif folder == 'mapxblock':
            process_mapxblock_folder(source_dir, output_dir)
        elif folder == 'map':
            process_map_folder(source_dir, output_dir)
        elif folder == 'excel':
            process_excel_folder(source_dir, output_dir)
        elif folder == 'itempreset':
            process_itempreset_folder(source_dir, output_dir)
        elif folder == 'itemdata':
            process_itemdata_folder(source_dir, output_dir)
        elif folder == 'groundeffect':
            process_direct_copy(source_dir, output_dir, 'groundeffect')
        elif folder == 'additionaleffect':
            process_additionaleffect(source_dir, output_dir)
        elif folder == 'exportedugcmap':
            process_direct_copy(source_dir, output_dir, 'exportedugcmap')
        elif folder == 'effect':
            process_direct_copy(source_dir, output_dir, 'effect')
        else:
            print(f"Unsupportedfolder: {folder}")

    print(f"\n{'='*50}")
    print("All processing completed!")
    print(f"{'='*50}")


#======================================================================
# npcdata Converting相关（2026-05-18 新增）
#======================================================================

# KMS <environment> attribute中不属于 GMS <basic>  （feature/locale 是 environment 自身attribute）
_NPC_ENV_SKIP = {"feature", "locale"}

# GMS <basic> allattribute默认值
_NPC_BASIC_DEFAULTS = {
    'friendly': '2', 'npcAttackGroup': '2', 'npcDefenseGroup': '1',
    'kind': '0', 'iconName': '', 'minimapIconName': '', 'shopId': '0',
    'nametag': '1', 'nametagSize': '18', 'local': '0', 'minimap': '1',
    'attackDamage': '0', 'hpBar': '0', 'defenceMaterial': '0',
    'hitImmune': '1', 'abnormalImmune': '1', 'level': '1', 'class': '5',
    'rankIcon': '', 'rotationDisabled': '0', 'carePathToEnemy': '1',
    'npcSoundStart': '', 'npcSoundEnd': '', 'npcSoundCombatStart': '',
    'npcSoundCombatEnd': '', 'npcSoundDead': '', 'maxSpawnCount': '0',
    'groupSpawnCount': '0', 'rareDegree': '0', 'difficulty': '0',
    'propertyTags': '', 'raceString': '', 'bossNotify': '0',
    'gender': '0', 'illust': '', 'emotionID': '0', 'mainTags': '',
    'subTags': '', 'portrait': '', 'talkAni': '1',  # Bug#5: 默认"1"非"0"
    'damagedColorScale': '2', 'damagedVibrateDuration': '0',
    'damagedVibrateAmp': '0', 'regenEffect': '', 'deadEffect': '',
    'damageEffect': '', 'createEffect': '', 'keepEffect': '',
    'skipFrame': '1', 'checkCameraDistance': '0',
    'extraCameraDistance': '0', 'bossSoundDistance': '2000',
    'bossSoundEndDistance': '3000',
}

# GMS <stat> attribute默认值
_NPC_STAT_DEFAULTS = {
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

# KMS <stat> -> GMS attribute映射
_NPC_KMS_STAT_MAP = {
    'hp': 'hp', 'msp': 'msp', 'atp': 'atp', 'evp': 'evp',
    'ndd': 'ndd', 'pap': 'pap', 'map': 'map',
}

# GMS 其他子node默认值（Bug#1: model 不含 shadowScale/rotationSpeed/walkSpeed/runSpeed）
_NPC_OTHER_DEFAULTS = {
    'model': {'kfm': '', 'scale': '', 'anispeed': '1', 'anispeedfix': 'false', 'spawnAlphaAnimation': '0', 'offset': '0.000000, 0.000000, 0.000000'},
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
    'lookattarget': {'targetdummy': '', 'lookAtMyPCWhenTalking': '0', 'useTalkMotion': '1'},
}

def _create_gms_environment(kms_npc):
    """从 KMS <npc> 创建 GMS <environment> node
    GMS 子node顺序: model -> basic -> stat -> speed -> ... -> crystals
    effectdummy 在 environment 外部，and environment 同级
    """
    env = kms_npc.find('environment')
    if env is None:
        return None, None

    new_env = ET.Element('environment')
    new_env.set('feature', env.get('feature', ''))
    new_env.set('locale', '')

    # 先读取 KMS <model>，requires其attribute映射到 <speed> and <shadow>
    kms_model = env.find('model')
    _KMS_MODEL_SKIP = {'shadowScale', 'rotationSpeed', 'walkSpeed', 'runSpeed'}

    # --- GMS 子node顺序: model, basic, stat, 然后其余 ---

    # 1. <model> - 不Copy shadowScale/rotationSpeed/walkSpeed/runSpeed
    new_model = ET.SubElement(new_env, 'model')
    if kms_model is not None:
        for k, v in kms_model.attrib.items():
            if k not in _KMS_MODEL_SKIP:
                new_model.set(k, v)
    for k, default in _NPC_OTHER_DEFAULTS['model'].items():
        if k not in new_model.attrib:
            if k == 'scale' and 'scale' not in new_model.attrib:
                new_model.set(k, '1.000000')
            elif k != 'scale':
                new_model.set(k, default)
    # offset format统一：逗号后加空格
    offset_val = new_model.get('offset', '')
    if offset_val and ', ' not in offset_val:
        new_model.set('offset', offset_val.replace(',', ', '))

    # 2. <basic> - KMS <environment> 上所有attribute都迁移（除了 feature/locale）
    basic = ET.SubElement(new_env, 'basic')
    for attr, val in env.attrib.items():
        if attr not in _NPC_ENV_SKIP:
            basic.set(attr, val)
    for attr, default in _NPC_BASIC_DEFAULTS.items():
        if attr not in basic.attrib:
            basic.set(attr, default)

    # 3. <stat>
    stat = env.find('stat')
    new_stat = ET.SubElement(new_env, 'stat')
    if stat is not None:
        for kms_attr, gms_attr in _NPC_KMS_STAT_MAP.items():
            val = stat.get(kms_attr)
            if val is not None:
                new_stat.set(gms_attr, val)
    for k, default in _NPC_STAT_DEFAULTS.items():
        if k not in new_stat.attrib:
            new_stat.set(k, default)

    # 4. 其他子node
    for tag, defaults in _NPC_OTHER_DEFAULTS.items():
        if tag in ('model', 'stat'):
            continue
        node = env.find(tag)
        new_node = ET.SubElement(new_env, tag)
        if node is not None:
            for k, v in node.attrib.items():
                new_node.set(k, v)
        for k, default in defaults.items():
            if k not in new_node.attrib:
                new_node.set(k, default)

    # <speed> 从 KMS <model>   rotationSpeed/walkSpeed/runSpeed 映射
    speed_node = new_env.find('speed')
    if kms_model is not None and speed_node is not None:
        rot = kms_model.get('rotationSpeed')
        walk = kms_model.get('walkSpeed')
        run = kms_model.get('runSpeed')
        if rot:
            speed_node.set('rotation', rot)
        if walk:
            speed_node.set('walk', walk)
        if run:
            speed_node.set('run', run)

    # <shadow> scale 使用 KMS <model>   shadowScale
    if kms_model is not None:
        shadow_scale = kms_model.get('shadowScale')
        shadow_node = new_env.find('shadow')
        if shadow_scale and shadow_node is not None:
            shadow_node.set('scale', shadow_scale)

    # 必须有 <crystals />
    if new_env.find('crystals') is None:
        ET.SubElement(new_env, 'crystals')

    # <effectdummy> 在 <environment> 外部
    # KMS 无 effectdummy 时，补 GMS 标准模板
    effectdummy = env.find('effectdummy')
    new_effectdummy = ET.Element('effectdummy')
    if effectdummy is not None:
        for k, v in effectdummy.attrib.items():
            new_effectdummy.set(k, v)
        for child in effectdummy:
            new_effectdummy.append(child)
    else:
        for name in ['Eff_Head', 'Eff_Body', 'Eff_Foot', 'Eff_UI',
                     'Eff_Damage', 'Eff_Head_World', 'Eff_Body_World', 'Eff_Foot_World']:
            d = ET.SubElement(new_effectdummy, 'dummy')
            d.set('name', name)

    return new_env, new_effectdummy


def _npc_id_to_gms_path(npc_id, output_base):
    """Converts NPC ID Convertingto GMS 嵌套path：id -> AA/BB/AAAAAAAA.xml"""
    sid = str(npc_id).zfill(8)
    if len(sid) >= 8:
        return os.path.join(output_base, 'npc', sid[:2], sid[2:4], f'{sid}.xml')
    else:
        return os.path.join(output_base, 'npc', sid[:2], sid[2:4], f'{int(sid):08d}.xml')

def process_npcdata_folder(source_dir, output_dir):
    """Processing npcdata directory（KMS collection -> GMS individualfile）"""
    src = os.path.join(source_dir, 'npcdata')
    if not os.path.exists(src):
        print('[!] npcdata Directory does not exist:', src)
        return
    print('\n' + '='*50)
    print('Processing npcdata (KMS collection -> GMS individual files)')
    print('='*50)
    xml_files = sorted([f for f in os.listdir(src) if f.endswith('.xml')])
    total = len(xml_files)
    total_npcs = 0
    errors = []
    print(f'Found {total} files')
    for fi, fname in enumerate(xml_files, 1):
        src_file = os.path.join(src, fname)
        try:
            tree = ET.parse(src_file)
            root = tree.getroot()
        except Exception as e:
            errors.append(f'{fname}: 解析Error {e}')
            continue
        npcs = root.findall('.//npc')
        total_npcs += len(npcs)
        for npc in npcs:
            npc_id = npc.get('id')
            if not npc_id:
                continue
            new_env, effectdummy = _create_gms_environment(npc)
            if new_env is None:
                errors.append(f'{fname}: NPC {npc_id} missing <environment>')
                continue
            out_path = _npc_id_to_gms_path(npc_id, output_dir)
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            new_root = ET.Element('ms2')
            new_root.append(new_env)
            if effectdummy is not None:
                new_root.append(effectdummy)
            new_tree = ET.ElementTree(new_root)
            ET.indent(new_tree)
            new_tree.write(out_path, encoding='utf-8', xml_declaration=True)
        if fi % 10 == 0 or fi == total:
            pct = fi * 100 // total
            print(f'\rProgress: {fi}/{total} ({pct}%)', end='', flush=True)
    print()
    print(f'\nConversion completed! Files: {total}, NPC: {total_npcs}')
    print(f'Success: {total_npcs - len(errors)}, Error: {len(errors)}')

#======================================================================
# riding Converting相关
#======================================================================

# GMS <riding>/<basic> 独有attribute默认值（KMS 缺失 attribute）
_RIDING_BASIC_DEFAULTS = {
    'hideRider': 'false', 'battleLife': 'true', 'enableRideOffUI': 'false',
    'useRidingUI': 'false', 'skillSetID': '0', 'rideBone2': '',
    'rideTranslation2': '0,0,0', 'rideRotation2': '0,0,0',
    'walkSpeed': '1', 'swimSpeed': '0', 'enableSwim': '0',
    'rideAniPC2': '', 'rideAniPC_Idle': '', 'rideAniPC_Run': '',
    'rideAniPC_Jump': '', 'rideAniPC_SP_Idle': '', 'rideAniPC_SP_Run': '',
    'rideAniPC_SP_Jump': '', 'fallDamageDown': '0',
    'pressXEffectIdle': '', 'releaseXEffectIdle': '',
    'pressXEffectRun': '', 'releaseXEffectRun': '',
    'pressXEffectIdleNonstop': '', 'pressXEffectRunNonstop': '',
    'loopEffect': '', 'nameTagOffsetY': '',
}

# GMS 独有子node默认值（按 GMS 顺序排列）
_RIDING_NODE_DEFAULTS_ORDER = ['collision', 'capsule', 'shadow', 'faceCamera', 'stat']
_RIDING_NODE_DEFAULTS = {
    'collision': {'shape': 'box', 'width': '100', 'height': '130', 'depth': '100'},
    'capsule': {'radius': '25', 'height': '150'},
    'shadow': {'bias': '1'},
    'stat': {'str': '0', 'dex': '0', 'int': '0', 'luk': '0', 'hp': '0',
             'hp_rgp': '0', 'hp_inv': '0', 'sp': '0', 'sp_rgp': '0', 'sp_inv': '0',
             'ep': '0', 'ep_rgp': '0', 'ep_inv': '0', 'asp': '0', 'msp': '0',
             'atp': '0', 'evp': '0', 'cap': '0', 'cad': '0', 'car': '0',
             'ndd': '0', 'abp': '0', 'jmp': '0', 'pap': '0', 'map': '0',
             'par': '0', 'mar': '0', 'wapmin': '0', 'wapmax': '0',
             'pen': '0', 'rmsp': '0', 'bap': '0'},
}

# GMS ridepassenger 默认attribute（含 GMS 独有）
_RIDING_PASSENGER_DEFAULTS = {
    'rideTranslation': '0,0,0', 'rideRotation': '0,0,0',
    'rideTranslation2': '0,0,0', 'rideAniPC': 'Ride_Idle_A', 'rideAniPC2': '',
    'rideAniPC_Idle': '', 'rideAniPC_Run': '', 'rideAniPC_Jump': '',
    'rideAniPC_SP_Idle': '', 'rideAniPC_SP_Run': '', 'rideAniPC_SP_Jump': '',
    'nameTagOffsetY': '',
}


def _transform_riding_basic(kms_basic):
    """Converts KMS <basic> Convertingto GMS <basic>，补全 GMS 独有attribute"""
    new_basic = ET.Element('basic')
    for k, v in kms_basic.attrib.items():
        new_basic.set(k, v)
    for k, default in _RIDING_BASIC_DEFAULTS.items():
        if k not in new_basic.attrib:
            new_basic.set(k, default)
    # rideAniPC2 默认Copy rideAniPC
    if not new_basic.get('rideAniPC2') and new_basic.get('rideAniPC'):
        new_basic.set('rideAniPC2', new_basic.get('rideAniPC'))
    return new_basic


def process_riding_folder(source_dir, output_dir):
    """Converting riding directory：主fileattribute补全 + passenger 拆分toindividualfile"""
    riding_dir = os.path.join(source_dir, 'riding')
    if not os.path.isdir(riding_dir):
        print('riding Directory does not exist')
        return

    out_riding = os.path.join(output_dir, 'riding')
    out_passenger = os.path.join(out_riding, 'passenger')
    out_effectdummy = os.path.join(out_riding, 'effectdummy')

    files = [f for f in os.listdir(riding_dir) if f.endswith('.xml')]
    total = len(files)
    count = 0
    passenger_count = 0
    errors = []

    # 1. Processing effectdummy 子directory（DirectCopy）
    kms_ed = os.path.join(riding_dir, 'effectdummy')
    if os.path.isdir(kms_ed):
        if os.path.exists(out_effectdummy):
            shutil.rmtree(out_effectdummy)
        shutil.copytree(kms_ed, out_effectdummy)
        print('effectdummy: Copy completed')

    # 2. Processing主 riding file
    for f in files:
        src = os.path.join(riding_dir, f)
        if not os.path.isfile(src):
            continue
        try:
            tree = ET.parse(src)
        except Exception as e:
            errors.append(f'{f}: {e}')
            continue

        root = tree.getroot()
        riding = root.find('riding')
        if riding is None:
            shutil.copy2(src, os.path.join(out_riding, f))
            continue

        # Converting <basic>
        kms_basic = riding.find('basic')
        if kms_basic is not None:
            new_basic = _transform_riding_basic(kms_basic)
            riding.remove(kms_basic)

        # 重建子node，按 GMS 顺序排列
        existing_children = list(riding)
        for child in existing_children:
            riding.remove(child)
        # basic 必须是第一子node
        if kms_basic is not None:
            riding.append(new_basic)
        for tag in _RIDING_NODE_DEFAULTS_ORDER:
            defaults = _RIDING_NODE_DEFAULTS.get(tag, {})
            # 从已有子node中找
            node = None
            for child in existing_children:
                if child.tag == tag:
                    node = child
                    break
            if node is None:
                node = ET.Element(tag)
            for k, default in defaults.items():
                if k not in node.attrib:
                    node.set(k, default)
            riding.append(node)
        # Add非标准顺序 剩余子node
        for child in existing_children:
            if child.tag not in _RIDING_NODE_DEFAULTS_ORDER:
                riding.append(child)

        # extraction passenger 数据并拆分toindividualfile
        passengers = riding.find('passengers')
        passenger_single = riding.find('passenger')
        passenger_list = []

        if passengers is not None:
            for p in passengers.findall('passenger'):
                passenger_list.append(p)
            riding.remove(passengers)

        if passenger_single is not None:
            riding.remove(passenger_single)

        # 写入 passenger individualfile
        for p in passenger_list:
            ride_id = kms_basic.get('id', '') if kms_basic is not None else ''
            rp_root = ET.Element('ms2')
            rp = ET.SubElement(rp_root, 'ridepassenger')
            rp.set('id', ride_id)
            for k, v in p.attrib.items():
                rp.set(k, v)
            for k, default in _RIDING_PASSENGER_DEFAULTS.items():
                if k not in rp.attrib:
                    rp.set(k, default)
            rp_tree = ET.ElementTree(rp_root)
            ET.indent(rp_tree)
            os.makedirs(out_passenger, exist_ok=True)
            rp_path = os.path.join(out_passenger, f'{ride_id}.xml')
            rp_tree.write(rp_path, encoding='utf-8', xml_declaration=True)
            passenger_count += 1

        # 写入主file
        new_tree = ET.ElementTree(root)
        ET.indent(new_tree)
        out_path = os.path.join(out_riding, f)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        new_tree.write(out_path, encoding='utf-8', xml_declaration=True)
        count += 1

        if count % 50 == 0:
            pct = count * 100 // total
            print(f'\rProgress: {count}/{total} ({pct}%)', end='', flush=True)

    print(f'\nriding Conversion completed! Files: {count}, passenger: {passenger_count}')
    if errors:
        print(f'Error: {len(errors)}')
        for e in errors[:5]:
            print(f'  {e}')


#======================================================================
# quest Converting相关
#======================================================================

# GMS <basic> 独有attribute默认值
_QUEST_BASIC_DEFAULTS = {
    'questType': '0', 'account': '0', 'autoStart': '0',
    'disableGiveup': '0', 'exceptChapterClear': '0', 'repeatable': '0',
    'usePeriod': '', 'eventTag': '', 'tabIndex': '-1', 'forceRegistGuide': '0',
}

# GMS 独有子node模板
_QUEST_GMS_NODES = {
    'notify': {'completeUiEffect': '', 'acceptSoundKey': '', 'completeSoundKey': ''},
    'require': {'maxLevel': '0', 'quest': '', 'selectableQuest': '', 'unrequire': '',
               'field': '', 'achievement': '0', 'unreqAchievement': '', 'groupID': '0',
               'dayOfWeek': '', 'gearScore': '0'},
    'acceptReward': {},
    'completeReward': {'karma': '0', 'lu': '0'},
    'progressMap': {'progressMap': ''},
    'guide': {'guideType': '', 'guideIcon': '', 'guideMinLevel': '0', 'guideMaxLevel': '0'},
    'gotoNpc': {'enable': '0', 'gotoField': '0', 'gotoPortal': '0'},
    'gotoDungeon': {'state': '0', 'gotoDungeon': '0', 'gotoInstanceID': '0'},
    'remoteAccept': {'useRemote': '0', 'requireField': '0'},
    'remoteComplete': {'useRemote': '0', 'requireField': '0', 'requireDungeonClear': '0'},
    'summonPortal': {'fieldID': '0', 'portalID': '0'},
    'eventMission': {'event': ''},
}

# GMS 独有子node 插入顺序
_QUEST_GMS_NODE_ORDER = [
    'notify', 'acceptReward', 'progressMap', 'guide',
    'gotoNpc', 'gotoDungeon', 'remoteAccept', 'remoteComplete',
    'summonPortal', 'eventMission',
]


def process_quest_folder(source_dir, output_dir):
    """Converting quest directory：补全 GMS 独有nodeandattribute"""
    quest_dir = os.path.join(source_dir, 'quest')
    if not os.path.isdir(quest_dir):
        print('quest Directory does not exist')
        return

    out_quest = os.path.join(output_dir, 'quest')
    files = [f for f in os.listdir(quest_dir) if f.endswith('.xml')]
    total = len(files)
    count = 0
    errors = []

    for f in files:
        src = os.path.join(quest_dir, f)
        try:
            tree = ET.parse(src)
        except Exception as e:
            errors.append(f'{f}: {e}')
            continue

        root = tree.getroot()
        env = root.find('environment')
        if env is None:
            shutil.copy2(src, os.path.join(out_quest, f))
            continue

        # Add locale="" 到 environment
        if 'locale' not in env.attrib:
            env.set('locale', '')

        quest = env.find('quest')
        if quest is None:
            shutil.copy2(src, os.path.join(out_quest, f))
            continue

        # 1. 补全 <basic> GMS 独有attribute
        basic = quest.find('basic')
        if basic is not None:
            for k, default in _QUEST_BASIC_DEFAULTS.items():
                if k not in basic.attrib:
                    basic.set(k, default)

        # 2. 补全 <require> GMS 独有attribute
        require = quest.find('require')
        if require is not None:
            for k, default in _QUEST_GMS_NODES['require'].items():
                if k not in require.attrib:
                    require.set(k, default)

        # 3. 补全 <completeReward> GMS 独有attribute
        cr = quest.find('completeReward')
        if cr is not None:
            for k, default in _QUEST_GMS_NODES['completeReward'].items():
                if k not in cr.attrib:
                    cr.set(k, default)

        # 4. 插入 GMS 独有子node
        for tag in _QUEST_GMS_NODE_ORDER:
            if tag == 'require':
                continue
            if quest.find(tag) is not None:
                node = quest.find(tag)
                for k, default in _QUEST_GMS_NODES[tag].items():
                    if k not in node.attrib:
                        node.set(k, default)
            else:
                new_node = ET.SubElement(quest, tag)
                for k, default in _QUEST_GMS_NODES[tag].items():
                    new_node.set(k, default)

        # 写入
        new_tree = ET.ElementTree(root)
        ET.indent(new_tree)
        out_path = os.path.join(out_quest, f)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        new_tree.write(out_path, encoding='utf-8', xml_declaration=True)
        count += 1

        if count % 200 == 0:
            pct = count * 100 // total
            print(f'\rProgress: {count}/{total} ({pct}%)', end='', flush=True)

    print(f'\nquest Conversion completed! Files: {count}/{total}')
    if errors:
        print(f'Error: {len(errors)}')
        for e in errors[:5]:
            print(f'  {e}')


def process_mapxblock_folder(source_dir, output_dir):
    """Converting mapxblock directory：KMS所有fileCopy，GMS-only4loginfile也Preserving"""
    kms_dir = os.path.join(source_dir, 'mapxblock')
    gms_dir = os.path.join(source_dir, '3GMSXml', 'mapxblock')
    out_dir = os.path.join(output_dir, 'mapxblock')

    if not os.path.exists(kms_dir):
        print('mapxblock: KMS directory does not exist, skipping')
        return

    os.makedirs(out_dir, exist_ok=True)

    kms_files = set(os.listdir(kms_dir))
    gms_files = set(os.listdir(gms_dir)) if os.path.exists(gms_dir) else set()

    # KMSfullCopy
    kms_count = 0
    for f in kms_files:
        shutil.copy2(os.path.join(kms_dir, f), os.path.join(out_dir, f))
        kms_count += 1

    # GMS-only 4loginfile也Copy
    gms_only = gms_files - kms_files
    gms_count = 0
    for f in gms_only:
        shutil.copy2(os.path.join(gms_dir, f), os.path.join(out_dir, f))
        gms_count += 1

    print(f'mapxblock Conversion completed: KMS={kms_count}, GMS-only={gms_count}, Total={kms_count+gms_count}')


def process_map_folder(source_dir, output_dir):
    """mapdirectory是GMS-only，Direct从3GMSXml/mapCopy"""
    gms_ref = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), '3GMSXml')
    gms_map_dir = os.path.join(gms_ref, 'map')
    out_dir = os.path.join(output_dir, 'map')

    if not os.path.exists(gms_map_dir):
        print('map: GMS directory does not exist, skipping')
        return

    os.makedirs(out_dir, exist_ok=True)

    count = 0
    for f in os.listdir(gms_map_dir):
        src = os.path.join(gms_map_dir, f)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(out_dir, f))
            count += 1

    print(f'map Conversion completed: Direct copyGMS original, Total{count}files')


def process_excel_folder(source_dir, output_dir):
    """exceldirectory是GMS-only，Direct从3GMSXml/excelCopy"""
    gms_ref = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), '3GMSXml')
    gms_excel_dir = os.path.join(gms_ref, 'excel')
    out_dir = os.path.join(output_dir, 'excel')

    if not os.path.exists(gms_excel_dir):
        print('excel: GMS directory does not exist, skipping')
        return

    os.makedirs(out_dir, exist_ok=True)

    # Copy整directory树（包括子directory）
    count = 0
    for root, dirs, files in os.walk(gms_excel_dir):
        rel_path = os.path.relpath(root, gms_excel_dir)
        target_dir = os.path.join(out_dir, rel_path)
        os.makedirs(target_dir, exist_ok=True)
        for f in files:
            src = os.path.join(root, f)
            dst = os.path.join(target_dir, f)
            shutil.copy2(src, dst)
            count += 1

    print(f'excel Conversion completed: Direct copyGMS original, Total{count}files')


def _item_id_to_path(item_id):
    """itemID -> A/BB/CCCCCCCC.xml path"""
    padded = item_id.zfill(8)
    d1 = padded[0]
    d2 = padded[1:3]
    return os.path.join(d1, d2, padded + '.xml')


def _convert_kms_itemmodel_to_gms(im_elem):
    """ConvertsKMS <ItemModel> ConvertingtoGMS itempresetformat <ms2> 根node"""
    ms2 = ET.Element('ms2')

    # <basic /> node
    basic = ET.SubElement(ms2, 'basic')
    # 如果KMS customize 有 capAttach=1，加 friendly="1"
    cust_elem = im_elem.find('customize')
    if cust_elem is not None and cust_elem.get('capAttach') == '1':
        basic.set('friendly', '1')

    # <customize> node
    if cust_elem is not None:
        gms_cust = ET.SubElement(ms2, 'customize')
        # attribute映射
        gms_cust.set('colorPalette', cust_elem.get('colorPalette', '0'))
        gms_cust.set('color', cust_elem.get('color', '0'))
        gms_cust.set('colordetail', cust_elem.get('colordetail', '0'))
        gms_cust.set('ch0', cust_elem.get('ch0', '0'))
        gms_cust.set('ch1', cust_elem.get('ch1', '0'))
        gms_cust.set('ch2', cust_elem.get('ch2', '0'))
        gms_cust.set('defaultColorIndex', cust_elem.get('defaultColorIndex', '-1'))
        if 'colorDye' in cust_elem.attrib:
            gms_cust.set('colorDye', cust_elem.get('colorDye'))

        # KMS scale -> HR scale, KMS translation -> FD, KMS rotation -> CP
        hr = ET.SubElement(gms_cust, 'HR')
        hr.set('scale', cust_elem.get('scale', '0'))
        hr.set('pony', '0')

        fd = ET.SubElement(gms_cust, 'FD')
        fd.set('translation', cust_elem.get('translation', '0'))
        fd.set('rotation', cust_elem.get('rotation', '0'))
        fd.set('scale', '0')

        cp = ET.SubElement(gms_cust, 'CP')
        cp.set('xrotation', '0')
        cp.set('yrotation', '0')
        cp.set('zrotation', '0')
        cp.set('scale', '0')
        cp.set('attach', '0')

        # capTransform -> CP/transform
        for ct in cust_elem.findall('capTransform'):
            transform = ET.SubElement(cp, 'transform')
            # 位置and旋转值转to6位浮点
            pos = ct.get('position', '')
            rot = ct.get('rotation', '')
            if pos:
                parts = pos.split(',')
                pos = ', '.join('{0:.6f}'.format(float(p)) for p in parts)
                transform.set('position', pos)
            if rot:
                parts = rot.split(',')
                rot = ', '.join('{0:.6f}'.format(float(p)) for p in parts)
                transform.set('rotation', rot)
            transform.set('scale', '1')
    else:
        # 无 customize 时Add空模板
        gms_cust = ET.SubElement(ms2, 'customize')
        gms_cust.set('colorPalette', '0')
        gms_cust.set('color', '0')
        gms_cust.set('colordetail', '0')
        gms_cust.set('ch0', '0')
        gms_cust.set('ch1', '0')
        gms_cust.set('ch2', '0')
        gms_cust.set('defaultColorIndex', '-1')
        hr = ET.SubElement(gms_cust, 'HR')
        hr.set('scale', '0')
        hr.set('pony', '0')
        fd = ET.SubElement(gms_cust, 'FD')
        fd.set('translation', '0')
        fd.set('rotation', '0')
        fd.set('scale', '0')
        cp = ET.SubElement(gms_cust, 'CP')
        cp.set('xrotation', '0')
        cp.set('yrotation', '0')
        cp.set('zrotation', '0')
        cp.set('scale', '0')
        cp.set('attach', '0')

    # <slots> node
    slots_elem = im_elem.find('slots')
    gms_slots = ET.SubElement(ms2, 'slots')
    if slots_elem is not None:
        for slot in slots_elem.findall('slot'):
            gms_slot = ET.SubElement(gms_slots, 'slot')
            gms_slot.set('name', slot.get('name', ''))
            for asset in slot.findall('asset'):
                gms_asset = ET.SubElement(gms_slot, 'asset')
                # CopyKMS所有assetattribute
                for k, v in asset.attrib.items():
                    gms_asset.set(k, v)
                # 补充GMS-onlyattribute（如果KMS没有）
                if 'attachnode' not in gms_asset.attrib:
                    gms_asset.set('attachnode', '')
                if 'pony' not in gms_asset.attrib:
                    gms_asset.set('pony', '0')
                if 'zalign' not in gms_asset.attrib:
                    gms_asset.set('zalign', '0')
                if 'earfold' not in gms_asset.attrib:
                    gms_asset.set('earfold', '0')
                if 'ani' not in gms_asset.attrib:
                    gms_asset.set('ani', '0')
                if 'emotionhide' not in gms_asset.attrib:
                    gms_asset.set('emotionhide', '0')
                if 'capscale' not in gms_asset.attrib:
                    gms_asset.set('capscale', '1')
                if 'weapon' not in gms_asset.attrib:
                    gms_asset.set('weapon', '0')
                if 'gender' not in gms_asset.attrib:
                    gms_asset.set('gender', '2')
                if 'placeable' not in gms_asset.attrib:
                    gms_asset.set('placeable', '0')
                if 'replace' not in gms_asset.attrib:
                    gms_asset.set('replace', '0')
                # physx 子node
                physx_elem = asset.find('physx')
                if physx_elem is not None:
                    gms_physx = ET.SubElement(gms_asset, 'physx')
                    for k, v in physx_elem.attrib.items():
                        gms_physx.set(k, v)
                    if 'action' not in gms_physx.attrib:
                        gms_physx.set('action', '')
                else:
                    gms_physx = ET.SubElement(gms_asset, 'physx')
                    gms_physx.set('action', '')
            for scale in slot.findall('scale'):
                gms_scale = ET.SubElement(gms_slot, 'scale')
                # value formatConverting: 0.2,0.4,... -> 0.200000,0.400000,...
                val = scale.get('value', '')
                if val:
                    parts = val.split(',')
                    val = ','.join('{0:.6f}'.format(float(p)) for p in parts)
                    gms_scale.set('value', val)
                else:
                    gms_scale.set('value', '')
                gms_scale.set('min', scale.get('min', '0'))
                gms_scale.set('max', scale.get('max', '1'))
                gms_scale.set('reverse', scale.get('reverse', '0'))
            # 每slotAdd decal
            ET.SubElement(gms_slot, 'decal')
    else:
        # 空 slot
        gms_slot = ET.SubElement(gms_slots, 'slot')
        gms_slot.set('name', '')
        ET.SubElement(gms_slot, 'decal')

    return ms2


def process_itempreset_folder(source_dir, output_dir):
    """ConvertsKMS itemmodelcollectionConvertingtoGMS itempresetindividualfile"""
    kms_dir = os.path.join(source_dir, 'itemmodel')
    out_dir = os.path.join(output_dir, 'itempreset')

    if not os.path.exists(kms_dir):
        print('itempreset: KMS itemmodel directory does not exist, skipping')
        return

    # 创建outputdirectory
    os.makedirs(out_dir, exist_ok=True)
    
    # Copy3模板file
    gms_ref = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), '3GMSXml')
    gms_preset_dir = os.path.join(gms_ref, 'itempreset')
    for tpl in ['empty.xml', 'empty_asset.xml', 'petequipment.xml']:
        src = os.path.join(gms_preset_dir, tpl)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(out_dir, tpl))

    count = 0
    errors = 0

    for f in sorted(os.listdir(kms_dir)):
        if not f.endswith('.xml'):
            continue
        fpath = os.path.join(kms_dir, f)
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
        except ET.ParseError:
            errors += 1
            continue

        for im in root.findall('ItemModel'):
            item_id = im.get('id')
            if not item_id:
                errors += 1
                continue
            try:
                gms_ms2 = _convert_kms_itemmodel_to_gms(im)
                rel_path = _item_id_to_path(item_id)
                out_path = os.path.join(out_dir, rel_path)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                tree_out = ET.ElementTree(gms_ms2)
                ET.indent(tree_out, space='\t')
                tree_out.write(out_path, encoding='utf-8', xml_declaration=True)
                count += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f'  Error converting {item_id}: {e}')

    print(f'itempreset conversion completed: {count}files, {errors}Error')


#======================================================================
# itemdata Converting相关（2026-05-19 新增）
#======================================================================

def _get_item_path(item_id):
    """根据 item ID 生成 GMS path: A/BB/ID.xml"""
    if len(item_id) < 3:
        return None
    a = item_id[0]
    bb = item_id[1:3]
    return f"{a}/{bb}/{item_id}.xml"

def _load_gms_item_template(gms_dir, item_id):
    """加载 GMS item file作to模板"""
    rel_path = _get_item_path(item_id)
    if not rel_path:
        return None
    fpath = os.path.join(gms_dir, 'item', rel_path)
    if not os.path.exists(fpath):
        return None
    try:
        tree = ET.parse(fpath)
        return tree.getroot()
    except:
        return None



def _convert_kms_item_to_gms(kms_item, gms_template, item_id):
    """Converts KMS itemdata  item Convertingto GMS format"""
    if gms_template is not None:
        # 深拷贝 GMS 模板
        gms_root = copy.deepcopy(gms_template)
    else:
        # 创建空  ms2 结构
        gms_root = ET.Element('ms2')
        ET.SubElement(gms_root, 'environment')
    
    # 获取 environment node
    gms_env = gms_root.find('environment')
    if gms_env is None:
        gms_env = ET.SubElement(gms_root, 'environment')
    
    # KMS item   environment 子node
    kms_env = kms_item.find('environment')
    if kms_env is None:
        return gms_root
    
    # requiresProcessing node名（KMS itemdata 只有这5）
    kms_nodes = ['basic', 'property', 'limit', 'material', 'tool', 'function', 'option']
    
    # KMS   option noderequires特殊Processing：从 environment 内移到 ms2 层级
    kms_option = None
    kms_function = None
    kms_property = None
    
    for node_name in kms_nodes:
        kms_node = kms_env.find(node_name)
        if kms_node is None:
            continue
        
        if node_name == 'option':
            # option requires移到 environment 外面
            kms_option = kms_node
            continue
        
        if node_name == 'function':
            # function requires映射 param1 -> parameter
            kms_function = kms_node
            continue
        
        if node_name == 'property':
            # property requires映射 global* attribute
            kms_property = kms_node
            continue
        
        # 查找or创建 GMS 对应node
        gms_node = gms_env.find(node_name)
        if gms_node is None:
            gms_node = ET.SubElement(gms_env, node_name)
        
        # 用 KMS attribute覆盖 GMS attribute
        if node_name == 'function':
            # KMS 用 param1，GMS 用 parameter，requires映射
            attr_map = {'param1': 'parameter'}
            for key, value in kms_node.attrib.items():
                gms_key = attr_map.get(key, key)
                gms_node.set(gms_key, value)
        else:
            for key, value in kms_node.attrib.items():
                gms_node.set(key, value)
    
    # Processing property node（global* attribute映射）
    if kms_property is not None:
        gms_property = gms_env.find('property')
        if gms_property is None:
            gms_property = ET.SubElement(gms_env, 'property')
        # attribute映射：KMS global* -> GMS 对应attribute
        attr_map = {
            'globalRePackingLimitCount': 'rePackingLimitCount',
            'globalRePackingItemConsumeCount': 'rePackingItemConsumeCount',
        }
        for key, value in kms_property.attrib.items():
            gms_key = attr_map.get(key, key)
            gms_property.set(gms_key, value)
        # 显式删除已映射 旧attribute（防止残留）
        for old_key in attr_map:
            if old_key in gms_property.attrib:
                del gms_property.attrib[old_key]
    
    # Processing function node（param1 -> parameter 映射）
    if kms_function is not None:
        gms_function = gms_env.find('function')
        if gms_function is None:
            gms_function = ET.SubElement(gms_env, 'function')
        # attribute映射
        attr_map = {'param1': 'parameter'}
        for key, value in kms_function.attrib.items():
            gms_key = attr_map.get(key, key)
            gms_function.set(gms_key, value)
    
    # Processing option node（移到 environment 外）
    if kms_option is not None:
        # 查找or创建 ms2 Direct子node  option
        gms_option = gms_root.find('option')
        if gms_option is None:
            gms_option = ET.Element('option')
            # 插入到 environment 之后
            env_idx = list(gms_root).index(gms_env) if gms_env in list(gms_root) else 0
            gms_root.insert(env_idx + 1, gms_option)
        
        # attribute映射
        attr_map = {
            'constantID': 'optionID',
            'randomID': 'random',
            'optionLevel': 'optionLevelFactor',
        }
        
        # Copy KMS attribute到 GMS option
        for key, value in kms_option.attrib.items():
            gms_key = attr_map.get(key, key)
            gms_option.set(gms_key, value)
        
        # 补充 GMS 独有attribute
        if 'title' not in gms_option.attrib:
            gms_option.set('title', item_id)
        if 'static' not in gms_option.attrib:
            gms_option.set('static', item_id)
        if 'constant' not in gms_option.attrib:
            gms_option.set('constant', item_id)
    
    return gms_root

def process_itemdata_folder(source_dir, output_dir):
    """Processing itemdata folder：KMS collection -> GMS individualfile"""
    kms_dir = os.path.join(source_dir, 'itemdata')
    gms_dir = output_dir  # 3GMSXml
    out_dir = os.path.join(output_dir, 'item')
    
    if not os.path.exists(kms_dir):
        print(f'KMS itemdata Directory does not exist: {kms_dir}')
        return
    
    # 读取模板
    template_path = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), 'item_template.xml')
    if not os.path.exists(template_path):
        print(f'Error: Template file does not exist: {template_path}')
        return
    try:
        item_template = ET.parse(template_path).getroot()
        print(f'Template loaded: {template_path}')
    except Exception as e:
        print(f'Error: Cannot parse template: {e}')
        return
    
    # 统计
    total = 0
    created = 0
    errors = 0
    
    # 遍历 KMS itemdata file
    print('Processing KMS itemdata...')
    files = [f for f in os.listdir(kms_dir) if f.endswith('.xml')]
    for i, fname in enumerate(files, 1):
        if i % 50 == 0:
            print(f'  Processing: {i}/{len(files)} ({fname})')
        
        fpath = os.path.join(kms_dir, fname)
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
        except ET.ParseError as e:
            errors += 1
            continue
        
        # 遍历每 item
        for kms_item in root.findall('item'):
            item_id = kms_item.get('id')
            if not item_id:
                continue
            
            total += 1
            
            # 确定outputpath
            rel_path = _get_item_path(item_id)
            if not rel_path:
                errors += 1
                continue
            out_path = os.path.join(out_dir, rel_path)
            
            # 使用通用模板
            gms_template = item_template
            
            # Converting
            try:
                gms_root = _convert_kms_item_to_gms(kms_item, gms_template, item_id)
                
                # 写入file
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                tree_out = ET.ElementTree(gms_root)
                ET.indent(tree_out, space='\t')
                tree_out.write(out_path, encoding='utf-8', xml_declaration=True)
                
                created += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f'  Error converting {item_id}: {e}')
    
    print(f'itemdata Conversion completed:')
    print(f'  Total: {total}')
    print(f'  Created: {created}')
    print(f'  Error: {errors}')


if __name__ == '__main__':
    main()
