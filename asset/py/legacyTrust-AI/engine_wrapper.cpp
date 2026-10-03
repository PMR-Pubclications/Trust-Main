#include <pybind11/pybind11.h>
#include "AudioVideoEngine.h" // Your C++ hardware header

namespace py = pybind11;

PYBIND11_MODULE(audio_video_engine, m) {
    m.doc() = "C++ Audio/Video Hardware Engine Binding";

    py::class_<AudioVideoEngine>(m, "HardwareController")
        .def(py::init<>())
        .def("initialize_hardware", &AudioVideoEngine::initializeHardware)
        .def("start_capture", &AudioVideoEngine::startCapture)
        .def("stop_capture", &AudioVideoEngine::stopCapture);
}
