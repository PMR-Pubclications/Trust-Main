import hashlib
import json
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Set
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

# --- Cryptographic Libraries ---
from eth_account import Account as EthAccount
from eth_account.messages import encode_defunct
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature


# ==========================================
# 1. Models & Enums
# ==========================================
class SignatureScheme(str, Enum):
    EVM_ECDSA = "EVM_ECDSA"  # secp256k1 EIP-191 personal_sign (0x-hex)
    ED25519 = "ED25519"      # Ed25519 raw public key hex signature


class TrusteeSignature(BaseModel):
    trustee_id: str
    pubkey_or_address: str  # Ethereum address or Ed25519 public key hex
    scheme: SignatureScheme
    signature_hex: str      # Hex encoded signature
    signed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CanonicalTransactionPayload(BaseModel):
    trust_id: str
    disbursement_id: str
    amount: Decimal
    destination_account_id: str
    nonce: str  # Unique transaction nonce / timestamp to prevent replay attacks
    
    def to_canonical_bytes(self) -> bytes:
        """Deterministic UTF-8 payload serialization for cryptographic hashing."""
        payload_dict = {
            "trust_id": self.trust_id,
            "disbursement_id": self.disbursement_id,
            "amount": f"{self.amount:.2f}",
            "destination_account_id": self.destination_account_id,
            "nonce": self.nonce
        }
        # Sorted keys guarantee uniform byte rendering across all trustee environments
        canonical_json = json.dumps(payload_dict, sort_keys=True, separators=(',', ':'))
        return canonical_json.encode('utf-8')


class VerificationStatus(str, Enum):
    RELEASE_APPROVED = "RELEASE_APPROVED"
    FAILED_INVALID_SIGNATURE = "FAILED_INVALID_SIGNATURE"
    FAILED_INSUFFICIENT_QUORUM = "FAILED_INSUFFICIENT_QUORUM"
    FAILED_UNAUTHORIZED_ROLE = "FAILED_UNAUTHORIZED_ROLE"
    FAILED_DUPLICATE_SIGNER = "FAILED_DUPLICATE_SIGNER"


class VerificationReport(BaseModel):
    disbursement_id: str
    status: VerificationStatus
    required_signatures: int
    valid_signatures_count: int
    verified_trustees: List[str]
    errors: List[str] = Field(default_factory=list)


# ==========================================
# 2. Cryptographic Multi-Sig Verifier Engine
# ==========================================
class TrustSignatureVerifier:
    """Verifies cryptographic multi-sig approvals prior to disbursing Tier 3/4 capital."""

    def __init__(self, policy_governance: Dict):
        """
        :param policy_governance: Dict containing 'trustees' list from trust-policy.yaml
        """
        self.trustees_by_id = {t["id"]: t for t in policy_governance.get("trustees", [])}
        self.trustees_by_address = {
            t["pubkey_or_address"].lower(): t for t in policy_governance.get("trustees", [])
        }

    def _verify_evm_ecdsa(self, payload_bytes: bytes, signature_hex: str, expected_address: str) -> bool:
        """Verifies EIP-191 Ethereum personal_sign signatures against expected 0x address."""
        try:
            signable_msg = encode_defunct(primitive=payload_bytes)
            recovered_address = EthAccount.recover_message(signable_msg, signature=signature_hex)
            return recovered_address.lower() == expected_address.lower()
        except Exception:
            return False

    def _verify_ed25519(self, payload_bytes: bytes, signature_hex: str, pubkey_hex: str) -> bool:
        """Verifies raw Ed25519 signatures using public key hex."""
        try:
            public_key_bytes = bytes.fromhex(pubkey_hex.removeprefix("0x"))
            signature_bytes = bytes.fromhex(signature_hex.removeprefix("0x"))
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            public_key.verify(signature_bytes, payload_bytes)
            return True
        except (InvalidSignature, ValueError):
            return False

    def verify_transaction_release(
        self,
        payload: CanonicalTransactionPayload,
        signatures: List[TrusteeSignature],
        required_signatures: int,
        allowed_roles: List[str]
    ) -> VerificationReport:
        """
        Validates all signatures against transaction payload, trustee registry, and policy rules.
        """
        errors: List[str] = []
        verified_trustees: List[str] = []
        seen_signers: Set[str] = set()

        payload_bytes = payload.to_canonical_bytes()

        for idx, sig in enumerate(signatures):
            # 1. Check if trustee exists in policy
            trustee = self.trustees_by_id.get(sig.trustee_id)
            if not trustee:
                # Fallback address lookup
                trustee = self.trustees_by_address.get(sig.pubkey_or_address.lower())

            if not trustee:
                errors.append(f"Signature #{idx+1}: Trustee '{sig.trustee_id}' not found in trust policy registry.")
                continue

            trustee_id = trustee["id"]
            trustee_role = trustee["role"]
            registered_address = trustee["pubkey_or_address"]

            # 2. Prevent duplicate signatures from the same trustee
            if trustee_id in seen_signers:
                errors.append(f"Signature #{idx+1}: Duplicate signature detected for Trustee '{trustee_id}'.")
                continue

            # 3. Role Authorization Check
            if allowed_roles and trustee_role not in allowed_roles:
                errors.append(
                    f"Signature #{idx+1}: Trustee '{trustee_id}' has role '{trustee_role}' "
                    f"which is not authorized for this tier (Allowed: {allowed_roles})."
                )
                continue

            # 4. Cryptographic Verification
            is_valid = False
            if sig.scheme == SignatureScheme.EVM_ECDSA:
                is_valid = self._verify_evm_ecdsa(payload_bytes, sig.signature_hex, registered_address)
            elif sig.scheme == SignatureScheme.ED25519:
                is_valid = self._verify_ed25519(payload_bytes, sig.signature_hex, registered_address)

            if not is_valid:
                errors.append(f"Signature #{idx+1}: Invalid cryptographic signature for Trustee '{trustee_id}'.")
                continue

            # Signature is valid
            seen_signers.add(trustee_id)
            verified_trustees.append(f"{trustee_id} ({trustee_role})")

        valid_count = len(seen_signers)

        # 5. Evaluate Quorum Status
        if valid_count < required_signatures:
            status = VerificationStatus.FAILED_INSUFFICIENT_QUORUM
            errors.append(
                f"Quorum check failed: Received {valid_count} valid signatures, "
                f"but {required_signatures} are required by policy."
            )
        else:
            status = VerificationStatus.RELEASE_APPROVED

        return VerificationReport(
            disbursement_id=payload.disbursement_id,
            status=status,
            required_signatures=required_signatures,
            valid_signatures_count=valid_count,
            verified_trustees=verified_trustees,
            errors=errors
        )
