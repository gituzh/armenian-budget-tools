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
  * The first two blocks are adjacent: no other state body total lies between
    them (Q123 Excel rows 3641 and 4419, Q1234 rows 3884 and 4740). In the
    processed CSV they form one run of rows with two sets of totals (Q123 lines
    490-603 and 604-664, Q1234 lines 527-653 and 654-719); the third block is
    separate (Q123 lines 833-880, Q1234 lines 901-950).
* **Prime Minister's Staff (ՀՀ վարչապետի աշխատակազմ), 2019 Q12, Q123, Q1234:**
  * Appears in **2** blocks, spelled with a double space in the first and a
    single space in the second (see §3). The blocks carry different totals, so
    this is a split body, not only a formatting difference.

**Programs split across a ministry's blocks (2019 Q123, Q1234):**

Some programs appear in more than one block of the same ministry, each time
with its own program totals. The first occurrence carries a zero annual plan.
Q123 values are annual plan, revised annual plan, period plan, revised period
plan, and actual; Q1234 values are annual plan, revised annual plan, and actual.

| Dataset | Ministry | Program | Excel rows | Program totals |
|---|---|---:|---:|---:|
| Q123 | Territorial Administration and Infrastructure | 1027 | 816, 3386 | `0`, `65,607.7`, `0`, `65,607.7`, `13,278.0`; `336,497.3`, `336,497.3`, `259,546.0`, `259,546.0`, `133,943.7` |
| Q123 | Territorial Administration and Infrastructure | 1072 | 1091, 3418 | `0`, `268,103.6`, `0`, `268,103.6`, `0`; `12,610,054.8`, `10,956,311.9`, `9,852,193.3`, `8,198,450.4`, `1,180,790.9` |
| Q123 | Education, Science, Culture and Sports | 1115 | 3820, 6279 | `0`, `54,509.4`, `0`, `54,509.4`, `54,509.4`; `978,187.4`, `943,374.7`, `743,473.3`, `874,625.6`, `732,966.7` |
| Q1234 | Territorial Administration and Infrastructure | 1004 | 815, 3501 | `0`, `85,680.0`, `0`; `16,901,296.9`, `26,020,510.6`, `21,884,551.0` |
| Q1234 | Territorial Administration and Infrastructure | 1027 | 865, 3629 | `0`, `65,607.7`, `26,100.9`; `336,497.3`, `336,497.3`, `323,725.4` |
| Q1234 | Territorial Administration and Infrastructure | 1072 | 1152, 3661 | `0`, `3,591,908.0`, `3,591,908.0`; `12,610,054.8`, `8,316,967.1`, `1,989,069.0` |
| Q1234 | Education, Science, Culture and Sports | 1115 | 4075, 6714 | `0`, `54,509.4`, `54,509.4`; `978,187.4`, `1,243,374.7`, `1,084,496.7` |

In 2019 Q123, program 1004 appears only once (Excel row 3264).

**Verified source rows for current 2019 failures:**

`2019_SPENDING_Q12` source workbook:
`data/extracted/spending_reports/2019/Q12/46e5e267/4. 2019_kisamyak_pat.crag.mij..xls`.
Values are annual plan, revised annual plan, period plan, revised period plan,
and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ էկոնոմիկայի նախարարություն | 2073, 2670 | `10,403,510.20`, `10,639,859.37`, `5,445,314.30`, `5,681,663.47`, `2,042,579.47`; `16,085,337.30`, `16,175,000.56`, `7,649,008.50`, `7,762,187.76`, `3,174,266.15` |
| ՀՀ վարչապետի աշխատակազմ | 84, 6013 | `20,439,178.80`, `21,463,749.92`, `9,046,954.30`, `10,059,490.52`, `5,651,189.50`; `1,153,554.80`, `1,153,554.80`, `447,429.20`, `447,429.20`, `177,601.40` |

`2019_SPENDING_Q123` source workbook:
`data/extracted/spending_reports/2019/Q123/8fc37ef0/Havelvac/2. 2019_9 amis_patasx.crag.mijocar..xls`.
Values are annual plan, revised annual plan, period plan, revised period plan,
and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 746, 3262 | `147,577,637.60`, `158,715,810.10`, `110,956,228.40`, `119,156,468.70`, `77,079,518.10`; `47,947,633.20`, `52,576,710.10`, `40,419,874.60`, `45,048,951.50`, `21,392,005.30` |
| ՀՀ էկոնոմիկայի նախարարություն | 2311, 2891 | `9,322,213.50`, `9,449,722.50`, `7,172,382.10`, `7,254,891.10`, `3,071,527.00`; `16,085,337.30`, `16,177,226.70`, `12,362,668.90`, `12,454,574.30`, `5,018,988.10` |
| ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 3641, 4419, 6095 | `141,696,953.90`, `145,564,471.20`, `96,512,764.00`, `98,572,132.70`, `88,783,397.60`; `15,933,738.60`, `18,570,314.70`, `11,270,749.90`, `13,872,668.80`, `11,717,734.50`; `4,361,319.50`, `4,954,635.30`, `3,501,613.10`, `4,244,691.70`, `2,912,848.50` |
| ՀՀ վարչապետի աշխատակազմ | 90, 6617 | `16,668,356.90`, `18,493,852.20`, `10,868,755.10`, `12,736,215.50`, `8,866,682.60`; `639,558.50`, `639,558.50`, `452,835.70`, `452,835.70`, `261,341.10` |

