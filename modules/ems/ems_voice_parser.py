import re
import time
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class EMSActionRecord:
    timestamp: float
    raw_transcript: str
    category: str  # 'MEDICATION', 'PROCEDURE', 'VITAL_SIGNS'
    entity: str
    dosage: str
    unit: str
    route: str

class EMSVoiceParser:
    def __init__(self):
        # Regular expressions for common EMS interventions
        self.med_pattern = re.compile(
            r'\b(administered|gave|giving|push|pushed|injected)\s+'
            r'(\d+(?:\.\d+)?)\s*(mg|mcg|g|ml|cc|units|puffs)?\s*(?:of\s+)?'
            r'([a-zA-Z\s]+?)\s*(?:via|iv|im|io|po|sq|sublingual|intranasal)?\b',
            re.IGNORECASE
        )
        self.route_pattern = re.compile(r'\b(iv|im|io|po|sq|sublingual|intranasal|endotracheal)\b', re.IGNORECASE)

    def parse_transcript(self, transcript_text: str) -> List[EMSActionRecord]:
        records = []
        now = time.time()
        
        # Process medication statements
        for match in self.med_pattern.finditer(transcript_text):
            action, amount, unit, med_name = match.groups()
            
            # Extract route if present in surrounding context
            route_match = self.route_pattern.search(transcript_text)
            route = route_match.group(1).upper() if route_match else "UNSPECIFIED"

            records.append(EMSActionRecord(
                timestamp=now,
                raw_transcript=transcript_text,
                category="MEDICATION",
                entity=med_name.strip().title(),
                dosage=amount,
                unit=unit.lower() if unit else "units",
                route=route
            ))

        return records
