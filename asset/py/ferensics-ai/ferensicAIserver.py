import tempfile
from video_ballistics import VideoBallisticsAnalyzer

# Initialize video analyzer instance
video_analyzer = VideoBallisticsAnalyzer()


@app.post("/api/v1/vision/video-trajectory", tags=["Computer Vision & Video"])
async def analyze_video_trajectory(
    file: UploadFile = File(...),
    pixels_per_foot: Optional[float] = Form(None, description="Optional calibration scale: pixels per foot"),
    bullet_mass_grains: float = Form(115.0, description="Bullet mass in grains (default: 115gr 9mm)"),
    drag_coefficient: float = Form(0.16, description="Ballistic drag coefficient"),
    cross_sectional_area_sq_in: float = Form(0.09, description="Cross sectional area in sq in")
):
    """
    Receives video file upload, runs frame-by-frame trajectory tracking, 
    extracts launching vector/angle, and predicts complete ballistic flight path.
    """
    if not file.filename.endswith(('.mp4', '.avi', '.mov', '.mkv')):
        raise HTTPException(
            status_code=400, 
            detail="Invalid video format. Upload .mp4, .avi, .mov, or .mkv"
        )

    try:
        # Save uploaded video stream to a temporary disk location
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # Execute video frame processing and trajectory analysis
        analysis_result = video_analyzer.analyze_trajectory_video(
            video_path=tmp_path,
            pixels_per_foot=pixels_per_foot,
            bullet_mass_grains=bullet_mass_grains,
            drag_coefficient=drag_coefficient,
            cross_area_sq_in=cross_sectional_area_sq_in
        )

        # Cleanup temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        return {
            "filename": file.filename,
            "analysis": analysis_result
        }

    except Exception as e:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
