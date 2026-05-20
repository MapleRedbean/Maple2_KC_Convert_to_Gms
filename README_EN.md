# MapleStory 2 KMS → GMS XML Converter

Convert Korean (KMS) XML data to Global (GMS) format for private server development.

## Project Status

**Completed 26/26 directories (100%)**

### By Strategy

| Strategy | Directories | File Count | Status |
|----------|-------------|------------|--------|
| **Direct Copy** | achieve, camera, ui, ugcmap, trigger, string, object, pet, emotion, musicscore, groundeffect, masteryhomemade, exportedugcmap, effect | - | ✅ |
| **Incremental Merge** | skilldata, additionaleffect | 9451 + 6071 | ✅ |
| **Format Conversion** | table, anikeyinfo | - | ✅ |
| **Large File Split** | script | NPC 3268 + Quest 14 | ✅ |
| **Split + Extract** | riding | 615 + 39 passenger | ✅ |
| **Add Nodes** | quest | 6809 | ✅ |
| **Collection Split** | npcdata | 10816 | ✅ |
| **Collection Split** | itemdata | 37617 | ✅ |
| **Directory Mapping** | itempreset (itemmodel→itempreset) | 6674 | ✅ |
| **robocopy** | mapxblock | 1780 | ✅ |
| **GMS Only** | map | 1686 | ✅ |

### KMS Directory Notes

KMS has **28 directories** in total:
- **26 processed**: Listed in the table above
- **2 skipped**:
  - `additional` - Legacy collection format of additionaleffect (5966 definitions), additionaleffect contains more complete data
  - `questdata` - Collection version of quest, quest directory already processed (6809 individual files)

## Directory Structure

```
Maple2_KC_Convert_to_Gms/
├── 2KMSXml/              # KMS source data
├── 3GMSXml/              # GMS original (conversion base)
├── 5newGMS/              # Conversion output
├── convert_cg_to_gms.py  # Main conversion script
├── skill_template.xml    # skilldata conversion template
├── item_template.xml     # itemdata conversion template
├── README.md             # Chinese documentation
└── README_EN.md          # English documentation
```

## Usage

```bash
python convert_cg_to_gms.py
```

Follow the prompts to select directories. The script will:
1. Read KMS source data (2KMSXml/)
2. Use GMS original (3GMSXml/) as base template
3. Incrementally update with KMS data / fill missing attributes
4. Output to 5newGMS/

## Conversion Strategies

### 1. Direct Copy
For directories where KMS/GMS formats are identical (achieve, camera, ui, etc.)

### 2. Incremental Update
Use GMS original as base, fill missing attributes with KMS data. Existing GMS values are preserved. (skilldata, itemdata, additionaleffect)

### 3. Format Conversion
KMS and GMS have different XML structures, requires node reorganization (anikeyinfo, quest)

### 4. Split/Merge
KMS uses collection files, GMS uses individual files, requires splitting (npcdata, itemdata, script)

### 5. Attribute Mapping
KMS and GMS use different attribute names, requires mapping:
- `param1` → `parameter` (function)
- `constantID` → `optionID` (option)
- `randomID` → `random` (option)
- `optionLevel` → `optionLevelFactor` (option)
- `globalRePackingLimitCount` → `rePackingLimitCount` (property)
- `globalRePackingItemConsumeCount` → `rePackingItemConsumeCount` (property)

## Important Notes

1. **Network Drive Performance**: File operations on SynologyDrive network path are slow. Use robocopy for large batch copies.
2. **Python Version**: Requires Python 3.12+ for multiline f-string support.
3. **Windows Console**: GBK encoding doesn't support Unicode symbols, use ASCII alternatives.
4. **Syntax Check**: Run `python -m py_compile convert_cg_to_gms.py` after each modification.
5. **Template Files**: skilldata and itemdata require corresponding template files (skill_template.xml, item_template.xml).

## Known Issues

### npcdata 6 Generic Bugs
Conversion may produce 6 generic bugs, fixed with post-processing script. Note: Rerunning `_create_gms_environment()` will reproduce these bugs.

### itemdata KMS-Only Items
552 KMS-only items use item_template.xml as template. Data may be incomplete and requires in-game verification.

## Technical Details

### itemdata Conversion
- KMS: Collection files (e.g., itemdata/112.xml contains 11200001, 11200002...)
- GMS: Individual files, path format `item/A/BB/ID.xml` (A=1st digit, BB=2nd-3rd digits)
- Processing: 37617 items total, 32589 intersection, 552 KMS-only

### option Node Position
- KMS: `<option>` inside `<environment>`
- GMS: `<option>` is direct child of `<ms2>`
- Conversion requires node relocation

### additional vs additionaleffect
- KMS has both `additional/` (75 collection files, 5966 definitions) and `additionaleffect/` (6071 individual files)
- `additional` uses legacy format: `<additional>` → `<level>` → `<Basic>`, `<Motion>`, `<Recovery>`
- `additionaleffect` uses incremental format: `<BasicProperty>`, `<MotionProperty>` (only changed attributes)
- `additional` is subset of `additionaleffect`, skipped in conversion

### questdata vs quest
- `questdata` is collection format (single 69K-line file)
- `quest` is individual file format (6809 files)
- GMS uses `quest` directory, so `questdata` is skipped

## Verification Results (2026-05-20)

All 26 completed directories verified:

| Type | Count | Directories | Status |
|------|-------|-------------|--------|
| Direct Copy | 13 | achieve, camera, ui, ugcmap, trigger, string, object, pet, emotion, musicscore, groundeffect, masteryhomemade, exportedugcmap, effect | ✅ |
| Incremental Merge | 2 | skilldata, additionaleffect | ✅ |
| Format Conversion | 2 | table, anikeyinfo | ✅ |
| Split Processing | 5 | script, riding, npcdata, quest, itemdata | ✅ |
| Special Processing | 4 | mapxblock, map, itempreset, additionaleffect | ✅ |

### Key Directory File Counts
- npc: 10816 files
- skill: 9451 files
- itempreset: 6674 files (from itemmodel)
- quest: 6809 files
- additionaleffect: 6071 files
- emotion: 4555 files
- mapxblock: 1780 files
- map: 1686 files

### Output Directory Naming Mapping
| KMS Directory | Output Directory | Notes |
|---------------|------------------|-------|
| npcdata | npc | Directory name simplified |
| itemdata | item | Directory name simplified |
| skilldata | skill | Directory name simplified |
| itemmodel | itempreset | Directory renamed |
| anikeyinfo | anikeytext.xml | Single file output |

## Development Log

See `memory/2026-05-19.md` and `memory/2026-05-20.md` for detailed development records.

## License

For private server development and learning only. Commercial use prohibited.
