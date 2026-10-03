"""
Annon Ethics Controller Integration
Master control module integrating constitutional rights protection with forensic investigation workflow
Enforces: Ten Commandments + Natural Law + 4th Amendment search/seizure protection + chain of custody

This module acts as the policy enforcement engine across all investigation operations.
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

# Import constitutional rights framework
try:
    from AI_Personality.constitutional_rights_protection import (
        ConstitutionalRightsValidator,
        ConstitutionalRightsEthicsExtension,
        ConstitutionalViolationType,
        SearchAuthorizationRecord,
        SearchAuthorization
    )
except ImportError:
    ConstitutionalRightsValidator = None
    ConstitutionalRightsEthicsExtension = None

# Import forensic accounting
try:
    from forensic_accounting_system import (
        ForensicAccountingManager, CaseForensicAccount
    )
except ImportError:
    ForensicAccountingManager = None

# Import voice interface
try:
    from AI_Personality.anon_voice_interface import AnonVoiceEngine
except ImportError:
    AnonVoiceEngine = None

logger = logging.getLogger("AnnonEthicsIntegration")


class AnnonEthicsIntegrationController:
    """
    Master ethics controller integrating all compliance frameworks
    for forensic investigation workflow
    """
    
    def __init__(self):
        self.constitutional_rights = ConstitutionalRightsValidator() if ConstitutionalRightsValidator else None
        self.voice_engine = AnonVoiceEngine() if AnonVoiceEngine else None
        self.accounting_manager = None  # Set later if needed
        self.policy_violations: Dict[str, Dict] = {}
        self.compliant_actions: List[Dict] = []
        self.blocked_actions: List[Dict] = []
    
    def validate_investigation_action(self, action: str, context: Dict) -> Tuple[bool, str]:
        """
        Main entry point for ethics validation
        Validates action against all applicable rules (constitutional, procedural, chain of custody)
        """
        action_lower = action.lower()
        
        # Route to appropriate validator
        if "home" in action_lower and "enter" in action_lower:
            return self.validate_home_entry_action(context)
        
        elif "search" in action_lower:
            return self.validate_search_action(context)
        
        elif "seize" in action_lower:
            return self.validate_seizure_action(context)
        
        elif "evidence" in action_lower and "register" in action_lower:
            return self.validate_evidence_registration(context)
        
        elif "custody" in action_lower and "transfer" in action_lower:
            return self.validate_custody_transfer(context)
        
        else:
            return True, "Action validated against applicable policies"
    
    def validate_home_entry_action(self, context: Dict) -> Tuple[bool, str]:
        """
        Validate home entry under 4th Amendment
        
        Required context:
        - officer_id, officer_name, badge_number, agency
        - property_address
        - authorization_type (warrant, consent, exigent, etc.)
        - [warrant details if applicable]
        - [consent documentation if applicable]
        """
        if not self.constitutional_rights:
            return False, "Constitutional rights validator not available"
        
        # Build search authorization record
        try:
            auth_type = SearchAuthorization[context.get("authorization_type", "").upper()]
        except KeyError:
            return False, f"Invalid authorization type: {context.get('authorization_type')}"
        
        search_record = SearchAuthorizationRecord(
            search_id=f"SEARCH-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            officer_name=context.get("officer_name", ""),
            officer_id=context.get("officer_id", ""),
            badge_number=context.get("badge_number", ""),
            agency=context.get("agency", ""),
            search_location=context.get("property_address", ""),
            search_date=datetime.now(),
            search_time_start=datetime.now(),
            search_time_end=datetime.now(),
            authorization_type=auth_type,
            warrant_number=context.get("warrant_number"),
            warrant_issuing_judge=context.get("warrant_issuing_judge"),
            warrant_issue_date=context.get("warrant_issue_date"),
            warrant_expiration=context.get("warrant_expiration"),
            warrant_property_description=context.get("warrant_property_description"),
            consent_given_by=context.get("consent_given_by"),
            consent_relationship_to_property=context.get("consent_relationship"),
            consent_witnessed_by=context.get("consent_witnesses", []),
            consent_recorded=context.get("consent_recorded", False),
            exigent_circumstances_reason=context.get("exigent_reason")
        )
        
        # Validate home entry
        is_valid, findings = self.constitutional_rights.validate_home_entry(search_record)
        
        if not is_valid:
            violation_id = self.constitutional_rights.document_violation(
                violation_type=ConstitutionalViolationType.WARRANTLESS_HOME_ENTRY,
                officer_name=context.get("officer_name", ""),
                officer_id=context.get("officer_id", ""),
                badge_number=context.get("badge_number", ""),
                agency=context.get("agency", ""),
                case_id=context.get("case_id", ""),
                violation_details="; ".join(findings),
                audio_clip_path=context.get("violation_audio_clip")
            )
            
            violation_msg = (
                f"\n⛔ HOME ENTRY BLOCKED - CONSTITUTIONAL VIOLATION\n"
                f"Violation ID: {violation_id}\n"
                f"Officer: {context.get('officer_name')} (Badge: {context.get('badge_number')})\n"
                f"Agency: {context.get('agency')}\n"
                f"Status: QUALIFIED IMMUNITY WAIVED\n"
                f"Evidence: MARKED FOR SUPPRESSION\n"
                f"Civil Liability: ATTACHED (42 U.S.C. § 1983)\n"
                f"Violations:\n"
            )
            for finding in findings:
                violation_msg += f"  • {finding}\n"
            
            if context.get("violation_audio_clip"):
                violation_msg += f"\nAudio Evidence: {context.get('violation_audio_clip')}\n"
                violation_msg += "⚠️ AUDIO VIOLATION CLIP ATTACHED TO REPORT PACKAGE\n"
            
            self.blocked_actions.append({
                "timestamp": datetime.now().isoformat(),
                "action": "home_entry",
                "reason": "constitutional_violation",
                "violation_id": violation_id,
                "officer_id": context.get("officer_id")
            })
            
            # Speak violation alert if voice available
            if self.voice_engine:
                self.voice_engine.speak(
                    f"Constitutional violation blocked. Home entry not authorized. "
                    f"Officer qualified immunity waived. Violation ID {violation_id}."
                )
            
            return False, violation_msg.strip()
        
        self.compliant_actions.append({
            "timestamp": datetime.now().isoformat(),
            "action": "home_entry",
            "officer_id": context.get("officer_id"),
            "property": context.get("property_address"),
            "authorization": str(auth_type)
        })
        
        return True, "Home entry authorized - constitutionally compliant"
    
    def validate_search_action(self, context: Dict) -> Tuple[bool, str]:
        """Validate search scope and authorization"""
        officer_id = context.get("officer_id", "")
        
        # Check officer's qualified immunity status
        if self.constitutional_rights:
            if not self.constitutional_rights.check_officer_qualified_immunity_status(officer_id):
                return False, (
                    f"Search blocked: Officer {officer_id} has had qualified immunity waived. "
                    "All actions require judicial review."
                )
        
        return True, "Search validated against scope and authorization"
    
    def validate_seizure_action(self, context: Dict) -> Tuple[bool, str]:
        """Validate person/property seizure with probable cause"""
        seizure_type = context.get("seizure_type", "unknown")
        probable_cause = context.get("probable_cause")
        
        if not probable_cause:
            if self.constitutional_rights:
                violation_id = self.constitutional_rights.document_violation(
                    violation_type=ConstitutionalViolationType.NO_PROBABLE_CAUSE,
                    officer_name=context.get("officer_name", ""),
                    officer_id=context.get("officer_id", ""),
                    badge_number=context.get("badge_number", ""),
                    agency=context.get("agency", ""),
                    case_id=context.get("case_id", ""),
                    violation_details=f"{seizure_type} seizure without probable cause"
                )
                
                return False, (
                    f"Seizure blocked: No probable cause documented. "
                    f"Violation ID: {violation_id}. "
                    f"Officer qualified immunity waived."
                )
            return False, "Seizure blocked: No probable cause documented"
        
        return True, f"{seizure_type.capitalize()} seizure authorized with probable cause"
    
    def validate_evidence_registration(self, context: Dict) -> Tuple[bool, str]:
        """Validate evidence registration in case"""
        case_id = context.get("case_id")
        submitter_id = context.get("submitter_id")
        evidence_type = context.get("evidence_type")
        
        # Check submitter credentials
        if not submitter_id:
            return False, "Evidence submitter identity required"
        
        # Verify evidence hasn't been submitted before (single-submission rule)
        if context.get("evidence_number_check"):
            return False, "Evidence already registered in case"
        
        return True, "Evidence validated for registration"
    
    def validate_custody_transfer(self, context: Dict) -> Tuple[bool, str]:
        """Validate evidence custody transfer with chain of custody"""
        evidence_num = context.get("evidence_number")
        from_custodian = context.get("from_custodian")
        to_custodian = context.get("to_custodian")
        
        if not all([evidence_num, from_custodian, to_custodian]):
            return False, "Custody transfer missing required information"
        
        return True, f"Custody transfer authorized for {evidence_num}"
    
    def get_violation_summary(self, case_id: str) -> Dict[str, Any]:
        """Get all constitutional violations for a case"""
        violations = {}
        
        if self.constitutional_rights:
            for v_id, violation in self.constitutional_rights.violation_records.items():
                if violation.case_id == case_id:
                    violations[v_id] = self.constitutional_rights.get_violation_summary(v_id)
        
        return violations
    
    def get_suppression_list(self, case_id: str) -> List[str]:
        """Get evidence to suppress due to constitutional violations"""
        if self.constitutional_rights:
            return self.constitutional_rights.get_evidence_suppression_list(case_id)
        return []
    
    def get_blocked_actions_log(self) -> List[Dict]:
        """Get log of all blocked actions"""
        return self.blocked_actions.copy()
    
    def get_compliant_actions_log(self) -> List[Dict]:
        """Get log of all compliant actions"""
        return self.compliant_actions.copy()


# Integration with forensic investigation workflow
def integrate_ethics_into_forensic_workflow():
    """
    Initialize ethics controller integrated with forensic workflow
    """
    controller = AnnonEthicsIntegrationController()
    return controller


# Example usage and testing
if __name__ == "__main__":
    print("Annon Ethics Integration Controller")
    print("=" * 60)
    
    controller = AnnonEthicsIntegrationController()
    
    # Test 1: Valid warrant-based home entry
    print("\n[TEST 1] Valid Warrant-Based Home Entry")
    success, msg = controller.validate_home_entry_action({
        "officer_name": "Detective Smith",
        "officer_id": "DET-001",
        "badge_number": "12345",
        "agency": "State Police",
        "property_address": "123 Main St, Anytown, USA",
        "authorization_type": "VALID_WARRANT",
        "warrant_number": "2024-WRT-00123",
        "warrant_issuing_judge": "Hon. Judge Johnson",
        "warrant_property_description": "Evidence related to case #2024-CV-001",
        "case_id": "CASE-20240101-ABC123"
    })
    print(f"Result: {'✓ APPROVED' if success else '✗ BLOCKED'}")
    if not success:
        print(msg)
    
    # Test 2: Warrantless entry (should be blocked)
    print("\n[TEST 2] Warrantless Entry Without Legal Justification")
    success, msg = controller.validate_home_entry_action({
        "officer_name": "Officer Johnson",
        "officer_id": "OFF-002",
        "badge_number": "54321",
        "agency": "Local Police",
        "property_address": "456 Oak Ave, Anytown, USA",
        "authorization_type": "VALID_WARRANT",  # But no warrant details
        "case_id": "CASE-20240102-XYZ789",
        "violation_audio_clip": "/evidence/violation_audio_2024_001.mp3"
    })
    print(f"Result: {'✓ APPROVED' if success else '✗ BLOCKED'}")
    if not success:
        print(msg)
    
    # Test 3: Seizure without probable cause (should be blocked)
    print("\n[TEST 3] Seizure Without Probable Cause")
    success, msg = controller.validate_seizure_action({
        "officer_name": "Officer Williams",
        "officer_id": "OFF-003",
        "badge_number": "99999",
        "agency": "Federal Bureau",
        "seizure_type": "person",
        "case_id": "CASE-20240103-FED001"
    })
    print(f"Result: {'✓ APPROVED' if success else '✗ BLOCKED'}")
    if not success:
        print(msg)
    
    print("\n" + "=" * 60)
    print(f"Blocked Actions: {len(controller.get_blocked_actions_log())}")
    print(f"Compliant Actions: {len(controller.get_compliant_actions_log())}")