`2019_SPENDING_Q1234` source workbook:
`data/extracted/spending_reports/2019/Q1234/38b4849d/3.Հավելված/3.Հավելված 1 աղյուսակ 2_ ծախսերն ըստ ծրագրերի և միջոց.xlsx`.
Values are annual plan, revised annual plan, and actual.

| State body | Excel rows | Block totals |
|---|---:|---:|
| ՀՀ տարածքային կառավարման և ենթակառուցվածքների նախարարություն | 776, 3499 | `147,577,637.60`, `175,528,847.30`, `139,336,023.30`; `47,947,633.20`, `51,344,887.10`, `32,308,095.00` |
| ՀՀ էկոնոմիկայի նախարարություն | 2511, 3122 | `9,322,213.50`, `8,969,716.50`, `4,356,519.00`; `16,085,337.30`, `12,777,853.90`, `8,133,979.50` |
| ՀՀ կրթության, գիտության, մշակույթի և սպորտի նախարարություն | 3884, 4740, 6524 | `141,696,953.90`, `144,261,843.80`, `134,875,641.90`; `15,933,738.60`, `18,884,769.80`, `17,563,849.30`; `4,361,319.50`, `5,448,873.30`, `4,868,153.70` |
| ՀՀ վարչապետի աշխատակազմ | 102, 7058 | `16,668,356.90`, `18,372,581.30`, `14,120,700.90`; `639,558.50`, `564,758.20`, `386,398.00` |

**Confirmed Case (2023 Q123, Q1234): Ministry of Internal Affairs (ՀՀ ներքին գործերի նախարարություն):**

The ministry has two total rows, and its two blocks are consecutive, so it looks
like one block in the processed CSV; only its `state_body_*` totals change
between the blocks. The Police (`ՀՀ ոստիկանություն`) is still a separate state
body in 2023.

* Block 1: programs 1028, 1085, 1089, 1090, 1107, 1112 (former Emergency
  Situations programs).
* Block 2: programs 1070 and 1106 (refugee integration and migration policy)
  and 1234 (ministry policy and management).

`2023_SPENDING_Q123` source workbook:
`data/extracted/spending_reports/2023/Q123/49c3ab4d/49c3ab4d/2. 2023_9 ամիս_ պատասխանատու,ծրագիր,միջոցառում.xls`.
Values are annual plan, revised annual plan, period plan, revised period plan,
and actual.

| Block | Excel row | Block totals |
|---|---:|---:|
| 1 | 6260 | `17,099,402.8`, `16,927,007.9`, `12,669,640.7`, `12,858,399.4`, `11,372,002.0` |
| 2 | 6425 | `391,973.2`, `913,714.7`, `279,048.6`, `527,986.1`, `414,636.6` |

`2023_SPENDING_Q1234` source workbook:
`data/extracted/spending_reports/2023/Q1234/eeb4fff4/4.Հավելվածներ/3.Հավելված N1 աղյուսակ N2_ծախսերն ըստ ծրագրերի և միջոցառումների.xls`.
Values are annual plan, revised annual plan, and actual.

| Block | Excel row | Block totals |
|---|---:|---:|
| 1 | 6483 | `17,099,402.8`, `16,711,698.8`, `15,861,142.1` |
| 2 | 6648 | `391,973.2`, `830,181.2`, `787,969.4` |

The `hierarchical_totals` deltas for this ministry equal the block 2 totals.

**Impact:**

* Parsers that assume a unique `State Body Name` -> `Total` mapping will overwrite the total or only capture the last one.
* Validation fails (`hierarchical_totals`) because the `Overall Total` includes *all* blocks, but the processed data might only reflect one block's total or the sum of programs doesn't match the partial total.

## 2. Suspected Split Bodies (Other Years)

Validation errors suggest similar patterns in other years, likely due to subsequent reorganizations.

* **2021 (Q1): Police (ՀՀ ոստիկանություն):**
  * Small discrepancy (`~1,416.9` AMD). Could be a small fragmented block or a line-item error.

## 3. Formatting Inconsistencies

* **Whitespace Variations:**
  * In 2019 files, the Prime Minister's Staff appears with two variations in the same file:
    * `ՀՀ վարչապետի  աշխատակազմ` (Double space)
    * `ՀՀ վարչապետի աշխատակազմ` (Single space)
  * This causes them to be treated as two distinct entities.
  * The two spellings label two blocks with different totals; see §1.

## Status

* **Current State:** The parser reads these as sequential blocks.
* **Proposed Fix (On Hold):** Logic to detect duplicate State Body names and "unify" their totals was proposed but put on hold to avoid diluting the original source structure without further consideration.

## Current validation failures

- `2019_SPENDING_Q12.csv`, `2019_SPENDING_Q123.csv`, and `2019_SPENDING_Q1234.csv`: All `hierarchical_totals` errors map to the split-body blocks described in §1 (multiple totals for the same ministry). The `duplicate_records` check reports the same split bodies, including the Prime Minister's Staff and the split programs (state bodies and programs in more than one block or with differing totals), and the Prime Minister's Staff whitespace variants from §3.
- `2023_SPENDING_Q123.csv` and `2023_SPENDING_Q1234.csv`: `hierarchical_totals` deltas (~0.3–0.9M AMD) for the Ministry of Internal Affairs equal the totals of its second block (§1). `duplicate_records` reports the ministry's differing totals.
- Other datasets currently have no errors; remaining warnings reflect source numbers (e.g., execution >100%, negative plan values).
