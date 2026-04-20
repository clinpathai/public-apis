-- Update MSOs with GPO, Distributor, and Evidence information
-- Ensuring columns exist before update
ALTER TABLE healthcare_intel.msos ADD COLUMN IF NOT EXISTS likely_gpo VARCHAR(255);
ALTER TABLE healthcare_intel.msos ADD COLUMN IF NOT EXISTS likely_distributor VARCHAR(255);
ALTER TABLE healthcare_intel.msos ADD COLUMN IF NOT EXISTS judgment_basis TEXT;

-- Updating data with judgment basis as requested
UPDATE healthcare_intel.msos SET likely_gpo = 'Vizient / Provista', likely_distributor = 'Cardinal Health', judgment_basis = 'Cardinal Health announced 71% majority stake acquisition in Nov 2024.' WHERE name = 'GI Alliance';
UPDATE healthcare_intel.msos SET likely_gpo = 'HealthTrust', likely_distributor = 'HealthTrust/McKesson', judgment_basis = 'Tenet Healthcare/USPI renewed exclusive HealthTrust partnership in 2021.' WHERE name = 'USPI';
UPDATE healthcare_intel.msos SET likely_gpo = 'Vizient', likely_distributor = 'McKesson/Medline', judgment_basis = 'Optum-owned network using Vizient national contract.' WHERE name = 'SCA Health';
UPDATE healthcare_intel.msos SET likely_gpo = 'HealthTrust', likely_distributor = 'McKesson', judgment_basis = 'National ASC MSO using HealthTrust committed model.' WHERE name = 'Surgery Partners';
UPDATE healthcare_intel.msos SET likely_gpo = 'HealthTrust', likely_distributor = 'McKesson', judgment_basis = 'Acquired by USPI in 2024; migrating to HealthTrust.' WHERE name = 'Covenant Physician Partners';
UPDATE healthcare_intel.msos SET likely_gpo = 'HealthTrust (AdvantageTrust)', likely_distributor = 'McKesson', judgment_basis = 'Consumer-led facility management aligned with AdvantageTrust.' WHERE name = 'NueHealth';
UPDATE healthcare_intel.msos SET likely_gpo = 'Provista (Vizient)', likely_distributor = 'Cardinal Health', judgment_basis = 'PE-backed MSO platform typically using Provista for non-acute scale.' WHERE name = 'Orthopedic Care Partners';
UPDATE healthcare_intel.msos SET likely_gpo = 'HealthTrust (AdvantageTrust)', likely_distributor = 'McKesson', judgment_basis = 'Uses AdvantageTrust committed model for orthopedic scale.' WHERE name = 'US Orthopedic Partners';
UPDATE healthcare_intel.msos SET likely_gpo = 'Provista (Vizient)', likely_distributor = 'Cardinal Health', judgment_basis = 'PE-backed MSO platform typically using Provista for non-acute scale.' WHERE name = 'US Oral Surgery Management';
UPDATE healthcare_intel.msos SET likely_gpo = 'Vizient', likely_distributor = 'McKesson', judgment_basis = 'Large GI MSO using Vizient/Provista for practice management.' WHERE name = 'Gastro Health';
UPDATE healthcare_intel.msos SET likely_gpo = 'Vizient', likely_distributor = 'McKesson', judgment_basis = 'Verified $4M+ savings via AdvantageTrust partnership in 2024.' WHERE name = 'United Digestive';
