"""The fixed list of Units. A Unit outside this list can never be saved."""

TO_TASTE = "ตามชอบ"

# (Thai name, English label). The Thai name is what gets stored.
UNITS: list[tuple[str, str]] = [
    ("กรัม", "g"),
    ("กิโลกรัม", "kg"),
    ("มิลลิลิตร", "ml"),
    ("ลิตร", "l"),
    ("ช้อนชา", "tsp"),
    ("ช้อนโต๊ะ", "tbsp"),
    ("ถ้วย", "cup"),
    ("ฟอง", "egg"),
    ("กลีบ", "clove"),
    ("เม็ด", "piece, as in chillies"),
    ("ชิ้น", "piece"),
    ("ต้น", "stalk"),
    (TO_TASTE, "to taste"),
]

UNIT_NAMES: frozenset[str] = frozenset(name for name, _ in UNITS)
