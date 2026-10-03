"""
Annon EthicsController
Enforces ethical decision-making and evidence integrity at the core level
"""

from ethics_framework import (
    AnnonEthicsEngine, EvidencePackage, CustodianRecord, Report,
    ChainOfCustodyStatus, EthicalPrinciple
)
from annon_ethics_integration import (
    AnnonEthicsVoiceInterface, AnnonEthicsCommandSet
)
from datetime import datetime
from typing import Dict, Tuple, Optional, List
import uuid
import hashlib


class EthicsController:
    """
    Core ethics enforcement layer for Annon
    Validates all major operations against ethical framework
    """
    
    def __init__(self):
        self.engine = AnnonEthicsEngine()
        self.voice_interface = AnnonEthicsVoiceInterface(self.engine)
        self.command_set = AnnonEthicsCommandSet(self.voice_interface)
        self.blocked_actions: List[Dict] = []
        self.approved_actions: List[Dict] = []
    
    def validate_and_execute(self, action: str, context: Dict) -> Tuple[bool, str, Optional[Dict]]:
        """
        Central validation point for all Annon operations
        
        Returns:
            (approved: bool, message: str, result: Optional[Dict])
        """
        # Validate against ethics framework
        is_approved, reason = self.engine.evaluate_action(action, context)
        
        if not is_approved:
            self._log_blocked_action(action, context, reason)
            return False, reason, None
        
        # Execute approved action
        result = self._execute_action(action, context)
        self._log_approved_action(action, context, result)
        
        return True, "Action approved and executed", result
    
    def _execute_action(self, action: str, context: Dict) -> Optional[Dict]:
        """Execute approved action based on type"""
        
        if action == "submit_evidence":
            return self._execute_submit_evidence(context)
        
        elif action == "transfer_custody":
            return self._execute_transfer_custody(context)
        
        elif action == "create_report":
            return self._execute_create_report(context)
        
        elif action == "amend_report":
            return self._execute_amend_report(context)
        
        elif action == "query_custody_chain":
            return self._execute_query_custody_chain(context)
        
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _execute_submit_evidence(self, context: Dict) -> Dict:
        """Execute evidence submission"""
        success, message = self.voice_interface.voice_submit_evidence(
            submitter_name=context.get("submitter_name", ""),
            submitter_id=context.get("submitter_id", ""),
            submitter_role=context.get("submitter_role", ""),
            organization=context.get("organization", ""),
            evidence_description=context.get("description", ""),
            evidence_data=context.get("evidence_data", {}),
            signature_hash=context.get("signature_hash", "")
        )
        return {
            "action": "submit_evidence",
            "success": success,
            "message": message
        }
    
    def _execute_transfer_custody(self, context: Dict) -> Dict:
        """Execute custody transfer"""
        success, message = self.voice_interface.voice_transfer_evidence(
            package_id=context.get("package_id", ""),
            from_custodian_name=context.get("from_name", ""),
            from_custodian_id=context.get("from_id", ""),
            from_role=context.get("from_role", ""),
            from_organization=context.get("from_org", ""),
            from_signature=context.get("from_signature", ""),
            to_custodian_name=context.get("to_name", ""),
            to_custodian_id=context.get("to_id", ""),
            to_role=context.get("to_role", ""),
            to_organization=context.get("to_org", ""),
            to_signature=context.get("to_signature", ""),
            transfer_notes=context.get("notes", "")
        )
        return {
            "action": "transfer_custody",
            "success": success,
            "message": message
        }
    
    def _execute_create_report(self, context: Dict) -> Dict:
        """Execute report creation"""
        success, message = self.voice_interface.voice_create_report(
            report_id=context.get("report_id", f"RPT-{uuid.uuid4().hex[:8]}"),
            report_content=context.get("content", ""),
            created_by=context.get("created_by", "System")
        )
        return {
            "action": "create_report",
            "success": success,
            "message": message,
            "report_id": context.get("report_id", "")
        }
    
    def _execute_amend_report(self, context: Dict) -> Dict:
        """Execute report amendment"""
        success, message = self.voice_interface.voice_amend_report(
            report_id=context.get("report_id", ""),
            amendment_text=context.get("amendment", ""),
            reason=context.get("reason", ""),
            amended_by=context.get("amended_by", "System"),
            amendment_authority=context.get("authority", "")
        )
        return {
            "action": "amend_report",
            "success": success,
            "message": message
        }
    
    def _execute_query_custody_chain(self, context: Dict) -> Dict:
        """Execute custody chain query"""
        success, custody = self.voice_interface.voice_check_custody_chain(
            package_id=context.get("package_id", "")
        )
        return {
            "action": "query_custody_chain",
            "success": success,
            "data": custody
        }
    
    def _log_blocked_action(self, action: str, context: Dict, reason: str):
        """Log blocked/rejected action"""
        self.blocked_actions.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "reason": reason,
            "context_user": context.get("user_name", "Unknown")
        })
    
    def _log_approved_action(self, action: str, context: Dict, result: Dict):
        """Log approved action"""
        self.approved_actions.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "context_user": context.get("user_name", "Unknown")
        })
    
    def get_action_audit_log(self) -> Dict:
        """Return complete action audit log"""
        return {
            "blocked_actions": self.blocked_actions,
            "approved_actions": self.approved_actions,
            "total_blocked": len(self.blocked_actions),
            "total_approved": len(self.approved_actions)
        }


