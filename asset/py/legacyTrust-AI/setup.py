from setuptools import setup, find_packages
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "annon.hardware._audio_video_engine",
        [
            "src/cxx/AudioVideoEngine-CPP/src/AudioVideoEngine.cpp",
            "src/cxx/AudioVideoEngine-CPP/src/bindings.cpp",
        ],
        include_dirs=["src/cxx/AudioVideoEngine-CPP/include"],
        cxx_std=17,
    ),
]

setup(
    name="annon-ai",
    version="0.1.0",
    description="Annon / LegacyTrust-AI Standalone Core Engine",
    packages=find_packages(),
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    entry_points={
        "console_scripts": [
            "annon=annon.cli:main",
            "annon-daemon=annon.server.ipc_server:start_server",
        ],
    },
    python_requires=">=3.9",
)
