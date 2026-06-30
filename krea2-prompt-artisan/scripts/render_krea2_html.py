#!/usr/bin/env python3
"""Render a Krea 2 prompt package into a local HTML page."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path
import re
import sys


def default_output_dir() -> Path:
    configured = os.environ.get("KREA2_OUTPUT_DIR")
    if configured:
        return Path(configured).expanduser()
    return Path.cwd() / "Krea2提示词"


DEFAULT_OUTPUT_DIR = default_output_dir()
DEFAULT_SIGNATURE = "—— Codex 协助整理，愿灵感顺手成图 🌸"
ILLEGAL_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|]+')
CJK_RE = re.compile(r"[\u3400-\u9fff]")
QUESTION_MOJIBAKE_RE = re.compile(r"\?{2,}")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")
PLACEHOLDER_RE = re.compile(r"{{([A-Z_]+)}}")
POEM_PUNCTUATION_RE = re.compile(r"[，。！？；：、,.!?;:]")
POEM_ALLOWED_CORE_RE = re.compile(r"^[\u3400-\u9fff，。！？；：、,.!?;:]+$")

SLOT_LABELS = {
    "subject details": ("主体细节", "Subject details"),
    "subject detail": ("主体细节", "Subject details"),
    "canvas and use": ("画布与用途", "Canvas and use"),
    "canvas/use": ("画布与用途", "Canvas and use"),
    "environment": ("环境氛围", "Environment"),
    "composition and camera": ("构图与镜头", "Composition and camera"),
    "composition/camera": ("构图与镜头", "Composition and camera"),
    "lighting and tone": ("光线与色调", "Lighting and tone"),
    "lighting/tone": ("光线与色调", "Lighting and tone"),
    "style and medium": ("风格与媒介", "Style and medium"),
    "style/medium": ("风格与媒介", "Style and medium"),
    "materials and colors": ("材质与色彩", "Materials and colors"),
    "materials/colors": ("材质与色彩", "Materials and colors"),
    "quality safeguards": ("质量控制", "Quality safeguards"),
    "quality safeguard": ("质量控制", "Quality safeguards"),
    "design note": ("设计说明", "Design note"),
}

RATIONALE_FALLBACKS = {
    "subject": "确保主体身份、姿态和关键视觉特征优先进入模型注意力，减少人物设定漂移。",
    "canvas": "提前限定画幅和用途，帮助 Krea 2 稳定构图密度与成片方向。",
    "environment": "用环境信息建立空间层次和氛围，让主体不悬浮、不空泛。",
    "composition": "明确镜头、机位和视觉动线，提升画面焦点与阅读顺序。",
    "lighting": "用光线和色调控制质感、体积感与情绪温度。",
    "style": "锁定媒介和审美边界，避免模型偏向不需要的画风。",
    "materials": "强化颜色、纹理和材质细节，让画面更具体、更可控。",
    "quality": "提前压制常见生成瑕疵，保护人物结构、画面清晰度和可用性。",
    "default": "补足该模块的生成意图，帮助模型理解这项描述在画面中的作用。",
}

TITLE_EMOJI_RULES = [
    (("花", "蔷薇", "玫瑰", "樱", "庭院", "flower", "rose", "floral", "garden"), "🌸"),
    (("月", "夜", "星", "星空", "宇宙", "银河", "moon", "night", "star", "space", "galaxy"), "🌙"),
    (("海", "湖", "雨", "水", "ocean", "sea", "lake", "rain", "water"), "🌊"),
    (("火", "焰", "熔岩", "fire", "flame", "lava"), "🔥"),
    (("城", "街", "赛博", "霓虹", "city", "street", "cyber", "neon"), "🌃"),
    (("森林", "树", "自然", "山", "forest", "tree", "nature", "mountain"), "🌿"),
    (("书", "纸", "页", "图书馆", "book", "paper", "page", "library"), "📖"),
    (("咖啡", "茶", "甜点", "coffee", "tea", "cake", "dessert"), "☕"),
    (("镜头", "摄影", "电影", "cinematic", "camera", "photo", "film"), "🎬"),
    (("魔法", "奇幻", "幻想", "magic", "fantasy", "dream"), "🔮"),
]
KNOWN_TITLE_EMOJIS = {emoji for _, emoji in TITLE_EMOJI_RULES} | {"✨", "🪄", "🖼️", "📷"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        help="JSON file containing title, prompt_text/english_prompt, translation_text/chinese_prompt, and optional fields. Reads stdin when omitted.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where the HTML file should be written.",
    )
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parents[1] / "assets" / "html_template.html"),
        help="HTML template path.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated HTML page in the default browser on Windows.",
    )
    parser.add_argument(
        "--open-existing",
        help="Open an existing checked HTML page and exit without rendering a new file.",
    )
    return parser.parse_args()


def read_payload(path: str | None) -> dict:
    if path:
        raw = Path(path).read_text(encoding="utf-8-sig")
    else:
        data = sys.stdin.buffer.read()
        raw = decode_stdin(data)
    if not raw.strip():
        raise SystemExit("No JSON input provided.")
    payload = json.loads(raw)
    validate_payload(payload)
    return payload


def decode_stdin(data: bytes) -> str:
    if not data:
        return ""
    encodings = ["utf-8-sig"]
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        encodings.append("utf-16")
    if b"\x00" in data[:80]:
        encodings.extend(["utf-16", "utf-16-le"])
    if os.name == "nt":
        encodings.extend(["mbcs", "cp936"])
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def clean_filename(value: str, fallback: str = "Krea2_prompt") -> str:
    value = ILLEGAL_FILENAME_CHARS.sub("", value).strip()
    value = re.sub(r"\s+", "_", value)
    value = value.strip("._ ")
    if not value:
        value = fallback
    return value[:80]


def unique_path(output_dir: Path, scene_name: str) -> Path:
    base_name = clean_filename(scene_name)
    candidate = output_dir / f"Krea2_prompt_{base_name}.html"
    counter = 1
    while candidate.exists():
        candidate = output_dir / f"Krea2_prompt_{base_name}_{counter}.html"
        counter += 1
    return candidate



def escape_text(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def first_present(payload: dict, *keys: str, default: object = "") -> object:
    for key in keys:
        value = payload.get(key)
        if value not in (None, ""):
            return value
    return default


def required_text(payload: dict, label: str, *keys: str) -> str:
    value = first_present(payload, *keys)
    text = str(value or "").strip()
    if not text:
        accepted = ", ".join(keys)
        raise SystemExit(f"{label} is required: provide a non-empty value in one of: {accepted}.")
    return text


def contains_cjk(value: object) -> bool:
    return bool(CJK_RE.search(str(value or "")))


def looks_like_question_mojibake(value: object) -> bool:
    text = str(value or "")
    return bool(QUESTION_MOJIBAKE_RE.search(text)) and not contains_cjk(text)


def iter_payload_strings(value: object, path: str = "payload"):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from iter_payload_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_payload_strings(child, f"{path}[{index}]")


def validate_payload(payload: dict) -> None:
    for path, value in iter_payload_strings(payload):
        if looks_like_question_mojibake(value):
            raise SystemExit(
                "Detected question-mark mojibake in Chinese/emoji payload text at "
                f"{path}. Rerun with UTF-8 payload input. In PowerShell, set "
                "$OutputEncoding=[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new($false) "
                "and $env:PYTHONUTF8='1', or pass a UTF-8 JSON file with --input."
            )


def strip_title_prefix(value: object) -> str:
    text = str(value or "").strip()
    text = re.sub(r"^[^\w\u3400-\u9fff]+", "", text)
    text = re.sub(r"^Krea\s*2\s*(?:Prompt|提示词)\s*[-—_:：]*\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^Krea2\s*(?:Prompt|提示词)\s*[-—_:：]*\s*", "", text, flags=re.IGNORECASE)
    return text.strip() or str(value or "").strip()


def is_chinese_title_name(value: object) -> bool:
    text = str(value or "").strip()
    return bool(text) and contains_cjk(text) and not ASCII_LETTER_RE.search(text)


def choose_chinese_title(payload: dict) -> str:
    title_keys = ("title_cn", "chinese_title", "title", "filename_title", "file_title", "scene_name_cn", "scene_name")
    for key in title_keys:
        candidate = strip_title_prefix(payload.get(key, ""))
        if candidate and is_chinese_title_name(candidate):
            return candidate
        if candidate and contains_cjk(candidate) and ASCII_LETTER_RE.search(candidate):
            raise SystemExit(
                f"Chinese title name must not contain English letters: {candidate}. "
                "Use a fully Chinese title name for both the visible title and file name."
            )
    raise SystemExit(
        "Chinese page title required: provide a full Chinese title in title_cn or chinese_title. "
        "The visible HTML title must use Krea 2 提示词 - 中文标题, and the output file "
        "will be named Krea2_prompt_中文标题.html."
    )


def choose_filename_title(payload: dict, rendered_title: str) -> str:
    return choose_chinese_title(payload)


def infer_title_emoji(payload: dict) -> str:
    supplied = str(first_present(payload, "title_emoji", "emoji", default="")).strip()
    if supplied:
        return supplied.split()[0]

    haystack = " ".join(
        str(first_present(payload, key, default=""))
        for key in ("scene_name", "title", "prompt_text", "english_prompt", "translation_text", "chinese_prompt")
    ).lower()
    for keywords, emoji in TITLE_EMOJI_RULES:
        if any(keyword.lower() in haystack for keyword in keywords):
            return emoji
    return "✨"


def normalize_title(raw_title: object, title_emoji: str) -> str:
    title_name = strip_title_prefix(raw_title)
    visible_title = f"Krea 2 提示词 - {title_name}"
    if title_emoji:
        return f"{title_emoji} {visible_title}"
    return visible_title


def slot_family(slot: object, slot_cn: object = "", slot_en: object = "") -> str:
    text = " ".join(str(part or "") for part in (slot, slot_cn, slot_en)).lower()
    if any(token in text for token in ("subject", "主体")):
        return "subject"
    if any(token in text for token in ("canvas", "画布", "画幅", "用途")):
        return "canvas"
    if any(token in text for token in ("environment", "环境", "氛围")):
        return "environment"
    if any(token in text for token in ("composition", "camera", "构图", "镜头")):
        return "composition"
    if any(token in text for token in ("lighting", "tone", "光线", "色调")):
        return "lighting"
    if any(token in text for token in ("style", "medium", "风格", "媒介")):
        return "style"
    if any(token in text for token in ("materials", "colors", "材质", "色彩")):
        return "materials"
    if any(token in text for token in ("quality", "safeguard", "质量", "规避", "负面")):
        return "quality"
    return "default"


def fallback_rationale(slot: object, slot_cn: object = "", slot_en: object = "") -> str:
    return RATIONALE_FALLBACKS[slot_family(slot, slot_cn, slot_en)]


def first_row_value(row: dict, *keys: str) -> object:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return ""


def render_slot_label(slot: object, slot_cn: object = "", slot_en: object = "") -> str:
    cn = str(slot_cn or "").strip()
    en = str(slot_en or "").strip()
    raw = str(slot or "Design note").strip()
    if not cn and not en:
        mapped = SLOT_LABELS.get(raw.lower())
        if mapped:
            cn, en = mapped
        elif " / " in raw:
            cn, en = [part.strip() for part in raw.split(" / ", 1)]
        else:
            cn = raw
    english_html = f'<span class="slot-en">{escape_text(en)}</span>' if en else ""
    return (
        '<strong class="slot-label">'
        f'<span class="slot-cn">{escape_text(cn)}</span>'
        f'{english_html}'
        '</strong>'
    )


def render_breakdown(rows: object) -> str:
    if not rows:
        rows = [
            {
                "slot": "Subject details",
                "content": "Core subject, action, pose, proportions, and priority visual traits.",
                "rationale": "Anchor the model on the most important visual information first.",
            },
            {
                "slot": "Canvas and use",
                "content": "Image purpose and aspect-ratio direction.",
                "rationale": "Help Krea 2 choose framing and density appropriate to the output.",
            },
            {
                "slot": "Environment",
                "content": "Setting, time, atmosphere, and spatial layers.",
                "rationale": "Give the subject believable context and depth.",
            },
            {
                "slot": "Composition and camera",
                "content": "Framing, angle, focal behavior, focus, and negative space.",
                "rationale": "Control readability and visual hierarchy.",
            },
            {
                "slot": "Lighting and tone",
                "content": "Key light, fill, rim light, contrast, color temperature, and shadows.",
                "rationale": "Shape mood and dimensionality.",
            },
            {
                "slot": "Style and medium",
                "content": "Photography, illustration, cinematic, product, anime, or concept-art language.",
                "rationale": "Align rendering style with the user's intent.",
            },
            {
                "slot": "Materials and colors",
                "content": "Texture, palette, reflective behavior, and surface detail.",
                "rationale": "Make the image tactile and visually specific.",
            },
            {
                "slot": "Quality safeguards",
                "content": "Clarity and negative constraints such as no text, no logo, no watermark.",
                "rationale": "Reduce common generation artifacts.",
            },
        ]

    rendered = []
    for row in rows:
        if isinstance(row, dict):
            slot = first_row_value(row, "slot", "name", "module", "模块")
            slot_cn = first_row_value(row, "slot_cn", "name_cn", "module_cn", "模块中文")
            slot_en = first_row_value(row, "slot_en", "name_en", "module_en", "模块英文")
            content = first_row_value(row, "content", "design_content", "description", "details", "设计内容")
            rationale = first_row_value(
                row,
                "rationale",
                "logic",
                "design_logic",
                "consideration",
                "considerations",
                "design_consideration",
                "design_considerations",
                "reason",
                "reasoning",
                "why",
                "note",
                "notes",
                "设计考虑",
                "设计逻辑",
            )
            if not str(rationale).strip():
                rationale = fallback_rationale(slot, slot_cn, slot_en)
        else:
            slot, slot_cn, slot_en, content, rationale = "Design note", "", "", str(row), fallback_rationale("Design note")
        rendered.append(
            "<tr>"
            f"<td>{render_slot_label(slot, slot_cn, slot_en)}</td>"
            f"<td><span>{escape_text(content)}</span></td>"
            f"<td><span>{escape_text(rationale)}</span></td>"
            "</tr>"
        )
    return "\n".join(rendered)


def render_notes(notes: object) -> str:
    if not notes:
        notes = [
            "Balanced the prompt across subject, scene, composition, light, style, materials, and quality safeguards.",
            "Kept negative constraints natural so the prompt remains readable in Krea 2.",
        ]
    if isinstance(notes, str):
        notes = [notes]
    return "\n".join(f"<li>{escape_text(note)}</li>" for note in notes)


def punctuate_poem(core: str) -> str:
    chinese_chars = "".join(CJK_RE.findall(core))
    if POEM_PUNCTUATION_RE.search(core):
        return core
    if len(chinese_chars) == 28:
        return f"{chinese_chars[:7]}，{chinese_chars[7:14]}。{chinese_chars[14:21]}，{chinese_chars[21:]}。"
    return core


def normalize_poem(value: object) -> str:
    poem = re.sub(r"\s+", "", str(value or "").strip())
    if not poem:
        raise SystemExit("poem is required: provide an original one-line seven-character quatrain wrapped with flower marks.")
    while poem.startswith("🌸"):
        poem = poem[1:]
    while poem.endswith("🌸"):
        poem = poem[:-1]
    if not POEM_ALLOWED_CORE_RE.fullmatch(poem):
        raise SystemExit(
            "poem body may contain only Chinese characters and punctuation; "
            "wrap the poem only with flower marks, no other emoji or decorative symbols."
        )
    chinese_count = len(CJK_RE.findall(poem))
    if chinese_count != 28:
        raise SystemExit(
            "poem must be a one-line seven-character quatrain: "
            f"28 Chinese characters excluding punctuation and flower marks, got {chinese_count}."
        )
    return f"🌸{punctuate_poem(poem)}🌸"


def build_title(payload: dict) -> str:
    title_text = choose_chinese_title(payload)
    title_emoji = infer_title_emoji(payload)
    return normalize_title(title_text, title_emoji)


def render_html(template: str, payload: dict, title: str) -> str:
    signature = payload.get("signature") or DEFAULT_SIGNATURE
    prompt_text = required_text(payload, "English prompt", "prompt_text", "english_prompt", "prompt")
    translation_text = required_text(
        payload,
        "Chinese translation",
        "translation_text",
        "chinese_prompt",
        "translation",
        "chinese_translation",
    )
    replacements = {
        "TITLE": escape_text(title),
        "INTRO_TEXT": escape_text(payload.get("intro_text", "")),
        "PROMPT_TEXT": escape_text(prompt_text),
        "TRANSLATION_TEXT": escape_text(translation_text),
        "BREAKDOWN_ROWS": render_breakdown(payload.get("breakdown_rows")),
        "OPTIMIZATION_NOTES": render_notes(payload.get("optimization_notes")),
        "POEM": escape_text(normalize_poem(payload.get("poem"))),
        "SIGNATURE": escape_text(signature),
    }

    def replace(match: re.Match[str]) -> str:
        return replacements.get(match.group(1), "")

    return PLACEHOLDER_RE.sub(replace, template)


def is_direct_child(path: Path, parent: Path) -> bool:
    try:
        return path.resolve().parent == parent.resolve()
    except OSError:
        return False


def cleanup_input_json_file(input_path: str | None, output_dir: Path) -> list[str]:
    if not input_path:
        return []
    source = Path(input_path)
    if source.suffix.lower() != ".json":
        return []
    if not source.is_file() or not is_direct_child(source, output_dir):
        return []
    deleted = [str(source)]
    source.unlink()
    return deleted


def open_file(path: Path) -> bool:
    if os.name != "nt":
        return False
    try:
        os.startfile(str(path))  # type: ignore[attr-defined]
        return True
    except OSError:
        return False


def main() -> int:
    args = parse_args()
    if args.open_existing:
        target = Path(args.open_existing)
        if not target.exists():
            raise SystemExit(f"HTML file not found: {target}")
        result = {"path": str(target), "opened": open_file(target)}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    payload = read_payload(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    template = Path(args.template).read_text(encoding="utf-8")
    title = build_title(payload)
    filename_title = choose_filename_title(payload, title)
    output_path = unique_path(output_dir, filename_title)
    output_path.write_text(render_html(template, payload, title), encoding="utf-8-sig")
    deleted_json = cleanup_input_json_file(args.input, output_dir)

    result = {"path": str(output_path), "opened": False, "deleted_json": deleted_json}
    if args.open:
        result["opened"] = open_file(output_path)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())