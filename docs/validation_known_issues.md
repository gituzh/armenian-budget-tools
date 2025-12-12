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

## Current validation failures (Dec 2025 run)

- `2019_SPENDING_Q123.csv` and `2019_SPENDING_Q1234.csv`: All `hierarchical_totals` errors map to the split-body blocks described in §1 (multiple totals for the same ministry).
- `2023_SPENDING_Q123.csv` and `2023_SPENDING_Q1234.csv`: `hierarchical_totals` deltas (~0.4–0.8M AMD) for the Ministry of Internal Affairs align with the Police + Emergency Situations merger described in §2.
- Other datasets currently have no errors; remaining warnings reflect source numbers (e.g., execution >100%, negative plan values).