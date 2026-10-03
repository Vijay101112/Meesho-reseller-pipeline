"""Part 2: guardrail & growth-detection engine (standard library only)."""
import csv
import math

REQUIRED_COLUMNS = ["month", "category", "revenue", "n_orders"]


def mom_growth(previous: float, current: float) -> float:
    """Month-on-Month growth percentage, rounded to 2 decimals.

    A previous value of 0 makes growth undefined, so it raises instead of
    returning a misleading number.
    """
    if previous == 0:
        raise ValueError("previous revenue is 0; month-on-month growth is undefined")
    return round((current - previous) / previous * 100, 2)


def is_flagged(mom_pct: float, threshold: float = 8.0) -> str:
    """Return 'flagged', 'not_flagged' or 'escalate_exact_boundary' (never a bool).

    An exact-boundary value is never auto-decided: it is held for human review.
    """
    size = abs(mom_pct)
    if size > threshold:
        return "flagged"
    if size < threshold:
        return "not_flagged"
    return "escalate_exact_boundary"


def validate_feed(csv_path: str) -> tuple[bool, list[str]]:
    """Input guardrail for a month,category,revenue,n_orders CSV.

    Line numbers are 1-indexed with the header as line 1.
    Returns (True, []) only when there are zero errors.
    """
    errors: list[str] = []
    try:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing_cols = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
            if missing_cols:
                return False, [f"line 1: missing column(s): {', '.join(missing_cols)}"]
            for row in reader:
                line = reader.line_num
                month = (row.get("month") or "").strip()
                category = (row.get("category") or "").strip()
                revenue = (row.get("revenue") or "").strip()

                if category == "":
                    errors.append(f"line {line}: missing category (month={month})")
                if revenue == "":
                    errors.append(f"line {line}: missing revenue (category={category})")
                else:
                    try:
                        value = float(revenue)
                        if not math.isfinite(value):
                            raise ValueError
                    except ValueError:
                        errors.append(f"line {line}: revenue not numeric: {revenue!r}")
                    else:
                        if value < 0:
                            errors.append(
                                f"line {line}: negative revenue ({value}) for category={category}"
                            )
    except FileNotFoundError:
        return False, [f"file not found: {csv_path}"]
    return (len(errors) == 0), errors
