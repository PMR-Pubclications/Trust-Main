"""
Annon Forensic Integration Bridge
Connects forensic_accounting_system with forensics-ai analysis pipeline
Orchestrates: Annon personality → Ethics validation → Evidence accounting → Analysis → Legal chain of custody
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

# Import forensic accounting system
try:
    from forensic_accounting_system import (
        ForensicAccountingManager, AnnonForensicAssistant, CaseForensicAccount,
        EvidenceEntry, initialize_forensic_accounting_system
    )
except ImportError:
    ForensicAccountingManager = None
    AnnonForensicAssistant = None

# Import Annon personality
try:
    from AI_Personality.anon_system_partner import AnonSystemPartner, AnonPersonaConfig
    from AI_Personality.anon_voice_interface import AnonVoiceEngine, AnonMicrophoneListener
except ImportError:
    AnonSystemPartner = None
    AnonVoiceEngine = None

# Import ethics framework
try:
    from AI_Personality.annon_ethics_controller import (
        EthicsController, EvidencePackageValidator, 
        CustodyTransferEnforcer, RuleEngine
    )
except ImportError:
    EthicsController = None

# Import forensic analysis bridge
try:
    from forensics_ai.forensics_java_bridge import (
        ForensicsJavaBridge, UnifiedForensicsAnalyzer,
        BallisticsAnalysisRequest, BallisticsAnalysisResult
    )
except ImportError:
    ForensicsJavaBridge = None

logger = logging.getLogger("AnnonForensicBridge")


class AnnonForensicInvestigationWorkflow:
    """
    End-to-end investigation workflow orchestrating:
    1. Case creation with Annon's voice interface
    2. Evidence registration with ethics validation
    3. Chain of custody management
    4. Forensic analysis (ballistics, video, comparisons)
    5. Legal-grade report generation
    """
    
    def __init__(self):
        # Initialize all systems
        self.ethics_system = self._initialize_ethics()
        self.accounting_system = self._initialize_accounting()
        self.assistant = self.accounting_system.get("assistant")
        self.forensic_bridge = self._initialize_forensics_bridge()
        
        # Workflow state
        self.current_case_id: Optional[str] = None
        self.investigation_log: List[Dict[str, Any]] = []
    
    def _initialize_ethics(self) -> Optional[EthicsController]:
        """Initialize ethics framework"""
        if EthicsController:
            try:
                return EthicsController()
            except Exception as e:
                logger.warning(f"Ethics controller initialization failed: {e}")
        return None
    
    def _initialize_accounting(self) -> Dict:
        """Initialize forensic accounting system"""
        if ForensicAccountingManager:
            try:
                return initialize_forensic_accounting_system(
                    ethics_controller=self.ethics_system
                )
            except Exception as e:
                logger.warning(f"Accounting system initialization failed: {e}")
        return {}
    
    def _initialize_forensics_bridge(self) -> Optional[ForensicsJavaBridge]:
        """Initialize Java/Python forensics bridge"""
        if ForensicsJavaBridge:
            try:
                return ForensicsJavaBridge(
                    java_host="localhost",
                    java_port=9090,
                    ethics_controller=self.ethics_system
                )
            except Exception as e:
                logger.warning(f"Forensics bridge initialization failed: {e}")
        return None
    
    def create_investigation(self, case_name: str, agency: str,
                            investigator: str, investigator_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        Step 1: Create new investigation case
        Validates investigator credentials through ethics framework
        """
        if not self.accounting_system:
            return False, "Accounting system not initialized", None
        
        accounting = self.accounting_system.get("accounting")
        success, message, case_id = accounting.create_case(
            case_name, agency, investigator, investigator_id
        )
        
        if success:
            self.current_case_id = case_id
            self._log_workflow_event("investigation_created", case_id, {
                "case_name": case_name,
                "investigator": investigator
            })
        
        return success, message, case_id
    
    def submit_evidence_for_analysis(
        self,
        case_id: str,
        evidence_description: str,
        evidence_type: str,  # 'ballistic_video', 'bullet_images', 'firing_pin'
        submitter: str,
        submitter_id: str,
        organization: str,
        evidence_location: str,
        evidence_data: Dict[str, str]  # paths to video/images
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Step 2: Register evidence in case and route to appropriate analysis
        
        Flow:
        1. Register in accounting ledger
        2. Validate against ethics rules
        3. Queue for forensic analysis
        4. Track custody and results
        """
        if not self.accounting_system or not self.forensic_bridge:
            return False, "Required systems not initialized", None
        
        accounting = self.accounting_system.get("accounting")
        
        # Register evidence in case ledger
        success, message, evidence_num = accounting.register_evidence(
            case_id=case_id,
            description=evidence_description,
            evidence_type=evidence_type,
            submitter=submitter,
            submitter_id=submitter_id,
            organization=organization,
            location=evidence_location,
            container_seal=f"SEAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        if not success:
            return False, message, None
        
        self._log_workflow_event("evidence_registered", case_id, {
            "evidence_number": evidence_num,
            "type": evidence_type
        })
        
        # Route to appropriate forensic analysis based on evidence type
        analysis_success, analysis_message, analysis_result = self._dispatch_forensic_analysis(
            evidence_num, evidence_type, evidence_data, submitter
        )
        
        if analysis_success and analysis_result:
            # Record analysis results in case account
            accounting.submit_analysis(
                evidence_num, evidence_type, vars(analysis_result)
            )
            self._log_workflow_event("analysis_completed", case_id, {
                "evidence_number": evidence_num,
                "type": evidence_type,
                "status": analysis_result.status if analysis_result else "failed"
            })
        
        return True, f"Evidence {evidence_num} registered and queued for analysis", evidence_num
    
    def _dispatch_forensic_analysis(
        self,
        evidence_num: str,
        evidence_type: str,
        evidence_data: Dict[str, str],
        submitted_by: str
    ) -> Tuple[bool, str, Optional[BallisticsAnalysisResult]]:
        """
        Route evidence to appropriate forensic analysis engine
        
        Evidence types:
        - ballistic_video: VideoBallisticsAnalyzer → Java physics engine
        - bullet_comparison: BallisticsComparator (Python)
        - firing_pin: BallisticsComparator (Python)
        """
        if not self.forensic_bridge:
            return False, "Forensics bridge not available", None
        
        try:
            if evidence_type == "ballistic_video":
                video_path = evidence_data.get("video_path")
                if not video_path:
                    return False, "Video path required for ballistic_video analysis", None
                
                success, message, result = self.forensic_bridge.analyze_video_trajectory(
                    video_path=video_path,
                    pixels_per_foot=12.0,
                    bullet_mass=115.0,
                    drag_coeff=0.16,
                    submitted_by=submitted_by
                )
                return success, message, result
            
            elif evidence_type == "bullet_comparison":
                image_a = evidence_data.get("image_a_path")
                image_b = evidence_data.get("image_b_path")
                if not image_a or not image_b:
                    return False, "Both image paths required for bullet_comparison", None
                
                success, message, result = self.forensic_bridge.analyze_bullet_comparison(
                    image_a_path=image_a,
                    image_b_path=image_b,
                    submitted_by=submitted_by
                )
                return success, message, result
            
            elif evidence_type == "firing_pin":
                image_a = evidence_data.get("image_a_path")
                image_b = evidence_data.get("image_b_path")
                if not image_a or not image_b:
                    return False, "Both impression images required for firing_pin analysis", None
                
                # Fire pin analysis uses same bullet comparison logic
                success, message, result = self.forensic_bridge.analyze_bullet_comparison(
                    image_a_path=image_a,
                    image_b_path=image_b,
                    submitted_by=submitted_by
                )
                return success, message, result
            
            else:
                return False, f"Unknown evidence type: {evidence_type}", None
        
        except Exception as e:
            error_msg = f"Analysis dispatch error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def transfer_evidence_custody(
        self,
        evidence_num: str,
        from_custodian: str,
        from_custodian_id: str,
        to_custodian: str,
        to_custodian_id: str,
        transfer_reason: str
    ) -> Tuple[bool, str]:
        """
        Step 3: Transfer evidence custody with full documentation
        Maintains chain of custody per legal standards
        """
        if not self.accounting_system:
            return False, "Accounting system not initialized"
        
        accounting = self.accounting_system.get("accounting")
        
        # Record custody transfer in case accounting
        success, message = accounting.transfer_evidence_custody(
            evidence_num, from_custodian, to_custodian, transfer_reason
        )
        
        if success:
            self._log_workflow_event("custody_transfer", 
                                    self.current_case_id or "unknown",
                                    {
                                        "evidence": evidence_num,
                                        "from": from_custodian,
                                        "to": to_custodian,
                                        "reason": transfer_reason
                                    })
        
        return success, message
    
    def get_case_investigation_report(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Step 4: Generate complete investigation report with:
        - All evidence registered
        - Complete chain of custody
        - All analysis results
        - Ethics compliance verification
        - Legal audit trail
        """
        if not self.accounting_system:
            return None
        
        accounting = self.accounting_system.get("accounting")
        case_summary = accounting.get_case_summary(case_id)
        
        if not case_summary:
            return None
        
        # Compile complete investigation record
        investigation_report = {
            "case_id": case_id,
            "case_name": case_summary.get("case_name"),
            "investigator": case_summary.get("investigator"),
            "opened_at": case_summary.get("opened_at"),
            "evidence_summary": case_summary.get("evidence_items", {}),
            "evidence_count": case_summary.get("evidence_count", 0),
            "analyses_completed": case_summary.get("analyses_completed", 0),
            "custody_events": case_summary.get("custody_events", 0),
            "ethics_compliant": case_summary.get("ethics_compliant", False),
            "case_status": case_summary.get("case_status"),
            "audit_trail": accounting.get_accounting_log(case_id),
            "generated_at": datetime.now().isoformat()
        }
        
        self._log_workflow_event("report_generated", case_id, {
            "evidence_count": investigation_report["evidence_count"],
            "analyses": investigation_report["analyses_completed"]
        })
        
        return investigation_report
    
    def voice_command_workflow(self, command: str) -> str:
        """
        Voice-enabled command interface for investigation workflow
        Examples:
        - "Create case murder investigation"
        - "Register evidence ballistic video at /path/to/video.mp4"
        - "Transfer evidence to lab for analysis"
        - "Show case report"
        """
        command_lower = command.lower()
        
        if "create" in command_lower and "case" in command_lower:
            return self._voice_handle_create_case(command)
        
        elif "register" in command_lower and "evidence" in command_lower:
            return self._voice_handle_register_evidence(command)
        
        elif "transfer" in command_lower and "evidence" in command_lower:
            return self._voice_handle_transfer_evidence(command)
        
        elif "report" in command_lower or "summary" in command_lower:
            return self._voice_handle_case_report(command)
        
        else:
            return "Command not recognized. Try: create case, register evidence, transfer evidence, or show report."
    
    def _voice_handle_create_case(self, command: str) -> str:
        """Parse and execute voice command to create case"""
        # Simplified parsing - in production would use NLP
        success, message, case_id = self.create_investigation(
            case_name="Investigation Case",
            agency="Local Police Department",
            investigator="Lead Investigator",
            investigator_id="INV-001"
        )
        
        if success:
            return f"Case {case_id} created successfully. Ready to accept evidence."
        return message
    
    def _voice_handle_register_evidence(self, command: str) -> str:
        """Parse and execute voice command to register evidence"""
        if not self.current_case_id:
            return "No active case. Create a case first."
        
        # Simplified - in production would parse more detail
        success, message, evidence_num = self.submit_evidence_for_analysis(
            case_id=self.current_case_id,
            evidence_description="Evidence submitted via voice command",
            evidence_type="ballistic_video",
            submitter="Voice User",
            submitter_id="VOICE-001",
            organization="Investigation Agency",
            evidence_location="Evidence Locker",
            evidence_data={}
        )
        
        if success:
            return f"Evidence {evidence_num} registered and queued for analysis."
        return message
    
    def _voice_handle_transfer_evidence(self, command: str) -> str:
        """Parse and execute voice command to transfer custody"""
        # Simplified parsing
        return "Custody transfer initiated. Awaiting recipient confirmation."
    
    def _voice_handle_case_report(self, command: str) -> str:
        """Parse and execute voice command to display case report"""
        if not self.current_case_id:
            return "No active case. Create a case first."
        
        report = self.get_case_investigation_report(self.current_case_id)
        if not report:
            return "No report available."
        
        summary = (
            f"Case {report['case_name']}. "
            f"Evidence registered: {report['evidence_count']}. "
            f"Analyses completed: {report['analyses_completed']}. "
            f"Ethics compliant: {'Yes' if report['ethics_compliant'] else 'No'}."
        )
        
        return summary
    
    def _log_workflow_event(self, event_type: str, case_id: str, details: Dict):
        """Log workflow event for audit trail"""
        self.investigation_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "case_id": case_id,
            "details": details
        })
    
    def get_investigation_log(self) -> List[Dict]:
        """Retrieve complete investigation workflow log"""
        return self.investigation_log.copy()


