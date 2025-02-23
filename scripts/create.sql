CREATE SCHEMA IF NOT EXISTS elections;

-- DROP schema elections cascade;
--
--
--
-- delete * from elections.candidate;
-- delete * from elections.voter;
-- delete * from elections.vote;
-- delete * from elections.passport;
-- delete * from elections.voter_election;
-- delete * from elections.candidate_election;
-- delete * from elections.candidate_account;
-- delete * from elections.campaign_program;

--GRANT CONNECT ON DATABASE elections TO readonly_user;
--
---- Дать права на использование схемы (например, public)
--GRANT USAGE ON SCHEMA elections TO readonly_user;
--
---- Дать права на выборку (SELECT) на всех таблицах схемы public
--GRANT SELECT ON ALL TABLES IN SCHEMA elections TO readonly_user;
--
---- Настроить автоматическую выдачу прав SELECT на вновь создаваемых таблицах
--ALTER DEFAULT PRIVILEGES IN SCHEMA elections GRANT SELECT ON TABLES TO readonly_user;
--
---- Создаем роль для репликации с паролем
--CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'replicator_password';

CREATE TABLE IF NOT EXISTS elections.passport (
    passport_id SERIAL PRIMARY KEY,            -- Уникальный идентификатор паспорта
    passport_number VARCHAR(50) UNIQUE NOT NULL, -- Номер паспорта
    issued_by VARCHAR(255),                    -- Орган, выдавший паспорт
    issue_date DATE,                           -- Дата выдачи
    country VARCHAR(100) NOT NULL              -- Страна, выдавшая паспорт
);


CREATE TABLE IF NOT EXISTS elections.candidate (
    candidate_id SERIAL PRIMARY KEY,           -- Уникальный идентификатор кандидата
    full_name VARCHAR(255) NOT NULL,           -- Полное имя кандидата
    birth_date DATE NOT NULL CHECK (birth_date <= CURRENT_DATE), -- Дата рождения не может быть в будущем
    passport_id INT UNIQUE REFERENCES elections.passport(passport_id), -- Внешний ключ на паспорт кандидата
    campaign_program_id INT,                   -- Внешний ключ на предвыборную программу
    account_id INT,                            -- Внешний ключ на избирательный счет
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата добавления кандидата
);

CREATE TABLE IF NOT EXISTS elections.campaign_program (
    campaign_program_id SERIAL PRIMARY KEY,    -- Уникальный идентификатор программы
    candidate_id INT UNIQUE REFERENCES elections.candidate(candidate_id), -- Ссылка на кандидата
    description TEXT                           -- Описание предвыборной программы
);

CREATE TABLE IF NOT EXISTS elections.candidate_account (
    account_id SERIAL PRIMARY KEY,             -- Уникальный идентификатор счета
    candidate_id INT UNIQUE REFERENCES elections.candidate(candidate_id), -- Ссылка на кандидата
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.0 CHECK (balance >= 0), -- Баланс счета не может быть отрицательным
    last_transaction_date TIMESTAMP            -- Дата последней транзакции
);

--ALTER TABLE elections.candidate
--ADD CONSTRAINT IF NOT EXISTS fk_campaign_program FOREIGN KEY (campaign_program_id)
--REFERENCES elections.campaign_program(campaign_program_id);
--
--ALTER TABLE elections.candidate
--ADD CONSTRAINT IF NOT EXISTS fk_account FOREIGN KEY (account_id)
--REFERENCES elections.candidate_account(account_id);

CREATE TABLE IF NOT EXISTS elections.voter (
    voter_id SERIAL PRIMARY KEY,               -- Уникальный идентификатор избирателя
    full_name VARCHAR(255) NOT NULL,           -- Полное имя избирателя
    birth_date DATE NOT NULL CHECK (birth_date <= CURRENT_DATE), -- Дата рождения не может быть в будущем
    passport_id INT UNIQUE REFERENCES elections.passport(passport_id), -- Внешний ключ на паспорт избирателя
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Дата регистрации избирателя
);

-- Таблица выборов с ограничениями на даты
CREATE TABLE IF NOT EXISTS elections.election (
    election_id SERIAL PRIMARY KEY,            -- Уникальный идентификатор выборов
    election_name VARCHAR(255) NOT NULL,       -- Название выборов
    start_date DATE,
    end_date DATE CHECK (end_date >= start_date), -- Дата окончания не может быть раньше даты начала
    description TEXT                           -- Описание выборов
);


CREATE TABLE IF NOT EXISTS elections.vote (
    vote_id SERIAL PRIMARY KEY,                -- Уникальный идентификатор голоса
    voter_id INT REFERENCES elections.voter(voter_id) ON DELETE CASCADE, -- Ссылка на избирателя
    candidate_id INT REFERENCES elections.candidate(candidate_id) ON DELETE CASCADE, -- Ссылка на кандидата
    election_id INT REFERENCES elections.election(election_id) ON DELETE CASCADE, -- Ссылка на выборы
    vote_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Дата голосования
    CONSTRAINT unique_vote_per_election UNIQUE (voter_id, candidate_id, election_id) -- Уникальный голос в рамках одних выборов
);



CREATE TABLE IF NOT EXISTS elections.candidate_election (
    candidate_id INT REFERENCES elections.candidate(candidate_id) ON DELETE CASCADE,
    election_id INT REFERENCES elections.election(election_id) ON DELETE CASCADE,
    PRIMARY KEY (candidate_id, election_id)    -- Уникальная пара кандидат-выборы
);

CREATE TABLE IF NOT EXISTS elections.voter_election (
    voter_id INT REFERENCES elections.voter(voter_id) ON DELETE CASCADE,
    election_id INT REFERENCES elections.election(election_id) ON DELETE CASCADE,
    PRIMARY KEY (voter_id, election_id)        -- Уникальная пара избиратель-выборы
);








