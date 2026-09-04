// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TrustEvidenceMirror {
    struct EvidenceRecord {
        string caseNumber;
        string category;
        string description;
        uint256 timestamp;
        address submitter;
    }

    // Mapping from case number to its mirrored blockchain record
    mapping(string => EvidenceRecord) public evidenceMirror;

    event EvidenceMirrored(string indexed caseNumber, string category, uint256 timestamp);

    function recordEvidence(
        string memory _caseNumber, 
        string memory _category, 
        string memory _description
    ) public {
        require(bytes(evidenceMirror[_caseNumber].caseNumber).length == 0, "Evidence already recorded on-chain.");
        
        evidenceMirror[_caseNumber] = EvidenceRecord({
            caseNumber: _caseNumber,
            category: _category,
            description: _description,
            timestamp: block.timestamp,
            submitter: msg.sender
        });

        emit EvidenceMirrored(_caseNumber, _category, block.timestamp);
    }

    function getEvidence(string memory _caseNumber) public view returns (EvidenceRecord memory) {
        return evidenceMirror[_caseNumber];
    }
}
