# MapleStory 2 KMS → GMS XML 转换工具

将韩服(KMS)的 XML 数据转换为国际服(GMS)格式，用于私人服务器开发。

## 项目状态

**已完成 26/26 目录（全部完成）**

### 按策略分类

| 策略 | 目录 | 文件数 | 状态 |
|------|------|--------|------|
| **直接复制** | achieve, camera, ui, ugcmap, trigger, string, object, pet, emotion, musicscore, groundeffect, masteryhomemade, exportedugcmap, effect | - | ✅ |
| **增量合并** | skilldata, additionaleffect | 9451 + 6071 | ✅ |
| **格式转换** | table, anikeyinfo | - | ✅ |
| **大文件拆分** | script | NPC 3268 + Quest 14 | ✅ |
| **拆分+提取** | riding | 615 + 39 passenger | ✅ |
| **添加节点** | quest | 6809 | ✅ |
| **合集拆分** | npcdata | 10816 | ✅ |
| **合集拆分** | itemdata | 37617 | ✅ |
| **目录映射** | itempreset (itemmodel→itempreset) | 6674 | ✅ |
| **robocopy** | mapxblock | 1780 | ✅ |
| **GMS独有** | map | 1686 | ✅ |

### KMS 目录说明

KMS 共有 **28 个目录**，其中：
- **26 个已处理**：上述表格中的目录
- **2 个跳过**：
  - `additional` - additionaleffect 的旧版合集格式（5966定义），additionaleffect 已包含更完整数据
  - `questdata` - quest 的合集版本，quest 目录已处理（6809独立文件）

## 目录结构

```
Maple2_KC_Convert_to_Gms/
├── 2KMSXml/          # KMS 源数据
├── 3GMSXml/          # GMS 原版（作为转换基础）
├── 5newGMS/          # 转换输出
├── convert_cg_to_gms.py  # 主转换脚本
├── skill_template.xml     # skilldata 转换模板
├── item_template.xml      # itemdata 转换模板
└── README.md
```

## 使用方法

```bash
python convert_cg_to_gms.py
```

按提示选择要转换的目录，脚本会自动：
1. 读取 KMS 源数据（2KMSXml/）
2. 以 GMS 原版（3GMSXml/）为基础模板
3. 用 KMS 数据增量更新/补充缺失属性
4. 输出到 5newGMS/

## 转换策略

### 1. 直接复制
适用于 KMS/GMS 格式完全相同的情况（achieve, camera, ui 等）

### 2. 增量更新
以 GMS 原版为基础，用 KMS 数据填补缺失属性，GMS 已有值保持不变（skilldata, itemdata）

### 3. 格式转换
KMS 和 GMS 的 XML 结构不同，需要重新组织节点（anikeyinfo, quest）

### 4. 拆分/合并
KMS 是合集文件，GMS 是独立文件，需要拆分（npcdata, itemdata, script）

### 5. 属性映射
KMS 和 GMS 使用不同的属性名，需要映射：
- `param1` → `parameter` (function)
- `constantID` → `optionID` (option)
- `randomID` → `random` (option)
- `optionLevel` → `optionLevelFactor` (option)
- `globalRePackingLimitCount` → `rePackingLimitCount` (property)
- `globalRePackingItemConsumeCount` → `rePackingItemConsumeCount` (property)

## 注意事项

1. **网络盘性能**: SynologyDrive 网络路径上文件操作较慢，大批量复制建议使用 robocopy
2. **Python 版本**: 需要 Python 3.12+ 支持多行 f-string
3. **Windows 控制台**: GBK 编码不支持 Unicode 符号，用 ASCII 替代
4. **语法检查**: 每次修改后运行 `python -m py_compile convert_cg_to_gms.py` 验证
5. **模板文件**: skilldata 和 itemdata 需要对应的模板文件（skill_template.xml, item_template.xml）

## 已知问题

### npcdata 6个通用 Bug
转换后可能产生 6 个通用 Bug，已用后处理脚本修复。注意：重跑 `_create_gms_environment()` 会重现这些 Bug。

### itemdata KMS 独有物品
KMS 独有的 552 个物品使用 item_template.xml 作为模板，数据可能不完整，需要在游戏中进一步验证。

## 技术细节

### itemdata 转换
- KMS: 合集文件（如 itemdata/112.xml 包含 11200001, 11200002...）
- GMS: 独立文件，路径格式 `item/A/BB/ID.xml`（A=ID第1位，BB=ID第2-3位）
- 处理: 37617 个物品，32589 个交集，552 个 KMS 独有

### option 节点位置
- KMS: `<option>` 在 `<environment>` 内
- GMS: `<option>` 是 `<ms2>` 的直接子节点
- 转换时需要移动节点位置

## 验证结果（2026-05-20）

全部 22 个已完成目录验证通过：

| 目录类型 | 数量 | 目录 | 状态 |
|---------|------|------|------|
| 直接复制 | 10 | achieve, camera, ui, ugcmap, trigger, string, object, pet, emotion, musicscore | ✅ |
| 格式转换 | 3 | table, anikeyinfo, skilldata | ✅ |
| 拆分处理 | 5 | script, riding, npcdata, quest, itemdata | ✅ |
| 特殊处理 | 4 | mapxblock, map, itempreset, masteryhomemade | ✅ |

### 关键目录文件数
- npc: 10816 文件
- skill: 9451 文件  
- itempreset: 9094 文件
- quest: 6809 文件
- emotion: 4555 文件（新增）
- mapxblock: 1780 文件
- map: 1686 文件

### 输出目录命名映射
| KMS 目录 | 输出目录 | 说明 |
|---------|---------|------|
| npcdata | npc | 目录名简化 |
| itemdata | item | 目录名简化 |
| skilldata | skill | 目录名简化 |
| anikeyinfo | anikeytext.xml | 单文件输出 |

## 开发日志

详细开发记录见 `memory/2026-05-19.md`

## 许可证

仅供私人服务器开发学习使用，禁止商业用途。
