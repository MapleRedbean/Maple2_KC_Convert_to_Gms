# Conversion Logic Documentation

This document explains the conversion strategy and implementation details for each directory.

---

## Overview

| Category | Directory Count | Description |
|----------|-----------------|-------------|
| Direct Copy | 14 | KMS and GMS formats identical, copy directly |
| Incremental Merge | 2 | Use GMS as base, update with KMS data |
| Format Conversion | 2 | Requires XML structure or attribute adjustments |
| Split Processing | 3 | Split collection files into individual files |
| GMS-Only | 2 | Only exists in GMS, copy from GMS directly |
| Other | 4 | Special processing logic |

**Total: 27 directories**

---

## 1. Direct Copy (14 directories)

**Directory List:**
- achieve (Achievements)
- camera (Camera)
- ui (User Interface)
- ugcmap (UGC Maps)
- trigger (Triggers)
- string (Strings)
- object (Objects)
- pet (Pets)
- emotion (Emotes)
- musicscore (Music Scores)
- groundeffect (Ground Effects)
- masteryhomemade (Mastery Homemade)
- exportedugcmap (Exported UGC Maps)
- effect (Effects)

**Conversion Logic:**
```
Input: KMS XML file
Process: Direct file copy, no modifications
Output: Identical copy of input
```

**Implementation Function:** `process_direct_copy(source_dir, output_dir, folder_name)`

**Reason:** KMS and GMS XML structures are completely identical, including:
- Root node `<ms2>`
- Child node structure
- Attribute names
- Value formats

---

## 2. Incremental Merge (2 directories)

### 2.1 skilldata (Skill Data)

**Conversion Logic:**
```
Input: KMS skill file (incremental format) + GMS skill file (complete format)
Process:
  1. Load GMS version as base template
  2. Parse KMS incremental attributes
  3. Update GMS nodes by node path
  4. Preserve existing GMS values, only add KMS new attributes
Output: Merged complete skill file
```

**Key Implementation:**
- Template file: `skill_template.xml` (copied from typical GMS skill file)
- KMS format: Contains only changed attribute nodes
- GMS format: Contains complete 28 child nodes (BasicProperty, MotionProperty, etc.)
- Special handling:
  - `global*` attribute mapping (remove global prefix)
  - conditionSkill nested beginCondition structure
  - Child node order must match GMS requirements

**File Count:** 9,451

**Implementation Function:** `process_skilldata_folder(source_dir, output_dir)`

---

### 2.2 additionaleffect (Additional Effects)

**Conversion Logic:**
```
Input: KMS additional effect file + GMS additional effect file
Process:
  1. Load GMS version as base
  2. Update corresponding nodes with KMS attributes
  3. Direct attribute merge (no complex nesting)
Output: Merged additional effect file
```

**Key Implementation:**
- GMS base: Complete 15+ node tree
- KMS format: Simplified incremental update format
- Merge strategy: Attribute-level merge, preserve GMS structure

**File Count:** 6,071

**Implementation Function:** `process_additionaleffect(source_dir, output_dir)`

---

## 3. Format Conversion (2 directories)

### 3.1 table (Tables)

**Conversion Logic:**
```
Input: KMS table files (cn/kr versions)
Process:
  1. Let user choose cn (Chinese) or kr (Korean)
  2. Copy chosen version to output directory
  3. Rename to na/ directory (North America server)
Output: Table files in na/ directory
```

**Key Implementation:**
- Interactive selection: User inputs language version choice
- Directory renaming: cn/kr → na
- Content unchanged

**Implementation Function:** `process_table_folder(source_dir, output_dir)`

---

### 3.2 anikeyinfo (Animation Keyframe Info)

**Conversion Logic:**
```
Input: KMS anikeyinfo directory (multiple XML files) + GMS anikeytext.xml (single file)
Process:
  1. Parse GMS anikeytext.xml as base
  2. Traverse each KMS XML file
  3. Find or create node by kfm name attribute
  4. Update or append animation keyframe info
Output: Updated anikeytext.xml
```

**Key Implementation:**
- KMS format: One XML file per KFM
- GMS format: All KFMs aggregated in one XML file
- Incremental update: Replace existing kfm, append new kfm

**Prerequisite:** Output directory must have GMS original `anikeytext.xml`

**Implementation Function:** `process_anikeyinfo_folder(source_dir, output_dir)`

---

## 4. Split Processing (3 directories)

### 4.1 script (Scripts)

