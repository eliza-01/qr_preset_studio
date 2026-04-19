# qr_preset_studio/domain/constants.py
SWYP_PUBLIC_DOMAIN = "https://swyp.ru"
SWYP_PUBLIC_CARD_PATH_PREFIX = "/u"

BODY_SHAPES = ["square", "rounded", "liquid", "spikes", "claws"]
EYE_FRAME_SHAPES = ["square", "rounded", "classy_rounded", "classy"]
EYE_BALL_SHAPES = ["square", "circle", "rounded", "classy_rounded", "classy"]
GRADIENT_DIRECTIONS = ["horizontal", "vertical", "diagonal_down", "diagonal_up"]

QR_ERROR_CORRECTION_LEVELS = ["L", "M", "Q", "H"]
QR_VERSION_VALUES = ["auto"] + [str(index) for index in range(1, 41)]
QR_MASK_PATTERN_VALUES = ["auto"] + [str(index) for index in range(8)]


def swyp_public_base_url() -> str:
    return f"{SWYP_PUBLIC_DOMAIN.rstrip('/')}{SWYP_PUBLIC_CARD_PATH_PREFIX}"


def build_swyp_card_url(slug: str) -> str:
    clean_slug = (slug or "").strip().strip("/")
    if not clean_slug:
        return ""
    return f"{swyp_public_base_url().rstrip('/')}/{clean_slug}"
