Feature: E2E scenario for eVoting with Pytest-BDD
  In order to verify the entire flow of the e-voting system,
  we want to test authentication, voter registration, candidate registration,
  election creation, voting, and results retrieval in one scenario.

  Scenario: Successful end-to-end process without external server
    Given a technical user with email "tech@example.com" and password "secret"
    When this user logs in and obtains a JWT token
    Then a token should be returned and status code is 200

    When the voter is registered with full_name "Voter One", birth_date "1990-01-01", passport_number "VOTER-PASS-125", issued_by "Voter Issuer", issue_date "2010-01-01", country "Россия"
    Then the voter_id is returned with status 201

    When the candidate is registered with full_name "Candidate One", birth_date "1975-05-05", passport_number "CAND-PASS-125", issued_by "Candidate Issuer", issue_date "2000-01-01", country "Россия", program_description "Test Program", initial_balance "1000.0"
    Then the candidate_id is returned with status 201

    When an election is created with election_name "E2E Test Election", start_date "today", end_date "tomorrow", description "Demo election"
    Then the election_id is returned with status 201

    When the voter votes for the candidate in that election
    Then a vote_id is returned with status 201

    When the results are requested for that election
    Then the results should indicate at least 1 vote
