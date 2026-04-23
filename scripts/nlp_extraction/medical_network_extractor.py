import json
import re
import sys

class MedicalNetworkExtractor:
    def __init__(self):
        # Configuration for extraction
        self.doc_prefixes = [r'Dr\.', r'Professor', r'Prof\.', r'Dr']
        self.doc_suffixes = [r'MD', r'PhD', r'FACS', r'DO', r'M\.D\.|P\.H\.D\.', r'M\.P\.H\.', r'M\.S\.']
        self.inst_keywords = ["Hospital", "Cancer Center", "Center", "Institute", "University", "Medicine", "Clinic", "School of Medicine"]
        self.spec_keywords = [
            "oncologist", "cardiologist", "pathology specialist", "surgeon",
            "specialist", "physician", "internist", "pediatrician", "pathology"
        ]

    def clean_name(self, name):
        """Strips common prefixes and suffixes."""
        name = re.sub(r'^(?:' + '|'.join(self.doc_prefixes) + r')\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r',\s*(?:' + '|'.join(self.doc_suffixes) + r')\b', '', name, flags=re.IGNORECASE)
        return name.strip()

    def extract_doctors(self, text):
        docs = []
        # Pattern 1: [Prefix] [First] [Last]
        pref_pattern = "|".join(self.doc_prefixes)
        pattern1 = fr'\b(?:{pref_pattern})\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        for m in re.finditer(pattern1, text):
            docs.append({"name": self.clean_name(m.group(1)), "start": m.start(), "end": m.end()})

        # Pattern 2: [First] [Last], [Suffix]
        suff_pattern = "|".join(self.doc_suffixes)
        pattern2 = fr'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+),\s*(?:{suff_pattern})\b'
        for m in re.finditer(pattern2, text):
            docs.append({"name": self.clean_name(m.group(1)), "start": m.start(), "end": m.end()})

        # Deduplicate and handle overlaps
        unique_docs = []
        seen_ranges = []
        for d in sorted(docs, key=lambda x: len(x["name"]), reverse=True):
            overlap = False
            for r in seen_ranges:
                if d["start"] < r[1] and d["end"] > r[0]:
                    overlap = True
                    break
            if not overlap:
                unique_docs.append(d)
                seen_ranges.append((d["start"], d["end"]))

        return sorted(unique_docs, key=lambda x: x["start"])

    def extract_institutions(self, text):
        insts = []
        kw_pattern = "|".join(self.inst_keywords)
        # Handle "University of [Place]"
        pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + kw_pattern + r')|University of [A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        for m in re.finditer(pattern, text):
            insts.append({
                "name": m.group(0).strip(),
                "start": m.start(),
                "end": m.end()
            })
        return insts

    def find_specialty(self, text, doc_start, doc_end):
        window = 100
        start = max(0, doc_start - window)
        end = min(len(text), doc_end + window)
        context = text[start:end]
        for spec in self.spec_keywords:
            if re.search(fr'\b{spec}\b', context, re.IGNORECASE):
                if "pathology" in spec.lower(): return "Pathology Specialist"
                return spec.title()
        return None

    def extract(self, text):
        doctors = self.extract_doctors(text)
        institutions = self.extract_institutions(text)
        results = []

        # Map properties and build initial graph
        for doc in doctors:
            doc["specialty"] = self.find_specialty(text, doc["start"], doc["end"])

            # Find closest institution in text with directional priority
            best_inst = None
            min_dist = float('inf')
            for inst in institutions:
                # Priority: same sentence/proximity
                dist = abs(doc["start"] - inst["start"])
                if dist < 250:
                     # Check if it follows "at" or "from"
                     s = min(doc["start"], inst["start"])
                     e = max(doc["end"], inst["end"])
                     mid = text[s:e].lower()
                     weight = dist
                     if "at " in mid or "from " in mid:
                          weight -= 150 # Strong priority

                     if weight < min_dist:
                          min_dist = weight
                          best_inst = inst["name"]
            doc["inst"] = best_inst

        # Second pass for colleague inference
        for doc in doctors:
            if not doc["inst"]:
                # Look for "colleague" linking to another doctor with an institution
                for doc2 in doctors:
                    if doc2["name"] != doc["name"] and doc2["inst"]:
                         s = min(doc["start"], doc2["start"])
                         e = max(doc["end"], doc2["end"])
                         if "colleague" in text[s:e].lower():
                              doc["inst"] = doc2["inst"]
                              break

        # Build relationship list
        for doc in doctors:
            if doc["inst"]:
                results.append({
                    "source_node": {"type": "Doctor", "name": doc["name"], "specialty": doc["specialty"]},
                    "target_node": {"type": "Institution", "name": doc["inst"]},
                    "relationship": "AFFILIATED_WITH"
                })

        for i in range(len(doctors)):
            for j in range(i + 1, len(doctors)):
                d1, d2 = doctors[i], doctors[j]
                dist = abs(d1["start"] - d2["start"])
                if dist < 400:
                    s = min(d1["start"], d2["start"])
                    e = max(d1["end"], d2["end"])
                    context = text[max(0, s-50):min(len(text), e+50)].lower()

                    if any(x in context for x in ["published", "research", "clinical trial", "co-authored"]):
                        results.append({
                            "source_node": {"type": "Doctor", "name": d1["name"], "specialty": d1["specialty"]},
                            "target_node": {"type": "Doctor", "name": d2["name"], "specialty": d2["specialty"]},
                            "relationship": "CO_AUTHOR"
                        })
                    if any(x in context for x in ["colleague", "department", "closely", "team"]):
                        results.append({
                            "source_node": {"type": "Doctor", "name": d1["name"], "specialty": d1["specialty"]},
                            "target_node": {"type": "Doctor", "name": d2["name"], "specialty": d2["specialty"]},
                            "relationship": "COLLEAGUE"
                        })

        # Deduplication
        final_results = []
        seen_keys = set()
        for r in results:
            if r["target_node"]["type"] == "Doctor":
                names = sorted([r["source_node"]["name"], r["target_node"]["name"]])
                key = (r["relationship"], names[0], names[1])
            else:
                key = (r["relationship"], r["source_node"]["name"], r["target_node"]["name"])

            if key not in seen_keys:
                final_results.append(r)
                seen_keys.add(key)

        return json.dumps(final_results, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    if not sys.stdin.isatty():
        input_data = sys.stdin.read()
    elif len(sys.argv) > 1:
        input_data = sys.argv[1]
    else:
        input_data = ""
    extractor = MedicalNetworkExtractor()
    print(extractor.extract(input_data))
