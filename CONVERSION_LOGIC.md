# 转换逻辑详细说明

本文档详细说明每个目录的转换策略和具体实现逻辑。

---

## 目录分类总览

| 分类 | 目录数量 | 说明 |
|------|---------|------|
| 直接复制 | 14 | KMS与GMS格式完全一致，直接复制 |
| 增量合并 | 2 | 以GMS为基础，用KMS数据更新缺失属性 |
| 格式转换 | 2 | 需要调整XML结构或属性名 |
| 拆分处理 | 3 | 将合集文件拆分为独立文件 |
| GMS独有 | 2 | 只存在于GMS，直接从GMS复制 |
| 其他 | 4 | 特殊处理逻辑 |

**总计：27个目录**

---

## 一、直接复制（14个目录）

**目录列表：**
- achieve（成就）
- camera（相机）
- ui（界面）
- ugcmap（UGC地图）
- trigger（触发器）
- string（字符串）
- object（对象）
- pet（宠物）
- emotion（表情）
- musicscore（乐谱）
- groundeffect（地面特效）
- masteryhomemade（自制精通）
- exportedugcmap（导出的UGC地图）
- effect（特效）

**转换逻辑：**
```
输入：KMS XML文件
处理：直接复制文件内容
输出：保持原样，无任何修改
```

**实现函数：** `process_direct_copy(source_dir, output_dir, folder_name)`

**原因：** KMS和GMS的XML结构完全一致，包括：
- 根节点 `<ms2>`
- 子节点结构
- 属性名称
- 值格式

---

## 二、增量合并（2个目录）

### 2.1 skilldata（技能数据）

**转换逻辑：**
```
输入：KMS技能文件（增量格式）+ GMS技能文件（完整格式）
处理：
  1. 加载GMS版本作为基础模板
  2. 解析KMS增量属性
  3. 按节点路径更新GMS对应节点
  4. GMS已有值保持不变，只更新KMS新增属性
输出：合并后的完整技能文件
```

**关键实现：**
- 模板文件：`skill_template.xml`（复制自GMS典型技能文件）
- KMS格式：仅包含变化的属性节点
- GMS格式：包含完整的28个子节点（BasicProperty, MotionProperty等）
- 特殊处理：
  - `global*` 属性映射（去掉global前缀）
  - conditionSkill 嵌套 beginCondition 结构
  - 子节点顺序必须符合GMS要求

**文件数：** 9451个

**实现函数：** `process_skilldata_folder(source_dir, output_dir)`

---

### 2.2 additionaleffect（附加效果）

**转换逻辑：**
```
输入：KMS附加效果文件 + GMS附加效果文件
处理：
  1. 加载GMS版本作为基础
  2. 用KMS属性更新对应节点
  3. 直接属性合并（不涉及复杂嵌套）
输出：合并后的附加效果文件
```

**关键实现：**
- GMS基础：完整的15+节点树
- KMS格式：简化增量更新格式
- 合并策略：属性级别合并，GMS结构保持不变

**文件数：** 6071个

**实现函数：** `process_additionaleffect(source_dir, output_dir)`

---

## 三、格式转换（2个目录）

### 3.1 table（表格）

**转换逻辑：**
```
输入：KMS表格文件（cn/kr两个版本）
处理：
  1. 让用户选择cn（中文）或kr（韩文）
  2. 复制选择的版本到输出目录
  3. 重命名为na/目录（北美服务器）
输出：na/目录下的表格文件
```

**关键实现：**
- 交互式选择：用户输入选择语言版本
- 目录重命名：cn/kr → na
- 内容保持不变

**实现函数：** `process_table_folder(source_dir, output_dir)`

---

### 3.2 anikeyinfo（动画关键帧信息）

**转换逻辑：**
```
输入：KMS的anikeyinfo目录（多个XML文件）+ GMS的anikeytext.xml（单一文件）
处理：
  1. 解析GMS的anikeytext.xml作为基础
  2. 遍历KMS的每个XML文件
  3. 按 kfm name 属性查找或创建节点
  4. 更新或追加动画关键帧信息
输出：更新后的anikeytext.xml
```

**关键实现：**
- KMS格式：每个KFM一个独立XML文件
- GMS格式：所有KFM聚合在一个XML文件中
- 增量更新：已存在的kfm替换，新kfm追加

**前置条件：** 输出目录必须已有GMS原版 `anikeytext.xml`

**实现函数：** `process_anikeyinfo_folder(source_dir, output_dir)`

---

## 四、拆分处理（3个目录）

### 4.1 script（脚本）

