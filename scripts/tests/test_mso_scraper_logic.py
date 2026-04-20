import unittest
from bs4 import BeautifulSoup
import sys
import os

# Add scripts directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../scripts')))

class TestScraperLogic(unittest.TestCase):
    def test_leadership_extraction(self):
        mock_html = """
        <div class="team-member">
            <h3 class="name">John Doe</h3>
            <span class="title">CEO</span>
        </div>
        <div class="executive">
            <h4 class="name">Jane Smith</h4>
            <p class="position">COO</p>
        </div>
        """
        soup = BeautifulSoup(mock_html, "html.parser")
        leadership_data = []
        team_members = soup.select(".team-member, .executive, .leader")
        for member in team_members:
            name = member.select_one("h3, h4, .name")
            title = member.select_one(".title, .position, .role")
            if name:
                name_text = name.get_text(strip=True)
                title_text = title.get_text(strip=True) if title else "N/A"
                leadership_data.append({"name": name_text, "title": title_text})

        self.assertEqual(len(leadership_data), 2)
        self.assertEqual(leadership_data[0]["name"], "John Doe")
        self.assertEqual(leadership_data[0]["title"], "CEO")
        self.assertEqual(leadership_data[1]["name"], "Jane Smith")
        self.assertEqual(leadership_data[1]["title"], "COO")

    def test_location_extraction(self):
        mock_html = """
        <div class="location">123 Health St, Dallas, TX 75201</div>
        <div itemprop="address">456 Surgery Ave, Nashville, TN 37203</div>
        """
        soup = BeautifulSoup(mock_html, "html.parser")
        locations_data = []
        address_elements = soup.select(".location, .address, [itemprop='address']")
        for el in address_elements:
            locations_data.append(el.get_text(separator=" ", strip=True))

        self.assertEqual(len(locations_data), 2)
        self.assertIn("123 Health St, Dallas, TX 75201", locations_data)
        self.assertIn("456 Surgery Ave, Nashville, TN 37203", locations_data)

if __name__ == "__main__":
    unittest.main()
