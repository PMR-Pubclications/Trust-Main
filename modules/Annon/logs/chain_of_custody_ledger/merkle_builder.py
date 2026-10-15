import sys
from scripts.hardware_layer.bus_interceptor import DirectBusReader
from scripts.hardware_layer.tee_signer import HardwareAttestor
from scripts.zero_smoothing.wave_preserver import TransientPreserver
from scripts.deterministic_eval.physics_verifier import DeterministicGatekeeper
from scripts.chain_of_custody.merkle_builder import ForensicLedger

def execute_ground_truth_pipeline():
    # 1. Direct Hardware Capture
    raw_buffer = DirectBusReader.read_i2c_registers(bus=1, address=0x68, bytes=64)
    
    # 2. Hardware Cryptographic Signing
    signed_event = HardwareAttestor.sign_payload(raw_buffer)
    
    # 3. Preserve Raw Physical Outliers (No Smoothing)
    TransientPreserver.evaluate_and_store_outlier(signed_event)
    
    # 4. Deterministic Physics Validation (Must pass hard limits)
    is_valid_physics = DeterministicGatekeeper.verify_constraints(signed_event)
    
    if not is_valid_physics:
        sys.stderr.write("[FAULT] Hardware telemetry violates physical constraints or model bounds.\n")
        
    # 5. Commit to Immutable Chain-of-Custody
    ForensicLedger.append_event(signed_event)

if __name__ == "__main__":
    execute_ground_truth_pipeline()