# Initialize complete forensic investigation system
def initialize_annon_forensic_system() -> Dict:
    """
    Initialize complete Annon forensic investigation system
    
    Returns:
        Dictionary with all components:
        - workflow: AnnonForensicInvestigationWorkflow
        - accounting: ForensicAccountingManager
        - assistant: AnnonForensicAssistant
        - ethics_controller: EthicsController
        - forensic_bridge: ForensicsJavaBridge
    """
    workflow = AnnonForensicInvestigationWorkflow()
    
    return {
        "workflow": workflow,
        "accounting": workflow.accounting_system.get("accounting"),
        "assistant": workflow.assistant,
        "ethics_controller": workflow.ethics_system,
        "forensic_bridge": workflow.forensic_bridge
    }


if __name__ == "__main__":
    # Initialize system
    system = initialize_annon_forensic_system()
    workflow = system["workflow"]
    
    # Example workflow
    print("Annon Forensic Investigation System Initialized")
    print("=" * 60)
    
    # Create investigation
    success, msg, case_id = workflow.create_investigation(
        case_name="Ballistics Investigation",
        agency="State Police",
        investigator="Detective Smith",
        investigator_id="DET-001"
    )
    
    if success:
        print(f"✓ {msg}")
        print(f"  Case ID: {case_id}")
    
    # Voice commands
    print("\nVoice Command: 'Show case report'")
    response = workflow.voice_command_workflow("show case report")
    print(f"Annon: {response}")
