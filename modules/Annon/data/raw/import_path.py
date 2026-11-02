import os
from pathlib import Path

# Define the Annon project directory structure
DIRECTORY_SCHEMATIC = [
    "Annon/data/Raw/images",
    "Annon/data/Raw/texts",
    "Annon/data/Raw/csv",
    "Annon/data/Processed/train",
    "Annon/data/Processed/val",
    "Annon/data/Processed/test",
    "Annon/data/Annotations/labels",
    "Annon/data/Annotations/masks",
    "Annon/config",
    "Annon/scripts/preprocessing",
    "Annon/scripts/models",
    "Annon/scripts/training",
    "Annon/scripts/utils",
    "Annon/scripts/deploy",
    "Annon/notebooks",
    "Annon/models/saved_models",
    "Annon/models/checkpoints",
    "Annon/models/export/onnx",
    "Annon/logs/training_logs",
    "Annon/logs/results/plots",
    "Annon/logs/results/reports"
]

def initialize_annon_repository():
    print("Initializing Annon project file layout...")
    for dir_path in DIRECTORY_SCHEMATIC:
        path = Path(dir_path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Create a placeholder keep file to ensure empty directories track in GitHub
        keep_file = path / ".gitkeep"
        if not keep_file.exists():
            keep_file.write_text("# Placeholder for Annon directory tracking\n")
            
    print("Annon repository structure created successfully.")

if __name__ == "__main__":
    initialize_annon_repository()
