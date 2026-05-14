# MapleStory KMS → GMS 格式转换项目

> 合并 CMS（国服）与 KMS（韩服）的游戏数据，转换为 GMS 格式

---

## 项目结构

```
Maple2_KC_Convert_to_Gms/
├── 1CMSXml/              # CMS 国服原始版本
├── 2KMSXml/              # KMS 韩服更新版本
├── 3GMSXml/              # GMS 参考格式
├── 4C&GXml/               # 合并版本（CMS + KMS）
├── 5NewGMS/               # 输出目录（GMS 格式）
├── convert_cg_to_gms.py  # 主转换脚本
└── README.md              # 本文档
```

---

## 快速开始

### 前置要求

- Python 3.12+（Windows: `C:\Program Files\Python312\python.exe`）

### 使用步骤

1. **准备源数据**
   - 确保 `4C&GXml` 目录包含已合并的 CMS + KMS 数据
   - 确保 `3GMSXml` 目录包含 GMS 参考格式（用于 anikeytext.xml）

2. **运行转换脚本**
   ```bash
   "C:\Program Files\Python312\python.exe" convert_cg_to_gms.py
   ```

3. **按提示操作**
   ```
   请输入源目录路径: K:\SynologyDrive\RedMxdserver\Maple2_KC_Convert_to_Gms\4C&GXml
   
   请选择要处理的目录:
   1. achieve
   2. camera
   3. ui
   4. ugcmap
   5. anikeyinfo
   6. 全部处理
   ```

4. **查看输出**
   - 转换后的文件位于 `5NewGMS` 目录

---

## 目录转换状态

| 目录 | 状态 | 处理方式 | 说明 |
|------|------|----------|------|
| **achieve** | ✅ 已完成 | 格式转换 | 添加 locking/target 属性，调整属性顺序 |
| **camera** | ✅ 已完成 | 直接复制 | 三版内容完全一致 |
| **ui** | ✅ 已完成 | 直接复制 | 三版内容完全一致 |
| **ugcmap** | ✅ 已完成 | 直接复制 | 使用 KMS 最低价格规格 |
| **anikeyinfo** | ✅ 已完成 | 增量更新 | 合并为 anikeytext.xml（GMS 单文件格式） |
| **anikeytext.xml** | ✅ 已生成 | 从 anikeyinfo 合并 | 2306 个 kfm 条目 |
| **table** | ✅ 已完成 | 用户选择（cn/kr） | 转换时让用户选择 cn 或 kr，输出为 na/ |
| **string** | ✅ 已完成 | 直接复制 | 使用 2KMSXml 版本 |
| **trigger** | ✅ 已完成 | 直接复制 | 926个子目录，差异为非结构性（本地化/注释/内联） |
| additional | ⏸️ 暂跳过 | - | 3GMS 无此目录，处理方式未知，待后续分析 |
| additionaleffect | ⏸️ 暂不处理 | - | 尚未分析运作方式 |
| anikeytext.xml | ✅ 已生成 | 从 anikeyinfo 合并 | 2306 个 kfm 条目 |

---

## 转换规则详解

### 1. achieve（成就目录）

**格式转换规则**:
```xml
<!-- 原始格式 (4C&G) -->
<achieves id="..." feature="...">

<!-- GMS 格式 -->
<achieves id="..." account="" icon="" noticePercent="" locking="" categoryTag="" feature="" locale="">
```

**转换步骤**:
1. 添加 `locking=""` 属性
2. 为每个 `<condition>` 添加 `target=""` 属性
3. 为没有 reward 的 grade 添加空 reward
4. 调整属性顺序为 GMS 标准格式
5. 为 reward 添加 `rank="1"`（如果没有）

### 2. anikeyinfo（动画关键帧）

**GMS 格式说明**:
- KMS 使用拆分格式：`anikeyinfo\*.xml`（每个动画一个文件）
- GMS 使用单文件格式：`anikeytext.xml`

**转换逻辑（增量更新）**:
1. 检查 `5NewGMS\anikeytext.xml` 是否存在
2. 如不存在，提示用户先放入原始 GMS 文件
3. 如存在，读取 `4C&GXml\anikeyinfo\*.xml`
4. 对每个文件执行：
   - 如果 `<kfm name="filename">` 已存在 → 替换内容
   - 如果 `<kfm name="filename">` 不存在 → 追加到 `</ms2ani>` 之前

### 3. ugcmap（UGC 房屋配置）

**合并策略**: 使用 KMS 最低价格规格
- `contractPrice`: KMS 定价远低于 CMS
- `extensionPrice`: KMS 续约价远低于 CMS

### 4. table（表格数据）

**目录结构**:
- `cn/` - 国服（CMS）版本
- `kr/` - 韩服（KMS）版本  
- `default/` - 默认版本

**转换逻辑（用户选择）**:
1. 脚本提示用户选择使用 cn 或 kr
2. 用户选择后，将对应文件夹复制到输出目录并重命名为 `na/`
3. `default/` 直接复制
4. 可选：同时复制 cn 和 kr（cn 作为 na，kr 作为 kr）

---

