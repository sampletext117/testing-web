Feature: Аутентификация пользователя

  # Сценарий успешного логина
  Scenario: Успешный логин
    Given Технический пользователь с email "tech@example.com" и паролем "secret"
    When Пользователь отправляет запрос на логин с этими данными
    Then В ответе должен быть получен JWT-токен и статус 200

  # Сценарий неуспешного логина
  Scenario: Неверный пароль при логине
    Given Технический пользователь с email "tech@example.com" и паролем "wrongpassword"
    When Пользователь отправляет запрос на логин с этими данными
    Then В ответе должна быть ошибка авторизации со статусом 401

  # Сценарий успешной смены пароля
  Scenario: Успешная смена пароля
    Given Технический пользователь с email "tech@example.com" и паролем "secret"
    And Пользователь успешно залогинен и получил токен
    When Пользователь отправляет запрос на смену пароля с текущим паролем "secret" и новым паролем "newsecret"
    Then Ответ подтверждает успешную смену пароля со статусом 200

  # Сценарий неуспешной смены пароля (неверный текущий пароль)
  Scenario: Смена пароля с неверным текущим паролем
    Given Технический пользователь с email "tech@example.com" и паролем "secret"
    And Пользователь успешно залогинен и получил токен
    When Пользователь отправляет запрос на смену пароля с текущим паролем "wrongsecret" и новым паролем "newsecret"
    Then В ответе должна быть ошибка смены пароля с сообщением 'Current password is incorrect' и статусом 400


  # Сценарий успешной двухфакторной аутентификации
  Scenario: Успешная двухфакторная аутентификация
    Given Технический пользователь с email "tech@example.com"
    When Пользователь отправляет запрос на 2FA с кодом "123456"
    Then Ответ подтверждает успешную валидацию 2FA со статусом 200

  # Сценарий неуспешной двухфакторной аутентификации
  Scenario: Неверный код двухфакторной аутентификации
    Given Технический пользователь с email "tech@example.com"
    When Пользователь отправляет запрос на 2FA с кодом "000000"
    Then В ответе должна быть ошибка с сообщением "Invalid 2FA code" и статусом 400
