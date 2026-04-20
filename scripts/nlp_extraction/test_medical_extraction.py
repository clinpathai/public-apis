import unittest
import json
from medical_network_extractor import MedicalNetworkExtractor

class TestMedicalNetworkExtractor(unittest.TestCase):
    def setUp(self):
        self.extractor = MedicalNetworkExtractor()

    def test_user_input_extraction(self):
        text = "Dr. Alice Wang, an attending oncologist at Memorial Sloan Kettering Cancer Center, recently published a clinical trial report on immunotherapy with Dr. James Wilson from the University of Pennsylvania. During this research, Dr. Wang collaborated closely with her departmental colleague, Dr. Emily Chen, a leading pathology specialist."

        result_json = self.extractor.extract(text)
        result = json.loads(result_json)

        # Check Doctors
        doctor_names = [r["source_node"]["name"] for r in result if r["source_node"]["type"] == "Doctor"] + \
                       [r["target_node"]["name"] for r in result if r["target_node"]["type"] == "Doctor"]
        doctor_names = list(set(doctor_names))

        self.assertIn("Alice Wang", doctor_names)
        self.assertIn("James Wilson", doctor_names)
        self.assertIn("Emily Chen", doctor_names)

        # Check Institutions
        institution_names = [r["target_node"]["name"] for r in result if r["target_node"]["type"] == "Institution"]
        self.assertIn("Memorial Sloan Kettering Cancer Center", institution_names)
        self.assertIn("University of Pennsylvania", institution_names)

        # Check Relationships
        relationships = [r["relationship"] for r in result]
        self.assertIn("AFFILIATED_WITH", relationships)
        self.assertIn("CO_AUTHOR", relationships)
        self.assertIn("COLLEAGUE", relationships)

        print("\nExtraction Result:")
        print(result_json)

    def test_clean_name(self):
        self.assertEqual(self.extractor.clean_name("Dr. Michael Chen"), "Michael Chen")

if __name__ == "__main__":
    unittest.main()
