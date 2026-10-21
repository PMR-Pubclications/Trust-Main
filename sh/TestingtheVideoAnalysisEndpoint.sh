curl -X 'POST' \
  'http://localhost:8000/api/v1/vision/video-trajectory' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample_ballistic_video.mp4;type=video/mp4' \
  -F 'pixels_per_foot=45.5' \
  -F 'bullet_mass_grains=115'