**转换逻辑：**
```
输入：KMS的script目录（npc.xml, quest.xml合集文件）
处理：
  NPC拆分：
    1. 解析npc.xml合集文件
    2. 每个npc节点拆分为独立文件
    3. 按NPC ID分组（1000-1999, 2000-2999等）
    4. 每组生成一个XML文件
  
  Quest拆分：
    1. 解析quest.xml合集文件
    2. 每个quest节点拆分为独立文件
    3. 按Quest ID范围分组
    4. 每组生成一个XML文件
输出：独立的小XML文件
```

**关键实现：**
- 输入文件大小：npc.xml ~58MB, quest.xml ~69MB
- 拆分策略：按ID范围分组（减少文件数量）
- 输出结构：
  ```
  npc/1000-1999.xml
  npc/2000-2999.xml
  ...
  quest/0-999.xml
  quest/1000-1999.xml
  ...
  ```

**文件数：** NPC 3268文件 + Quest 14文件

**实现函数：** `process_script_folder(cg_dir, out_dir)`

---

### 4.2 npcdata（NPC数据）

**转换逻辑：**
```
输入：KMS的npcdata目录（合集XML文件）+ GMS的npcdata目录（独立文件）
处理：
  1. 解析KMS合集文件（每个文件包含多个NPC定义）
  2. 每个NPC节点拆分为独立文件
  3. 文件路径：npc/A/BB/CCCCCCCC.xml（ID路径化）
  4. 合并GMS已有文件的数据
输出：每个NPC一个独立XML文件
```

**关键实现：**
- KMS格式：合集文件（如npc_0001-1000.xml）
- GMS格式：独立文件（如npc/0/00/00000001.xml）
- ID路径化：将NPC ID转换为目录路径（如ID=10000001 → npc/1/00/10000001.xml）
- 增量合并：KMS数据更新GMS模板

**文件数：** 10816个

**实现函数：** `process_npcdata_folder(source_dir, output_dir)`

---

### 4.3 itemdata（物品数据）

**转换逻辑：**
```
输入：KMS的itemdata目录（合集XML文件）+ GMS的itemdata目录（独立文件）
处理：
  1. 解析KMS合集文件
  2. 每个item节点拆分为独立文件
  3. 文件路径：item/A/BB/CCCCCCCC.xml
  4. 使用item_template.xml作为基础模板
  5. 合并KMS数据到GMS模板
输出：每个物品一个独立XML文件
```

**关键实现：**
- KMS格式：合集文件（104个文件）
- GMS格式：独立文件（37065个文件）
- 模板策略：`item_template.xml` 包含完整28个子节点
- ID路径化：类似npcdata

**文件数：** 37617个

**实现函数：** `process_itemdata_folder(source_dir, output_dir)`

---

## 五、特殊处理（4个目录）

### 5.1 riding（坐骑）

**转换逻辑：**
```
输入：KMS的riding目录 + GMS的riding目录
处理：
  1. 解析KMS合集文件
  2. 每个riding节点拆分为独立文件
  3. 提取passenger信息（乘客座位）
  4. passenger单独保存为独立文件
  5. 子节点按GMS顺序输出
输出：riding独立文件 + passenger独立文件
```

**关键实现：**
- 坐骑拆分：每个坐骑一个文件
- Passenger提取：从坐骑定义中提取乘客座位配置
- 节点顺序约束：
  ```
  basic → collision → capsule → shadow → faceCamera → stat
  ```
  （必须按此顺序，非字母序）

**文件数：** 615个riding + 39个passenger

**实现函数：** `process_riding_folder(source_dir, output_dir)`

---

### 5.2 quest（任务）

**转换逻辑：**
```
输入：KMS的quest目录（独立文件）+ GMS的quest目录（独立文件）
处理：
  1. 复制KMS文件到输出目录
  2. 在每个quest文件中添加GMS必需节点：
     - <notify> 节点
     - <notifyIcon> 节点
     - 其他GMS特有配置
输出：包含GMS节点的quest文件
```

**关键实现：**
- KMS格式：已有独立文件（非合集）
- GMS差异：需要额外的通知配置节点
- 节点插入位置：在 `</ms2>` 结束标签前

**文件数：** 6809个

**实现函数：** `process_quest_folder(source_dir, output_dir)`

---

### 5.3 itempreset（物品预设）

**转换逻辑：**
```
输入：KMS的itemmodel目录（合集XML文件）+ GMS的itempreset目录（独立文件）
处理：
  1. 解析KMS的itemmodel合集文件
  2. 每个item节点转换为itempreset格式
  3. 按ID路径化输出：itempreset/A/BB/CCCCCCCC.xml
  4. 复制GMS的模板文件（empty.xml, empty_asset.xml, petequipment.xml）
输出：itempreset独立文件
```

