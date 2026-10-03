"""
Annon Ethics Integration Module
Integrates ethical framework with voice interface and evidence management
"""

from ethics_framework import (
    AnnonEthicsEngine, EvidencePackage, CustodianRecord, Report,
    ChainOfCustodyStatus, EthicalPrinciple
)
from datetime import datetime
from typing import Dict, Tuple, Optional
import uuid


class AnnonEthicsVoiceInterface:
    """
    Voice-enabled interface for ethical evidence management
    Enforces: Single submission per package, Amendment-only reports, Chain of custody
    """
    
    def __init__(self, engine: AnnonEthicsEngine = None):
        self.engine = engine or AnnonEthicsEngine()
        self.session_id = str(uuid.uuid4())
        self.voice_log: list = []
    
    def log_voice_action(self, action: str, user: str, details: Dict):
        """Log all voice-initiated actions"""
        self.voice_log.append({
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "action": action,
            "user": user,
            "details": details
        })
    
    def voice_submit_evidence(self, submitter_name: str, submitter_id: str,
                             submitter_role: str, organization: str,
                             evidence_description: str, evidence_data: Dict,
                             signature_hash: str) -> Tuple[bool, str]:
        """
        Voice-initiated evidence submission with full chain of custody
        
        SOP:
        1. Verify submitter credentials
        2. Create evidence package
        3. Establish chain of custody with submitter as initial custodian
        4. Submit with single-submission enforcement
        5. Return evidence receipt number
        """
        try:
            # Create custodian record for submitter
            submitter_custodian = CustodianRecord(
                custodian_name=submitter_name,
                custodian_id=submitter_id,
                role=submitter_role,
                organization=organization,
                handover_timestamp=datetime.now(),
                signature_hash=signature_hash,
                condition_notes=evidence_description
            )
            
            # Create evidence package
            package = EvidencePackage(
                package_id=f"PKG-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}",
                content_hash=self._compute_content_hash(evidence_data),
                timestamp=datetime.now(),
                submitter=submitter_name,
                submitter_id=submitter_id,
                submitter_role=submitter_role,
                submitter_organization=organization,
                evidence_data=evidence_data,
            )
            
            # Override initial custodian
            package.chain_of_custody.original_custodian = submitter_custodian
            package.chain_of_custody.custody_chain[0] = submitter_custodian
            
            # Submit evidence
            success, message = self.engine.submit_evidence(package)
            
            if success:
                receipt = self.engine.submission_registry.get_submission_proof(package.package_id)
                self.log_voice_action(
                    "submit_evidence",
                    submitter_name,
                    {"package_id": package.package_id, "receipt": receipt}
                )
                return True, f"✓ Evidence received. Receipt: {receipt['evidence_number']}"
            else:
                self.log_voice_action(
                    "submit_evidence_failed",
                    submitter_name,
                    {"error": message}
                )
                return False, message
                
        except Exception as e:
            error_msg = f"Error submitting evidence: {str(e)}"
            self.log_voice_action("submit_evidence_error", submitter_name, {"error": str(e)})
            return False, error_msg
    
    def voice_transfer_evidence(self, package_id: str, from_custodian_name: str,
                               from_custodian_id: str, from_role: str,
                               from_organization: str, from_signature: str,
                               to_custodian_name: str, to_custodian_id: str,
                               to_role: str, to_organization: str,
                               to_signature: str, transfer_notes: str = "") -> Tuple[bool, str]:
        """
        Voice-initiated evidence transfer with legal chain of custody compliance
        """
        try:
            # Verify package exists
            if not self.engine.submission_registry.is_submitted(package_id):
                return False, f"Package {package_id} not found in evidence system"
            
            from_custodian = CustodianRecord(
                custodian_name=from_custodian_name,
                custodian_id=from_custodian_id,
                role=from_role,
                organization=from_organization,
                handover_timestamp=datetime.now(),
                signature_hash=from_signature
            )
            
            to_custodian = CustodianRecord(
                custodian_name=to_custodian_name,
                custodian_id=to_custodian_id,
                role=to_role,
                organization=to_organization,
                handover_timestamp=datetime.now(),
                signature_hash=to_signature,
                location="Evidence Management System"
            )
            
            success, message = self.engine.transfer_evidence(
                package_id, from_custodian, to_custodian, transfer_notes
            )
            
            if success:
                self.log_voice_action(
                    "transfer_evidence",
                    to_custodian_name,
                    {"package_id": package_id, "from": from_custodian_name, "to": to_custodian_name}
                )
            else:
                self.log_voice_action(
                    "transfer_evidence_failed",
                    to_custodian_name,
                    {"error": message}
                )
            
            return success, message
            
        except Exception as e:
            error_msg = f"Transfer error: {str(e)}"
            self.log_voice_action("transfer_error", to_custodian_name, {"error": str(e)})
            return False, error_msg
    
    def voice_create_report(self, report_id: str, report_content: str,
                           created_by: str) -> Tuple[bool, str]:
        """
        Voice-initiated immutable report creation
        """
        try:
            report = self.engine.create_report(report_id, report_content, created_by)
            self.log_voice_action(
                "create_report",
                created_by,
                {"report_id": report_id, "original_hash": report.original_hash}
            )
            return True, f"✓ Report created: {report_id}"
        except Exception as e:
            self.log_voice_action(
                "create_report_error",
                created_by,
                {"error": str(e)}
            )
            return False, f"Report creation error: {str(e)}"
    
    def voice_amend_report(self, report_id: str, amendment_text: str,
                          reason: str, amended_by: str,
                          amendment_authority: str = "") -> Tuple[bool, str]:
        """
        Voice-initiated report amendment (original immutable)
        """
        try:
            amendment = self.engine.amend_report(
                report_id, amendment_text, reason, amended_by, amendment_authority
            )
            self.log_voice_action(
                "amend_report",
                amended_by,
                {"report_id": report_id, "amendment_id": amendment["amendment_id"]}
            )
            return True, f"✓ Report amended. Amendment ID: {amendment['amendment_id']}"
        except Exception as e:
            self.log_voice_action(
                "amend_report_error",
                amended_by,
                {"error": str(e)}
            )
            return False, f"Amendment error: {str(e)}"
    
    def voice_check_custody_chain(self, package_id: str) -> Tuple[bool, Dict]:
        """
        Voice query for evidence custody chain status
        """
        try:
            custody = self.engine.get_chain_of_custody(package_id)
            if not custody:
                return False, {"error": "Package not found"}
            
            self.log_voice_action(
                "check_custody_chain",
                "QUERY",
                {"package_id": package_id, "status": custody["current_status"]}
            )
            return True, custody
        except Exception as e:
            return False, {"error": str(e)}
    
    def _compute_content_hash(self, data: Dict) -> str:
        """Compute SHA256 hash of evidence data"""
        import hashlib
        import json
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_voice_session_log(self) -> list:
        """Retrieve complete voice action log for audit"""
        return self.voice_log.copy()


