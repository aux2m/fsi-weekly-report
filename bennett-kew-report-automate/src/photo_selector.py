"""
Photo Selector: Uses Anthropic Vision API to select best 2 photos and generate captions.
"""

import os
import io
import json
import base64
from pathlib import Path
from datetime import date
from PIL import Image
from anthropic import AsyncAnthropic

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

PHOTO_TOOLS = [{
    "name": "photo_scores",
    "description": "Score and caption construction photos",
    "input_schema": {
        "type": "object",
        "properties": {
            "scores": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "relevance": {"type": "number"},
                        "progress_demo": {"type": "number"},
                        "quality": {"type": "number"},
                        "total_score": {"type": "number"},
                        "description": {"type": "string"},
                        "caption": {"type": "string"},
                    },
                    "required": ["index", "relevance", "progress_demo",
                                 "quality", "total_score", "description", "caption"],
                }
            }
        },
        "required": ["scores"],
    }
}]


def _encode_image(path: str, quality: int = 80) -> tuple[str, str]:
    """Read, compress, and base64-encode an image. Returns (data, media_type)."""
    ext = os.path.splitext(path)[1].lower()
    media_types = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png'}
    media_type = media_types.get(ext, 'image/jpeg')

    img = Image.open(path)
    buf = io.BytesIO()
    fmt = 'PNG' if ext == '.png' else 'JPEG'
    img.save(buf, format=fmt, quality=quality, optimize=True)
    data = base64.standard_b64encode(buf.getvalue()).decode('utf-8')
    return data, media_type


async def select_photos(client: AsyncAnthropic,
                        candidate_photos: list[tuple[date, str]],
                        activities_completed: list[str],
                        num_photos: int = 2) -> dict:
    """
    Analyze candidate photos, select best ones, generate captions.
    Returns dict with photos, photo_captions, photo_scores, mismatch_warning.
    """
    if not candidate_photos:
        return {
            "photos": [],
            "photo_captions": [],
            "photo_scores": [],
            "mismatch_warning": "No candidate photos found for this week.",
        }

    # Limit to 4 candidates max to manage API costs (we only pick 2)
    candidates = candidate_photos[:4]
    system = (PROMPTS_DIR / "photo_selection_system.md").read_text(encoding="utf-8")

    # Build message with images and activities context
    content = []
    content.append({
        "type": "text",
        "text": (
            f"This week's completed activities:\n"
            + "\n".join(f"- {a}" for a in activities_completed)
            + f"\n\nPlease analyze these {len(candidates)} candidate photos "
            f"and score each one. The photos are indexed 0 through {len(candidates)-1}."
        )
    })

    for i, (d, path) in enumerate(candidates):
        try:
            data, media_type = _encode_image(path)
            content.append({
                "type": "text",
                "text": f"\n--- Photo {i} (dated {d.isoformat()}, file: {os.path.basename(path)}) ---"
            })
            content.append({
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": data}
            })
        except Exception as e:
            print(f"  Warning: Could not load photo {path}: {e}")

    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system,
        tools=PHOTO_TOOLS,
        tool_choice={"type": "tool", "name": "photo_scores"},
        messages=[{"role": "user", "content": content}],
    )

    scores = []
    for block in response.content:
        if block.type == "tool_use":
            scores = block.input.get("scores", [])

    if not scores:
        # Fallback: use first 2 photos
        selected = candidates[:num_photos]
        return {
            "photos": [p for _, p in selected],
            "photo_captions": ["Construction progress" for _ in selected],
            "photo_scores": [],
            "mismatch_warning": "Photo scoring failed, using most recent photos.",
        }

    # Sort by total score, select top N
    scores.sort(key=lambda s: s.get("total_score", 0), reverse=True)
    selected_scores = scores[:num_photos]

    photos = []
    captions = []
    for s in selected_scores:
        idx = s["index"]
        if idx < len(candidates):
            photos.append(candidates[idx][1])
            captions.append(s["caption"])

    # Mismatch detection
    avg_score = sum(s.get("total_score", 0) for s in selected_scores) / max(len(selected_scores), 1)
    mismatch = None
    if avg_score < 2.5:
        mismatch = (
            f"Low photo match score ({avg_score:.1f}/5.0). "
            f"Available photos may not represent this week's activities well. "
            f"Consider taking new photos showing: "
            + ", ".join(activities_completed[:3])
        )

    return {
        "photos": photos,
        "photo_captions": captions,
        "photo_scores": scores,
        "mismatch_warning": mismatch,
    }
