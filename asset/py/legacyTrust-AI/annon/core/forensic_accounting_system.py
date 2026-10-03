"""
Forensic Evidence Accounting System
Connects Annon AI-Personality with Forensics-AI for unified evidence tracking and chain of custody

Integrates:
- Annon system partner (diagnostics & health monitoring)
- Annon voice interface (voice-enabled evidence submission)
- Ethics framework (Ten Commandments & Natural Law)
- Forensic analysis (ballistics, video, comparisons)
- Java bridge (unified analysis with physics)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
import uuid
import hashlib
import json

# Import from Annon personality system
try:
    from anon_system_partner import AnonSystemPartner, AnonPersonaConfig
    from anon_voice_interface import AnonVoiceEngine, AnonMicrophoneListener
except ImportError:
    AnonSystemPartner = None
    AnonVoiceEngine = None
    AnonMicrophoneListener = None

# Import from ethics framework
try:
    from annon_ethics_controller import (
        EthicsController, EvidencePackageValidator, 
        CustodyTransferEnforcer, AmendmentOnlyReport, RuleEngine
    )
except ImportError:
    EthicsController = None

# Import from forensics bridge
try:
    from forensics_java_bridge import ForensicsJavaBridge, UnifiedForensicsAnalyzer
except ImportError:
    ForensicsJavaBridge = None


@dataclass
class EvidenceEntry:
    """Single piece of forensic evidence with full accounting"""
    evidence_number: str
    case_id: str
    description: str
    evidence_type: str  # "ballistic_comparison", "video_trajectory", "firing_pin", etc.
    submitter: str
    submitter_id: str
    organization: str
    submitted_at: datetime
    evidence_location: str
    container_seal_number: str
    
    # Chain of custody
    current_custodian: str
    custody_chain: List[Dict] = field(default_factory=list)
    last_custody_change: Optional[datetime] = None
    
    # Analysis results
    analysis_results: Dict[str, Any] = field(default_factory=dict)
    analysis_status: str = "pending"  # pending, in_progress, completed, failed
    
    # Integrity
    content_hash: str = ""
    sealed: bool = False
    
    def compute_content_hash(self) -> str:
        """Compute cryptographic hash of evidence record"""
        evidence_data = {
            "evidence_number": self.evidence_number,
            "case_id": self.case_id,
            "description": self.description,
            "evidence_type": self.evidence_type,
            "submitted_at": self.submitted_at.isoformat(),
            "analysis_results": self.analysis_results
        }
        self.content_hash = hashlib.sha256(
            json.dumps(evidence_data, sort_keys=True, default=str).encode()
        ).hexdigest()
        return self.content_hash


@dataclass
class CaseForensicAccount:
    """Complete forensic accounting for a single case"""
    case_id: str
    case_name: str
    opened_at: datetime
    investigating_agency: str
    investigator: str
    investigator_id: str
    
    # Evidence ledger
    evidence_items: Dict[str, EvidenceEntry] = field(default_factory=dict)
    total_evidence_count: int = 0
    
    # Custody audit trail
    custody_log: List[Dict] = field(default_factory=list)
    
    # Analysis summary
    completed_analyses: Dict[str, Dict] = field(default_factory=dict)
    
    # Report
    findings: List[Dict] = field(default_factory=list)
    case_status: str = "open"  # open, pending_review, closed
    
    # Ethics compliance
    ethics_checks_passed: bool = True
    violations: List[str] = field(default_factory=list)
    
    def add_evidence(self, evidence: EvidenceEntry) -> Tuple[bool, str]:
        """Add evidence to case with validation"""
        if evidence.evidence_number in self.evidence_items:
            return False, f"Evidence {evidence.evidence_number} already in case"
        
        evidence.compute_content_hash()
        self.evidence_items[evidence.evidence_number] = evidence
        self.total_evidence_count += 1
        
        return True, f"Evidence {evidence.evidence_number} added to case {self.case_id}"
    
    def record_custody_action(self, evidence_number: str, action: str, 
                            from_custodian: str, to_custodian: str,
                            notes: str = "") -> Tuple[bool, str]:
        """Record custody change in audit log"""
        if evidence_number not in self.evidence_items:
            return False, f"Evidence {evidence_number} not found in case"
        
        self.custody_log.append({
            "timestamp": datetime.now().isoformat(),
            "evidence_number": evidence_number,
            "action": action,
            "from": from_custodian,
            "to": to_custodian,
            "notes": notes
        })
        
        evidence = self.evidence_items[evidence_number]
        evidence.current_custodian = to_custodian
        evidence.last_custody_change = datetime.now()
        
        return True, f"Custody action recorded for {evidence_number}"
    
    def record_analysis(self, evidence_number: str, analysis_type: str,
                       analysis_result: Dict) -> Tuple[bool, str]:
        """Record forensic analysis results"""
        if evidence_number not in self.evidence_items:
            return False, f"Evidence {evidence_number} not found"
        
        evidence = self.evidence_items[evidence_number]
        evidence.analysis_results[analysis_type] = analysis_result
        evidence.analysis_status = "completed"
        
        self.completed_analyses[evidence_number] = {
            "type": analysis_type,
            "result": analysis_result,
            "timestamp": datetime.now().isoformat()
        }
        
        return True, f"Analysis recorded for {evidence_number}"


class ForensicAccountingManager:
    """
    Central accounting system for forensic investigations
    Maintains single-entry ledger with chain of custody
    Enforces ethics compliance via rule engine
    """
    
    def __init__(self, ethics_controller=None):
        self.ethics_controller = ethics_controller
        self.active_cases: Dict[str, CaseForensicAccount] = {}
        self.closed_cases: Dict[str, CaseForensicAccount] = {}
        self.evidence_index: Dict[str, str] = {}  # evidence_number -> case_id
        self.accounting_log: List[Dict] = []
        self.next_evidence_number = 1
    
    def create_case(self, case_name: str, investigating_agency: str,
                   investigator: str, investigator_id: str) -> Tuple[bool, str, Optional[str]]:
        """Create new case with ethics validation"""
        case_id = f"CASE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        if self.ethics_controller:
            # Validate investigator credentials through ethics framework
            approved, reason = self.ethics_controller.engine.evaluate_action(
                "submit_evidence",
                {
                    "user_name": investigator,
                    "user_id": investigator_id,
                    "organization": investigating_agency
                }
            )
            if not approved:
                return False, f"Investigator validation failed: {reason}", None
        
        case = CaseForensicAccount(
            case_id=case_id,
            case_name=case_name,
            opened_at=datetime.now(),
            investigating_agency=investigating_agency,
            investigator=investigator,
            investigator_id=investigator_id
        )
        
        self.active_cases[case_id] = case
        self._log_accounting_event("case_created", case_id, {"case_name": case_name})
        
        return True, f"Case {case_id} created", case_id
    
    def register_evidence(self, case_id: str, description: str, evidence_type: str,
                         submitter: str, submitter_id: str, organization: str,
                         location: str, container_seal: str) -> Tuple[bool, str, Optional[str]]:
        """Register evidence in case"""
        if case_id not in self.active_cases:
            return False, f"Case {case_id} not found", None
        
        evidence_number = f"EVD-{datetime.now().strftime('%Y%m%d')}-{self.next_evidence_number:06d}"
        self.next_evidence_number += 1
        
        evidence = EvidenceEntry(
            evidence_number=evidence_number,
            case_id=case_id,
            description=description,
            evidence_type=evidence_type,
            submitter=submitter,
            submitter_id=submitter_id,
            organization=organization,
            submitted_at=datetime.now(),
            evidence_location=location,
            container_seal_number=container_seal,
            current_custodian=submitter,
            custody_chain=[{
                "custodian": submitter,
                "timestamp": datetime.now().isoformat(),
                "action": "initial_receipt"
            }]
        )
        
        case = self.active_cases[case_id]
        success, msg = case.add_evidence(evidence)
        
        if success:
            self.evidence_index[evidence_number] = case_id
            self._log_accounting_event("evidence_registered", case_id, 
                                      {"evidence_number": evidence_number, "type": evidence_type})
        
        return success, msg, evidence_number if success else None
    
    def transfer_evidence_custody(self, evidence_number: str, from_custodian: str,
                                 to_custodian: str, notes: str = "") -> Tuple[bool, str]:
        """Transfer custody with full documentation"""
        if evidence_number not in self.evidence_index:
            return False, f"Evidence {evidence_number} not found"
        
        case_id = self.evidence_index[evidence_number]
        case = self.active_cases[case_id]
        
        success, msg = case.record_custody_action(
            evidence_number, "transfer", from_custodian, to_custodian, notes
        )
        
        if success:
            self._log_accounting_event("custody_transfer", case_id,
                                      {"evidence": evidence_number, 
                                       "from": from_custodian, "to": to_custodian})
        
        return success, msg
    
    def submit_analysis(self, evidence_number: str, analysis_type: str,
                       analysis_result: Dict) -> Tuple[bool, str]:
        """Record forensic analysis"""
        if evidence_number not in self.evidence_index:
            return False, f"Evidence {evidence_number} not found"
        
        case_id = self.evidence_index[evidence_number]
        case = self.active_cases[case_id]
        
        success, msg = case.record_analysis(evidence_number, analysis_type, analysis_result)
        
        if success:
            self._log_accounting_event("analysis_recorded", case_id,
                                      {"evidence": evidence_number, "type": analysis_type})
        
        return success, msg
    
    def get_case_summary(self, case_id: str) -> Optional[Dict]:
        """Get complete case accounting summary"""
        case = self.active_cases.get(case_id)
        if not case:
            return None
        
        return {
            "case_id": case_id,
            "case_name": case.case_name,
            "investigator": case.investigator,
            "opened_at": case.opened_at.isoformat(),
            "evidence_count": case.total_evidence_count,
            "evidence_items": {
                evid_num: {
                    "description": ev.description,
                    "type": ev.evidence_type,
                    "custodian": ev.current_custodian,
                    "analysis_status": ev.analysis_status,
                    "hash": ev.content_hash
                }
                for evid_num, ev in case.evidence_items.items()
            },
            "custody_events": len(case.custody_log),
            "analyses_completed": len(case.completed_analyses),
            "ethics_compliant": case.ethics_checks_passed,
            "case_status": case.case_status
        }
    
    def get_evidence_chain_of_custody(self, evidence_number: str) -> Optional[List[Dict]]:
        """Get complete chain of custody for evidence"""
        if evidence_number not in self.evidence_index:
            return None
        
        case_id = self.evidence_index[evidence_number]
        case = self.active_cases[case_id]
        evidence = case.evidence_items.get(evidence_number)
        
        if not evidence:
            return None
        
        return evidence.custody_chain
    
    def _log_accounting_event(self, event_type: str, case_id: str, details: Dict):
        """Log accounting event for audit trail"""
        self.accounting_log.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "case_id": case_id,
            "details": details
        })
    
    def get_accounting_log(self, case_id: Optional[str] = None) -> List[Dict]:
        """Retrieve accounting log, optionally filtered by case"""
        if case_id:
            return [e for e in self.accounting_log if e["case_id"] == case_id]
        return self.accounting_log.copy()


class AnnonForensicAssistant:
    """
    Combines Annon's voice personality with forensic accounting
    Provides voice-enabled evidence submission and case management
    """
    
    def __init__(self, accounting_manager: ForensicAccountingManager = None,
                 ethics_controller: EthicsController = None):
        self.accounting = accounting_manager or ForensicAccountingManager(ethics_controller)
        self.ethics_controller = ethics_controller
        
        # Initialize Annon persona if available
        if AnonSystemPartner:
            self.anon = AnonSystemPartner(config=AnonPersonaConfig(
                name="Anon",
                tagline="Evidence doesn't lie. Let's count it straight."
            ))
        else:
            self.anon = None
        
        # Initialize voice interface if available
        if AnonVoiceEngine:
            self.voice = AnonVoiceEngine()
        else:
            self.voice = None
    
    def voice_create_case(self, case_name: str, agency: str,
                         investigator: str, investigator_id: str) -> str:
        """Voice command: Create new investigation case"""
        success, message, case_id = self.accounting.create_case(
            case_name, agency, investigator, investigator_id
        )
        
        response = f"Case created: {case_id}." if success else f"Failed: {message}"
        
        if self.voice:
            self.voice.speak(response)
        
        return case_id if success else ""
    
    def voice_register_evidence(self, case_id: str, description: str,
                               evidence_type: str, submitter: str,
                               submitter_id: str, organization: str,
                               location: str, seal: str) -> str:
        """Voice command: Register evidence"""
        success, message, evidence_num = self.accounting.register_evidence(
            case_id, description, evidence_type, submitter, 
            submitter_id, organization, location, seal
        )
        
        response = f"Evidence registered: {evidence_num}." if success else f"Failed: {message}"
        
        if self.voice:
            self.voice.speak(response)
        
        return evidence_num if success else ""
    
    def voice_transfer_evidence(self, evidence_number: str, to_custodian: str,
                               from_custodian: str, notes: str = "") -> bool:
        """Voice command: Transfer custody"""
        success, message = self.accounting.transfer_evidence_custody(
            evidence_number, from_custodian, to_custodian, notes
        )
        
        if self.voice:
            self.voice.speak(message)
        
        return success
    
    def speak_case_summary(self, case_id: str):
        """Voice output: Speak complete case summary"""
        summary = self.accounting.get_case_summary(case_id)
        
        if not summary:
            if self.voice:
                self.voice.speak(f"Case {case_id} not found.")
            return
        
        summary_text = (
            f"Case {summary['case_name']}. "
            f"Investigator: {summary['investigator']}. "
            f"Evidence registered: {summary['evidence_count']} items. "
            f"Analyses completed: {summary['analyses_completed']}. "
            f"Ethics compliant: {'Yes' if summary['ethics_compliant'] else 'No'}."
        )
        
        if self.voice:
            self.voice.speak(summary_text)
        else:
            print(summary_text)


# Initialize complete forensic accounting system
def initialize_forensic_accounting_system(ethics_controller=None) -> Dict:
    """
    Initialize complete forensic accounting system with Annon integration
    
    Returns:
        Dictionary with all components ready for use
    """
    if ethics_controller is None and EthicsController:
        from annon_ethics_controller import initialize_annon_ethics_system
        sys = initialize_annon_ethics_system()
        ethics_controller = sys["controller"]
    
    accounting = ForensicAccountingManager(ethics_controller)
    assistant = AnnonForensicAssistant(accounting, ethics_controller)
    
    return {
        "accounting": accounting,
        "assistant": assistant,
        "ethics_controller": ethics_controller
    }
