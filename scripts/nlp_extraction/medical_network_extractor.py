import json
import re
import sys

class MedicalNetworkExtractor:
    def __init__(self):
        # Configuration for heuristics
        self.spec_keywords = [
            "oncologist", "cardiologist", "pathology specialist", "surgeon",
            "specialist", "physician", "internist", "pediatrician", "pathology"
        ]
        self.inst_keywords = ["Hospital", "Cancer Center", "Center", "Institute", "University", "Medicine", "Clinic", "School of Medicine"]

    def clean_name(self, name):
        """Strips Dr., MD, etc."""
        name = re.sub(r'^(Dr\.|Professor|Prof\.)\s+', '', name, flags=re.IGNORECASE)
        name = re.sub(r',\s*(MD|PhD|FACS|MPH|DO|M\.D\.|P\.H\.D\.|F\.A\.C\.S\.)\b', '', name, flags=re.IGNORECASE)
        return name.strip()

    def extract(self, text):
        results = []

        # 1. Standardize for regex
        norm_text = text.replace("Dr. ", "Dr_")

        # 2. Identify Doctors
        docs = []
        doc_pattern = r'Dr_([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
        for m in re.finditer(doc_pattern, norm_text):
            full_name = m.group(1)
            docs.append({
                "name": self.clean_name(full_name),
                "start": m.start(),
                "end": m.end(),
                "institution": None,
                "specialty": None
            })

        # 3. Identify Institutions
        insts = []
        kw_pattern = "|".join(self.inst_keywords)
        inst_pattern = r'\b(?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:' + kw_pattern + r')|University of Pennsylvania)\b'
        for m in re.finditer(inst_pattern, norm_text):
            insts.append({
                "name": m.group(0).strip(),
                "start": m.start(),
                "end": m.end()
            })

        # 4. Sentence Split
        sentences_norm = re.split(r'\.\s+', norm_text)
        sentences = [s.replace("Dr_", "Dr. ") for s in sentences_norm]

        # 5. Specialties
        for doc in docs:
            ctx = norm_text[max(0, doc["start"]-100):min(len(norm_text), doc["end"]+100)]
            for s in self.spec_keywords:
                if re.search(fr'\b{s}\b', ctx, re.IGNORECASE):
                    if "pathology" in s.lower():
                        doc["specialty"] = "Pathology Specialist"
                    else:
                        doc["specialty"] = s.title()
                    break

        # 6. Direct Affiliations (same sentence)
        for doc in docs:
            for snt in sentences:
                if doc["name"] in snt or doc["name"].split()[-1] in snt:
                    for inst in insts:
                        if inst["name"] in snt:
                            # Direct check
                            if re.search(fr'\b{re.escape(doc["name"].split()[-1])}\b.*?\b(?:at|from)\b.*?\b{re.escape(inst["name"])}\b', snt, re.IGNORECASE):
                                doc["institution"] = inst["name"]
                                break
                    if doc["institution"]: break

        # 7. Colleague Inference
        for doc in docs:
            if not doc["institution"]:
                 for snt in sentences:
                      if doc["name"] in snt or doc["name"].split()[-1] in snt:
                           if "colleague" in snt.lower():
                                for other in docs:
                                     if other["name"] != doc["name"] and other["institution"]:
                                          if other["name"] in snt or other["name"].split()[-1] in snt:
                                               doc["institution"] = other["institution"]
                                               break
                      if doc["institution"]: break

        # 8. Affiliation results
        for doc in docs:
            if doc["institution"]:
                results.append({
                    "source_node": {"type": "Doctor", "name": doc["name"], "specialty": doc["specialty"]},
                    "target_node": {"type": "Institution", "name": doc["institution"]},
                    "relationship": "AFFILIATED_WITH"
                })

        # 9. Collaborations
        for snt in sentences:
            sent_docs = []
            for d in docs:
                if d["name"] in snt or d["name"].split()[-1] in snt:
                    sent_docs.append(d)

            u_docs = []
            u_names = set()
            for sd in sent_docs:
                if sd["name"] not in u_names:
                    u_docs.append(sd)
                    u_names.add(sd["name"])

            if len(u_docs) >= 2:
                is_coauthor = any(x in snt.lower() for x in ["published", "research", "clinical trial", "paper"])
                is_colleague = any(x in snt.lower() for x in ["colleague", "department", "closely"])

                for i in range(len(u_docs)):
                    for j in range(i + 1, len(u_docs)):
                        d1 = u_docs[i]
                        d2 = u_docs[j]
                        if is_coauthor:
                            results.append({
                                "source_node": {"type": "Doctor", "name": d1["name"], "specialty": d1["specialty"]},
                                "target_node": {"type": "Doctor", "name": d2["name"], "specialty": d2["specialty"]},
                                "relationship": "CO_AUTHOR"
                            })
                        if is_colleague:
                            results.append({
                                "source_node": {"type": "Doctor", "name": d1["name"], "specialty": d1["specialty"]},
                                "target_node": {"type": "Doctor", "name": d2["name"], "specialty": d2["specialty"]},
                                "relationship": "COLLEAGUE"
                            })

        # 10. Deduplication
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
    t = sys.stdin.read() if not sys.stdin.isatty() else (sys.argv[1] if len(sys.argv) > 1 else "")
    print(MedicalNetworkExtractor().extract(t))