class EvidencePackageValidator:
    """
    Validates evidence packages for integrity and compliance
    Prevents duplicate submissions, ensures proper custody documentation
    """
    
    def __init__(self, ethics_controller: EthicsController):
        self.controller = ethics_controller
    
    def validate_package(self, package: EvidencePackage) -> Tuple[bool, List[str]]:
        """
        Comprehensive evidence package validation
        
        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # Check for empty content
        if not package.evidence_data:
            errors.append("Evidence package contains no data")
        
        # Check for submitter identity
        if not package.submitter or not package.submitter_id:
            errors.append("Submitter identity incomplete")
        
        # Check for organization
        if not package.submitter_organization:
            errors.append("Submitter organization required for chain of custody")
        
        # Check for duplicate submission
        if self.controller.engine.submission_registry.is_submitted(package.package_id):
            errors.append(f"Package {package.package_id} already submitted (single-submission rule violated)")
        
        # Check chain of custody integrity
        if package.chain_of_custody:
            is_valid, validation_msg = package.chain_of_custody.verify_integrity()
            if not is_valid:
                errors.append(f"Chain of custody validation failed: {validation_msg}")
        
        return len(errors) == 0, errors
    
    def validate_and_submit(self, package: EvidencePackage, context: Dict = None) -> Tuple[bool, str]:
        """
        Validate and submit evidence package through ethics controller
        """
        is_valid, validation_errors = self.validate_package(package)
        
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            return False, error_msg
        
        # Route through ethics controller
        ctx = context or {}
        ctx["package_id"] = package.package_id
        ctx["submitter_name"] = package.submitter
        ctx["submitter_id"] = package.submitter_id
        ctx["submitter_role"] = package.submitter_role
        ctx["organization"] = package.submitter_organization
        ctx["evidence_data"] = package.evidence_data
        
        approved, message, result = self.controller.validate_and_execute("submit_evidence", ctx)
        
        return approved, message


class CustodyTransferEnforcer:
    """
    Enforces legal custody transfer procedures
    Prevents unauthorized transfers, verifies signatures, maintains chain integrity
    """
    
    def __init__(self, ethics_controller: EthicsController):
        self.controller = ethics_controller
    
    def validate_transfer(self, from_custodian: CustodianRecord,
                         to_custodian: CustodianRecord,
                         package_id: str) -> Tuple[bool, List[str]]:
        """
        Validate custody transfer compliance
        
        Returns:
            (is_valid: bool, errors: List[str])
        """
        errors = []
        
        # Check custodian credentials
        if not from_custodian.custodian_id or not from_custodian.custodian_name:
            errors.append("From custodian identity incomplete")
        
        if not to_custodian.custodian_id or not to_custodian.custodian_name:
            errors.append("To custodian identity incomplete")
        
        # Check signatures
        if not from_custodian.signature_hash:
            errors.append("From custodian signature required")
        
        if not to_custodian.signature_hash:
            errors.append("To custodian signature required")
        
        # Verify organizations
        if not from_custodian.organization:
            errors.append("From custodian organization required")
        
        if not to_custodian.organization:
            errors.append("To custodian organization required")
        
        # Verify package exists
        if not self.controller.engine.submission_registry.is_submitted(package_id):
            errors.append(f"Package {package_id} not found in evidence system")
        
        return len(errors) == 0, errors
    
    def execute_transfer(self, package_id: str, from_custodian: CustodianRecord,
                        to_custodian: CustodianRecord, transfer_notes: str = "",
                        authorized_by: str = "") -> Tuple[bool, str]:
        """
        Execute legal custody transfer through ethics controller
        """
        is_valid, validation_errors = self.validate_transfer(
            from_custodian, to_custodian, package_id
        )
        
        if not is_valid:
            error_msg = "; ".join(validation_errors)
            return False, error_msg
        
        context = {
            "package_id": package_id,
            "from_name": from_custodian.custodian_name,
            "from_id": from_custodian.custodian_id,
            "from_role": from_custodian.role,
            "from_org": from_custodian.organization,
            "from_signature": from_custodian.signature_hash,
            "to_name": to_custodian.custodian_name,
            "to_id": to_custodian.custodian_id,
            "to_role": to_custodian.role,
            "to_org": to_custodian.organization,
            "to_signature": to_custodian.signature_hash,
            "notes": transfer_notes,
            "authorized_by": authorized_by
        }
        
        approved, message, result = self.controller.validate_and_execute(
            "transfer_custody", context
        )
        
        return approved, message


class AmendmentOnlyReport:
    """
    Immutable-first report implementation
    Blocks direct edits, enforces amendment-only modification policy
    """
    
    def __init__(self, ethics_controller: EthicsController, report_id: str,
                 content: str, created_by: str):
        self.controller = ethics_controller
        self.report_id = report_id
        self.original_content = content
        self.original_hash = hashlib.sha256(content.encode()).hexdigest()
        self.created_by = created_by
        self.created_at = datetime.now()
        self.amendments: List[Dict] = []
        self.edit_attempts: List[Dict] = []
    
    def attempt_direct_edit(self, new_content: str, user: str) -> Tuple[bool, str]:
        """
        Reject direct edit attempts, maintain immutability
        """
        self.edit_attempts.append({
            "timestamp": datetime.now().isoformat(),
            "user": user,
            "attempted": True,
            "rejected": True
        })
        
        return False, "Direct editing prohibited. Use amendment process to modify reports."
    
    def add_amendment(self, amendment_content: str, reason: str,
                     amended_by: str, amendment_authority: str = "") -> Tuple[bool, str, Optional[Dict]]:
        """
        Add amendment through ethics controller
        Maintains original immutability
        """
        context = {
            "report_id": self.report_id,
            "amendment": amendment_content,
            "reason": reason,
            "amended_by": amended_by,
            "authority": amendment_authority
        }
        
        approved, message, result = self.controller.validate_and_execute(
            "amend_report", context
        )
        
        if approved:
            self.amendments.append({
                "timestamp": datetime.now().isoformat(),
                "content": amendment_content,
                "reason": reason,
                "amended_by": amended_by,
                "authority": amendment_authority
            })
        
        return approved, message, result
    
    def get_full_record(self) -> Dict:
        """
        Return complete immutable record with original + all amendments
        """
        return {
            "report_id": self.report_id,
            "original": {
                "content": self.original_content,
                "hash": self.original_hash,
                "created_by": self.created_by,
                "created_at": self.created_at.isoformat()
            },
            "amendments_count": len(self.amendments),
            "amendments": self.amendments,
            "edit_attempts_rejected": len(self.edit_attempts)
        }
    
    def get_audit_trail(self) -> List[Dict]:
        """Return complete audit trail"""
        trail = [{
            "type": "original",
            "timestamp": self.created_at.isoformat(),
            "created_by": self.created_by,
            "hash": self.original_hash
        }]
        
        trail.extend([{
            "type": "amendment",
            **amendment
        } for amendment in self.amendments])
        
        trail.extend([{
            "type": "edit_attempt_blocked",
            **attempt
        } for attempt in self.edit_attempts])
        
        return trail


class RuleEngine:
    """
    Decision engine enforcing ethical rules
    Blocks improper edits, duplicate submissions, unauthorized chain breaks
    """
    
    def __init__(self, ethics_controller: EthicsController):
        self.controller = ethics_controller
        self.rules: Dict[str, callable] = {
            "no_direct_edits": self.rule_no_direct_edits,
            "single_submission": self.rule_single_submission,
            "chain_integrity": self.rule_chain_integrity,
            "authorized_transfer": self.rule_authorized_transfer,
            "truth_requirement": self.rule_truth_requirement
        }
        self.violated_rules: List[Dict] = []
    
    def evaluate_rules(self, action: str, context: Dict) -> Tuple[bool, List[str]]:
        """
        Evaluate all applicable rules for action
        
        Returns:
            (passes_all_rules: bool, violations: List[str])
        """
        violations = []
        
        # Apply relevant rules based on action
        if action == "edit_report":
            violations.extend(self.rule_no_direct_edits(context))
            violations.extend(self.rule_truth_requirement(context))
        
        if action == "submit_evidence":
            violations.extend(self.rule_single_submission(context))
            violations.extend(self.rule_truth_requirement(context))
        
        if action == "transfer_custody":
            violations.extend(self.rule_chain_integrity(context))
            violations.extend(self.rule_authorized_transfer(context))
        
        if violations:
            self.violated_rules.append({
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "violations": violations
            })
        
        return len(violations) == 0, violations
    
    def rule_no_direct_edits(self, context: Dict) -> List[str]:
        """Rule: Direct edits to reports are prohibited"""
        violations = []
        
        if context.get("is_direct_edit") or context.get("edit_type") == "direct":
            violations.append("RULE_VIOLATION: Direct editing prohibited - use amendment process")
        
        return violations
    
    def rule_single_submission(self, context: Dict) -> List[str]:
        """Rule: Only one submission per evidence package"""
        violations = []
        
        package_id = context.get("package_id")
        if package_id and self.controller.engine.submission_registry.is_submitted(package_id):
            violations.append(f"RULE_VIOLATION: Package {package_id} already submitted")
        
        return violations
    
    def rule_chain_integrity(self, context: Dict) -> List[str]:
        """Rule: Chain of custody must be maintained"""
        violations = []
        
        package_id = context.get("package_id")
        if package_id:
            custody = self.controller.engine.get_chain_of_custody(package_id)
            if custody and not custody.get("integrity_verified"):
                violations.append("RULE_VIOLATION: Chain of custody integrity compromised")
        
        return violations
    
    def rule_authorized_transfer(self, context: Dict) -> List[str]:
        """Rule: Only authorized custodians can transfer evidence"""
        violations = []
        
        from_sig = context.get("from_signature")
        to_sig = context.get("to_signature")
        
        if not from_sig or not to_sig:
            violations.append("RULE_VIOLATION: Transfer requires signatures from both custodians")
        
        return violations
    
    def rule_truth_requirement(self, context: Dict) -> List[str]:
        """Rule: No false or misleading content"""
        violations = []
        
        if context.get("contains_falsehood"):
            violations.append("RULE_VIOLATION: Content contains falsehood (violates TRUTH principle)")
        
        return violations
    
    def get_violation_log(self) -> List[Dict]:
        """Return all rule violations"""
        return self.violated_rules.copy()


# Initialize complete ethics system
def initialize_annon_ethics_system() -> Dict:
    """
    Initialize complete Annon ethics system with all enforcement layers
    
    Returns:
        Dictionary with all components ready for integration
    """
    ethics_controller = EthicsController()
    
    return {
        "controller": ethics_controller,
        "evidence_validator": EvidencePackageValidator(ethics_controller),
        "custody_enforcer": CustodyTransferEnforcer(ethics_controller),
        "rule_engine": RuleEngine(ethics_controller),
        "voice_interface": ethics_controller.voice_interface,
        "command_set": ethics_controller.command_set
    }
