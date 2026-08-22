CATEGORY_LABELS: dict[str, str] = {
    "hospitalization": "אשפוז",
    "specialist_visit": "ביקור מומחה",
    "dental": "טיפול שיניים",
    "optical": "אופטיקה",
    "medications": "תרופות",
    "emergency": "חדר מיון",
    "surgery": "ניתוח",
    "physiotherapy": "פיזיותרפיה",
    "mental_health": "בריאות הנפש",
    "lab_tests": "בדיקות מעבדה",
    "imaging": "הדמיה",
    "alternative": "רפואה משלימה",
}


def resolve(category_code: str) -> str:
    """Return the Hebrew label for a category code, or the code itself if unknown."""
    return CATEGORY_LABELS.get(category_code, category_code)
