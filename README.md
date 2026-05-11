# 目录比对汇总

> 记录每次目录比对的结果，方便追踪变。

---

## 目录结构

| 目录名 | 说明 |
|--------|------|
| 1CMSXml | CMS国服原始版本 |
| 2KMSXml | KMS韩服更新版本 |
| 4C&GXml | 合并后的版本
> 仅 achieve 目录已完成合并 |

---

## 比对记录

### 1. achieve（成就目录）

**比对时间**: 2026-05-11 10:27

**统计**: 
- 1CMSXml: 2101 个文件
- 2KMSXml: 2116 个文件
- 新增: 15 个
- 大小不同: 17 个

**新增文件（15个）**:

| 文件 | 说明 |
|------|------|
| 21300118.xml | Zakum01 BOSS成就，statPoint 5点 |
| 22300151.xml | 冒险任务成就 |
| 23100449.xml | 技能熟练度成就 (code=90000834) |
| 23200044.xml | 消费金币成就（整体被注释） |
| 23300071.xml | 收集装备成就，statPoint 1点 |
| 23300072.xml | 收集道具成就 |
| 92000158~92000164.xml | Event猜拳活动成就，称号奖励 |
| 92000165.xml | 技能熟练度成就 |
| 93000010.xml | 消费金币成就（整体被注释） |

**奖励移除/注释（需恢复）**:

| 文件 | 原CMS奖励 | KMS移除内容 |
|------|----------|-------------|
| 22200452.xml | statPoint 1点 | 整条奖励删除 |
| 22200454.xml | skillPoint 1点 | 整条奖励删除 |
| 22200456.xml | skillPoint 1点 | 整条奖励删除 |
| 23100112.xml | title 10000170 | 被注释掉 |
| 23200044.xml | 全部内容 | 整体被注释 |
| 93000010.xml | 全部内容+奖励 | 整体被注释 |

---

### 2. 4C&GXml vs 3GMSXml（成就目录结构比对）

**比对时间**: 2026-05-11 11:01

**统计**:
- 4C&GXml: 2116 个文件
- 3GMSXml: 2207 个文件
- 共有文件: 2081 个
- 3GMSXml独有: 126 个
- 4C&GXml独有: 35 个

**结构差异**: 135 个文件

---

#### Grade数量差异（129个文件）

| 模式 | 数量 | 说明 |
|------|------|------|
| 3GM grade 更多 | 120+ | 大多数文件3GM有更多grade阶段 |
| 4CG grade 更多 | 少数 | 如23100112.xml多1个grade |

**典型差异示例**:
| 文件 | 4CG grade | 3GM grade | 差异 |
|------|-----------|-----------|------|
| 21210003.xml | 9 | 45 | -36 |
| 21220032.xml | 5 | 25 | -20 |
| 21300042~21300070.xml | 2 | 6 | -4 |
| 23100112.xml | 10 | 9 | +1 |
| 92000123.xml | 1 | 3 | -2 |

---

#### StatPoint差异（6个文件）

| 文件 | 哪边更多 | 说明 |
|------|----------|------|
| 21210001.xml | 4C&GXml | 4CG有statPoint奖励，3GM没有 |
| 23100112.xml | 4C&GXml | 4CG有statPoint且多1个grade |
| 22200246.xml | 3GM | 3GM有statPoint奖励，4CG没有 |
| 22200303.xml | 3GM | 3GM有statPoint奖励，4CG没有 |
| 22200453.xml | 3GM | 3GM有statPoint奖励，4CG没有 |
| 22300017.xml | 3GM | 3GM有statPoint奖励，4CG没有 |

---

#### 属性差异

| 属性 | 4C&GXml | 3GMSXml |
|------|---------|---------|
| locking | 无 | 有（全部2081个文件都有locking=""） |
| feature | 有 | 部分有 |
| condition target | 无空值 | 有空值target="" |
| reward rank | 无 | 有（3GM有空的reward带rank="1"） |
| 空reward | 无 | 4844个（type="" code="0" value="0"） |

**3GMSXml特有属性**:
```xml
<condition ... target="" />        <!-- 额外的空target属性 -->
<reward type="" code="0" value="0" rank="1" />  <!-- 空奖励带rank -->
<achieves ... locking="">          <!-- 额外的locking属性 -->
```

---

#### 结论

**3GMSXml比4C&GXml多的内容**:
- 126个独有文件
- 更细化的grade阶段（更多小目标）
- 空target、空reward属性
- locking属性

**4C&GXml比3GMSXml多的内容**:
- 35个独有文件（新增的KMS成就）
- 保留的statPoint奖励（部分）
- 完整的grade结构（无空值填充）

---

---

## 3. 脚本与转换

**时间**: 2026-05-11 11:20

### convert_cg_to_gms.py

**脚本位置**: `K:\SynologyDrive\RedMxdserver\togms\convert_cg_to_gms.py`

**功能**: 将4C&GXml的achieve文件转换为3GMSXml格式

**转换规则**:
1. achieves标签添加 `locking=""` 属性
2. condition标签添加 `target=""` 属性（如果没有）
3. 为每个grade添加空reward（如果没有reward）
4. 属性顺序调整为GMS格式: `id, account, icon, noticePercent, locking, categoryTag, feature, locale`
5. 为没有rank的reward添加 `rank="1"`

### 5GMSXml

**输出目录**: `K:\SynologyDrive\RedMxdserver\togms\5GMSXml\achieve`

**统计**:
- 输入: 2116 个文件（来自4C&GXml）
- 输出: 2116 个文件
- 成功率: 100%

**转换验证**:
| 项目 | 状态 |
|------|------|
| 属性顺序 | ✅ |
| noticePercent="1" | ✅ |
| locking="" | ✅ |
| target="" | ✅ |
| rank="1" | ✅ |
| 空reward添加 | ✅ |
| ms2包装 | ✅ |

**使用方法**:
```bash
python K:\SynologyDrive\RedMxdserver\togms\convert_cg_to_gms.py
```

---

<!-- 后续比对结果追加在此 -->