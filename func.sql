CREATE OR REPLACE FUNCTION elections.check_eligibility(
    user_id INT,
    is_candidate BOOLEAN,
    election_id INT
) RETURNS BOOLEAN AS $$
DECLARE
    age_check BOOLEAN;
    citizenship_check BOOLEAN;
    already_voted_check BOOLEAN;
    account_program_check BOOLEAN;
BEGIN
    -- Ветвление на кандидата и избирателя
    IF is_candidate THEN
        -- Проверка для кандидата

        -- 1. Проверка совершеннолетия (18 лет)
        SELECT (CURRENT_DATE - birth_date) / 365 >= 18
        INTO age_check
        FROM elections.candidate
        WHERE candidate_id = user_id;

        -- Если кандидат несовершеннолетний, вернуть FALSE
        IF NOT age_check THEN
            RETURN FALSE;
        END IF;

        -- 2. Проверка гражданства РФ
        SELECT country = 'Россия'
        INTO citizenship_check
        FROM elections.passport p
        JOIN elections.candidate c ON p.passport_id = c.passport_id
        WHERE c.candidate_id = user_id;

        -- Если гражданство не РФ, вернуть FALSE
        IF NOT citizenship_check THEN
            RETURN FALSE;
        END IF;

        -- 3. Проверка, что участие в этих выборах не принималось
        SELECT NOT EXISTS (
            SELECT 1 FROM elections.candidate_election as ce
            WHERE candidate_id = user_id AND ce.election_id = $3
        )
        INTO already_voted_check;

        -- Если кандидат уже участвовал в этих выборах, вернуть FALSE
        IF NOT already_voted_check THEN
            RETURN FALSE;
        END IF;

        -- 4. Проверка наличия программы и счета
        SELECT EXISTS (
            SELECT 1 FROM elections.candidate_account
            WHERE candidate_id = user_id
        ) AND EXISTS (
            SELECT 1 FROM elections.campaign_program
            WHERE candidate_id = user_id
        )
        INTO account_program_check;

        -- Если у кандидата нет программы или счета, вернуть FALSE
        IF NOT account_program_check THEN
            RETURN FALSE;
        END IF;

    ELSE
        -- Проверка для избирателя

        -- 1. Проверка совершеннолетия (18 лет)
        SELECT (CURRENT_DATE - birth_date) / 365 >= 18
        INTO age_check
        FROM elections.voter
        WHERE voter_id = user_id;

        -- Если избиратель несовершеннолетний, вернуть FALSE
        IF NOT age_check THEN
            RETURN FALSE;
        END IF;

        -- 2. Проверка гражданства РФ
        SELECT country = 'Россия'
        INTO citizenship_check
        FROM elections.passport p
        JOIN elections.voter v ON p.passport_id = v.passport_id
        WHERE v.voter_id = user_id;

        -- Если гражданство не РФ, вернуть FALSE
        IF NOT citizenship_check THEN
            RETURN FALSE;
        END IF;

        -- 3. Проверка, что участие в этих выборах не принималось
        SELECT NOT EXISTS (
            SELECT 1 FROM elections.voter_election as ve
            WHERE voter_id = user_id AND ve.election_id = $3
        )
        INTO already_voted_check;

        -- Если избиратель уже участвовал в этих выборах, вернуть FALSE
        IF NOT already_voted_check THEN
            RETURN FALSE;
        END IF;
    END IF;

    -- Если все условия выполнены, вернуть TRUE
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;


-- Проверка для кандидата с ID 1 на участие в выборах с ID 2
SELECT elections.check_eligibility(8, TRUE, 2);

-- Проверка для избирателя с ID 3 на участие в выборах с ID 2
SELECT elections.check_eligibility(6429, TRUE, 2);
