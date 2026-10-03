import os
import cv2
import numpy as np
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import our previously constructed modules
from forensic_physics import ForensicPhysicsEngine
from forensic_rag_lancedb import ForensicVectorStore
from fingerprint_extractor import FingerprintMinutiaeExtractor
from ballistics_comparator import BallisticsComparator

# Initialize FastAPI App
app = FastAPI(
    title="Lightweight Forensic AI Engine",
    description="Microservice API for forensic physics, ballistics, minutiae CV, and standard retrieval.",
    version="1.0.0"
)

# Enable CORS for frontend/client integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances of vector store & CV extractors
vector_store = None
fingerprint_extractor = None


@app.on_event("startup")
async def startup_event():
    global vector_store, fingerprint_extractor
    print("[INIT] Booting lightweight forensic services...")
    vector_store = ForensicVectorStore(db_path="./forensic_lancedb")
    fingerprint_extractor = FingerprintMinutiaeExtractor(device="cpu")
    print("[INIT] All forensic microservices ready.")


# =============================================================================
# 1. PYDANTIC REQUEST & RESPONSE SCHEMAS
# =============================================================================

class ChatRequest(BaseModel):
    prompt: str = Field(..., example="A 9mm bullet (115 gr, drag 0.16) was fired at 1150 fps. What is its drop?")

class BallisticRequest(BaseModel):
    velocity_fps: float = Field(..., example=1150.0)
    angle_degrees: float = Field(..., example=5.0)
    bullet_mass_grains: float = Field(..., example=115.0)
    drag_coefficient: float = Field(..., example=0.16)
    cross_sectional_area_sq_in: float = Field(..., example=0.09)

class FlashoverRequest(BaseModel):
    room_length_m: float = Field(..., example=5.0)
    room_width_m: float = Field(..., example=4.0)
    vent_width_m: float = Field(..., example=1.0)
    vent_height_m: float = Field(..., example=2.0)

class BucklingRequest(BaseModel):
    elastic_modulus_psi: float = Field(..., example=29000000.0)
    moment_of_inertia_in4: float = Field(..., example=15.0)
    length_inches: float = Field(..., example=120.0)
    effective_length_factor_k: float = Field(default=1.0, example=1.0)

class RAGQueryRequest(BaseModel):
    query: str = Field(..., example="What are the level 2 friction ridge detail definitions?")
    top_k: int = Field(default=3, ge=1, le=10)
    filter_standard: Optional[str] = Field(default=None, example="NFPA 921")


# =============================================================================
# 2. DETERMINISTIC PHYSICS ENDPOINTS
# =============================================================================

@app.post("/api/v1/physics/ballistics", tags=["Physics Engine"])
async def calculate_ballistics(req: BallisticRequest):
    try:
        return ForensicPhysicsEngine.calculate_ballistic_trajectory(
            velocity_fps=req.velocity_fps,
            angle_degrees=req.angle_degrees,
            bullet_mass_grains=req.bullet_mass_grains,
            drag_coefficient=req.drag_coefficient,
            cross_sectional_area_sq_in=req.cross_sectional_area_sq_in
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/physics/flashover", tags=["Physics Engine"])
async def calculate_flashover(req: FlashoverRequest):
    try:
        return ForensicPhysicsEngine.calculate_compartment_flashover(
            room_length_m=req.room_length_m,
            room_width_m=req.room_width_m,
            vent_width_m=req.vent_width_m,
            vent_height_m=req.vent_height_m
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/physics/buckling", tags=["Physics Engine"])
async def calculate_buckling(req: BucklingRequest):
    try:
        return ForensicPhysicsEngine.calculate_column_buckling(
            elastic_modulus_psi=req.elastic_modulus_psi,
            moment_of_inertia_in4=req.moment_of_inertia_in4,
            length_inches=req.length_inches,
            effective_length_factor_k=req.effective_length_factor_k
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 3. LANCEDB FORENSIC RAG RETRIEVAL ENDPOINT
# =============================================================================

@app.post("/api/v1/rag/search", tags=["RAG Standards Search"])
async def search_standards(req: RAGQueryRequest):
    if not vector_store:
        raise HTTPException(status_code=503, detail="Vector store service not initialized.")
    try:
        results = vector_store.search_hybrid(
            query=req.query,
            top_k=req.top_k,
            filter_standard=req.filter_standard
        )
        return {"query": req.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 4. COMPUTER VISION & BALLISTICS ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/api/v1/vision/fingerprint-minutiae", tags=["Computer Vision"])
async def extract_fingerprint_minutiae(file: UploadFile = File(...)):
    """Uploads a fingerprint image and returns Level-2 minutiae coordinates."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)

        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image file upload.")

        # Process image using minutiae pipeline
        binary_mask = (img > 128).astype(np.uint8)
        skeleton = fingerprint_extractor._morphological_thinning_fallback(binary_mask)
        minutiae = fingerprint_extractor.extract_minutiae(skeleton)

        return {
            "filename": file.filename,
            "termination_count": len(minutiae["terminations"]),
            "bifurcation_count": len(minutiae["bifurcations"]),
            "minutiae": minutiae
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/vision/compare-striations", tags=["Computer Vision"])
async def compare_bullet_striations(
    file_a: UploadFile = File(...), 
    file_b: UploadFile = File(...)
):
    """Compares two bullet land engraved area (LEA) images using CCFr algorithm."""
    try:
        bytes_a = await file_a.read()
        bytes_b = await file_b.read()
        
        img_a = cv2.imdecode(np.frombuffer(bytes_a, np.uint8), cv2.IMREAD_GRAYSCALE)
        img_b = cv2.imdecode(np.frombuffer(bytes_b, np.uint8), cv2.IMREAD_GRAYSCALE)

        if img_a is None or img_b is None:
            raise HTTPException(status_code=400, detail="Invalid image pair upload.")

        comparison_result = BallisticsComparator.compare_bullet_striations(img_a, img_b)
        return {
            "file_a": file_a.filename,
            "file_b": file_b.filename,
            "metrics": comparison_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 5. HEALTH CHECK & ROOT
# =============================================================================

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "online", "vram_allocated_mb": 0.0, "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
