#!/usr/bin/env python3
import os
import io
import base64
import tempfile
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse

try:
    from PIL import Image as PILImage
except Exception:
    PILImage = None

os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
os.environ.setdefault("GLOG_minloglevel", "2")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

from marker.config.parser import ConfigParser
from marker.models import create_model_dict

app = FastAPI(title="Marker PDF -> JSON API")


def _encode_pil_image_to_base64(img, fmt: Optional[str] = None) -> str:
    """Encode a PIL image to a base64 data URL string."""
    if PILImage is None:
        return str(img)
    if not isinstance(img, PILImage.Image):
        return str(img)
    format_used = (fmt or getattr(img, "format", None) or "PNG").upper()
    buf = io.BytesIO()
    if format_used == "JPEG" and getattr(img, "mode", "").upper() in {"RGBA", "P"}:
        format_used = "PNG"
    img.save(buf, format=format_used)
    data = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"{data}"


def _serialize_images(obj):
    """Recursively serialize image containers into JSON-serializable structures with base64 strings."""
    if PILImage is not None and isinstance(obj, PILImage.Image):
        return _encode_pil_image_to_base64(obj)
    if isinstance(obj, (bytes, bytearray)):
        return base64.b64encode(bytes(obj)).decode("utf-8")
    if isinstance(obj, dict):
        return {k: _serialize_images(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_serialize_images(v) for v in obj]
    try:
        import json
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def convert_pdf_to_markdown_output(
    fpath: str,
    config_kwargs: Optional[Dict[str, Any]] = None,
):
    """Run marker conversion and return the MarkdownOutput object."""
    cfg = dict(config_kwargs or {})
    cfg.setdefault("output_format", "markdown")
    models = create_model_dict()
    config_parser = ConfigParser(cfg)
    converter_cls = config_parser.get_converter_cls()
    converter = converter_cls(
        config=config_parser.generate_config_dict(),
        artifact_dict=models,
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    rendered = converter(fpath)
    return rendered


def build_mistral_like_response(rendered):
    """Build JSON with only markdown and images per page."""
    document = getattr(rendered, "document", None) or getattr(rendered, "doc", None)
    if not document or not hasattr(document, "pages"):
        per_page_markdown = [rendered.markdown]
    else:
        per_page_markdown = []
        for page in document.pages:
            page_render = page.render(document)
            md = getattr(page_render, "markdown", None)
            if not md:
                blocks = page.contained_blocks(document)
                md = "\n".join(getattr(b, "markdown", getattr(b, "text", str(b))) for b in blocks)
            per_page_markdown.append(md)
    images_serialized = _serialize_images(rendered.images)
    content = []
    for i, md in enumerate(per_page_markdown):
        content.append({
            "index": i,
            "markdown": md,
            "images": images_serialized
        })
    response = {"content": content}

    return response


app = FastAPI(title="Marker PDF -> JSON API")


@app.post("/convert-pdf-to-json")
async def convert_pdf(
    file: UploadFile = File(...),
    output_format: str = Query("markdown", description="Renderer output format for marker (e.g., 'markdown')"),
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name
    try:
        rendered = convert_pdf_to_markdown_output(temp_path, {"output_format": output_format})
        response_data = build_mistral_like_response(rendered)
        return JSONResponse(content=response_data)
    finally:
        try:
            os.unlink(temp_path)
        except OSError:
            pass


@app.get("/health")
def health():
    return {"status": "ok"}