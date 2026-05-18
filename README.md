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
├── 5newGMS/               # 输出目录（GMS 格式）
├── convert_cg_to_gms.py  # 主转换脚本
├── skill_template.xml    # GMS 技能模板
└── README.md              # 本文档
```

---

## 目录转换状态

| 目录 | 状态 | 处理方式 | 说明 |
|------|------|----------|------|
| achieve | ✅ 完成 | 格式转换 | 添加 locking/target 属性 |
| camera | ✅ 完成 | 直接复制 | 三版内容完全一致 |
| ui | ✅ 完成 | 直接复制 | 三版内容完全一致 |
| ugcmap | ✅ 完成 | 直接复制 | 使用 KMS 最低价格规格 |
| anikeyinfo | ✅ 完成 | 增量更新 | 2306个条目 → anikeytext.xml |
| trigger | ✅ 完成 | 直接复制 | 格式化差异不影响解析 |
| table | ✅ 完成 | 结构合并 | cn/kr 保留，转换映射为 na/ |
| string | ✅ 完成 | 直接复制 | 1093个文件 |
| skilldata | ✅ 完成 | KMS→GMS 结构转换 | 9451技能，9个解析错误 |
| script | ✅ 完成 | NPC/Quest 大文件→分类文件 | NPC 3268个，Quest 4388个/14文件 |
| riding | ✅ 完成 | 骑宠主文件+passenger拆分 | 主文件+N/29个passenger独立文件 |
| additional | ⏸️ 跳过 | - | GMS 无此目录 |
| quest | ✅ 完成 | 补GMS独有节点和属性 | quest/ 目录，14个分类文件 |
| pet | ✅ 完成 | 直接复制 | KMS=GMS，105个文件 |
| object | ✅ 完成 | 直接复制 | KMS多6个新增+nurturing节点 |
| npcdata | ✅ 完成 | 合集拆分+格式转换 | KMS合集→GMS独立文件，10816个NPC |
| additionaleffect | ⏸️ 待分析 | - | 6034共同文件全部大小不同 |

---

## skilldata 转换详情

### 技能数量统计

| 统计项 | 数量 |
|--------|------|
| KMS 总技能 | 8092 |
| GMS 总文件 | 9915 |
| 共同技能 | 7961 |
| KMS 独有 | 131（来自 44/130/12/62 文件夹） |
| GMS 独有 | 1954（KMS 没有对应数据） |
| 转换输出 | 8794 文件 |
| 解析错误 | 9 个文件 |

### KMS vs GMS 结构映射

| KMS | GMS | 处理方式 |
|-----|-----|----------|
| `<skill id="X">` | `<ms2 feature="">` | 根节点替换 |
| `<basic mainType="1">` | `<mainType type="1"/>` | 属性→子节点 |
| `<level cooldown="600">` | `<beginCondition cooldownTime="0.6">` | 属性迁移+ms→s |
| `<motion>` 属性 | `<motionProperty>` | 属性→子节点 |
| `<range>` | `<rangeProperty>` | 标签重命名+rangeAdd格式化 |
| `<sensor>` | `<sensorProperty>` | 标签重命名 |
| `<pause>` | `<pauseProperty>` | 标签重命名 |
| `<arrow>` | `<arrowProperty>` | 标签重命名 |
| `<damage>` | `<damageProperty>` | 标签重命名 |
| `<actionAdditional additionalID>` | `<conditionSkill skillID>` | 标签+属性重命名 |
| `<detectProperty>` | `<detectProperty>` | 同标签，复制KMS真实数据 |
| `<chain>` | 无 | KMS独有，跳过 |
| `<actionSkill>` | 无 | KMS独有，跳过 |

### 坐标/数值格式化规则

整型逗号分隔 → 浮点6位小数逗号分隔，适用于：
- `rangeAdd`: `"0,25,0"` → `"0.000000,25.000000,0.000000"`
- `collision`: `"50,25,25"` → `"50.000000,25.000000,25.000000"`
- `collisionAdd`: 同上
- `rangeOffset`: `"0,0,3000"` → `"0.000000,0.000000,3000.000000"`

### cooldownTime 格式

- 整秒不带小数：`1000ms` → `"1"`，`2000ms` → `"2"`
- 非整秒保留小数：`600ms` → `"0.6"`

### 技能ID路径映射

```
id < 100000000: 补零到8位 → 前2位作文件夹 → 8位.xml
  例: id=1 → "00/00000001.xml"

id >= 100000000: 9位 → 前3位作文件夹 → 9位.xml
  例: id=100000007 → "100/100000007.xml"
