"""Part 3.4: masking policy - external narratives never expose raw reseller names."""


def alias_for(reseller_id: str) -> str:
    """RS019 -> ALIAS-19, RS006 -> ALIAS-06."""
    return f"ALIAS-{reseller_id[3:]}"


def assert_no_raw_names_leak(text: str, reseller_names: list[str]) -> bool:
    """True when no raw reseller name appears verbatim in text, else False."""
    return not any(name and name in text for name in reseller_names)
