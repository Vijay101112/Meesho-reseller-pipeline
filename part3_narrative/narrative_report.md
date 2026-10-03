# Narrative Report (Part 3)

All numbers come from Part 1 (`monthly_category_revenue.csv`) and Part 2 (`mom_growth`, `is_flagged`).
Revenue is `SUM(quantity * unit_price)` over all order statuses, in INR.

## 3.2 Worked narratives

### May: Ethnic Wear (+77.1% MoM, flagged)

**Context.** This update measures Ethnic Wear revenue for May compared with April 2026, across all Meesho resellers.

**Insight (fact).** Ethnic Wear revenue rose from INR 104520.77 in April to INR 185107.61 in May, a month-on-month change of **77.1%**. Orders in the category went from 64 to 104 over the same period.

**Implication.** *(Hypothesis, not proven by this data):* the jump may be driven by a promotion or festive demand. **Recommended next step:** ask each regional manager to check whether the extra orders came from many resellers or only a few, and confirm that stock and fulfilment capacity for Ethnic Wear can handle a similar volume in June.

### June: Ethnic Wear (-58.74% MoM, flagged in the opposite direction)

**Context.** This update measures Ethnic Wear revenue for June compared with May 2026, across all Meesho resellers.

**Insight (fact).** Ethnic Wear revenue fell from INR 185107.61 in May to INR 76371.53 in June, a month-on-month change of **-58.74%**. Orders went from 104 to 52. June's revenue is also below April's INR 104520.77, so this is more than a return to the April level.

**Implication.** *(Hypothesis, not proven by this data):* the May spike may have pulled demand forward, or the May promotion may have ended, or stock-outs may have limited sales. **Recommended next step:** ask regional managers to list the Ethnic Wear resellers whose orders dropped most from May to June, check those listings for stock-outs, and decide before the next review whether a repeat promotion is worth running.

### Self-score against the 4-criterion refinement checklist

**May Ethnic Wear (+77.1%)**

| Criterion | Score | Why it passes |
|---|---|---|
| Specificity | Pass | Names Ethnic Wear, April and May, and uses the exact figures 77.1%, INR 104520.77 and INR 185107.61. |
| Audience fit | Pass | Plain business language for a regional manager, with no SQL, code or statistical terms. |
| Completeness | Pass | Has a Context, an Insight labelled as fact, and an Implication labelled as hypothesis with a next step. |
| Actionability | Pass | Tells regional managers to check reseller concentration of the extra orders and confirm June capacity. |

**June Ethnic Wear (-58.74%)**

| Criterion | Score | Why it passes |
|---|---|---|
| Specificity | Pass | Names Ethnic Wear, May and June, and uses the exact figures -58.74%, INR 185107.61 and INR 76371.53. |
| Audience fit | Pass | Explains the drop in plain language and compares with April's level instead of using technical terms. |
| Completeness | Pass | Has a Context, an Insight labelled as fact, and an Implication with three labelled hypotheses and a next step. |
| Actionability | Pass | Tells regional managers to list the resellers with the biggest drops, check stock-outs, and decide on a repeat promotion. |

## 3.3 Chart-choice justification (text only, no images)

**Q1. "Which month had the highest total revenue?"** (April INR 419417.43, May INR 444594.25, June INR 398055.24)
Use a **vertical bar chart** with one bar per month. This is **univariate**: one measure (revenue) across one categorical variable (month). Bars let a reader see in under 10 seconds that May is tallest, but only if the **y-axis starts at zero**; truncating the axis would exaggerate a 6.0% May-vs-April gap. With a single series, no legend is needed, and no 3D effects should be used because they distort bar heights.

**Q2. "What percentage share does Ethnic Wear represent of April's total revenue?"** (INR 104520.77 of INR 419417.43 = 24.92%)
Use a **single 100% stacked bar with two segments (Ethnic Wear vs all other categories)** with the 24.92% labelled directly, rather than a pie with five slices. This is **univariate part-to-whole** (one month, one measure split by category). A bar makes the share readable within 10 seconds because length is easier to judge than angle, and the axis runs from 0 to 100%. A legend is only needed if the other categories are shown as separate segments (multiple series); with just two segments, direct labels replace it. No 3D.

**Q3. "How do the four regions compare on total revenue?"** (North INR 337125.46, West INR 333106.33, South INR 316736.68, East INR 275098.45)
Use a **horizontal bar chart sorted from highest to lowest**. This is **univariate** (one measure across one categorical variable with four values). Sorting makes the ranking (North first, East last) obvious within 10 seconds, the **axis starts at zero** so the gaps between regions are not exaggerated, and with one series there is no legend. Avoid a map or 3D chart, which add decoration without adding comparison accuracy.

*(Framework note: a bivariate chart such as a line of revenue by month, split by category, becomes **multivariate** and is the right choice only when the question is about category trends; none of the three questions above needs it.)*

## 3.4 Top-reseller narrative (masked)

Masking policy: resellers are referenced only by region and `alias_for(reseller_id)`, never by raw name. `test_masking.py` checks this block with `assert_no_raw_names_leak`.

<!-- TOP_RESELLER_NARRATIVE_START -->
**Context.** This note covers the five resellers whose total spend across April to June 2026 exceeded INR 50000.

**Insight (fact).** ALIAS-19 (West region) led with INR 75295.09, followed by ALIAS-22 (West) with INR 73882.33, ALIAS-12 (South) with INR 69936.46, ALIAS-06 (North) with INR 64238.97 and ALIAS-05 (North) with INR 61825.02. Together they account for INR 345177.87, which is 27.35% of the INR 1262066.92 total revenue.

**Implication.** *(Hypothesis, not proven by this data):* these five may be the most reliable repeat sellers in their regions. **Recommended next step:** have the West regional manager review what ALIAS-19 and ALIAS-22 do differently from other West resellers, and have the North and South managers check whether ALIAS-06, ALIAS-05 and ALIAS-12 have stock and support to keep their volume steady.
<!-- TOP_RESELLER_NARRATIVE_END -->
