# -*- coding: utf-8 -*-
"""
CG to GMS Format Converter
用于将4C&GXml的achieve文件转换为3GMSXml格式
Converts 4C&GXml achieve files to 3GMSXml format
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

def find_subfolders(source_dir):
    """
    查找源目录下的所有子文件夹
    Find all subfolders in source directory
    """
    folders = []
    for item in os.listdir(source_dir):
        item_path = os.path.join(source_dir, item)
        if os.path.isdir(item_path):
            folders.append(item)
    return folders

def convert_achieve_to_gms(content):
    """
    将CG格式转换为GMS格式 / Convert CG format to GMS format
    
    转换规则 / Conversion rules:
    1. achieves标签添加locking=""属性，调整属性顺序
       Add locking="" attribute to achieves tag, reorder attributes
    2. condition标签添加target=""属性（如果没有）
       Add target="" attribute to condition tag (if not exists)
    3. 为每个grade添加空reward（如果该grade没有reward）
       Add empty reward to each grade (if no reward exists)
    """
    
    # 解析XML / Parse XML
    try:
        # 处理注释中的乱码，不影响解析
        # Keep garbled comments, won't affect parsing
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"  XML解析错误 / XML Parse Error: {e}")
        return None
    
    achieves_list = root.findall('achieves')
    
    for achieves in achieves_list:

        # 1. 处理achieves标签属性 / Process achieves tag attributes
        current_attrs = achieves.attrib.copy()
        
        # 定义GMS属性顺序 / Define GMS attribute order
        attr_order = ['id', 'account', 'icon', 'noticePercent', 'locking', 'categoryTag', 'feature', 'locale']
        
        # 移除所有属性后按GMS顺序重建
        # Remove all attributes and rebuild in GMS order
        new_attrs_list = []
        for attr in attr_order:
            if attr == 'locking':
                new_attrs_list.append(('locking', ''))  # locking强制为空 / locking forced to empty
            elif attr == 'noticePercent':
                new_attrs_list.append(('noticePercent', current_attrs.get('noticePercent', '1')))  # 默认1 / default 1
            elif attr in current_attrs:
                new_attrs_list.append((attr, current_attrs[attr]))
        
        # 清空并重新设置属性 / Clear and reset attributes
        for key in list(achieves.attrib.keys()):
            del achieves.attrib[key]
        for k, v in new_attrs_list:
            achieves.set(k, v)
        
        # 2. 处理每个grade / Process each grade
        for grade in achieves.findall('grade'):
            conditions = grade.findall('condition')
            rewards = grade.findall('reward')
            
            # 为每个condition添加target=""（如果没有）
            # Add target="" to each condition (if not exists)
            for cond in conditions:
                if 'target' not in cond.attrib:
                    cond.set('target', '')
            
            # 检查是否有reward / Check if reward exists
            if len(rewards) == 0:
                # 添加空reward / Add empty reward
                empty_reward = ET.SubElement(grade, 'reward')
                empty_reward.set('type', '')
                empty_reward.set('code', '0')
                empty_reward.set('value', '0')
                empty_reward.set('rank', '1')
            else:
                # 为没有rank的reward添加rank="1"
                # Add rank="1" to reward without rank
                for reward in rewards:
                    if 'rank' not in reward.attrib:
                        reward.set('rank', '1')
    
    # 重新生成XML字符串 / Regenerate XML string
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="utf-8"?>')
    
    # 保留原注释 / Keep original comments
    if '<!--' in content and '-->' in content:
        comment_match = re.search(r'(<!--.*?-->)', content, re.DOTALL)
        if comment_match:
            xml_lines.append(comment_match.group(1))
    
    def elem_to_str(element, indent=1):
        """
        将元素转换为格式化的XML字符串
        Convert element to formatted XML string
        """
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
    
    # 处理root本身（ms2标签）/ Process root itself (ms2 tag)
    xml_lines.append(elem_to_str(root))
    
    return '\n'.join(xml_lines)

def process_achieve_folder(source_dir, output_dir):
    """
    处理achieve文件夹 / Process achieve folder
    """
    source_achieve = os.path.join(source_dir, 'achieve')
    output_achieve = os.path.join(output_dir, 'achieve')
    
    if not os.path.exists(source_achieve):
        print(f"错误: 源目录不存在 / Error: Source directory not found: {source_achieve}")
        return
    
    # 创建输出目录 / Create output directory
    os.makedirs(output_achieve, exist_ok=True)
    
    # 获取所有xml文件 / Get all xml files
    xml_files = [f for f in os.listdir(source_achieve) if f.endswith('.xml')]
    total = len(xml_files)
    
    print(f"\n找到 / Found {total} 个XML文件 / XML files")
    print("开始转换... / Starting conversion...\n")
    
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
            print(f"  处理时出错 / Error processing {filename}: {e}")
            failed += 1
        
        if i % 100 == 0 or i == total:
            print(f"进度 / Progress: {i}/{total}")
    
    print(f"\n转换完成! / Conversion completed!")
    print(f"成功 / Success: {success}")
    print(f"失败 / Failed: {failed}")
    print(f"输出目录 / Output: {output_achieve}")

def _count_items(folder_path):
    """递归计算目录中的文件和子目录总数"""
    count = 0
    for root, dirs, files in os.walk(folder_path):
        count += len(files)
    return count

def process_table_folder(source_dir, output_dir):
    """
    处理table文件夹：让用户选择cn或kr，复制到输出目录并重命名为na/
    Process table folder: let user choose cn or kr, copy to output and rename to na/
    """
    import shutil
    source_table = os.path.join(source_dir, 'table')
    output_table = os.path.join(output_dir, 'table')
    
    if not os.path.exists(source_table):
        print(f"错误: 源目录不存在 / Error: Source directory not found: {source_table}")
        return
    
    cn_path = os.path.join(source_table, 'cn')
    kr_path = os.path.join(source_table, 'kr')
    default_path = os.path.join(source_table, 'default')
    
    if not os.path.exists(cn_path) and not os.path.exists(kr_path):
        print(f"错误: 源目录缺少cn/或kr/子文件夹 / Error: Missing cn/ or kr/ subfolder in {source_table}")
        return
    
    # 让用户选择 / Let user choose
    print("\ntable 转换: 请选择要使用的版本 / Please select version to use:")
    if os.path.exists(cn_path):
        cn_count = _count_items(cn_path)
        print(f"  1. cn (国服 / CMS) - {cn_count} 个文件 / files")
    if os.path.exists(kr_path):
        kr_count = _count_items(kr_path)
        print(f"  2. kr (韩服 / KMS) - {kr_count} 个文件 / files")
    print("  3. 两个都要 / Both")
    
    choice = input("请输入选择 (1/2/3) / Enter choice (1/2/3): ").strip()
    
    # 创建输出目录 / Create output directory
    os.makedirs(output_table, exist_ok=True)
    
    copied = 0
    
    def copy_and_rename(src, dst_name):
        """复制文件夹并重命名 / Copy folder and rename"""
        dst = os.path.join(output_table, dst_name)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        count = _count_items(dst)
        print(f"  已复制 / Copied: {src} -> {dst} ({count} files)")
        return count
    
    if choice == '1' and os.path.exists(cn_path):
        copied += copy_and_rename(cn_path, 'na')
    elif choice == '2' and os.path.exists(kr_path):
        copied += copy_and_rename(kr_path, 'na')
    elif choice == '3':
        print("  提示: cn 将作为 na/ 输出 / Note: cn will be output as na/")
        copied += copy_and_rename(cn_path, 'na')
        copied += copy_and_rename(kr_path, 'kr')
    else:
        print("无效选择，默认使用 cn / Invalid choice, defaulting to cn")
        copied += copy_and_rename(cn_path, 'na')
    
    # 复制default / Copy default
    if os.path.exists(default_path):
        copied += copy_and_rename(default_path, 'default')
    
    print(f"\ntable 处理完成! / Table processing completed! ({copied} files)")
    print(f"输出目录 / Output: {output_table}")

def process_direct_copy(source_dir, output_dir, folder_name):
    """
    直接复制文件夹（无转换）/ Copy folder directly (no conversion)
    用于camera、ui、ugcmap、trigger等不需要转换的文件夹
    """
    import shutil
    source_folder = os.path.join(source_dir, folder_name)
    output_folder = os.path.join(output_dir, folder_name)
    
    if not os.path.exists(source_folder):
        print(f"错误: 源目录不存在 / Error: Source directory not found: {source_folder}")
        return
    
    # 先统计文件总数 / Count total files first
    total_files = _count_items(source_folder)
    print(f"共 {total_files} 个文件待复制 / {total_files} files to copy")
    
    # 如果输出目录已存在，先删除 / Remove existing output if present
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    
    # 创建输出目录 / Create output directory
    os.makedirs(output_folder, exist_ok=True)
    
    # 复制所有文件（带进度） / Copy all files with progress
    copied = 0
    for item in os.listdir(source_folder):
        source_item = os.path.join(source_folder, item)
        output_item = os.path.join(output_folder, item)
        
        if os.path.isfile(source_item):
            shutil.copy2(source_item, output_item)
            copied += 1
        elif os.path.isdir(source_item):
            # 子目录：逐文件复制以显示进度
            for root, dirs, files in os.walk(source_item):
                rel_root = os.path.relpath(root, source_folder)
                dest_root = os.path.join(output_folder, rel_root)
                os.makedirs(dest_root, exist_ok=True)
                for f in files:
                    shutil.copy2(os.path.join(root, f), os.path.join(dest_root, f))
                    copied += 1
        
        # 每处理一个顶层项显示进度
        pct = copied * 100 // total_files if total_files > 0 else 100
        print(f"\r进度 / Progress: {copied}/{total_files} ({pct}%)", end='', flush=True)
    
    print()  # 换行
    print(f"复制完成! / Copy completed! {folder_name} ({copied} files)")
    print(f"输出目录 / Output: {output_folder}")

def process_anikeyinfo_folder(source_dir, output_dir):
    r"""
    处理anikeyinfo文件夹，增量更新anikeytext.xml
    Process anikeyinfo folder, incrementally update anikeytext.xml
    
    逻辑 / Logic:
    1. 检查源目录是否存在 / Check if source directory exists
    2. 检查输出目录是否有anikeytext.xml，如果没有 → 报错提示用户先放入原始文件
       Check if anikeytext.xml exists in output directory, if not → error and prompt user
    3. 如果有 → 读取4C&GXml/anikeyinfo/*.xml
       If yes → read 4C&GXml/anikeyinfo/*.xml
    4. 增量更新：已有<kfm>替换内容，新增<kfm>追加到</ms2ani>之前
       Incremental update: replace existing <kfm> content, append new <kfm> before </ms2ani>
    """
    source_anikeyinfo = os.path.join(source_dir, 'anikeyinfo')
    output_anikeytext = os.path.join(output_dir, 'anikeytext.xml')
    
    # 检查源目录 / Check source directory
    if not os.path.exists(source_anikeyinfo):
        print(f"错误: 源目录不存在 / Error: Source directory not found: {source_anikeyinfo}")
        return
    
    # 检查输出目录是否有anikeytext.xml / Check if anikeytext.xml exists in output directory
    if not os.path.exists(output_anikeytext):
        print(f"错误: 输出目录缺少 anikeytext.xml / Error: anikeytext.xml not found in output directory")
        print(f"请先将原始GMS的 anikeytext.xml 放入: {output_dir}")
        print(f"Please put the original GMS anikeytext.xml into: {output_dir}")
        return
    
    print(f"\n读取 anikeytext.xml: {output_anikeytext}")
    
    # 解析anikeytext.xml / Parse anikeytext.xml
    try:
        tree = ET.parse(output_anikeytext)
        root = tree.getroot()
    except Exception as e:
        print(f"错误: 无法解析 anikeytext.xml / Error: Cannot parse anikeytext.xml: {e}")
        return
    
    # 读取所有anikeyinfo XML文件 / Read all anikeyinfo XML files
    xml_files = [f for f in os.listdir(source_anikeyinfo) if f.endswith('.xml')]
    total = len(xml_files)
    
    print(f"找到 / Found {total} 个XML文件 / XML files in anikeyinfo")
    print("开始增量更新... / Starting incremental update...\n")
    
    replace_count = 0
    append_count = 0
    error_count = 0
    
    for i, filename in enumerate(xml_files, 1):
        # 获取文件名（不含扩展名）作为kfm name / Get filename without extension as kfm name
        kfm_name = os.path.splitext(filename)[0]
        
        # 读取anikeyinfo XML文件 / Read anikeyinfo XML file
        source_file = os.path.join(source_anikeyinfo, filename)
        try:
            file_tree = ET.parse(source_file)
            file_root = file_tree.getroot()  # <ms2> tag
            
            # 检查是否已存在同名<kfm> / Check if <kfm> with same name already exists
            existing_kfm = root.find(f"kfm[@name='{kfm_name}']")
            
            if existing_kfm is not None:
                # 替换：删除旧的子元素，添加新的子元素
                # Replace: remove old children, add new children
                for child in list(existing_kfm):
                    existing_kfm.remove(child)
                for child in file_root:
                    existing_kfm.append(child)
                replace_count += 1
            else:
                # 追加：创建新的<kfm>元素，插入到</ms2ani>之前
                # Append: create new <kfm> element, insert before </ms2ani>
                new_kfm = ET.Element('kfm')
                new_kfm.set('name', kfm_name)
                for child in file_root:
                    new_kfm.append(child)
                # 插入到root的倒数第二个位置（最后一个是</ms2ani>的话）
                # Insert at second to last position (before </ms2ani>)
                root.append(new_kfm)
                append_count += 1
            
        except Exception as e:
            print(f"  处理时出错 / Error processing {filename}: {e}")
            error_count += 1
        
        if i % 100 == 0 or i == total:
            print(f"进度 / Progress: {i}/{total}")
    
    print(f"\n正在写入 / Writing: {output_anikeytext}")
    
    try:
        tree.write(output_anikeytext, encoding='utf-8', xml_declaration=True)
    except Exception as e:
        print(f"错误: 无法写入 anikeytext.xml / Error: Cannot write anikeytext.xml: {e}")
        return
    
    print(f"\n更新完成! / Update completed!")
    print(f"替换 / Replaced: {replace_count}")
    print(f"追加 / Appended: {append_count}")
    print(f"错误 / Errors: {error_count}")
    print(f"输出文件 / Output file: {output_anikeytext}")

def _skill_id_to_path(sid_str):
    """
    将技能ID映射为GMS文件路径（文件夹+文件名）
    KMS skilldata: 文件名格式 000.xml（3位），每个文件多个技能
    GMS skill:     skill/{前2位或3位}/{8位或9位}.xml
    
    映射规则:
    - 8位以内: 补零到8位 → 取前2位作文件夹 → 文件名=补零8位
    - 9位:     直接取前3位作文件夹 → 文件名=原ID
    """
    sid = int(sid_str)
    if sid < 100000000:  # 8位以内
        padded = str(sid).zfill(8)
        folder = padded[:2]
        fname = padded + '.xml'
    else:  # 9位
        folder = str(sid)[:3]
        fname = str(sid) + '.xml'
    return folder, fname

def _node_rename_map():
    """KMS节点名 → GMS节点名的映射"""
    return {
        'pause': 'pauseProperty',
        'range': 'rangeProperty',
        'arrow': 'arrowProperty',
        'damage': 'damageProperty',
    }

def _convert_kms_skill_to_gms(skill_elem, template_tree):
    """
    将一个KMS skill节点转换为GMS格式
    使用template_tree作为基础结构，填入KMS数据
    
    关键转换:
    1. <skill id="X"> → <ms2 feature="X"> (id通过文件名编码，不在XML中)
    2. 节点重命名: pause→pauseProperty, range→rangeProperty等
    3. <condition><weapon> → <beginCondition>内含<weapon>
    4. <level value="N" cooldown="500"> → <level value="N"> + <beginCondition cooldownTime="0.5">
    """
    rename_map = _node_rename_map()
    
    # 深拷贝模板 / Deep copy template
    import copy
    new_root = copy.deepcopy(template_tree.getroot())  # <ms2 feature="">
    
    skill_id = skill_elem.attrib.get('id', '')
    if not skill_id:
        return None
    
    # 设置feature属性为skill id
    new_root.set('feature', skill_id)
    
    # ===== 处理 basic 节点 =====
    kms_basic = skill_elem.find('basic')
    if kms_basic is not None:
        gms_basic = new_root.find('basic')
        if gms_basic is not None:
            # 遍历 KMS basic 的子节点，覆盖 GMS template 的属性
            for child in kms_basic:
                tag = child.tag
                # 节点重命名
                gms_tag = rename_map.get(tag, tag)
                
                # 查找或创建对应的 GMS 子节点
                gms_child = gms_basic.find(gms_tag)
                if gms_child is None:
                    # 如果模板没有这个节点，创建它
                    gms_child = ET.SubElement(gms_basic, gms_tag)
                
                # 合并属性：模板默认值 + KMS实际值覆盖
                for k, v in child.attrib.items():
                    gms_child.set(k, v)
    
    # ===== 处理每个 level 节点 =====
    kms_levels = skill_elem.findall('level')
    gms_level_template = new_root.find('level')  # 模板中只有一个level
    
    if kms_levels and gms_level_template is not None:
        # 清除模板中的level（准备重建）
        new_root.remove(gms_level_template)
    
    for lvl in kms_levels:
        lvl_value = lvl.attrib.get('value', '1')
        lvl_cooldown = lvl.attrib.get('cooldown', None)
        
        # 克隆模板level作为基础
        lvl_copy = copy.deepcopy(gms_level_template)
        lvl_copy.set('value', lvl_value)
        
        # 处理 cooldown: 从 level 移到 beginCondition，并转换 ms→s
        begin_cond = lvl_copy.find('beginCondition')
        if begin_cond is not None and lvl_cooldown is not None:
            try:
                cooldown_sec = float(lvl_cooldown) / 1000.0
                begin_cond.set('cooldownTime', str(cooldown_sec))
            except ValueError:
                pass  # 非数字cooldown忽略
        
        # 遍历 KMS level 的子节点，填入/覆盖 GMS level
        for child in lvl:
            tag = child.tag
            gms_tag = rename_map.get(tag, tag)
            
            if tag == 'condition':
                # <condition><weapon> → <beginCondition>内含<weapon>
                if begin_cond is not None:
                    for wc in child.findall('weapon'):
                        # 将 <weapon> 追加到 beginCondition
                        wc_copy = copy.deepcopy(wc)
                        begin_cond.append(wc_copy)
            else:
                gms_child = lvl_copy.find(gms_tag)
                if gms_child is None:
                    gms_child = ET.SubElement(lvl_copy, gms_tag)
                for k, v in child.attrib.items():
                    gms_child.set(k, v)
        
        new_root.append(lvl_copy)
    
    return new_root

def process_skilldata_folder(source_dir, output_dir):
    """
    处理skilldata文件夹：KMS格式 → GMS格式
    KMS: skilldata/*.xml，每文件多个技能，节点名不含Property
    GMS: skill/{00-99,100,120,130}/00000001.xml，单技能单文件，节点名含Property
    
    转换逻辑:
    1. 读取 skill_template.xml 作为模板
    2. 遍历 2KMSXml/skilldata/*.xml，提取每个 <skill> 节点
    3. 用模板生成GMS格式，填入KMS数据，重命名节点
    4. 按ID映射路径输出到 5NewGMS/skill/
    """
    import shutil
    
    source_skill = os.path.join(source_dir, 'skilldata')
    output_skill = os.path.join(output_dir, 'skill')
    
    # 检查源目录
    if not os.path.exists(source_skill):
        print(f"错误: 源目录不存在 / Error: Source directory not found: {source_skill}")
        return
    
    # 读取模板
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(os.path.dirname(source_dir), 'skill_template.xml')
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在 / Error: Template not found: {template_path}")
        return
    
    try:
        template_tree = ET.parse(template_path)
    except Exception as e:
        print(f"错误: 无法解析模板 / Error: Cannot parse template: {e}")
        return
    
    # 读取所有 KMS skilldata XML 文件
    xml_files = sorted([f for f in os.listdir(source_skill) if f.endswith('.xml')])
    total_files = len(xml_files)
    total_skills = 0
    written = 0
    errors = 0
    
    print(f"\n找到 / Found {total_files} 个XML文件 in skilldata")
    print("开始转换... / Starting conversion...\n")
    
    # 创建输出目录（会按需创建子文件夹）
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
                
                # 格式化输出
                ET.indent(gms_root)
                tree_out = ET.ElementTree(gms_root)
                tree_out.write(out_path, encoding='utf-8', xml_declaration=True)
                written += 1
                
            except Exception as e:
                print(f"  转换技能 {sid} 时出错: {e}")
                errors += 1
        
        if fi % 10 == 0 or fi == total_files:
            pct = fi * 100 // total_files
            print(f"\r进度 / Progress: {fi}/{total_files} ({pct}%)", end='', flush=True)
    
    print()
    print(f"\n转换完成! / Conversion completed!")
    print(f"处理文件 / Files: {total_files}, 技能总数 / Total skills: {total_skills}")
    print(f"成功写入 / Written: {written}, 错误 / Errors: {errors}")
    print(f"输出目录 / Output: {output_skill}")

def main():
    print("=" * 50)
    print("CG格式转GMS格式转换器 / CG to GMS Converter")
    print("=" * 50)
    
    # 第一步：输入源目录 / Step 1: Enter source directory
    while True:
        source_dir = input("\n请输入源目录路径 / Enter source directory: ").strip().strip('"')
        if os.path.exists(source_dir):
            break
        print(f"目录不存在 / Directory not found, please re-enter")
    
    # 第二步：列出子文件夹供选择 / Step 2: List subfolders for selection
    subfolders = find_subfolders(source_dir)
    
    if not subfolders:
        print("源目录下没有子文件夹 / No subfolders in source directory")
        return
    
    print(f"\n可用文件夹 / Available folders:")
    for i, folder in enumerate(subfolders, 1):
        print(f"  {i}. {folder}")
    
    # 显示支持的文件夹 / Show supported folders
    print("\n支持的文件夹 / Supported folders: achieve, camera, ui, ugcmap, anikeyinfo, trigger, table, string, skilldata")
    
    # 如果有anikeyinfo目录，提示需要先放入anikeytext.xml / If anikeyinfo exists, prompt about anikeytext.xml
    if 'anikeyinfo' in subfolders:
        print("\n注意 / Note: 处理 anikeyinfo 需要输出目录已有原始 anikeytext.xml")
        print("         Processing anikeyinfo requires original anikeytext.xml in output directory")
    
    # 如果有skilldata目录，提示需要的模板文件 / If skilldata exists, prompt about skill_template.xml
    if 'skilldata' in subfolders:
        parent_dir = os.path.dirname(source_dir.rstrip(os.sep))
        tpl = os.path.join(parent_dir, 'skill_template.xml')
        print(f"\n注意 / Note: 处理 skilldata 需要模板文件 skill_template.xml")
        print(f"         如果还没生成模板，脚本会自动使用已有GMS文件作为参考")
        print(f"         如需自定义模板，请检查: {tpl}")
    
    choice = input("\n请选择要处理的文件夹编号 (多个用逗号分隔，直接回车选择全部 / Enter for all): ").strip()
    
    if not choice:
        # 默认选择所有支持的文件夹 / Default: select all supported folders
        supported = ['achieve', 'camera', 'ui', 'ugcmap', 'anikeyinfo', 'trigger', 'table', 'string', 'skilldata']
        selected = [f for f in subfolders if f in supported]
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = [subfolders[i-1] for i in indices]
        except:
            print("选择无效，默认选择全部 / Invalid selection, selecting all")
            supported = ['achieve', 'camera', 'ui', 'ugcmap', 'anikeyinfo', 'trigger', 'table', 'string', 'skilldata']
            selected = [f for f in subfolders if f in supported]
    
    # 第三步：输入输出目录 / Step 3: Enter output directory
    while True:
        output_dir = input("\n请输入输出目录路径 / Enter output directory: ").strip().strip('"')
        if output_dir:
            break
        print("输出目录不能为空 / Output directory cannot be empty")
    
    # 创建输出目录 / Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # 显示转换信息 / Show conversion info
    print("\n" + "=" * 50)
    print("转换信息 / Conversion Info")
    print("=" * 50)
    print(f"源目录 / Source: {source_dir}")
    print(f"输出目录 / Output: {output_dir}")
    print(f"处理内容 / Processing: {', '.join(selected)}")
    
    print("\n转换规则 / Conversion rules:")
    print("  achieve: 格式转换（locking、target 属性）")
    print("  camera/ui/ugcmap/trigger/string: 直接复制")
    print("  anikeyinfo: 增量更新 anikeytext.xml（需输出目录已有原始文件）")
    print("  skilldata: KMS多技能文件 → GMS单技能文件（节点重命名+属性转换）")
    
    confirm = input("\n确认开始转换? (y/n) / Confirm to start? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消 / Cancelled")
        return
    
    # 执行转换 / Execute conversion
    for folder in selected:
        print(f"\n{'='*50}")
        print(f"处理文件夹 / Processing folder: {folder}")
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
            print("  ✓ string 目录已复制")
        elif folder == 'skilldata':
            process_skilldata_folder(source_dir, output_dir)
        else:
            print(f"未支持的文件夹 / Unsupported folder: {folder}")
    
    print(f"\n{'='*50}")
    print("全部处理完成! / All processing completed!")
    print(f"{'='*50}")

if __name__ == '__main__':
    main()