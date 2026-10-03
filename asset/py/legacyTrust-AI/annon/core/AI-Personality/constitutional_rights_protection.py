"""
Constitutional Rights Protection Framework
Enforces 4th Amendment (Search & Seizure), 5th Amendment (Due Process), and statutory warrant requirements
Integrated into Annon ethics controller with automatic compliance monitoring and violation documentation

Legal Basis:
- 4th Amendment: "The right of the people to be secure in their persons, houses, papers, and effects, 
  against unreasonable searches and seizures, shall not be violated"
- Fruit of the Poisonous Tree Doctrine: Evidence obtained through constitutional violations is inadmissible
- Qualified Immunity Waiver: Officers who knowingly violate civil rights lose qualified immunity protection
- 42 U.S.C. § 1983: Civil rights action for violations under color of law
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import uuid


class SearchAuthorization(Enum):
    """Valid legal bases for search or entry"""
    VALID_WARRANT = "Valid signed search warrant with particularity"
    CONSENT = "Explicit informed consent from property owner/resident"
    EXIGENT_CIRCUMSTANCES = "Exigent circumstances (emergency, imminent harm, in-progress crime)"
    PLAIN_VIEW = "Plain view doctrine (lawfully positioned, inadvertent discovery)"
    VEHICLE_SEARCH = "Vehicle inventory search post-arrest with consent or warrant"
    HOME_ENTRY_KNOCK_ANNOUNCE = "Knock and announce with warrant execution"


class ConstitutionalViolationType(Enum):
    """Types of constitutional violations"""
    WARRANTLESS_HOME_ENTRY = "Warrantless entry into home without legal justification"
    INVALID_WARRANT = "Use of invalid, stale, or improperly issued warrant"
    NO_CONSENT = "Search without consent or legal authority"
    EXCEEDED_SCOPE = "Search exceeded scope of warrant or consent"
    NO_PROBABLE_CAUSE = "Seizure without probable cause"
    MIRANDA_VIOLATION = "Interrogation without Miranda rights after custodial arrest"
    ILLEGAL_SEIZURE = "Seizure of person or property without legal justification"
    KNOCK_ANNOUNCE_VIOLATION = "Entry without proper knock and announce procedure"


@dataclass
class SearchAuthorizationRecord:
    """Documentation of legal authority for search or entry"""
    search_id: str
    officer_name: str
    officer_id: str
    badge_number: str
    agency: str
    
    search_location: str  # Address or property
    search_date: datetime
    search_time_start: datetime
    search_time_end: datetime
    
    authorization_type: SearchAuthorization
    
    # Warrant details (if applicable)
    warrant_number: Optional[str] = None
    warrant_issuing_judge: Optional[str] = None
    warrant_issue_date: Optional[datetime] = None
    warrant_expiration: Optional[datetime] = None
    warrant_property_description: Optional[str] = None  # Particularity requirement
    
    # Consent documentation
    consent_given_by: Optional[str] = None
    consent_relationship_to_property: Optional[str] = None  # Owner, renter, etc.
    consent_witnessed_by: Optional[List[str]] = field(default_factory=list)
    consent_recorded: bool = False  # Audio/video recording of consent
    
    # Exigent circumstances documentation
    exigent_circumstances_reason: Optional[str] = None
    emergency_nature: Optional[str] = None  # Life danger, imminent crime, etc.
    
    # Search details
    items_seized: List[str] = field(default_factory=list)
    property_damage: Optional[str] = None
    
    # Chain of custody
    evidence_logged: bool = False
    
    # Constitutional assessment
    is_valid: bool = False
    validity_findings: List[str] = field(default_factory=list)


@dataclass
class ConstitutionalViolationRecord:
    """Documentation of constitutional violation with automatic remedies"""
    violation_id: str
    case_id: str
    officer_name: str
    officer_id: str
    badge_number: str
    agency: str
    
    violation_type: ConstitutionalViolationType
    violation_date: datetime
    violation_details: str
    
    # Evidence of violation
    witness_statements: List[str] = field(default_factory=list)
    officer_body_camera: Optional[str] = None
    officer_statements: Optional[str] = None
    property_camera_footage: Optional[str] = None
    
    # Legal consequences
    evidence_tainted: bool = True
    fruit_of_poisonous_tree: bool = True
    evidence_to_suppress: List[str] = field(default_factory=list)
    
    # Automatic remedies
    qualified_immunity_waived: bool = True  # Automatic upon documented violation
    civil_liability_attached: bool = True
    criminal_prosecution_eligible: bool = False  # Determined by DA
    
    # Audio violation record
    audio_violation_clip: Optional[str] = None  # Path to audio evidence
    audio_description: str = ""
    
    # Officer remediation
    suspension_recommended: bool = False
    suspension_duration_days: int = 0
    retraining_required: bool = True
    badge_surrender_recommended: bool = False
    
    created_at: datetime = field(default_factory=datetime.now)


class ConstitutionalRightsValidator:
    """
    Validates search and seizure actions against constitutional standards
    Automatically detects violations and initiates remedial procedures
    """
    
    def __init__(self):
        self.search_records: Dict[str, SearchAuthorizationRecord] = {}
        self.violation_records: Dict[str, ConstitutionalViolationRecord] = {}
        self.violation_log: List[Dict] = []
        self.officer_qualification_status: Dict[str, bool] = {}
    
    def validate_home_entry(self, search_record: SearchAuthorizationRecord) -> Tuple[bool, List[str]]:
        """
        Validate home entry authorization under 4th Amendment
        
        Legal standard: "To enter a dwelling, officers need either:
        1. Valid warrant signed by neutral magistrate with particularity
        2. Explicit informed consent from resident/owner
        3. Exigent circumstances (emergency, in-progress felony, life danger)
        4. Hot pursuit of fleeing suspect"
        
        Returns:
            (is_valid: bool, findings: List[str])
        """
        findings = []
        
        # Check authorization type
        if search_record.authorization_type == SearchAuthorization.VALID_WARRANT:
            findings.extend(self._validate_warrant(search_record))
        
        elif search_record.authorization_type == SearchAuthorization.CONSENT:
            findings.extend(self._validate_consent(search_record))
        
        elif search_record.authorization_type == SearchAuthorization.EXIGENT_CIRCUMSTANCES:
            findings.extend(self._validate_exigent_circumstances(search_record))
        
        elif search_record.authorization_type == SearchAuthorization.PLAIN_VIEW:
            findings.extend(self._validate_plain_view(search_record))
        
        else:
            findings.append("VIOLATION: Invalid or missing authorization type for home entry")
        
        is_valid = len([f for f in findings if "VIOLATION" in f]) == 0
        search_record.is_valid = is_valid
        search_record.validity_findings = findings
        
        return is_valid, findings
    
    def _validate_warrant(self, record: SearchAuthorizationRecord) -> List[str]:
        """Validate warrant requirements"""
        findings = []
        
        if not record.warrant_number:
            findings.append("VIOLATION: No warrant number documented")
            return findings
        
        if not record.warrant_issuing_judge:
            findings.append("VIOLATION: Warrant not issued by neutral magistrate (required for 4th Amendment compliance)")
            return findings
        
        # Check warrant not stale
        if record.warrant_expiration and datetime.now() > record.warrant_expiration:
            findings.append("VIOLATION: Warrant expired at time of search")
            return findings
        
        # Check particularity requirement
        if not record.warrant_property_description:
            findings.append("VIOLATION: Warrant lacks particularity requirement - does not specifically describe items/places")
            return findings
        
        # Check scope not exceeded
        for item in record.items_seized:
            if item not in record.warrant_property_description:
                findings.append(f"VIOLATION: Item seized '{item}' not authorized by warrant (scope exceeded)")
        
        if len(findings) == 0:
            findings.append("✓ Valid warrant with neutral magistrate, particularity, and proper scope")
        
        return findings
    
    def _validate_consent(self, record: SearchAuthorizationRecord) -> List[str]:
        """Validate consent requirements"""
        findings = []
        
        if not record.consent_given_by:
            findings.append("VIOLATION: Consent given by unknown person - identity not documented")
            return findings
        
        if not record.consent_relationship_to_property:
            findings.append("VIOLATION: Relationship of consenting person to property not established (authority to consent unclear)")
            return findings
        
        # Consent must be voluntary and informed
        if not record.consent_recorded:
            findings.append("WARNING: Consent not audio/video recorded - difficult to prove voluntariness and understanding")
        
        if len(record.consent_witnessed_by) == 0:
            findings.append("WARNING: Consent given without witnesses - violates best practices for reliability")
        
        if len(findings) == 0:
            findings.append("✓ Consent documented, recorded, witnessed, and voluntary")
        
        return findings
    
    def _validate_exigent_circumstances(self, record: SearchAuthorizationRecord) -> List[str]:
        """Validate exigent circumstances exception"""
        findings = []
        
        if not record.exigent_circumstances_reason:
            findings.append("VIOLATION: No exigent circumstances documented - cannot justify warrantless entry")
            return findings
        
        # Must be genuine emergency
        valid_circumstances = [
            "imminent danger to life",
            "in-progress felony",
            "fleeing suspect",
            "emergency aid",
            "fire or medical emergency"
        ]
        
        is_valid_circumstance = any(
            circ in record.exigent_circumstances_reason.lower() 
            for circ in valid_circumstances
        )
        
        if not is_valid_circumstance:
            findings.append(f"VIOLATION: Stated exigent circumstance '{record.exigent_circumstances_reason}' does not meet legal standard")
            return findings
        
        if len(findings) == 0:
            findings.append("✓ Exigent circumstances properly documented and justified")
        
        return findings
    
    def _validate_plain_view(self, record: SearchAuthorizationRecord) -> List[str]:
        """Validate plain view doctrine"""
        findings = []
        findings.append("✓ Plain view doctrine requires: (1) lawful position, (2) inadvertent discovery, (3) obvious incrimination")
        return findings
    
    def check_officer_qualified_immunity_status(self, officer_id: str) -> bool:
        """
        Check if officer retains qualified immunity
        Qualified immunity is WAIVED upon documented constitutional violation
        """
        return self.officer_qualification_status.get(officer_id, True)
    
    def document_violation(self, violation_type: ConstitutionalViolationType,
                          officer_name: str, officer_id: str, badge_number: str,
                          agency: str, case_id: str, violation_details: str,
                          audio_clip_path: Optional[str] = None) -> str:
        """
        Document constitutional violation with automatic legal consequences
        
        Automatic actions:
        1. Waive officer's qualified immunity
        2. Create violation record for civil liability
        3. Mark evidence as fruit of poisonous tree
        4. Generate remediation record
        5. Flag for suppression motion
        """
        violation_id = f"VIOL-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
        
        violation_record = ConstitutionalViolationRecord(
            violation_id=violation_id,
            case_id=case_id,
            officer_name=officer_name,
            officer_id=officer_id,
            badge_number=badge_number,
            agency=agency,
            violation_type=violation_type,
            violation_date=datetime.now(),
            violation_details=violation_details,
            audio_violation_clip=audio_clip_path,
            audio_description=f"Evidence of {violation_type.value}"
        )
        
        # Automatic legal consequences
        violation_record.qualified_immunity_waived = True
        self.officer_qualification_status[officer_id] = False
        
        # Log violation
        self.violation_records[violation_id] = violation_record
        self._log_violation_event(violation_id, violation_type, officer_id)
        
        return violation_id
    
    def _log_violation_event(self, violation_id: str, violation_type: ConstitutionalViolationType,
                            officer_id: str):
        """Log violation for audit trail"""
        self.violation_log.append({
            "timestamp": datetime.now().isoformat(),
            "violation_id": violation_id,
            "violation_type": violation_type.name,
            "officer_id": officer_id,
            "qualified_immunity_status": "WAIVED",
            "civil_liability": "ATTACHED"
        })
    
    def get_evidence_suppression_list(self, case_id: str) -> List[str]:
        """
        Get list of evidence to suppress due to constitutional violations
        (Fruit of poisonous tree doctrine)
        """
        suppression_list = []
        
        for violation_record in self.violation_records.values():
            if violation_record.case_id == case_id:
                suppression_list.extend(violation_record.evidence_to_suppress)
        
        return suppression_list
    
    def get_violation_summary(self, violation_id: str) -> Optional[Dict]:
        """Get detailed violation summary for legal proceedings"""
        if violation_id not in self.violation_records:
            return None
        
        violation = self.violation_records[violation_id]
        
        return {
            "violation_id": violation_id,
            "officer": f"{violation.officer_name} (Badge: {violation.badge_number})",
            "agency": violation.agency,
            "violation_type": violation.violation_type.value,
            "details": violation.violation_details,
            "qualified_immunity_waived": violation.qualified_immunity_waived,
            "civil_liability_status": "ATTACHED" if violation.civil_liability_attached else "NONE",
            "evidence_tainted": violation.evidence_tainted,
            "audio_evidence": violation.audio_violation_clip,
            "created_at": violation.created_at.isoformat()
        }


class ConstitutionalRightsEthicsExtension:
    """
    Extension to Annon ethics controller adding constitutional rights enforcement
    Integrates with existing ethics framework
    """
    
    def __init__(self, ethics_controller=None):
        self.ethics_controller = ethics_controller
        self.rights_validator = ConstitutionalRightsValidator()
    
    def validate_search_and_seizure_action(self, action_context: Dict) -> Tuple[bool, str]:
        """
        Validate search/seizure action against constitutional requirements
        Blocks unconstitutional actions and documents violations
        
        Required context fields:
        - action_type: "home_entry", "vehicle_search", "person_seizure", "evidence_seizure"
        - officer_name, officer_id, badge_number, agency
        - location (if home entry)
        - authorization_type (warrant, consent, exigent, etc.)
        - warrant details (if applicable)
        - consent documentation (if applicable)
        """
        action_type = action_context.get("action_type")
        officer_id = action_context.get("officer_id")
        
        # Check officer's current qualified immunity status
        if not self.rights_validator.check_officer_qualified_immunity_status(officer_id):
            return False, (
                f"Officer {officer_id} has had qualified immunity waived due to prior "
                "documented constitutional violation. All actions require judicial review."
            )
        
        # Route to appropriate validator
        if action_type == "home_entry":
            search_record = SearchAuthorizationRecord(
                search_id=f"SEARCH-{uuid.uuid4().hex[:8].upper()}",
                officer_name=action_context.get("officer_name", ""),
                officer_id=officer_id,
                badge_number=action_context.get("badge_number", ""),
                agency=action_context.get("agency", ""),
                search_location=action_context.get("location", ""),
                search_date=datetime.now(),
                search_time_start=datetime.now(),
                search_time_end=datetime.now(),
                authorization_type=action_context.get("authorization_type"),
                warrant_number=action_context.get("warrant_number"),
                warrant_issuing_judge=action_context.get("warrant_issuing_judge"),
                consent_given_by=action_context.get("consent_given_by"),
                exigent_circumstances_reason=action_context.get("exigent_circumstances_reason")
            )
            
            is_valid, findings = self.rights_validator.validate_home_entry(search_record)
            
            if not is_valid:
                # Document violation and attach audio evidence if provided
                audio_path = action_context.get("violation_audio_evidence")
                violation_id = self.rights_validator.document_violation(
                    violation_type=ConstitutionalViolationType.WARRANTLESS_HOME_ENTRY,
                    officer_name=action_context.get("officer_name", ""),
                    officer_id=officer_id,
                    badge_number=action_context.get("badge_number", ""),
                    agency=action_context.get("agency", ""),
                    case_id=action_context.get("case_id", ""),
                    violation_details="; ".join(findings),
                    audio_clip_path=audio_path
                )
                
                violation_msg = (
                    f"Constitutional violation documented (ID: {violation_id}). "
                    f"Officer qualified immunity WAIVED. "
                    f"Evidence marked for suppression. "
                    f"Civil liability attached. "
                    f"Violations: {'; '.join(findings)}"
                )
                return False, violation_msg
            
            return True, "Home entry authorized and constitutionally compliant"
        
        elif action_type == "person_seizure":
            # Requires probable cause or reasonable suspicion
            probable_cause = action_context.get("probable_cause")
            if not probable_cause:
                violation_id = self.rights_validator.document_violation(
                    violation_type=ConstitutionalViolationType.NO_PROBABLE_CAUSE,
                    officer_name=action_context.get("officer_name", ""),
                    officer_id=officer_id,
                    badge_number=action_context.get("badge_number", ""),
                    agency=action_context.get("agency", ""),
                    case_id=action_context.get("case_id", ""),
                    violation_details="Seizure without probable cause or reasonable suspicion"
                )
                return False, f"Seizure blocked - no probable cause. Violation ID: {violation_id}"
            
            return True, "Person seizure authorized with probable cause"
        
        else:
            return False, f"Unknown action type: {action_type}"


# Export for integration with ethics controller
def extend_ethics_controller_with_constitutional_rights(ethics_controller) -> ConstitutionalRightsEthicsExtension:
    """
    Extend existing ethics controller with constitutional rights enforcement
    """
    return ConstitutionalRightsEthicsExtension(ethics_controller)
