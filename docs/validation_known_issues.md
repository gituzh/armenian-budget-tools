# Source Data Issues & Anomalies

This document tracks structural anomalies and data quality issues identified in the official source Excel files.

## 1. Split State Bodies (2019-2024)

A significant issue affects the 2019 spending reports (and potentially others) where a single State Body appears in multiple disjoint blocks within the same Excel sheet. Each block has its own "State Body Total" row, and the totals differ.

**Root Cause:**
This structure reflects government reorganizations (mergers). The source file groups budget lines by their *former* distinct entities but labels them all with the *new* unified Ministry name.

**Confirmed Cases (2019 Q1-Q4):**

* **Ministry of Economy (ՀՀ էկոնոմիկայի նախարարություն):**
  * Appears in **2** separate blocks.
  * Likely corresponds to the merger of the Ministry of Economic Development and Investments and the Ministry of Agriculture.
* **Ministry of Territorial Administration and Infrastructure (ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն):**
  * Appears in **2** separate blocks.
  * Likely corresponds to the merger of the Ministry of Territorial Administration and Development and the Ministry of Energy Infrastructures and Natural Resources.
* **Ministry of Education, Science, Culture and Sports (ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն):**
  * Appears in **3** separate blocks.
  * Likely corresponds to the merger of the Ministry of Education and Science, Ministry of Culture, and Ministry of Sport and Youth Affairs.

**Verified source rows for current 2019 failures:**

`2019_SPENDING_Q12` source workbook:
`data/extracted/spending_reports/2019/Q12/46e5e267/4. 2019_kisamyak_pat.crag.mij..xls`.
Values are annual plan, revised annual plan, period plan, revised period plan,
and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ էկոնոմիկայի նախարարություն | 2073, 2670 | `10,403,510.20`, `10,639,859.37`, `5,445,314.30`, `5,681,663.47`, `2,042,579.47`; `16,085,337.30`, `16,175,000.56`, `7,649,008.50`, `7,762,187.76`, `3,174,266.15` |

`2019_SPENDING_Q123` source workbook:
`data/extracted/spending_reports/2019/Q123/8fc37ef0/Havelvac/2. 2019_9 amis_patasx.crag.mijocar..xls`.
Values are annual plan, revised annual plan, period plan, revised period plan,
and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 746, 3262 | `147,577,637.60`, `158,715,810.10`, `110,956,228.40`, `119,156,468.70`, `77,079,518.10`; `47,947,633.20`, `52,576,710.10`, `40,419,874.60`, `45,048,951.50`, `21,392,005.30` |
| ՀՀ էկոնոմիկայի նախարարություն | 2311, 2891 | `9,322,213.50`, `9,449,722.50`, `7,172,382.10`, `7,254,891.10`, `3,071,527.00`; `16,085,337.30`, `16,177,226.70`, `12,362,668.90`, `12,454,574.30`, `5,018,988.10` |
| ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 3641, 4419, 6095 | `141,696,953.90`, `145,564,471.20`, `96,512,764.00`, `98,572,132.70`, `88,783,397.60`; `15,933,738.60`, `18,570,314.70`, `11,270,749.90`, `13,872,668.80`, `11,717,734.50`; `4,361,319.50`, `4,954,635.30`, `3,501,613.10`, `4,244,691.70`, `2,912,848.50` |

`2019_SPENDING_Q1234` source workbook:
`data/extracted/spending_reports/2019/Q1234/38b4849d/3.Հավելված/3.Հավելված 1 աղյուսակ 2_ ծախսերն ըստ ծրագրերի և միջոց.xlsx`.
Values are annual plan, revised annual plan, and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 776, 3499 | `147,577,637.60`, `175,528,847.30`, `139,336,023.30`; `47,947,633.20`, `51,344,887.10`, `32,308,095.00` |
| ՀՀ էկոնոմիկայի նախարարություն | 2511, 3122 | `9,322,213.50`, `8,969,716.50`, `4,356,519.00`; `16,085,337.30`, `12,777,853.90`, `8,133,979.50` |
| ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 3884, 4740, 6524 | `141,696,953.90`, `144,261,843.80`, `134,875,641.90`; `15,933,738.60`, `18,884,769.80`, `17,563,849.30`; `4,361,319.50`, `5,448,873.30`, `4,868,153.70` |

**Impact:**

* Parsers that assume a unique `State Body Name` -> `Total` mapping will overwrite the total or only capture the last one.
* Validation fails (`hierarchical_totals`) because the `Overall Total` includes *all* blocks, but the processed data might only reflect one block's total or the sum of programs doesn't match the partial total.

## 2. Suspected Split Bodies (Other Years)

Validation errors suggest similar patterns in other years, likely due to subsequent reorganizations.

* **2023 (Q3): Ministry of Internal Affairs (ՀՀ ներքին գործերի նախարարություն):**
  * Validation shows a discrepancy of `~414,636.6` AMD.
  * Likely due to the 2023 merger of the Police and the Ministry of Emergency Situations.
* **2021 (Q1): Police (ՀՀ ոստիկանություն):**
  * Small discrepancy (`~1,416.9` AMD). Could be a small fragmented block or a line-item error.

## 3. Formatting Inconsistencies

* **Whitespace Variations:**
  * In 2019 files, the Prime Minister's Staff appears with two variations in the same file:
    * `ՀՀ վարչապետի  աշխատակազմ` (Double space)
    * `ՀՀ վարչապետի աշխատակազմ` (Single space)
  * This causes them to be treated as two distinct entities.

## Status

* **Current State:** The parser reads these as sequential blocks.
* **Proposed Fix (On Hold):** Logic to detect duplicate State Body names and "unify" their totals was proposed but put on hold to avoid diluting the original source structure without further consideration.

## Current validation failures

- `2019_SPENDING_Q12.csv`, `2019_SPENDING_Q123.csv`, and `2019_SPENDING_Q1234.csv`: All `hierarchical_totals` errors map to the split-body blocks described in §1 (multiple totals for the same ministry).
- `2023_SPENDING_Q123.csv` and `2023_SPENDING_Q1234.csv`: `hierarchical_totals` deltas (~0.4–0.8M AMD) for the Ministry of Internal Affairs align with the Police + Emergency Situations merger described in §2.
- Other datasets currently have no errors; remaining warnings reflect source numbers (e.g., execution >100%, negative plan values).
