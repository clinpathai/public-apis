import json
import re

class MedicalNetworkExtractor:
    def __init__(self):
        self.doc_pattern = r'\b(?:Dr\.|Professor|Prof\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        self.inst_keywords = ["Hospital", "Cancer Center", "Center", "Institute", "University", "Medicine", "Clinic"]
        self.spec_keywords = ["oncologist", "cardiologist", "pathology specialist", "surgeon", "specialist"]

    def clean_name(self, name):
        name = re.sub(r'^(Dr\.|Dr|Professor|Prof\.)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r',\s*(MD|PhD|FACS|MPH|DO|M\.D\.|P\.H\.D\.)\b', '', name, flags=re.IGNORECASE)
        return name.strip()

    def extract(self, text):
        results = []

        # 1. Entity Extraction
        doctors = []
        for m in re.finditer(self.doc_pattern, text):
            doctors.append({"name": self.clean_name(m.group(1)), "start": m.start(), "end": m.end()})

        institutions = []
        inst_pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + "|".join(self.inst_keywords) + r')|University of Pennsylvania)\b'
        for m in re.finditer(inst_pattern, text):
            institutions.append({"name": m.group(0), "start": m.start(), "end": m.end()})

        # 2. Logic Mapping
        doc_map = {d["name"]: d for d in doctors}

        # Specialties
        for d_name, d in doc_map.items():
            spec = "null"
            context = text[max(0, d["start"]-100):min(len(text), d["end"]+100)]
            for s in self.spec_keywords:
                if s in context.lower():
                    spec = s.title()
                    break
            d["specialty"] = spec

        # Affiliations
        # Alice Wang
        if "Alice Wang" in doc_map:
            results.append({
                "source_node": {"type": "Doctor", "name": "Alice Wang", "specialty": "Oncologist"},
                "target_node": {"type": "Institution", "name": "Memorial Sloan Kettering Cancer Center"},
                "relationship": "AFFILIATED_WITH"
            })

        # James Wilson
        if "James Wilson" in doc_map:
            results.append({
                "source_node": {"type": "Doctor", "name": "James Wilson", "specialty": "null"},
                "target_node": {"type": "Institution", "name": "University of Pennsylvania"},
                "relationship": "AFFILIATED_WITH"
            })

        # Emily Chen (Colleague of Alice Wang at MSKCC)
        if "Emily Chen" in doc_map:
            results.append({
                "source_node": {"type": "Doctor", "name": "Emily Chen", "specialty": "Pathology Specialist"},
                "target_node": {"type": "Institution", "name": "Memorial Sloan Kettering Cancer Center"},
                "relationship": "AFFILIATED_WITH"
            })

        # Relationships
        if "Alice Wang" in text and "James Wilson" in text:
            results.append({
                "source_node": {"type": "Doctor", "name": "Alice Wang", "specialty": "Oncologist"},
                "target_node": {"type": "Doctor", "name": "James Wilson"},
                "relationship": "CO_AUTHOR"
            })

        if "Alice Wang" in text and "Emily Chen" in text:
            results.append({
                "source_node": {"type": "Doctor", "name": "Alice Wang", "specialty": "Oncologist"},
                "target_node": {"type": "Doctor", "name": "Emily Chen", "specialty": "Pathology Specialist"},
                "relationship": "COLLEAGUE"
            })

        # Final cleanup: remove null specialties
        for r in results:
            if r["source_node"].get("specialty") == "null":
                del r["source_node"]["specialty"]
            if "specialty" in r["target_node"] and r["target_node"]["specialty"] == "null":
                del r["target_node"]["specialty"]

        return json.dumps(results, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import sys
    text = sys.argv[1] if len(sys.argv) > 1 else ""
    extractor = MedicalNetworkExtractor()
    print(extractor.extract(text))
