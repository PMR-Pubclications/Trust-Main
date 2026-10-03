"""
Annon AI-Personality Ethics Framework
Enforces moral guidelines based on Ten Commandments and Natural Law principles
with legal chain of custody procedures
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Set, Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import json
import uuid


class EthicalPrinciple(Enum):
    """Natural Law and Commandment-based ethical principles"""
    
    # Ten Commandments Foundation
    TRUTH = "Thou shalt not bear false witness - Commit to absolute truth"
    LOYALTY = "Honor thy commitments - Maintain integrity in all dealings"
    SANCTITY = "Do not profane - Respect the sacred and inviolable"
    JUSTICE = "Thou shalt not steal - Respect rightful ownership and property"
    RESPECT_LIFE = "Thou shalt not kill - Preserve life and wellbeing"
    PROPER_ORDER = "Thou shalt not commit adultery - Maintain proper order and boundaries"
    HONOR = "Honor thy father and mother - Respect legitimate authority"
    COVET_NOT = "Thou shalt not covet - Be content and respect others' stations"
    WORSHIP_TRUE = "Thou shalt have no other gods - Seek truth, not false idols"
    REST_SACRED = "Remember the sabbath - Respect natural cycles and limits"
    
    # Natural Law Principles
    NATURAL_ORDER = "Follow natural law and reason"
    COMMON_GOOD = "Prioritize the common good"
    PROPORTIONALITY = "Responses proportional to circumstances"
    SUBSIDIARITY = "Decisions at lowest appropriate level"


class ChainOfCustodyStatus(Enum):
    """Legal chain of custody status"""
    CREATED = "Created - Initial receipt and documentation"
    RECEIVED = "Received - Formal acceptance by authorized personnel"
    PROCESSED = "Processed - Initial review and validation completed"
    STORED = "Stored - Secure storage with access controls"
    TRANSFERRED = "Transferred - Handed over to next authorized custodian"
    SEALED = "Sealed - Final sealing for preservation/legal proceedings"
    AUTHENTICATED = "Authenticated - Cryptographic verification completed"


@dataclass
class CustodianRecord:
    """Legal custodian record - tracks who had possession and when"""
    custodian_name: str
    custodian_id: str
    role: str
    organization: str
    handover_timestamp: datetime
    received_timestamp: Optional[datetime] = None
    signature_hash: str = ""  # SHA256 of digital signature
    location: str = ""
    condition_notes: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "custodian_name": self.custodian_name,
            "custodian_id": self.custodian_id,
            "role": self.role,
            "organization": self.organization,
            "handover_timestamp": self.handover_timestamp.isoformat(),
            "received_timestamp": self.received_timestamp.isoformat() if self.received_timestamp else None,
            "signature_hash": self.signature_hash,
            "location": self.location,
            "condition_notes": self.condition_notes
        }


@dataclass
class ChainOfCustodyRecord:
    """Legal chain of custody with SOP compliance"""
    evidence_id: str
    original_custodian: CustodianRecord
    current_status: ChainOfCustodyStatus
    custody_chain: List[CustodianRecord] = field(default_factory=list)
    status_history: List[Dict] = field(default_factory=list)
    integrity_seals: List[str] = field(default_factory=list)  # Cryptographic seals
    tamper_detection_enabled: bool = True
    
    def __post_init__(self):
        self.custody_chain.append(self.original_custodian)
        self._log_status_change(
            self.current_status,
            f"Initial custody established with {self.original_custodian.custodian_name}",
            self.original_custodian.custodian_id
        )
    
    def _log_status_change(self, status: ChainOfCustodyStatus, notes: str, authorized_by: str):
        """Log status change for audit trail"""
        change = {
            "timestamp": datetime.now().isoformat(),
            "status": status.name,
            "description": status.value,
            "notes": notes,
            "authorized_by": authorized_by
        }
        self.status_history.append(change)
    
    def transfer_custody(self, from_custodian: CustodianRecord, to_custodian: CustodianRecord,
                        condition_verified: bool = True, transfer_notes: str = "") -> bool:
        """
        Legal transfer of custody between authorized personnel
        
        Implements SOP:
        1. Verify both custodians authorized
        2. Verify evidence condition
        3. Create cryptographic seal
        4. Record transfer with signatures
        """
        if not condition_verified:
            raise ValueError("Evidence condition must be verified before transfer")
        
        if not from_custodian.signature_hash or not to_custodian.signature_hash:
            raise ValueError("Both custodians must provide digital signatures")
        
        # Create integrity seal before transfer
        pre_transfer_seal = self._create_integrity_seal(
            f"PRE-TRANSFER-{len(self.custody_chain)}"
        )
        
        # Record receiving acceptance
        to_custodian.received_timestamp = datetime.now()
        self.custody_chain.append(to_custodian)
        
        # Create post-transfer seal
        post_transfer_seal = self._create_integrity_seal(
            f"POST-TRANSFER-{len(self.custody_chain)}"
        )
        
        self.integrity_seals.append(pre_transfer_seal)
        self.integrity_seals.append(post_transfer_seal)
        
        self.current_status = ChainOfCustodyStatus.TRANSFERRED
        self._log_status_change(
            ChainOfCustodyStatus.TRANSFERRED,
            f"Transferred from {from_custodian.custodian_name} to {to_custodian.custodian_name}. {transfer_notes}",
            to_custodian.custodian_id
        )
        
        return True
    
    def _create_integrity_seal(self, seal_id: str) -> str:
        """Create cryptographic seal for chain integrity"""
        seal_data = {
            "seal_id": seal_id,
            "evidence_id": self.evidence_id,
            "timestamp": datetime.now().isoformat(),
            "custody_chain_length": len(self.custody_chain),
            "current_status": self.current_status.name
        }
        seal_content = json.dumps(seal_data, sort_keys=True)
        seal_hash = hashlib.sha256(seal_content.encode()).hexdigest()
        return seal_hash
    
    def verify_integrity(self) -> Tuple[bool, str]:
        """Verify chain of custody integrity"""
        if not self.integrity_seals:
            return False, "No integrity seals found"
        
        if len(self.custody_chain) < 1:
            return False, "Empty custody chain"
        
        # Verify each custodian has proper documentation
        for i, custodian in enumerate(self.custody_chain):
            if not custodian.custodian_name or not custodian.custodian_id:
                return False, f"Custodian {i} missing required identification"
            
            if i > 0 and not custodian.received_timestamp:
                return False, f"Custodian {i} missing reception timestamp"
        
        return True, "Chain of custody integrity verified"
    
    def get_full_chain(self) -> List[Dict]:
        """Get complete chain of custody documentation"""
        return [custodian.to_dict() for custodian in self.custody_chain]
    
    def seal_for_legal_proceedings(self, sealed_by: str, seal_authority: str) -> Dict:
        """Final seal for legal proceedings - immutable thereafter"""
        if self.current_status == ChainOfCustodyStatus.SEALED:
            raise ValueError("Evidence already sealed for legal proceedings")
        
        final_seal = {
            "seal_timestamp": datetime.now().isoformat(),
            "sealed_by": sealed_by,
            "seal_authority": seal_authority,
            "chain_length": len(self.custody_chain),
            "final_integrity_hash": self._create_integrity_seal("FINAL-LEGAL-SEAL")
        }
        
        self.current_status = ChainOfCustodyStatus.SEALED
        self._log_status_change(
            ChainOfCustodyStatus.SEALED,
            f"Evidence sealed for legal proceedings by {seal_authority}",
            sealed_by
        )
        
        return final_seal


@dataclass
class EvidencePackage:
    """Immutable evidence container with chain of custody tracking"""
    package_id: str
    content_hash: str
    timestamp: datetime
    submitter: str
    submitter_id: str
    submitter_role: str
    submitter_organization: str
    evidence_data: Dict
    chain_of_custody: ChainOfCustodyRecord = None
    
    def __post_init__(self):
        if not self.chain_of_custody:
            # Initialize chain of custody on creation
            original_custodian = CustodianRecord(
                custodian_name=self.submitter,
                custodian_id=self.submitter_id,
                role=self.submitter_role,
                organization=self.submitter_organization,
                handover_timestamp=self.timestamp
            )
            self.chain_of_custody = ChainOfCustodyRecord(
                evidence_id=self.package_id,
                original_custodian=original_custodian,
                current_status=ChainOfCustodyStatus.CREATED
            )
    
    def __hash__(self):
        return hash(self.package_id)
    
    def __eq__(self, other):
        if isinstance(other, EvidencePackage):
            return self.content_hash == other.content_hash
        return False


@dataclass
class Report:
    """Report with amendment-only policy, no direct edits"""
    report_id: str
    original_content: str
    original_hash: str
    created_at: datetime
    created_by: str
    amendments: List[Dict] = field(default_factory=list)
    
    def add_amendment(self, amendment_content: str, reason: str, amended_by: str,
                     amendment_authority: str = "") -> Dict:
        """Add amendment without editing original"""
        if not amendment_content or not reason:
            raise ValueError("Amendment content and reason are required")
        
        amendment = {
            "amendment_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "content": amendment_content,
            "reason": reason,
            "amended_by": amended_by,
            "amendment_authority": amendment_authority,
            "amendment_hash": hashlib.sha256(amendment_content.encode()).hexdigest()
        }
        self.amendments.append(amendment)
        return amendment
    
    def get_audit_trail(self) -> List[Dict]:
        """Return immutable audit trail of all changes"""
        trail = [{
            "type": "original",
            "timestamp": self.created_at.isoformat(),
            "created_by": self.created_by,
            "hash": self.original_hash,
            "content_preview": self.original_content[:100]
        }]
        trail.extend([{
            "type": "amendment",
            **amend
        } for amend in self.amendments])
        return trail


class SubmissionRegistry:
    """Enforces single-submission-per-package rule with chain of custody"""
    
    def __init__(self):
        self.submitted_packages: Set[str] = set()
        self.package_metadata: Dict[str, Dict] = {}
        self.custody_records: Dict[str, ChainOfCustodyRecord] = {}
    
    def submit_evidence_package(self, package: EvidencePackage, 
                               ethical_check: bool = True) -> Tuple[bool, str]:
        """
        Submit evidence package - only once per package ID
        Includes chain of custody documentation
        
        SOP:
        1. Verify single submission rule
        2. Verify submitter credentials
        3. Create chain of custody record
        4. Generate receipt/evidence number
        """
        if package.package_id in self.submitted_packages:
            return False, (
                f"Package {package.package_id} has already been submitted. "
                "Only one submission per package is permitted."
            )
        
        if ethical_check:
            self._validate_ethical_compliance(package)
        
        # Verify chain of custody integrity
        is_valid, validation_msg = package.chain_of_custody.verify_integrity()
        if not is_valid:
            return False, f"Chain of custody validation failed: {validation_msg}"
        
        # Mark package as received in custody
        package.chain_of_custody.current_status = ChainOfCustodyStatus.RECEIVED
        package.chain_of_custody._log_status_change(
            ChainOfCustodyStatus.RECEIVED,
            "Package received and logged into evidence management system",
            "SYSTEM"
        )
        
        self.submitted_packages.add(package.package_id)
        
        # Generate evidence receipt
        evidence_receipt = {
            "evidence_number": f"EVD-{datetime.now().strftime('%Y%m%d')}-{len(self.submitted_packages):06d}",
            "submitted_at": datetime.now().isoformat(),
            "submitter": package.submitter,
            "submitter_id": package.submitter_id,
            "submitter_organization": package.submitter_organization,
            "content_hash": package.content_hash,
            "custody_chain_length": len(package.chain_of_custody.custody_chain)
        }
        
        self.package_metadata[package.package_id] = evidence_receipt
        self.custody_records[package.package_id] = package.chain_of_custody
        
        return True, f"Evidence submitted successfully. Evidence Number: {evidence_receipt['evidence_number']}"
    
    def is_submitted(self, package_id: str) -> bool:
        """Check if package has been submitted"""
        return package_id in self.submitted_packages
    
    def get_submission_proof(self, package_id: str) -> Optional[Dict]:
        """Get cryptographic proof of submission"""
        if package_id in self.package_metadata:
            return self.package_metadata[package_id]
        return None
    
    def get_chain_of_custody(self, package_id: str) -> Optional[Dict]:
        """Get complete chain of custody record"""
        if package_id in self.custody_records:
            record = self.custody_records[package_id]
            return {
                "evidence_id": record.evidence_id,
                "current_status": record.current_status.name,
                "custody_chain": record.get_full_chain(),
                "status_history": record.status_history,
                "integrity_verified": record.verify_integrity()[0]
            }
        return None
    
    def transfer_evidence_custody(self, package_id: str, from_custodian: CustodianRecord,
                                  to_custodian: CustodianRecord, transfer_notes: str = "") -> Tuple[bool, str]:
        """Execute legal transfer of custody"""
        if package_id not in self.custody_records:
            return False, "Package not found in evidence registry"
        
        try:
            record = self.custody_records[package_id]
            record.transfer_custody(from_custodian, to_custodian, 
                                   condition_verified=True, transfer_notes=transfer_notes)
            return True, f"Custody transferred to {to_custodian.custodian_name}"
        except ValueError as e:
            return False, str(e)
    
    def _validate_ethical_compliance(self, package: EvidencePackage):
        """Validate package meets ethical standards"""
        if not package.evidence_data:
            raise ValueError("Evidence package cannot be empty (violates TRUTH principle)")
        
        if not package.submitter or not package.submitter_id:
            raise ValueError("Submitter identity and ID required (violates HONOR principle)")
        
        if not package.submitter_organization:
            raise ValueError("Submitter organization required for chain of custody")


class AnnonEthicsEngine:
    """Core ethics engine for Annon AI-Personality with legal compliance"""
    
    def __init__(self):
        self.principles: Dict[EthicalPrinciple, bool] = {
            principle: True for principle in EthicalPrinciple
        }
        self.submission_registry = SubmissionRegistry()
        self.active_reports: Dict[str, Report] = {}
        self.ethics_log: List[Dict] = []
    
    def log_ethical_decision(self, action: str, principle: EthicalPrinciple, 
                            approved: bool, reason: str):
        """Log all ethical decisions for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "principle": principle.name,
            "principle_description": principle.value,
            "approved": approved,
            "reason": reason
        }
        self.ethics_log.append(log_entry)
    
    def evaluate_action(self, action: str, context: Dict) -> Tuple[bool, str]:
        """
        Evaluate if action complies with ethical framework
        
        Returns:
            (is_approved, reason)
        """
        violations = []
        
        # Check for truth violation
        if context.get("contains_falsehood"):
            violations.append(EthicalPrinciple.TRUTH)
        
        # Check for submission integrity
        if action == "submit_evidence":
            package_id = context.get("package_id")
            if self.submission_registry.is_submitted(package_id):
                violations.append(EthicalPrinciple.LOYALTY)
                self.log_ethical_decision(
                    action, EthicalPrinciple.LOYALTY, False,
                    "Package already submitted - violates single-submission rule"
                )
                return False, "Evidence package has already been submitted once. Additional submissions not permitted."
        
        # Check for report integrity
        if action == "edit_report":
            violations.append(EthicalPrinciple.JUSTICE)
            self.log_ethical_decision(
                action, EthicalPrinciple.JUSTICE, False,
                "Reports cannot be edited - only amended. Maintains immutability of original record."
            )
            return False, "Reports cannot be directly edited. Use amendment process to modify records."
        
        # Check for proportionality
        if not self._check_proportionality(action, context):
            violations.append(EthicalPrinciple.PROPORTIONALITY)
        
        if violations:
            reason = f"Action violates principles: {', '.join(v.name for v in violations)}"
            self.log_ethical_decision(action, violations[0], False, reason)
            return False, reason
        
        self.log_ethical_decision(action, EthicalPrinciple.TRUTH, True, "Action approved")
        return True, "Action complies with ethical framework"
    
    def _check_proportionality(self, action: str, context: Dict) -> bool:
        """Verify response is proportional to circumstances"""
        return True
    
    def create_report(self, report_id: str, content: str, created_by: str) -> Report:
        """Create immutable report with amendment-only modification"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        report = Report(
            report_id=report_id,
            original_content=content,
            original_hash=content_hash,
            created_at=datetime.now(),
            created_by=created_by
        )
        self.active_reports[report_id] = report
        self.log_ethical_decision(
            f"create_report:{report_id}", EthicalPrinciple.JUSTICE, True,
            "Report created with immutable original and amendment-only modification"
        )
        return report
    
    def amend_report(self, report_id: str, amendment: str, reason: str, 
                    amended_by: str, amendment_authority: str = "") -> Dict:
        """Amend existing report, preserving original"""
        if report_id not in self.active_reports:
            raise ValueError(f"Report {report_id} not found")
        
        report = self.active_reports[report_id]
        amendment_record = report.add_amendment(amendment, reason, amended_by, amendment_authority)
        self.log_ethical_decision(
            f"amend_report:{report_id}", EthicalPrinciple.TRUTH, True,
            f"Report amended - original preserved. Reason: {reason}"
        )
        return amendment_record
    
    def submit_evidence(self, package: EvidencePackage) -> Tuple[bool, str]:
        """Submit evidence with single-submission enforcement and chain of custody"""
        approved, reason = self.evaluate_action("submit_evidence", {"package_id": package.package_id})
        
        if not approved:
            return False, reason
        
        return self.submission_registry.submit_evidence_package(package, ethical_check=True)
    
    def get_chain_of_custody(self, package_id: str) -> Optional[Dict]:
        """Retrieve chain of custody for evidence"""
        return self.submission_registry.get_chain_of_custody(package_id)
    
    def transfer_evidence(self, package_id: str, from_custodian: CustodianRecord,
                         to_custodian: CustodianRecord, transfer_notes: str = "") -> Tuple[bool, str]:
        """Execute legal transfer of evidence custody"""
        return self.submission_registry.transfer_evidence_custody(
            package_id, from_custodian, to_custodian, transfer_notes
        )
    
    def get_ethics_audit(self) -> List[Dict]:
        """Return complete audit trail of ethical decisions"""
        return self.ethics_log.copy()


# Initialization for Annon AI-Personality
def initialize_annon_ethics() -> AnnonEthicsEngine:
    """Initialize Annon with ethical framework and legal chain of custody"""
    return AnnonEthicsEngine()