```

---

## 已修复的 Bug

| # | Bug | 症状 | 修复日期 |
|---|-----|------|----------|
| 1 | `arrowProperty.collision/collisionAdd` 格式 | `"50,25,25"` 未转浮点 | 2026-05-15 |
| 2 | `detectProperty.rangeOffset` 格式 | `"50,50,50"` 未转浮点 | 2026-05-15 |
| 3 | `rangeProperty.rangeOffset` 格式 | `"0,0,3000"` 未转浮点 | 2026-05-15 |
| 4 | `cooldownTime` 浮点格式 | `"1.0"` 应为 `"1"` | 2026-05-15 |
| 5 | `_LEVEL_ONLY_TAGS` 未定义 | NameError | 2026-05-15 |
| 6 | `<motion>` 属性未迁移 | motionProperty 缺失 | 2026-05-15 |
| 7 | 模板缺 `allowMapleSurvival` | 技能1对比差异 | 2026-05-15 |
| 8 | 模板 attack 重复 | 转换前未清空 | 2026-05-15 |
| 9 | `talkAni` 默认值错误 | `"0"` 应为 `"1"` | 2026-05-18 |
| 10 | `<model>` 多了不属于它的属性 | `shadowScale/rotationSpeed/walkSpeed/runSpeed` 在 `<model>` 中 | 2026-05-18 |
| 11 | `<speed>` 使用了默认值 | `rotation="190" walk="120" run="0"` (默认值) | 2026-05-18 |
| 12 | `<shadow>` scale 值错误 | `scale="250"` (默认值) 应为 KMS `shadowScale` 值 | 2026-05-18 |
| 13 | 缺失 `<crystals />` 节点 | `</environment>` 前无 `<crystals />` | 2026-05-18 |
| 14 | `<effectdummy>` 位置错误 | 在 `</environment>` 内部，应在外部 | 2026-05-18 |

---

## 已知未解决问题

### 🔴 9个解析错误文件

转换时 XML 解析报错，未处理：
```
00/01000003.xml, 01/01000003.xml, 11/11000026.xml,
43/43000011.xml, 45/45000010.xml, 59/59999999.xml,
61/61000240.xml, 99/99900171.xml, 100/100000007.xml
```
**原因未知**，需逐个排查是否为 KMS 源文件格式异常。

### 🟡 GMS 独有属性缺失（无法从 KMS 生成）

以下属性在 GMS 原版中存在但 KMS 没有对应数据，当前使用模板默认值或留空：

| 属性 | 位置 | 缺失数 | 说明 |
|------|------|--------|------|
| `sp` | stat | ~1034 | 技能消耗SP |
| `targetHasBuffID/Owner` | detect/sensor | ~800 | 目标buff检测 |
| `targetStatCompare` | detect/sensor | ~791 | 目标属性比较 |
| `skillIDs/skillLevels` | upgrade | ~732 | 升级关联技能 |
| `id` | item | ~727 | 关联物品ID |
| `eventCondition/hasBuffID` | target | ~400+ | 事件条件 |
| `isShadowWorld` | beginCondition | ~340 | 影子世界标记 |
| `compulsionHit` | attack | ~72 | 强制命中 |
| `useItem` | consume | ~91 | 消耗物品 |

**建议**：从 GMS 原版文件增量合并（类似 anikeyinfo 做法），以 GMS 原版为基础，用 KMS 数据覆盖。

### 🟡 模板零值属性（GMS 不写，转换输出了 0）

GMS 原版不写值为 0 的属性，但模板会输出默认值 0：
- `castTarget=0`、`includeCaster=0`、`rangeZRotateDegree=0`（共 ~15866 处）
- `allowMapleSurvival`（~14771 处）

**影响**：功能无影响，但文件比 GMS 原版多出冗余属性。可后处理清理。

### 🟡 1393 个 GMS 独有技能文件

GMS 有 1954 个 KMS 没有的技能，其中 1393 个在共同子目录中，272 个在 KMS 独有子目录（130/44/62）。
这些技能在 KMS 中没有源数据，无法通过转换生成。

### 🟡 additionaleffect 目录

4C&G 有 6071 个文件，GMS 有 6090 个，6034 个共同文件**全部大小不同**。
差异性质未确认（可能是格式差异也可能是数值差异），需抽样对比。

### riding 转换详情

**结构差异**:

| 目录 | KMS | GMS |
|------|-----|-----|
| `riding/` 主目录 | N 个骑宠文件，无 00000000.xml | 同上 + **00000000.xml**（默认模板） |
| `effectdummy/` | 20个 9991xxxx.xml | 同上 |
| `passenger/` | **不存在**（嵌套在主文件 `<passengers>`） | 29个 5060xxxx/5062xxxx.xml |

**主文件转换**:
- 读取 KMS `riding/50600208.xml`
- 移除 `<passengers>` 节点（已移到 passenger/ 独立文件）
- 复制到 `riding/50600208.xml`
- 保留所有其他节点（basic/collision/shadow/faceCamera）
- GMS 额外节点（capsule/stat）来自 GMS 00000000.xml 模板，KMS 没有则不生成

**passenger/ 目录转换**:
- 从每个 KMS 主文件的 `<passengers>/<passenger>` 提取乘客数据
- 重命名 `<passenger>` → `<ridepassenger>`
- 将 `id` 从父级 `<basic>` 提升到 `<ridepassenger>` 上
- 写入 `riding/passenger/{id}.xml`
- 29个文件，1:1对应，无遗漏

**00000000.xml 模板**: GMS 专用默认模板，不来自 KMS，直接从 3GMSXml 复制。

### script 转换详情

**NPC 转换**：
- 源：KMS `npcscript_final.xml`（2.3MB，3268个NPC）
- 输出：GMS `npc/*.xml`（3268个独立文件）
- 处理：`<npc id="X">` → `<ms2>`，`<select/script/monologue>` 添加 `feature="" locale=""`，`<distractor>` 添加 `gotoFail=""`

**Quest 转换**：
- 源：KMS `questscript_final.xml`（4.3MB，4388个任务）
- 输出：GMS `quest/*.xml`（14个分类文件）
- 分类依据：GMS ID精确映射 + KMS-only ID按区间Fallback

| 输出文件 | Quest数 | 说明 |
|----------|---------|------|
| questscript_epic.xml | 1417 | 主线/剧情 |
| questscript_eventkr.xml | 561 | 韩服活动 |
| questscript_eventcn.xml | 196 | 国服活动 |
| questscript_eventjp.xml | 69 | 日服活动 |
| questscript_eventna.xml | 85 | 国际服活动 |
| questscript_eventcommon.xml | 38 | 通用活动 |
| questscript_world.xml | 873 | 世界/其他（含9701xxxx KMS独有100个）|
| questscript_famemission.xml | 607 | 声望任务 |
| questscript_famecontents.xml | 168 | 声望内容 |
| questscript_guide.xml | 164 | 引导 |
| questscript_famefield.xml | 106 | 声望地图 |
| questscript_guild.xml | 60 | 公会 |
| questscript_tutorial.xml | 33 | 教程 |
| questscript_item.xml | 11 | 物品相关 |

**KMS独有Quest**：178个任务在GMS中不存在，全部写入world.xml。其中100个在9701xxxx区间（韩服独有内容）。

---
---

## npcdata 转换详情

### NPC 数量统计

| 统计项 | 数量 |
|--------|------|
| KMS 总文件 | 69 |
| KMS 总 NPC | 10816 |
| 输出文件 | 10816 |
| 生成错误 | 0 |

### KMS vs GMS 结构映射

| KMS | GMS | 处理方式 |
|-----|-----|----------|
| `<ms2><npc id="X">` | `<ms2>` | 移除 `<npc>` 包装 |
| `<environment>` 属性 | `<basic>` 子节点 | 属性迁移到 `<basic>` |
| `<environment>` 子节点 | `<environment>` 子节点 | 保留并补充GMS独有节点 |
| `<effectdummy>` | `<effectdummy>` | 保留 |

### GMS 独有子节点（需补充默认值）

`<basic>`, `<speed>`, `<skill>`, `<additionalEffect>`, `<interact>`, `<combat>`, `<assist>`, `<aiInfo>`, `<collision>`, `<corpse>`, `<validBattleCylinder>`, `<dead>`, `<push>`, `<exp>`, `<shadow>`, `<dropiteminfo>`, `<lookattarget>`, `<crystals>`

### NPC ID 路径映射

```
id=11000001 → npc/11/00/11000001.xml
id=2040998 → npc/02/04/02040998.xml
```


## 使用说明

### 运行转换

```bash
python convert_cg_to_gms.py
```

脚本会列出 4C&GXml 下的子目录，输入序号选择要转换的目录。
skilldata 和 riding 数据在 2KMSXml 下（4C&GXml 不含这两个目录），脚本会自动从 2KMSXml 读取。

### 技能转换流程

1. 读取 `skill_template.xml` 作为 GMS 格式模板
2. 解析 KMS `skilldata/*.xml` 中的每个 `<skill>` 节点
3. 转换为 GMS 格式后按 ID 输出到 `5newGMS/skill/{00-99}/` 子目录
4. 解析错误的技能会跳过并记录

---

## 更新日志

- **2026-05-18**: 完成 npcdata 目录转换（合集→独立文件+格式转换，10816个NPC）
- **2026-05-15**: 完成 riding 目录转换（骑宠主文件+passenger/29个独立文件）；完成 script 目录转换（NPC 3268个 + Quest 4388个/14文件），修复 skilldata 4个格式Bug
- **2026-05-14**: 完成 skilldata 核心转换逻辑，完成 table/string 集成
- **2026-05-13**: 集成 anikeyinfo 增量更新，分析 skilldata 结构差异
- **2026-05-11**: 创建项目基础结构，完成 achieve/camera/ui/ugcmap/trigger

---

## 作者

MxdServer - MapleStory KMS→GMS 格式转换工具