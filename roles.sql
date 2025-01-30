CREATE ROLE election_admin NOINHERIT LOGIN PASSWORD 'admin_password';
CREATE ROLE voter NOINHERIT LOGIN PASSWORD 'voter_password';
CREATE ROLE candidate NOINHERIT LOGIN PASSWORD 'candidate_password';

-- election_admin
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA elections TO election_admin;
GRANT ALL PRIVILEGES ON SCHEMA elections TO election_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA elections TO election_admin;



-- voter
REVOKE UPDATE, DELETE ON ALL TABLES IN SCHEMA elections FROM voter;


GRANT SELECT ON elections.candidate TO voter;
GRANT SELECT ON elections.election TO voter;
GRANT SELECT on elections.candidate_account TO voter;
GRANT SELECT on elections.campaign_program TO voter;
GRANT INSERT ON elections.vote TO voter;
GRANT INSERT ON elections.voter TO voter;


-- candidate
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA elections FROM candidate;

GRANT SELECT ON elections.election TO candidate;
GRANT SELECT, INSERT, UPDATE ON elections.candidate TO candidate;
GRANT SELECT ON elections.campaign_program TO candidate;
GRANT SELECT ON elections.candidate_account TO candidate;
GRANT INSERT, UPDATE ON elections.campaign_program TO candidate;
GRANT INSERT, UPDATE ON elections.candidate_account TO candidate;

-- Установить дефолтную роль при подключении
ALTER ROLE voter SET ROLE=voter;
ALTER ROLE candidate SET ROLE=candidate;
ALTER ROLE election_admin SET ROLE=election_admin;
