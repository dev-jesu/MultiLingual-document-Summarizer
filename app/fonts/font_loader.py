"""Font loader and management utility for ReportLab Unicode rendering."""
import os
from typing import Optional
from app.utils.logger import logger

_REGISTERED_FONT_NAME: Optional[str] = None


def get_registered_font_name() -> str:
    """
    Registers a Unicode-capable font in ReportLab (e.g., Nirmala UI for Indian scripts).
    Returns the registered font name string.
    """
    global _REGISTERED_FONT_NAME
    if _REGISTERED_FONT_NAME is not None:
        return _REGISTERED_FONT_NAME

    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont

        candidate_fonts = [
            ("NirmalaUI", "C:/Windows/Fonts/Nirmala.ttc", 0),
            ("NirmalaUI-Bold", "C:/Windows/Fonts/NirmalaB.ttc", 0),
            ("SegoeUI", "C:/Windows/Fonts/segoeui.ttf", None),
            ("Arial", "C:/Windows/Fonts/arial.ttf", None),
            ("FreeSerif", "/usr/share/fonts/truetype/freefont/FreeSerif.ttf", None),
            ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None),
        ]

        for font_name, font_path, sub_index in candidate_fonts:
            if os.path.exists(font_path):
                try:
                    if sub_index is not None:
                        font_obj = TTFont(font_name, font_path, subfontIndex=sub_index)
                    else:
                        font_obj = TTFont(font_name, font_path)
                    pdfmetrics.registerFont(font_obj)
                    _REGISTERED_FONT_NAME = font_name
                    logger.info("Successfully registered ReportLab font: %s from %s", font_name, font_path)
                    return font_name
                except Exception as err:
                    logger.warning("Could not register font %s from %s: %s", font_name, font_path, err)

    except Exception as exc:
        logger.warning("ReportLab font metrics registration failed: %s", exc)

    _REGISTERED_FONT_NAME = "Helvetica"
    return _REGISTERED_FONT_NAME