**Conversion Logic:**
```
Input: KMS script directory (npc.xml, quest.xml collection files)
Process:
  NPC Split:
    1. Parse npc.xml collection file
    2. Split each npc node into individual file
    3. Group by NPC ID (1000-1999, 2000-2999, etc.)
    4. Each group generates one XML file
  
  Quest Split:
    1. Parse quest.xml collection file
    2. Split each quest node into individual file
    3. Group by Quest ID range
    4. Each group generates one XML file
Output: Individual small XML files
```

**Key Implementation:**
- Input file size: npc.xml ~58MB, quest.xml ~69MB
- Split strategy: Group by ID range (reduce file count)
- Output structure:
  ```
  npc/1000-1999.xml
  npc/2000-2999.xml
  ...
  quest/0-999.xml
  quest/1000-1999.xml
  ...
  ```

**File Count:** NPC 3,268 files + Quest 14 files

**Implementation Function:** `process_script_folder(cg_dir, out_dir)`

---

### 4.2 npcdata (NPC Data)

**Conversion Logic:**
```
Input: KMS npcdata directory (collection XML files) + GMS npcdata directory (individual files)
Process:
  1. Parse KMS collection files (each contains multiple NPC definitions)
  2. Split each NPC node into individual file
  3. File path: npc/A/BB/CCCCCCCC.xml (ID path-based)
  4. Merge data with existing GMS files
Output: One XML file per NPC
```

**Key Implementation:**
- KMS format: Collection files (e.g., npc_0001-1000.xml)
- GMS format: Individual files (e.g., npc/0/00/00000001.xml)
- ID path conversion: Convert NPC ID to directory path (e.g., ID=10000001 → npc/1/00/10000001.xml)
- Incremental merge: KMS data updates GMS template

**File Count:** 10,816

**Implementation Function:** `process_npcdata_folder(source_dir, output_dir)`

---

### 4.3 itemdata (Item Data)

**Conversion Logic:**
```
Input: KMS itemdata directory (collection XML files) + GMS itemdata directory (individual files)
Process:
  1. Parse KMS collection files
  2. Split each item node into individual file
  3. File path: item/A/BB/CCCCCCCC.xml
  4. Use item_template.xml as base template
  5. Merge KMS data into GMS template
Output: One XML file per item
```

**Key Implementation:**
- KMS format: Collection files (104 files)
- GMS format: Individual files (37,065 files)
- Template strategy: `item_template.xml` contains complete 28 child nodes
- ID path conversion: Similar to npcdata

**File Count:** 37,617

**Implementation Function:** `process_itemdata_folder(source_dir, output_dir)`

---

## 5. Special Processing (4 directories)

### 5.1 riding (Mounts)

**Conversion Logic:**
```
Input: KMS riding directory + GMS riding directory
Process:
  1. Parse KMS collection files
  2. Split each riding node into individual file
  3. Extract passenger info (passenger seats)
  4. Save passenger as separate file
  5. Output child nodes in GMS order
Output: Individual riding files + individual passenger files
```

**Key Implementation:**
- Riding split: One file per mount
- Passenger extraction: Extract passenger seat configuration from mount definition
- Node order constraint:
  ```
  basic → collision → capsule → shadow → faceCamera → stat
  ```
  (Must be in this order, not alphabetical)

**File Count:** 615 riding + 39 passenger

**Implementation Function:** `process_riding_folder(source_dir, output_dir)`

---

### 5.2 quest (Quests)

**Conversion Logic:**
```
Input: KMS quest directory (individual files) + GMS quest directory (individual files)
Process:
  1. Copy KMS files to output directory
  2. Add GMS-required nodes to each quest file:
     - <notify> node
     - <notifyIcon> node
     - Other GMS-specific configurations
Output: Quest files with GMS nodes
```

**Key Implementation:**
- KMS format: Already has individual files (not collections)
- GMS difference: Requires extra notification configuration nodes
- Node insertion position: Before `</ms2>` closing tag

**File Count:** 6,809

**Implementation Function:** `process_quest_folder(source_dir, output_dir)`

---

### 5.3 itempreset (Item Presets)

**Conversion Logic:**
```
Input: KMS itemmodel directory (collection XML files) + GMS itempreset directory (individual files)
Process:
  1. Parse KMS itemmodel collection files
  2. Convert each item node to itempreset format
  3. Output by ID path: itempreset/A/BB/CCCCCCCC.xml
  4. Copy GMS template files (empty.xml, empty_asset.xml, petequipment.xml)
Output: Individual itempreset files
```

**Key Implementation:**
- Directory name mapping: `itemmodel` → `itempreset`
- Format conversion: `itemmodel` collection → `itempreset` individual files
- asset attribute mapping: Adjust resource reference paths

**File Count:** 6,674

