# -*- coding: utf-8 -*-
"""
CG to GMS Format Converter
用于将4C&GXml的achieve文件转换为3GMSXml格式
Converts 4C&GXml achieve files to 3GMSXml format
"""

import os
import re
import copy
import xml.etree.ElementTree as ET
from pathlib import Path

def find_subfolders(source_dir):
    """查找源目录下的所有子文件夹"""
    folders = []
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders

def convert_achieve_to_gms(content):
    """将CG格式转换为GMS格式"""
    try:
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  XML解析错误 / XML Parse Error: {e}")
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
    """处理achieve文件夹"""
    source_achieve = os.path.join(source_dir, 'achieve')
    output_achieve = os.path.join(output_dir, 'achieve')
    
    if not os.path.exists(source_achieve):
        print(f"错误: 源目录不存在: {source_achieve}")
        return
    
    os.makedirs(output_achieve, exist_ok=True)
    xml_files = [f for f in os.listdir(source_achieve) if f.endswith('.xml')]
    total = len(xml_files)
    
    print(f"\n找到 {total} 个XML文件")
    print("开始转换...\n")
    
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
            print(f"  处理时出错 {filename}: {e}")
            failed += 1
        if i % 100 == 0 or i == total:
            print(f"进度: {i}/{total}")
    
    print(f"\n转换完成! 成功: {success}, 失败: {failed}")
    print(f"输出目录: {output_achieve}")

def _count_items(folder_path):
    """递归计算目录中的文件总数"""
    count = 0
    for root, dirs, files in os.walk(folder_path):
        count += len(files)
    return count

