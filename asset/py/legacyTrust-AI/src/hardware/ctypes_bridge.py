import ctypes
import os

lib_path = os.path.abspath("libaudiovideoengine.so")
engine_lib = ctypes.CDLL(lib_path)

# Set argument and return types
engine_lib.Engine_Create.restype = ctypes.c_void_p
engine_lib.Engine_Init.argtypes = [ctypes.c_void_p]
engine_lib.Engine_Init.restype = ctypes.c_int

# Usage
engine_ptr = engine_lib.Engine_Create()
status = engine_lib.Engine_Init(engine_ptr)
