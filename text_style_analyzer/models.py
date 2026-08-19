from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Color:
    rgb: tuple[int, int, int]

    @property
    def hex(self) -> str:
        return "#{:02X}{:02X}{:02X}".format(*self.rgb)

    def to_dict(self) -> dict:
        return {"rgb": list(self.rgb), "hex": self.hex}


@dataclass(frozen=True)
class TextStyle:
    text: str
    confidence: float
    polygon: list[tuple[int, int]]
    text_color: Color
    background_color: Color
    font_size_px: int
    box_height_px: float

    def to_dict(self) -> dict:
        data = asdict(self)
        data["text_color"] = self.text_color.to_dict()
        data["background_color"] = self.background_color.to_dict()
        return data