def process_table_folder(source_dir, output_dir):
    """处理table文件夹：让用户选择cn或kr，复制到输出目录并重命名为na/"""
    import shutil
    source_table = os.path.join(source_dir, 'table')
    output_table = os.path.join(output_dir, 'table')
    
    if not os.path.exists(source_table):
        print(f"错误: 源目录不存在: {source_table}")
        return
    
    cn_path = os.path.join(source_table, 'cn')
    kr_path = os.path.join(source_table, 'kr')
    default_path = os.path.join(source_table, 'default')
    
    if not os.path.exists(cn_path) and not os.path.exists(kr_path):
        print(f"错误: 源目录缺少cn/或kr/子文件夹")
        return
    
    print("\ntable 转换: 请选择要使用的版本:")
    if os.path.exists(cn_path):
        cn_count = _count_items(cn_path)
        print(f"  1. cn (国服) - {cn_count} 个文件")
    if os.path.exists(kr_path):
        kr_count = _count_items(kr_path)
        print(f"  2. kr (韩服) - {kr_count} 个文件")
    print("  3. 两个都要")
    
    choice = input("请输入选择 (1/2/3): ").strip()
    os.makedirs(output_table, exist_ok=True)
    copied = 0
    
    def copy_and_rename(src, dst_name):
        dst = os.path.join(output_table, dst_name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        count = _count_items(dst)
        print(f"  已复制: {src} -> {dst} ({count} files)")
        return count
    
    if choice == '1' and os.path.exists(cn_path):
        copied += copy_and_rename(cn_path, 'na')
    elif choice == '2' and os.path.exists(kr_path):
        copied += copy_and_rename(kr_path, 'na')
    elif choice == '3':
        print("  提示: cn 将作为 na/ 输出")
        copied += copy_and_rename(cn_path, 'na')
        copied += copy_and_rename(kr_path, 'kr')
    else:
        print("无效选择，默认使用 cn")
        copied += copy_and_rename(cn_path, 'na')
    
    if os.path.exists(default_path):
        copied += copy_and_rename(default_path, 'default')
    
    print(f"\ntable 处理完成! ({copied} files)")

def process_direct_copy(source_dir, output_dir, folder_name):
    """直接复制文件夹（无转换）"""
    import shutil
    source_folder = os.path.join(source_dir, folder_name)
    output_folder = os.path.join(output_dir, folder_name)
    
    if not os.path.exists(source_folder):
        print(f"错误: 源目录不存在: {source_folder}")
        return
    
    total_files = _count_items(source_folder)
    print(f"共 {total_files} 个文件待复制")
    
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
        print(f"\r进度: {copied}/{total_files} ({pct}%)", end='', flush=True)
    
    print()
    print(f"复制完成! {folder_name} ({copied} files)")

def process_anikeyinfo_folder(source_dir, output_dir):
    """处理anikeyinfo文件夹，增量更新anikeytext.xml"""
    source_anikeyinfo = os.path.join(source_dir, 'anikeyinfo')
    output_anikeytext = os.path.join(output_dir, 'anikeytext.xml')
    
    if not os.path.exists(source_anikeyinfo):
        print(f"错误: 源目录不存在: {source_anikeyinfo}")
        return
    
    if not os.path.exists(output_anikeytext):
        print(f"错误: 输出目录缺少 anikeytext.xml")
        print(f"请先将原始GMS的 anikeytext.xml 放入: {output_dir}")
        return
    
    try:
        tree = ET.parse(output_anikeytext)
        root = tree.getroot()
    except Exception as e:
        print(f"错误: 无法解析 anikeytext.xml: {e}")
        return
    
    xml_files = [f for f in os.listdir(source_anikeyinfo) if f.endswith('.xml')]
    total = len(xml_files)
    print(f"找到 {total} 个XML文件 in anikeyinfo")
    print("开始增量更新...\n")
    
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
            print(f"  处理时出错 {filename}: {e}")
            error_count += 1
        if i % 100 == 0 or i == total:
            print(f"进度: {i}/{total}")
    
    try:
        tree.write(output_anikeytext, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"错误: 无法写入 anikeytext.xml: {e}")
        return
    
    print(f"\n更新完成! 替换: {replace_count}, 追加: {append_count}, 错误: {error_count}")

# ============================================================
# skilldata 转换相关函数
# ============================================================

def _skill_id_to_path(sid_str):
    """
    将技能ID映射为GMS文件路径（文件夹+文件名）
    - 8位以内: 补零到8位 → 取前2位作文件夹 → 文件名=补零8位
    - 9位:     直接取前3位作文件夹 → 文件名=原ID
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

# attack 子节点重命名映射

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
    转换 <attack> 的子节点: range→rangeProperty, sensor→sensorProperty, etc.
    gms_attack 已从模板深拷贝，包含完整默认属性。
    策略：以模板为基础，KMS 有什么覆盖什么；KMS 没有的保留模板默认值。
    """
    for child in kms_attack:
        tag = child.tag

        if tag in _ATTACK_CHILD_RENAME:
            # 标签重命名，从模板找对应节点，用 KMS 覆盖
            new_tag = _ATTACK_CHILD_RENAME[tag]
            new_elem = gms_attack.find(new_tag)
            if new_elem is None:
                new_elem = ET.SubElement(gms_attack, new_tag)
            for k, v in child.attrib.items():
                # rangeAdd / collision / collisionAdd 需要整型→浮点格式化
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
            # 其他未知子节点
            new_elem = gms_attack.find(child.tag)
            if new_elem is None:
                new_elem = ET.SubElement(gms_attack, child.tag)
            for k, v in child.attrib.items():
                new_elem.set(k, v)

def _convert_kms_skill_to_gms(skill_elem, template_tree):
    """
    将一个KMS <skill> 节点转换为GMS格式 <ms2 feature="">
    
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

    # ===== 处理 basic 节点 =====
    kms_basic = skill_elem.find('basic')
    if kms_basic is not None:
        gms_basic = new_root.find('basic')
        if gms_basic is not None:
            # mainType: KMS basic 属性，GMS basic 下不有此节点，跳过
            # (GMS 仅在特定职业技能中有 mainType，通用技能没有)

            # 复制 basic 的子节点属性到 GMS
            # 注意: autoTargeting/push 在 KMS basic 下，但在 GMS 中属于 level
            # 不复制到 basic，稍后用它们覆盖 level 模板默认值
            for child in kms_basic:
                if child.tag in _LEVEL_ONLY_TAGS:
                    continue  # 稍后在 level 层处理
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

    # ===== 处理每个 level 节点 =====
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

        # cooldown: level属性(ms) → beginCondition.cooldownTime(s)
        begin_cond = lvl_copy.find('beginCondition')
        if begin_cond is not None and lvl_cooldown is not None:
            try:
                cooldown_sec = float(lvl_cooldown) / 1000.0
                # GMS整秒不带小数点: 1.0→"1", 0.6→"0.6"
                cooldown_str = str(int(cooldown_sec)) if cooldown_sec == int(cooldown_sec) else str(cooldown_sec)
                begin_cond.set('cooldownTime', cooldown_str)
            except ValueError:
                pass

        # 遍历 KMS level 的直接子节点
        for child in lvl:
            tag = child.tag

            if tag == 'motion':
                # === <motion> 处理 ===
                gms_motion = lvl_copy.find('motion')
                if gms_motion is None:
                    gms_motion = ET.SubElement(lvl_copy, 'motion')

                # motion 属性 → motionProperty 子节点
                motion_prop = gms_motion.find('motionProperty')
                if motion_prop is None:
                    motion_prop = ET.SubElement(gms_motion, 'motionProperty')
                for k, v in child.attrib.items():
                    motion_prop.set(k, v)

                # Remove template attacks first
                for tpl_atk in list(gms_motion.findall('attack')):
                    gms_motion.remove(tpl_atk)

                # motion 下的 <attack> 节点
                for attack_child in child:
                    if attack_child.tag == 'attack':
                        # 从模板的 level 获取模板 attack（模板 motion 下的已被删除）
                        tpl_motion = gms_level_template.find('motion') if gms_level_template is not None else None
                        tpl_attack = tpl_motion.find('attack') if tpl_motion is not None else None
                        if tpl_attack is not None:
                            gms_attack = copy.deepcopy(tpl_attack)
                        else:
                            gms_attack = ET.Element('attack')
                        gms_motion.append(gms_attack)
                        # 用 KMS attack 属性覆盖模板默认值
                        for k, v in attack_child.attrib.items():
                            gms_attack.set(k, v)
                        # 转换 attack 子节点（模板已有默认值，KMS 覆盖）
                        _convert_attack_children(attack_child, gms_attack)
                    else:
                        # motion 下的其他子节点直接复制
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
                # level 直接子节点的 actionAdditional → conditionSkill
                cond_skill = ET.SubElement(lvl_copy, 'conditionSkill')
                for k, v in child.attrib.items():
                    if k == 'additionalID':
                        cond_skill.set('skillID', v)
                    else:
                        cond_skill.set(k, v)

            elif tag == 'chain':
                # KMS 独有，GMS 没有，跳过
                pass

            elif tag == 'detectProperty':
                # 同标签，复制 KMS 数据到 GMS detectProperty
                gms_detect = lvl_copy.find('detectProperty')
                if gms_detect is None:
                    gms_detect = ET.SubElement(lvl_copy, 'detectProperty')
                for k, v in child.attrib.items():
                    if k == 'rangeOffset':
                        v = _format_range_add(v)
                    gms_detect.set(k, v)

            else:
                # 其他 level 直接子节点直接复制
                gms_child = lvl_copy.find(tag)
                if gms_child is None:
                    gms_child = ET.SubElement(lvl_copy, tag)
                for k, v in child.attrib.items():
                    gms_child.set(k, v)

        new_root.append(lvl_copy)

    return new_root

def process_skilldata_folder(source_dir, output_dir):
    """处理skilldata文件夹：KMS格式 → GMS格式"""
    import shutil

    source_skill = os.path.join(source_dir, 'skilldata')
    output_skill = os.path.join(output_dir, 'skill')

    if not os.path.exists(source_skill):
        print(f"错误: 源目录不存在: {source_skill}")
        return

    # 读取模板
    template_path = os.path.join(os.path.dirname(source_dir.rstrip(os.sep)), 'skill_template.xml')
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在: {template_path}")
        return

    try:
        template_tree = ET.parse(template_path)
    except Exception as e:
        print(f"错误: 无法解析模板: {e}")
        return

    xml_files = sorted([f for f in os.listdir(source_skill) if f.endswith('.xml')])
    total_files = len(xml_files)
    total_skills = 0
    written = 0
    errors = 0

    print(f"\n找到 {total_files} 个XML文件 in skilldata")
    print("开始转换...\n")

    os.makedirs(output_skill, exist_ok=True)

    for fi, fname in enumerate(xml_files, 1):
        source_file = os.path.join(source_skill, fname)
        try:
            tree = ET.parse(source_file)
            root = tree.getroot()
        except Exception as e:
            print(f"  解析错误 {fname}: {e}")
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
                print(f"  转换技能 {sid} 时出错: {e}")
                errors += 1

        if fi % 10 == 0 or fi == total_files:
            pct = fi * 100 // total_files
            print(f"\r进度: {fi}/{total_files} ({pct}%)", end='', flush=True)

    print()
    print(f"\n转换完成! 文件: {total_files}, 技能: {total_skills}")
    print(f"成功: {written}, 错误: {errors}")
    print(f"输出目录: {output_skill}")


def main():
    print("=" * 50)
    print("CG格式转GMS格式转换器")
    print("=" * 50)

    while True:
        source_dir = input("\n请输入源目录路径: ").strip().strip('"')
        if os.path.exists(source_dir):
            break
        print(f"目录不存在，请重新输入")

    subfolders = find_subfolders(source_dir)

    if not subfolders:
        print("源目录下没有子文件夹")
        return

    print(f"\n可用文件夹:")
    for i, folder in enumerate(subfolders, 1):
        print(f"  {i}. {folder}")

    print("\n支持的文件夹: achieve, camera, ui, ugcmap, anikeyinfo, trigger, table, string, skilldata")

    if 'anikeyinfo' in subfolders:
        print("\n注意: 处理 anikeyinfo 需要输出目录已有原始 anikeytext.xml")

    if 'skilldata' in subfolders:
        parent_dir = os.path.dirname(source_dir.rstrip(os.sep))
        tpl = os.path.join(parent_dir, 'skill_template.xml')
        print(f"\n注意: 处理 skilldata 需要模板文件 skill_template.xml")
        print(f"  模板路径: {tpl}")

    choice = input("\n请选择要处理的文件夹编号 (多个用逗号分隔，直接回车选择全部): ").strip()

    supported = ['achieve', 'camera', 'ui', 'ugcmap', 'anikeyinfo', 'trigger', 'table', 'string', 'skilldata']

    if not choice:
        selected = [f for f in subfolders if f in supported]
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = [subfolders[i-1] for i in indices]
        except:
            print("选择无效，默认选择全部")
            selected = [f for f in subfolders if f in supported]

    while True:
        output_dir = input("\n请输入输出目录路径: ").strip().strip('"')
        if output_dir:
            break
        print("输出目录不能为空")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 50)
    print("转换信息")
    print("=" * 50)
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print(f"处理内容: {', '.join(selected)}")

    print("\n转换规则:")
    print("  achieve: 格式转换（locking、target 属性）")
    print("  camera/ui/ugcmap/trigger/string: 直接复制")
    print("  anikeyinfo: 增量更新 anikeytext.xml")
    print("  skilldata: KMS多技能文件 → GMS单技能文件")

    confirm = input("\n确认开始转换? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return

    for folder in selected:
        print(f"\n{'='*50}")
        print(f"处理文件夹: {folder}")
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
        else:
            print(f"未支持的文件夹: {folder}")

    print(f"\n{'='*50}")
    print("全部处理完成!")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()