## 已完成合并记录

### achieve（成就目录）

**统计**:
- 1CMSXml: 2101 个文件
- 2KMSXml: 2116 个文件
- 4C&GXml: 2116 个文件
- 新增: 15 个（KMS 新增成就）
- 差异: 17 个（KMS 移除部分奖励）

**新增文件**:
| 文件 | 说明 |
|------|------|
| 21300118.xml | Zakum BOSS 成就 |
| 22300151.xml | 冒险任务成就 |
| 23100449.xml | 技能熟练度成就 |
| 23300071/72.xml | 收集成就 |
| 23200044.xml | 消费金币成就（已恢复注释） |
| 92000158-164.xml | Event 猜拳活动成就 |
| 93000010.xml | 消费金币成就（已恢复注释） |

**恢复奖励**:
- 22200452/54/56.xml: 恢复 statPoint/skillPoint 奖励
- 23100112.xml: 恢复 title 奖励

---

### additional（技能配置）

**统计**:
- 1CMSXml: 74 个文件
- 2KMSXml: 75 个文件
- 4C&GXml: 75 个文件

**新增**: 1300.xml（领袖技能配置，55,478 bytes）

---

### additionaleffect（附加效果）

**统计**:
- 1CMSXml: 6070 个文件
- 2KMSXml: 6071 个文件
- 4C&GXml: 6071 个文件

**新增**: 50011032.xml

---

### anikeyinfo（动画关键帧）

**统计**:
- 1CMSXml: 2305 个文件
- 2KMSXml: 2306 个文件
- 4C&GXml: 2306 个文件

**新增**: 50620238_r_duckyball04.xml（UGC 小黄鸭坐骑）

**差异**: male.xml、female.xml（KMS 新增舞蹈/表情动作）

---

### ugcmap（UGC 房屋）

**统计**: 117 个文件

**差异**: 25 个文件价格不同，使用 KMS 最低规格

---

### trigger（触发器）

**统计**:
- 1CMSXml: 900 个子目录
- 2KMSXml: 926 个子目录
- 4C&GXml: 926 个子目录
- 3GMSXml: 882 个子目录

**2KMS 新增 26 个子目录**: 主要是 `61000023~35_me_item/` 和 `9090000~6/`

**4C&G vs 3GMS 差异分析（159个子目录有差异）**:

| 差异模式 | 数量 | 说明 |
|----------|------|------|
| korean_state_renamed | 57 | 韩文state名/空格微调，结构不变 |
| comment_vs_tag | 38 | CG注释掉了transition，GMS激活了它 |
| korean_text_removed | 23 | GMS移除了韩文注释 |
| minor_diff | 21 | 空格/空行差异 |
| structure_changed | 15 | GMS内联了dungeon_common的import（同义不同写法） |
| file_count_diff | 3 | 文件数量不同 |
| unknown | 5 | 待确认 |

**结论**: 所有差异为非结构性差异，直接复制即可

---

## 脚本使用说明

### convert_cg_to_gms.py

**主转换脚本**，支持以下目录处理：

```python
# 查看脚本帮助
python convert_cg_to_gms.py --help

# 交互模式（推荐）
python convert_cg_to_gms.py
```

**支持的处理类型**:
- `process_achieve_folder()` - 格式转换
- `process_direct_copy()` - 直接复制（camera、ui、ugcmap、trigger）
- `process_anikeyinfo_folder()` - 增量更新 anikeytext.xml
- `process_table_folder()` - 用户选择 cn/kr，输出为 na/

**默认路径**:
- 源目录: `K:\SynologyDrive\RedMxdserver\Maple2_KC_Convert_to_Gms\4C&GXml`
- 输出目录: `K:\SynologyDrive\RedMxdserver\Maple2_KC_Convert_to_Gms\5NewGMS`

---

## 注意事项

1. **anikeytext.xml 需要手动准备**
   - 第一次运行 anikeyinfo 转换前，需要在 `5NewGMS` 放入原始 GMS 的 `anikeytext.xml`
   - 脚本会提示用户操作

2. **additionaleffect 暂不处理**
   - 该目录运作方式尚未分析完成
   - 暂时直接复制，不做格式转换

3. **备份建议**
   - 运行转换前建议备份 `4C&GXml` 和 `5NewGMS` 目录
   - 脚本会自动创建 `.bak` 备份文件

---

## 更新日志

- **2026-05-14**: 完成 table 目录合并到 4C&GXml，集成到主脚本（用户选择 cn/kr）
- **2026-05-14**: 完成 string 目录合并到 4C&GXml，添加到主脚本（直接复制）
- **2026-05-14**: 完成 trigger 目录分析合并，添加到主脚本直接复制
- **2026-05-13**: 集成 anikeyinfo 增量更新功能到主脚本
- **2026-05-13**: 完成 ui、ugcmap 目录合并与转换
- **2026-05-11**: 完成 achieve、additional、additionaleffect 目录合并
- **2026-05-11**: 创建主转换脚本 convert_cg_to_gms.py

---

## 作者

MxdServer - MapleStory KMS→GMS 格式转换工具