**Implementation Function:** `process_itempreset_folder(source_dir, output_dir)`

---

### 5.4 mapxblock (Map Blocks)

**Conversion Logic:**
```
Input: KMS mapxblock directory + GMS mapxblock directory
Process:
  1. Use robocopy to copy KMS files
  2. Preserve GMS's 4 login files (login interface)
Output: Merged mapxblock directory
```

**Key Implementation:**
- Tool choice: robocopy (optimized for SynologyDrive network path)
- Commands:
  ```bash
  robocopy kms_mapxblock out_mapxblock /E /XD login
  robocopy gms_mapxblock out_mapxblock /E /XF login/*
  ```
- GMS preservation: 4 files under login directory

**File Count:** 1,780

**Implementation Function:** `process_mapxblock_folder(source_dir, output_dir)`

---

## 6. GMS-Only Directories (2 directories)

### 6.1 map (Maps)

**Conversion Logic:**
```
Input: GMS map directory
Process: Direct copy of GMS original to output directory
Output: GMS original map files
```

**Key Implementation:**
- KMS does not have this directory
- GMS-specific map configurations
- Direct copy from `3GMSXml/map`

**File Count:** 1,686

**Implementation Function:** `process_map_folder(source_dir, output_dir)`

---

### 6.2 excel (Excel Configurations)

**Conversion Logic:**
```
Input: GMS excel directory
Process: Direct copy of GMS original to output directory (including subdirectories)
Output: GMS original Excel configuration templates
```

**Key Implementation:**
- KMS does not have this directory
- Contains 4 subdirectories: config, controls, data, template
- Excel configuration templates for server-side table generation

**File Count:** 13

**Implementation Function:** `process_excel_folder(source_dir, output_dir)`

---

## 7. Skipped Directories (2 directories)

### 7.1 additional

**Skip Reason:**
- KMS-only legacy collection format
- Contains 5,966 `<additional>` definitions
- Duplicate of `additionaleffect`, which is more complete

**Relationship:**
- `additional` = Legacy collection (KMS-only)
- `additionaleffect` = Modern individual files (both KMS and GMS)

---

### 7.2 questdata

**Skip Reason:**
- KMS-only collection version
- Duplicate content with `quest` directory
- GMS uses individual file format, already processed via `quest` directory

**Relationship:**
- `questdata` = Collection version (KMS-only)
- `quest` = Individual file version (already processed 6,809 files)

---

## Key Technical Points

### 1. Child Node Order Constraint

Some GMS XMLs require specific node order, for example:
```xml
<riding>
  <basic/>      <!-- Must be first -->
  <collision/>  <!-- Must be second -->
  <capsule/>    <!-- Must be third -->
  ...
</riding>
```

**Solution:** Use `order_list` to define order, manually sort during output.

---

### 2. global* Attribute Mapping

KMS uses `global*` prefix attributes, GMS removes prefix:
```
globalRePackingLimitCount → rePackingLimitCount
globalGrade → grade
```

**Implementation:** Attribute dictionary mapping + explicit global* attribute deletion.

---

### 3. ID Path Conversion

Convert ID to directory path:
```
ID = 10000001 → path = A/BB/CCCCCCCC.xml
Formula:
  A = str(ID)[0]              # First character
  BB = str(ID)[:2]            # First two characters
  CCCCCCCC = str(ID).zfill(8) # Zero-pad to 8 digits
```

---

### 4. Template Filling Strategy

For KMS-only IDs, use template files:
- `skill_template.xml` - Skill template (28 nodes)
- `item_template.xml` - Item template (28 nodes)

Strategy: Copy template → Fill corresponding nodes with KMS data.

---

## File Statistics

| Directory Type | Count | File Count |
|---------------|-------|------------|
| Direct Copy | 14 | - |
| Incremental Merge | 2 | 15,522 |
| Format Conversion | 2 | - |
| Split Processing | 3 | 51,537 |
| Special Processing | 4 | 15,917 |
| GMS-Only | 2 | 1,699 |
| **Total** | **27** | **~84,675** |

---

## Important Notes

1. **Network Path Performance**: Use robocopy instead of shutil.copy2 for SynologyDrive paths
2. **Console Encoding**: Windows GBK console doesn't support Unicode symbols, use ASCII alternatives
3. **Python Version**: Requires Python 3.12+ (multiline f-string support)
4. **Memory Usage**: Large files (e.g., quest.xml 69MB) require streaming processing
5. **Backup Strategy**: Backup GMS original before conversion to avoid data loss

---

**Document Version:** v1.0  
**Update Date:** 2026-05-20