class AnnonEthicsCommandSet:
    """
    Natural language command interface for ethics operations
    Designed for voice activation via anon_voice_interface
    """
    
    def __init__(self, voice_interface: AnnonEthicsVoiceInterface = None):
        self.voice_interface = voice_interface or AnnonEthicsVoiceInterface()
        self.command_handlers = {
            "submit": self.handle_submit_command,
            "transfer": self.handle_transfer_command,
            "report": self.handle_report_command,
            "amend": self.handle_amend_command,
            "check": self.handle_check_command,
            "audit": self.handle_audit_command
        }
    
    def parse_command(self, command_text: str, context: Dict) -> Tuple[str, Dict, Dict]:
        """
        Parse natural language command
        Returns: (command_type, parameters, response)
        """
        command_lower = command_text.lower().strip()
        
        # Route to appropriate handler
        for cmd_type, handler in self.command_handlers.items():
            if cmd_type in command_lower:
                return cmd_type, context, handler(command_text, context)
        
        return "unknown", context, {"status": "error", "message": "Command not recognized"}
    
    def handle_submit_command(self, command: str, context: Dict) -> Dict:
        """Handle: Submit evidence [description]"""
        success, message = self.voice_interface.voice_submit_evidence(
            submitter_name=context.get("user_name", "Unknown"),
            submitter_id=context.get("user_id", ""),
            submitter_role=context.get("user_role", "Witness"),
            organization=context.get("organization", ""),
            evidence_description=command,
            evidence_data=context.get("evidence_data", {}),
            signature_hash=context.get("signature_hash", "")
        )
        return {
            "status": "success" if success else "error",
            "message": message
        }
    
    def handle_transfer_command(self, command: str, context: Dict) -> Dict:
        """Handle: Transfer evidence [package_id] from [from_name] to [to_name]"""
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
            "status": "success" if success else "error",
            "message": message
        }
    
    def handle_report_command(self, command: str, context: Dict) -> Dict:
        """Handle: Create report [report_id] [content]"""
        success, message = self.voice_interface.voice_create_report(
            report_id=context.get("report_id", f"RPT-{uuid.uuid4().hex[:8]}"),
            report_content=command,
            created_by=context.get("user_name", "System")
        )
        return {
            "status": "success" if success else "error",
            "message": message
        }
    
    def handle_amend_command(self, command: str, context: Dict) -> Dict:
        """Handle: Amend report [report_id] [amendment text]"""
        success, message = self.voice_interface.voice_amend_report(
            report_id=context.get("report_id", ""),
            amendment_text=command,
            reason=context.get("reason", ""),
            amended_by=context.get("user_name", "System"),
            amendment_authority=context.get("authority", "")
        )
        return {
            "status": "success" if success else "error",
            "message": message
        }
    
    def handle_check_command(self, command: str, context: Dict) -> Dict:
        """Handle: Check custody [package_id]"""
        success, custody = self.voice_interface.voice_check_custody_chain(
            package_id=context.get("package_id", "")
        )
        return {
            "status": "success" if success else "error",
            "data": custody
        }
    
    def handle_audit_command(self, command: str, context: Dict) -> Dict:
        """Handle: Audit [type] - returns complete audit trail"""
        audit_type = context.get("audit_type", "ethics")
        
        if audit_type == "voice":
            logs = self.voice_interface.get_voice_session_log()
        else:
            logs = self.voice_interface.engine.get_ethics_audit()
        
        return {
            "status": "success",
            "audit_type": audit_type,
            "entries": logs,
            "total_count": len(logs)
        }


# Initialize with ethical safeguards
def initialize_annon_with_ethics() -> AnnonEthicsVoiceInterface:
    """
    Initialize Annon AI-Personality with ethical framework
    
    Returns voice-enabled ethics interface ready for integration
    """
    engine = AnnonEthicsEngine()
    return AnnonEthicsVoiceInterface(engine)
