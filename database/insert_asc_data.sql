-- Data Seeding for ASC Facilities and NPIs
-- Populates the healthcare_intel schema with real target data found via NPPES cross-referencing.

-- 1. Insert Private Equity Firms (if not exists)
INSERT INTO healthcare_intel.private_equity_firms (name, headquarters) VALUES
('Apollo Global Management', 'New York, NY'),
('Varsity Healthcare Partners', 'Los Angeles, CA'),
('FFL Partners', 'San Francisco, CA'),
('Bain Capital', 'Boston, MA'),
('KKR', 'New York, NY'),
('OMERS Private Equity', 'Toronto, Canada'),
('Kohlberg & Company', 'Mount Kisco, NY'),
('Oak Hill Capital', 'New York, NY')
ON CONFLICT DO NOTHING;

-- 2. Insert MSOs
INSERT INTO healthcare_intel.msos (name, pe_firm_id, website) VALUES
('GI Alliance', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'Apollo Global Management'), 'https://gialliance.com'),
('Orthopedic Care Partners', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'Varsity Healthcare Partners'), 'https://ocpmgmt.com'),
('US Orthopedic Partners', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'FFL Partners'), 'https://us-orthopartners.com'),
('AmSurg', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'KKR'), 'https://amsurg.com'),
('Gastro Health', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'OMERS Private Equity'), 'https://gastrohealth.com'),
('United Digestive', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'Kohlberg & Company'), 'https://uniteddigestive.com'),
('USPI', NULL, 'https://uspi.com'), -- Tenet Healthcare (Public)
('SCA Health', NULL, 'https://sca.health'), -- Optum (Public)
('US Oral Surgery Management', (SELECT pe_id FROM healthcare_intel.private_equity_firms WHERE name = 'Oak Hill Capital'), 'https://usosm.com');

-- 3. Insert Management Entities (Proxies for TIN groupings)
-- TINs are randomized for this example to maintain HIPAA/Private integrity in mock-up, but structured for real use.
INSERT INTO healthcare_intel.management_entities (tin, legal_name, mso_id) VALUES
('123456781', 'TDDC Southlake LLC', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'GI Alliance')),
('123456782', 'Steadman Philippon ASC Group', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'Orthopedic Care Partners')),
('123456783', 'MS Sports Medicine & Ortho Center', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'US Orthopedic Partners')),
('123456784', 'AmSurg Nashville Holdings', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'AmSurg')),
('123456785', 'Gastro Health Miami LLC', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'Gastro Health')),
('123456786', 'Digestive Healthcare GA', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'United Digestive')),
('123456787', 'USPI Florida Centers LLC', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'USPI')),
('123456788', 'Tuscan Surgery Partners', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'USPI')),
('123456789', 'SCA Rockies Holding', (SELECT mso_id FROM healthcare_intel.msos WHERE name = 'SCA Health'));

-- 4. Insert ASC Facilities (Real NPIs found in NPPES)
INSERT INTO healthcare_intel.asc_facilities (npi, facility_name, management_entity_id, city, state) VALUES
('1508871211', 'Southlake Endoscopy Center', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456781'), 'Southlake', 'TX'),
('1457892028', 'G.I. Alliance Pharmacy - Houston', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456781'), 'The Woodlands', 'TX'),
('1619577582', 'Steadman Philippon Surgery Center', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456782'), 'Basalt', 'CO'),
('1649515354', 'Florida Orthopaedic Institute Surgery Center', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456782'), 'Temple Terrace', 'FL'),
('1073946216', 'The Surgery Center at MS Sports Medicine', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456783'), 'Flowood', 'MS'),
('1386833044', 'Schuylkill Endoscopy Center', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456784'), 'Pottsville', 'PA'),
('1043497019', 'Endocentre of Baltimore', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456784'), 'Pikesville', 'MD'),
('1770645905', 'Endoscopic Surgical Centre of Maryland', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456784'), 'Silver Spring', 'MD'),
('1548414816', 'Miami Kendall FL Endoscopy ASC', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456785'), 'Miami', 'FL'),
('1558365247', 'Digestive Healthcare of Georgia - Atlanta', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456786'), 'Atlanta', 'GA'),
('1326453325', 'Capital City Surgery Center', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456787'), 'Tallahassee', 'FL'),
('1013227248', 'Tuscan Surgery Center at Las Colinas', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456788'), 'Irving', 'TX'),
('1447846704', 'Orthopaedic & Spine Center of the Rockies', (SELECT entity_id FROM healthcare_intel.management_entities WHERE tin = '123456789'), 'Loveland', 'CO');
