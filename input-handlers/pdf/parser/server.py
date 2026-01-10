import os
import tempfile
from pathlib import Path
from typing import Optional
import shutil

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from tree_parser.tree import Tree
from tree_parser.treeparser import TreeParser

# Environment variables with defaults
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
VLLM_URL = os.getenv("VLLM_URL", "")
FORCE_OCR = os.getenv("FORCE_OCR", "false").lower() == "true"
EXTRACT_IMAGE = os.getenv("EXTRACT_IMAGE", "false").lower() == "true"
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "/tmp/parser-output")

# Validate configuration
if USE_LLM and not VLLM_URL:
    raise ValueError("VLLM_URL is required when USE_LLM is enabled")

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(
    title="PDF Parser API",
    description="FastAPI server for parsing PDFs using Marker",
    version="1.0.0"
)


def create_converter():
    """Create a PDF converter with the configured settings"""
    config = {
        "output_format": "markdown",
        "force_ocr": FORCE_OCR,
        "disable_image_extraction": not EXTRACT_IMAGE,
        "output_dir": OUTPUT_DIR,
    }
    
    if USE_LLM:
        config["use_llm"] = True
        config["llm_service"] = "marker.services.openai.OpenAIService"
        config["openai_base_url"] = VLLM_URL
        # OpenAI API key can be any non-empty string when using vLLM
        if not os.getenv("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = "dummy-key-for-vllm"
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY")
    
    config_parser = ConfigParser(config)
    
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    
    print("Created PDF Converter with config:", config)
    
    return converter, config_parser


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "PDF Parser API",
        "configuration": {
            "use_llm": USE_LLM,
            "vllm_url": VLLM_URL if USE_LLM else None,
            "force_ocr": FORCE_OCR,
            "extract_images": EXTRACT_IMAGE,
            "output_dir": OUTPUT_DIR
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/parse")
async def parse_pdf(
    file: UploadFile = File(..., description="PDF file to parse"),
    user: str = Form(..., description="Username for organizing outputs")
):
    """
    Parse a PDF file and return the results
    
    - **file**: PDF file to parse
    - **user**: Username for organizing outputs
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    user_dir = os.path.join(OUTPUT_DIR, user)
    pdf_base_name = os.path.splitext(file.filename)[0]
    pdf_dir = os.path.join(user_dir, pdf_base_name)
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, file.filename)
    
    try:
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        converter, config_parser = create_converter()
    
        tree = Tree(pdf_path, user_param=user, output_dir=OUTPUT_DIR)
        tree_parser = TreeParser(user, output_dir=OUTPUT_DIR)
        tree_parser.populate_tree(tree, converter)
        
        # Generate both JSON and text outputs
        json_output_path = tree_parser.generate_output_json(tree)
        text_output_path = tree_parser.generate_output_text(tree)
        
        if not json_output_path or not os.path.exists(json_output_path):
            raise HTTPException(status_code=500, detail="Failed to generate JSON output")
        
        if not text_output_path or not os.path.exists(text_output_path):
            raise HTTPException(status_code=500, detail="Failed to generate text output")
        
        response_data = {
            "status": "success",
            "filename": file.filename,
            "user": user,
            "output_directory": pdf_dir,
            "pdf_path": pdf_path,
            "json_output_path": json_output_path,
            "text_output_path": text_output_path
        }
        
        return JSONResponse(content=response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing PDF: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting PDF Parser API on {host}:{port}")
    print(f"Configuration:")
    print(f"  USE_LLM: {USE_LLM}")
    print(f"  VLLM_URL: {VLLM_URL if USE_LLM else 'N/A'}")
    print(f"  FORCE_OCR: {FORCE_OCR}")
    print(f"  EXTRACT_IMAGE: {EXTRACT_IMAGE}")
    print(f"  OUTPUT_DIR: {OUTPUT_DIR}")
    
    uvicorn.run(app, host=host, port=port)
