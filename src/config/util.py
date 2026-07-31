def matchWithKeyWords(
    value: list[str],
    requiredKeywords: list[str] = [],
    necessaryKeywords: list[str] = [],
    excludedKeywords: list[str] = [],
    prefix: str | None = None,
) -> list[str]:
    result = value
    if excludedKeywords:
        for keyword in excludedKeywords:
            result = [v for v in result if not keyword in v]
    if requiredKeywords:
        for keyword in requiredKeywords:
            result = [v for v in result if keyword in v]
    if necessaryKeywords:
        includingResult = {
            k: v
            for k, v in [(v, any([k in v for k in necessaryKeywords])) for v in result]
        }
        result = [v for v in result if includingResult[v]]
    if prefix:
        result = [prefix + r for r in result]
    return result
    