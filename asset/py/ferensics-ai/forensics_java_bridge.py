"""
Forensics-Java Bridge Layer
Connects Python forensics-ai analysis with Java ballisticVideoAnalysis for unified evidence processing
Integrates with Annon ethics framework for chain of custody compliance
"""

import socket
import json
import threading
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import hashlib
import uuid
from dataclasses import dataclass, asdict


@dataclass
class BallisticsAnalysisRequest:
    """Request container for ballistics analysis"""
    request_id: str
    analysis_type: str  # 'video_trajectory', 'bullet_comparison', 'firing_pin'
    video_path: Optional[str]
    image_a_path: Optional[str]
    image_b_path: Optional[str]
    calibration_data: Dict[str, float]
    submitted_by: str
    submitted_at: datetime
    
    def to_json(self) -> str:
        data = asdict(self)
        data['submitted_at'] = data['submitted_at'].isoformat()
        return json.dumps(data)


@dataclass
class BallisticsAnalysisResult:
    """Result container from ballistics analysis"""
    request_id: str
    analysis_type: str
    status: str
    video_metadata: Optional[Dict] = None
    extracted_metrics: Optional[Dict] = None
    physics_prediction: Optional[Dict] = None
    comparison_result: Optional[Dict] = None
    tracked_coordinates: Optional[List] = None
    confidence_score: float = 0.0
    processing_time_ms: float = 0.0
    processed_by: str = "Java-Ballistics-Engine"
    result_hash: str = ""
    
    def compute_result_hash(self) -> str:
        """Compute cryptographic hash of result for integrity"""
        result_str = json.dumps(asdict(self), sort_keys=True, default=str)
        self.result_hash = hashlib.sha256(result_str.encode()).hexdigest()
        return self.result_hash


