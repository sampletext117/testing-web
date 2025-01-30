from datetime import date

def typical_voter_data():
    return {
        "full_name": "Стандартный Тестов",
        "birth_date": date(1990, 1, 1),
        "passport_number": "9999 111111",
        "issued_by": "УФМС г.Москвы",
        "issue_date": date(2010, 1, 1),
        "country": "Россия"
    }

def voter_under_age_data():
    return {
        "full_name": "Молодой Тестов",
        "birth_date": date(2010, 1, 1),
        "passport_number": "0000 123456",
        "issued_by": "УФМС",
        "issue_date": date(2018, 1, 1),
        "country": "Россия"
    }
