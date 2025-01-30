import psycopg2
from psycopg2 import sql
from faker import Faker
import random
from datetime import timedelta, date

# Создание объекта Faker для генерации данных
fake = Faker('ru_RU')


# Функция для генерации случайной даты рождения
def generate_birth_date(min_age, max_age):
    today = date.today()
    birth_date = today - timedelta(days=random.randint(min_age * 365, max_age * 365))
    return birth_date


# Подключение к базе данных
def connect_to_db():
    return psycopg2.connect(
        dbname="elections",
        user="election_admin",
        password="admin_password",
        host="localhost",
        port="5432"
    )


# Генерация и вставка данных в таблицу passport
def insert_passports(conn, num_passports=100):
    with conn.cursor() as cur:
        for _ in range(num_passports):
            passport_number = fake.unique.random_number(digits=10)
            issued_by = fake.company()
            issue_date = fake.date_between(start_date="-30y", end_date="today")
            country = "Россия" if random.random() > 0.1 else fake.country()

            cur.execute(
                "INSERT INTO elections.passport (passport_number, issued_by, issue_date, country) VALUES (%s, %s, %s, %s) RETURNING passport_id",
                (passport_number, issued_by, issue_date, country)
            )
        conn.commit()


# Генерация и вставка данных в таблицы candidate, voter и участие в выборах
def insert_candidates_voters(conn, num_candidates=20, num_voters=80, num_elections=5):
    with conn.cursor() as cur:
        used_passports = set()  # Для отслеживания уже использованных паспортов

        # Вставка кандидатов и их участие в выборах
        for candidate_id in range(1, num_candidates + 1):
            full_name = fake.name()
            birth_date = generate_birth_date(min_age=14, max_age=80)
            passport_id = candidate_id  # Уникальный паспорт для каждого кандидата

            # Вставка кандидата
            cur.execute(
                "INSERT INTO elections.candidate (full_name, birth_date, passport_id) VALUES (%s, %s, %s) RETURNING candidate_id",
                (full_name, birth_date, passport_id)
            )
            used_passports.add(passport_id)

            # Вставка кандидатов в выборы (случайные выборы)
            election_id = random.randint(1, num_elections)
            cur.execute(
                "INSERT INTO elections.candidate_election (candidate_id, election_id) VALUES (%s, %s)",
                (candidate_id, election_id)
            )

            # Вставка программы и счета для кандидата
            program_description = fake.text(max_nb_chars=100)
            balance = random.uniform(0, 50000.0)

            # Вставка данных в campaign_program и сохранение campaign_program_id
            cur.execute(
                "INSERT INTO elections.campaign_program (candidate_id, description) VALUES (%s, %s) RETURNING campaign_program_id",
                (candidate_id, program_description)
            )
            campaign_program_id = cur.fetchone()[0]

            # Вставка данных в candidate_account и сохранение account_id
            cur.execute(
                "INSERT INTO elections.candidate_account (candidate_id, balance, last_transaction_date) VALUES (%s, %s, %s) RETURNING account_id",
                (candidate_id, balance, fake.date_between(start_date="-1y", end_date="today"))
            )
            account_id = cur.fetchone()[0]

            # Обновление таблицы candidate, чтобы добавить значения campaign_program_id и account_id
            cur.execute(
                "UPDATE elections.candidate SET campaign_program_id = %s, account_id = %s WHERE candidate_id = %s",
                (campaign_program_id, account_id, candidate_id)
            )

        # Вставка избирателей и их участие в выборах
        for voter_id in range(1, num_voters + 1):
            full_name = fake.name()
            birth_date = generate_birth_date(min_age=14, max_age=80)
            passport_id = num_candidates + voter_id  # Уникальный паспорт для каждого избирателя

            cur.execute(
                "INSERT INTO elections.voter (full_name, birth_date, passport_id) VALUES (%s, %s, %s) RETURNING voter_id",
                (full_name, birth_date, passport_id)
            )
            used_passports.add(passport_id)

            # Вставка избирателей в выборы (случайные выборы)
            election_id = random.randint(1, num_elections)
            cur.execute(
                "INSERT INTO elections.voter_election (voter_id, election_id) VALUES (%s, %s)",
                (voter_id, election_id)
            )

        conn.commit()


# Генерация и вставка данных в таблицу election
def insert_elections(conn, num_elections):
    with conn.cursor() as cur:
        for election_id in range(1, num_elections + 1):
            election_name = fake.sentence(nb_words=3)
            start_date = fake.date_between(start_date="-2y", end_date="today")
            end_date = start_date + timedelta(days=random.randint(1, 14))
            description = fake.text(max_nb_chars=200)

            cur.execute(
                "INSERT INTO elections.election (election_name, start_date, end_date, description) VALUES (%s, %s, %s, %s) RETURNING election_id",
                (election_name, start_date, end_date, description)
            )
        conn.commit()


# Генерация и вставка данных в таблицу vote (голоса) с проверкой уникальности
def insert_votes(conn, num_votes=100, num_candidates=20, num_elections=5):
    with conn.cursor() as cur:
        # Получение списка всех существующих voter_id
        cur.execute("SELECT voter_id FROM elections.voter")
        voter_ids = [row[0] for row in cur.fetchall()]  # Получаем все существующие voter_id

        # Проверка, что существуют хотя бы num_votes избирателей
        if len(voter_ids) < num_votes:
            raise ValueError("Количество голосов превышает количество избирателей.")

        # set используется для хранения уникальных комбинаций (voter_id, election_id)
        vote_combinations = set()

        for _ in range(num_votes):
            voter_id = random.choice(voter_ids)  # Выбираем случайный voter_id из существующих
            candidate_id = random.randint(1, num_candidates)  # Из 20 возможных кандидатов
            election_id = random.randint(1, num_elections)  # Из 5 возможных выборов

            # Проверка уникальности комбинации (voter_id, election_id)
            if (voter_id, election_id) not in vote_combinations:
                cur.execute(
                    "INSERT INTO elections.vote (voter_id, candidate_id, election_id) VALUES (%s, %s, %s)",
                    (voter_id, candidate_id, election_id)
                )
                vote_combinations.add((voter_id, election_id))

        conn.commit()

# Основная функция
def main():
    # Подключение к базе данных
    conn = connect_to_db()

    try:
        # Вставка данные
        print(1)
        insert_passports(conn, num_passports=200000)
        print(2)
        insert_elections(conn, num_elections=100000)
        print(3)
        insert_candidates_voters(conn, num_candidates=100000, num_voters=100000, num_elections=100000)
        print(4)
        insert_votes(conn, num_votes=100000, num_candidates=100000, num_elections=100000)
        print("Данные успешно вставлены.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