**关键实现：**
- 目录名映射：`itemmodel` → `itempreset`
- 格式转换：`itemmodel` 合集 → `itempreset` 独立文件
- asset属性映射：调整资源引用路径

**文件数：** 6674个

**实现函数：** `process_itempreset_folder(source_dir, output_dir)`

---

### 5.4 mapxblock（地图区块）

**转换逻辑：**
```
输入：KMS的mapxblock目录 + GMS的mapxblock目录
处理：
  1. 使用robocopy复制KMS文件
  2. 保留GMS的4个login文件（登录界面）
输出：合并后的mapxblock目录
```

**关键实现：**
- 工具选择：robocopy（SynologyDrive网络路径优化）
- 命令：
  ```bash
  robocopy kms_mapxblock out_mapxblock /E /XD login
  robocopy gms_mapxblock out_mapxblock /E /XF login/*
  ```
- GMS保留：login目录下的4个文件

**文件数：** 1780个

**实现函数：** `process_mapxblock_folder(source_dir, output_dir)`

---

## 六、GMS独有目录（2个目录）

### 6.1 map（地图）

**转换逻辑：**
```
输入：GMS的map目录
处理：直接复制GMS原版到输出目录
输出：GMS原版地图文件
```

**关键实现：**
- KMS无此目录
- GMS独有的地图配置
- 直接从 `3GMSXml/map` 复制

**文件数：** 1686个

**实现函数：** `process_map_folder(source_dir, output_dir)`

---

### 6.2 excel（Excel配置）

**转换逻辑：**
```
输入：GMS的excel目录
处理：直接复制GMS原版到输出目录（包括子目录）
输出：GMS原版Excel配置模板
```

**关键实现：**
- KMS无此目录
- 包含4个子目录：config, controls, data, template
- Excel配置模板，用于服务器端表格生成

**文件数：** 13个

**实现函数：** `process_excel_folder(source_dir, output_dir)`

---

## 七、跳过的目录（2个）

### 7.1 additional

**跳过原因：**
- KMS独有的旧版合集格式
- 包含5966个 `<additional>` 定义
- 与 `additionaleffect` 重复，additionaleffect 更完整

**关系：**
- `additional` = 旧版合集（KMS独有）
- `additionaleffect` = 新版独立文件（KMS和GMS都有）

---

### 7.2 questdata

**跳过原因：**
- KMS独有的合集版本
- 与 `quest` 目录内容重复
- GMS使用独立文件格式，已通过 `quest` 目录处理

**关系：**
- `questdata` = 合集版本（KMS独有）
- `quest` = 独立文件版本（已处理6809个文件）

---

## 关键技术点

### 1. 子节点顺序约束

某些GMS XML要求特定的节点顺序，例如：
```xml
<riding>
  <basic/>      <!-- 必须第一 -->
  <collision/>  <!-- 必须第二 -->
  <capsule/>    <!-- 必须第三 -->
  ...
</riding>
```

**解决方案：** 使用 `order_list` 定义顺序，手动排序输出。

---

### 2. global* 属性映射

KMS使用 `global*` 前缀属性，GMS去掉前缀：
```
globalRePackingLimitCount → rePackingLimitCount
globalGrade → grade
```

**实现：** 属性字典映射 + 显式删除 global* 属性。

---

### 3. ID路径化

将ID转换为目录路径：
```
ID = 10000001 → path = A/BB/CCCCCCCC.xml
公式：
  A = str(ID)[0]           # 首字符
  BB = str(ID)[:2]         # 前两字符
  CCCCCCCC = str(ID).zfill(8)  # 补零到8位
```

---

### 4. 模板填充策略

对于KMS独有ID，使用模板文件填充：
- `skill_template.xml` - 技能模板（28节点）
- `item_template.xml` - 物品模板（28节点）

策略：复制模板 → 用KMS数据填充对应节点。

---

## 文件统计

| 目录类型 | 目录数 | 文件数 |
|---------|--------|--------|
| 直接复制 | 14 | - |
| 增量合并 | 2 | 15,522 |
| 格式转换 | 2 | - |
| 拆分处理 | 3 | 51,537 |
| 特殊处理 | 4 | 15,917 |
| GMS独有 | 2 | 1,699 |
| **总计** | **27** | **~84,675** |

---

## 注意事项

1. **网络路径性能**：SynologyDrive路径使用robocopy代替shutil.copy2
2. **控制台编码**：Windows GBK控制台不支持Unicode符号，使用ASCII替代
3. **Python版本**：需要Python 3.12+（多行f-string支持）
4. **内存占用**：大文件（如quest.xml 69MB）需要流式处理
5. **备份策略**：转换前备份GMS原版，避免数据丢失

---

**文档版本**：v1.0  
**更新日期**：2026-05-20