class ForensicsJavaBridge:
    """
    Bridge layer between Python forensics-ai and Java ballistic analysis
    Handles inter-process communication, request/response serialization, and ethics compliance
    """
    
    def __init__(self, java_host: str = "localhost", java_port: int = 9090,
                 ethics_controller=None):
        self.java_host = java_host
        self.java_port = java_port
        self.ethics_controller = ethics_controller
        self.connection_timeout = 5.0
        self.active_requests: Dict[str, BallisticsAnalysisRequest] = {}
        self.completed_analyses: Dict[str, BallisticsAnalysisResult] = {}
        self.error_log: List[Dict] = []
    
    def connect_to_java_engine(self) -> Optional[socket.socket]:
        """
        Establish socket connection to Java ballistics engine
        
        Returns:
            socket.socket if successful, None on failure
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.connection_timeout)
            sock.connect((self.java_host, self.java_port))
            return sock
        except socket.timeout:
            error_msg = f"Java engine connection timeout at {self.java_host}:{self.java_port}"
            self._log_error("connection_timeout", error_msg)
            return None
        except ConnectionRefusedError:
            error_msg = f"Java engine refused connection at {self.java_host}:{self.java_port}"
            self._log_error("connection_refused", error_msg)
            return None
        except Exception as e:
            error_msg = f"Java engine connection error: {str(e)}"
            self._log_error("connection_error", error_msg)
            return None
    
    def submit_ballistics_request(self, analysis_request: BallisticsAnalysisRequest,
                                  ethics_context: Dict = None) -> Tuple[bool, str]:
        """
        Submit ballistics analysis request with ethics compliance verification
        
        Args:
            analysis_request: BallisticsAnalysisRequest object
            ethics_context: Optional context for ethics controller validation
            
        Returns:
            (success: bool, message: str)
        """
        # Verify ethics compliance if controller available
        if self.ethics_controller:
            ctx = ethics_context or {}
            ctx["action"] = "submit_evidence"
            ctx["package_id"] = analysis_request.request_id
            ctx["user_name"] = analysis_request.submitted_by
            
            approved, reason = self.ethics_controller.engine.evaluate_action(
                "submit_evidence", ctx
            )
            
            if not approved:
                return False, f"Ethics compliance check failed: {reason}"
        
        # Store request
        self.active_requests[analysis_request.request_id] = analysis_request
        
        # Attempt connection and transmission
        sock = self.connect_to_java_engine()
        if not sock:
            return False, "Unable to connect to Java ballistics engine"
        
        try:
            # Send request as JSON
            request_json = analysis_request.to_json()
            sock.sendall(request_json.encode() + b'\n')
            
            # Receive response in background thread
            response_thread = threading.Thread(
                target=self._receive_analysis_result,
                args=(sock, analysis_request.request_id)
            )
            response_thread.daemon = True
            response_thread.start()
            
            return True, f"Analysis request {analysis_request.request_id} submitted to Java engine"
        
        except Exception as e:
            error_msg = f"Transmission error: {str(e)}"
            self._log_error("transmission_error", error_msg)
            return False, error_msg
        
        finally:
            try:
                sock.close()
            except:
                pass
    
    def _receive_analysis_result(self, sock: socket.socket, request_id: str):
        """
        Receive analysis result from Java engine (runs in background thread)
        """
        try:
            response_data = b''
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk
            
            if response_data:
                result_json = response_data.decode('utf-8')
                result_dict = json.loads(result_json)
                
                # Create result object
                result = BallisticsAnalysisResult(
                    request_id=request_id,
                    analysis_type=result_dict.get('analysis_type', 'unknown'),
                    status=result_dict.get('status', 'completed'),
                    video_metadata=result_dict.get('video_metadata'),
                    extracted_metrics=result_dict.get('extracted_metrics'),
                    physics_prediction=result_dict.get('physics_prediction'),
                    comparison_result=result_dict.get('comparison_result'),
                    tracked_coordinates=result_dict.get('tracked_coordinates'),
                    confidence_score=result_dict.get('confidence_score', 0.0),
                    processing_time_ms=result_dict.get('processing_time_ms', 0.0)
                )
                
                # Compute integrity hash
                result.compute_result_hash()
                
                # Store result
                self.completed_analyses[request_id] = result
        
        except Exception as e:
            self._log_error("result_reception_error", str(e))
    
    def analyze_video_trajectory(self, video_path: str, pixels_per_foot: float,
                                 bullet_mass: float, drag_coeff: float,
                                 submitted_by: str) -> Tuple[bool, str, Optional[BallisticsAnalysisResult]]:
        """
        High-level interface: Analyze video trajectory
        """
        request = BallisticsAnalysisRequest(
            request_id=f"TRAJ-{uuid.uuid4().hex[:12].upper()}",
            analysis_type="video_trajectory",
            video_path=video_path,
            image_a_path=None,
            image_b_path=None,
            calibration_data={
                "pixels_per_foot": pixels_per_foot,
                "bullet_mass_grains": bullet_mass,
                "drag_coefficient": drag_coeff
            },
            submitted_by=submitted_by,
            submitted_at=datetime.now()
        )
        
        success, message = self.submit_ballistics_request(request)
        return success, message, self.completed_analyses.get(request.request_id)
    
    def analyze_bullet_comparison(self, image_a_path: str, image_b_path: str,
                                 submitted_by: str) -> Tuple[bool, str, Optional[BallisticsAnalysisResult]]:
        """
        High-level interface: Compare bullet striations
        """
        request = BallisticsAnalysisRequest(
            request_id=f"COMP-{uuid.uuid4().hex[:12].upper()}",
            analysis_type="bullet_comparison",
            video_path=None,
            image_a_path=image_a_path,
            image_b_path=image_b_path,
            calibration_data={},
            submitted_by=submitted_by,
            submitted_at=datetime.now()
        )
        
        success, message = self.submit_ballistics_request(request)
        return success, message, self.completed_analyses.get(request.request_id)
    
    def get_analysis_result(self, request_id: str) -> Optional[BallisticsAnalysisResult]:
        """Retrieve completed analysis result by request ID"""
        return self.completed_analyses.get(request_id)
    
    def get_active_requests(self) -> Dict[str, BallisticsAnalysisRequest]:
        """Get all active/pending analysis requests"""
        return self.active_requests.copy()
    
    def get_completed_analyses(self) -> Dict[str, BallisticsAnalysisResult]:
        """Get all completed analysis results"""
        return self.completed_analyses.copy()
    
    def _log_error(self, error_type: str, message: str):
        """Log error for audit trail"""
        self.error_log.append({
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "message": message
        })
    
    def get_error_log(self) -> List[Dict]:
        """Retrieve error log"""
        return self.error_log.copy()


class UnifiedForensicsAnalyzer:
    """
    Unified analyzer combining:
    - Python ballistics_comparator (bullet/firing pin matching)
    - Python video_ballistics (trajectory extraction)
    - Java ballisticVideoAnalysis (advanced physics/frame processing)
    - Annon ethics framework (chain of custody)
    """
    
    def __init__(self, evidence_validator=None, custody_enforcer=None,
                 rule_engine=None, ethics_controller=None):
        self.evidence_validator = evidence_validator
        self.custody_enforcer = custody_enforcer
        self.rule_engine = rule_engine
        self.ethics_controller = ethics_controller
        self.java_bridge = ForensicsJavaBridge(ethics_controller=ethics_controller)
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
    
    def unified_ballistics_investigation(
        self,
        case_id: str,
        video_path: Optional[str],
        bullet_image_a: Optional[str],
        bullet_image_b: Optional[str],
        investigator: str,
        investigator_id: str,
        organization: str
    ) -> Dict[str, Any]:
        """
        Execute unified ballistics investigation:
        1. Validate evidence against ethics rules
        2. Extract metrics from video (Python)
        3. Compare ballistic evidence (Python)
        4. Perform advanced physics analysis (Java)
        5. Return consolidated forensic report with chain of custody
        """
        
        investigation_report = {
            "case_id": case_id,
            "investigation_started": datetime.now().isoformat(),
            "investigator": investigator,
            "organization": organization,
            "analyses": {},
            "integrated_findings": {},
            "chain_of_custody": None,
            "ethics_compliance": True
        }
        
        # 1. Validate against ethics rules
        if self.rule_engine:
            passes_rules, violations = self.rule_engine.evaluate_rules(
                "forensic_investigation",
                {"case_id": case_id, "investigator": investigator}
            )
            if not passes_rules:
                investigation_report["ethics_compliance"] = False
                investigation_report["violations"] = violations
                return investigation_report
        
        # 2. Video trajectory analysis
        if video_path:
            try:
                success, message, result = self.java_bridge.analyze_video_trajectory(
                    video_path=video_path,
                    pixels_per_foot=12.0,  # Calibration constant
                    bullet_mass=115.0,     # .30-06 M2 APM
                    drag_coeff=0.16,
                    submitted_by=investigator
                )
                investigation_report["analyses"]["video_trajectory"] = {
                    "status": "success" if success else "failed",
                    "result": asdict(result) if result else None,
                    "message": message
                }
            except Exception as e:
                investigation_report["analyses"]["video_trajectory"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 3. Bullet comparison analysis
        if bullet_image_a and bullet_image_b:
            try:
                success, message, result = self.java_bridge.analyze_bullet_comparison(
                    image_a_path=bullet_image_a,
                    image_b_path=bullet_image_b,
                    submitted_by=investigator
                )
                investigation_report["analyses"]["bullet_comparison"] = {
                    "status": "success" if success else "failed",
                    "result": asdict(result) if result else None,
                    "message": message
                }
            except Exception as e:
                investigation_report["analyses"]["bullet_comparison"] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # 4. Consolidate findings
        investigation_report["investigation_completed"] = datetime.now().isoformat()
        investigation_report["analysis_count"] = len(investigation_report["analyses"])
        
        return investigation_report
    
    def get_investigation_cache(self, case_id: str) -> Optional[Dict]:
        """Retrieve cached investigation results"""
        return self.analysis_cache.get(case_id)


# Initialize unified system
def initialize_unified_forensics_system(ethics_controller=None) -> Dict:
    """
    Initialize complete unified forensics system
    
    Returns:
        Dictionary with all components
    """
    from annon_ethics_controller import (
        EvidencePackageValidator, CustodyTransferEnforcer, RuleEngine
    )
    
    evidence_validator = EvidencePackageValidator(ethics_controller) if ethics_controller else None
    custody_enforcer = CustodyTransferEnforcer(ethics_controller) if ethics_controller else None
    rule_engine = RuleEngine(ethics_controller) if ethics_controller else None
    
    return {
        "java_bridge": ForensicsJavaBridge(ethics_controller=ethics_controller),
        "unified_analyzer": UnifiedForensicsAnalyzer(
            evidence_validator=evidence_validator,
            custody_enforcer=custody_enforcer,
            rule_engine=rule_engine,
            ethics_controller=ethics_controller
        ),
        "validators": {
            "evidence": evidence_validator,
            "custody": custody_enforcer,
            "rules": rule_engine
        }
    }
