"""Part 3: offline, deterministic template-fill for the prompt pack.

No LLM / network / API key is used.  PROMPT_TEMPLATE is the text documented in
prompt_pack.md (what you would hand to an LLM); draft_message() is the offline
fill that Part 4 uses to draft stakeholder updates from verified numbers.
"""
import re

INPUT_VARIABLES = ["category", "previous_revenue", "current_revenue", "mom_pct", "month", "prev_month"]

PROMPT_TEMPLATE = (
    "You are drafting a short stakeholder update for a Meesho regional manager.\n"
    "Category: {category}. Period: {month} compared with {prev_month}.\n"
    "Verified numbers (use ONLY these): previous revenue INR {previous_revenue} in {prev_month}; "
    "current revenue INR {current_revenue} in {month}; month-on-month change {mom_pct}%.\n"
    "Write exactly three labelled parts: Context, Insight, Implication.\n"
    "- Context: what is measured and over which months.\n"
    "- Insight: state the change as a FACT using the verified numbers only.\n"
    "- Implication: one specific, actionable next step; label any proposed cause as a HYPOTHESIS.\n"
    "Rules: never state a number that is not one of the verified numbers above; "
    "never name a reseller (use aliases only); keep it under 120 words; plain language, no jargon."
)

_UP = (
    "Context: This update covers {category} revenue for {month} compared with {prev_month}. "
    "Insight (fact): {category} revenue rose from INR {previous_revenue} in {prev_month} to "
    "INR {current_revenue} in {month}, a month-on-month change of {mom_pct}%. "
    "Implication (hypothesis, not proven by this data): the rise may come from a promotion, "
    "seasonal demand or a few resellers driving volume. Recommended next step: ask regional "
    "managers to check whether the increase is broad-based or concentrated in a handful of "
    "resellers, and confirm stock and fulfilment capacity for {category} before the next month starts."
)
_DOWN = (
    "Context: This update covers {category} revenue for {month} compared with {prev_month}. "
    "Insight (fact): {category} revenue fell from INR {previous_revenue} in {prev_month} to "
    "INR {current_revenue} in {month}, a month-on-month change of {mom_pct}%. "
    "Implication (hypothesis, not proven by this data): the fall may come from a demand pullback, "
    "stock-outs or fewer active resellers listing {category}. Recommended next step: ask regional "
    "managers to check which resellers reduced {category} orders and whether any listings were out "
    "of stock, then report back before the next review."
)

_NUM = re.compile(r"-?\d+(?:\.\d+)?")


def _money(x: float) -> str:
    return f"{float(x):.2f}"


def fill_prompt(category, previous_revenue, current_revenue, mom_pct, month, prev_month) -> str:
    """Fill the LLM-ready prompt (optional use; the pipeline itself needs no LLM)."""
    return PROMPT_TEMPLATE.format(
        category=category, previous_revenue=_money(previous_revenue),
        current_revenue=_money(current_revenue), mom_pct=mom_pct, month=month, prev_month=prev_month)


def numbers_trace(text: str, allowed: list[str]) -> bool:
    """Checklist item 1: every number in text must be one of the supplied values."""
    return all(n in set(allowed) for n in _NUM.findall(text))


def draft_message(category, previous_revenue, current_revenue, mom_pct, month, prev_month) -> str:
    """Offline template-fill: Context -> Insight -> Implication, numbers verified."""
    template = _UP if mom_pct > 0 else _DOWN
    text = template.format(
        category=category, previous_revenue=_money(previous_revenue),
        current_revenue=_money(current_revenue), mom_pct=mom_pct, month=month, prev_month=prev_month)
    allowed = [_money(previous_revenue), _money(current_revenue), str(mom_pct)]
    if not numbers_trace(text, allowed):
        raise ValueError("drafted message contains a number that does not trace to the inputs")
    return text
