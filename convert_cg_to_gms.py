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
    
    # 目前只支持achieve / Currently only supports achieve
    if 'achieve' in subfolders:
        print(f"\n将处理 achieve 文件夹 (当前唯一支持) / Will process achieve folder (currently only supported)")
        selected = ['achieve']
    else:
        choice = input("\n请选择要处理的文件夹编号 (多个用逗号分隔) / Enter folder numbers (comma separated): ")
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            selected = [subfolders[i-1] for i in indices]
        except:
            print("选择无效，默认处理achieve / Invalid selection, defaulting to achieve")
            selected = ['achieve']
    
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
    print("  1. achieves标签添加 locking=\"\" 属性 / Add locking=\"\" to achieves tag")
    print("  2. condition标签添加 target=\"\" 属性 / Add target=\"\" to condition tag")
    print("  3. 每个grade添加空reward (如果没有) / Add empty reward to grade (if none)")
    print("  4. 属性顺序调整为GMS格式 / Reorder attributes to GMS format")
    
    confirm = input("\n确认开始转换? (y/n) / Confirm to start? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消 / Cancelled")
        return
    
    # 执行转换 / Execute conversion
    for folder in selected:
        print(f"\n处理文件夹 / Processing folder: {folder}")
        if folder == 'achieve':
            process_achieve_folder(source_dir, output_dir)

if __name__ == '__main__':
    main()
