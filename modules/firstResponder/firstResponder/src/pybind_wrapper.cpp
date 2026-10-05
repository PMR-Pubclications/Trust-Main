#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include "flir_boson_wrapper.hpp"

namespace py = pybind11;
using namespace Trust::FirstResponder;

PYBIND11_MODULE(pyboson, m) {
    m.doc() = "Trust FirstResponder C++ AudioVideoEngine FLIR Bindings";

    py::class_<FlirBosonCamera>(m, "FlirBosonCamera")
        .def(py::init<const std::string&>(), py::arg("device_path") = "/dev/video0")
        .def("initialize", &FlirBosonCamera::initialize)
        .def("close", &FlirBosonCamera::close)
        .def("get_next_frame", [](FlirBosonCamera& self) -> py::object {
            ThermalFrame frame;
            if (!self.capture_frame(frame)) {
                return py::none();
            }

            // Return 2D float32 NumPy array (Height x Width)
            std::vector<ssize_t> shape = { static_cast<ssize_t>(frame.height), static_cast<ssize_t>(frame.width) };
            std::vector<ssize_t> strides = { static_cast<ssize_t>(frame.width * sizeof(float)), sizeof(float) };

            return py::array_t<float>(shape, strides, frame.data_celsius.data());
        });
}
