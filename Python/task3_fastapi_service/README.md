# **API-сервис сокращения ссылок**

## Описание API

**Базовый URL**: https://localhost:9999/

### Аутентификация:

**Метод**: POST [/auth/register](https://colab.research.google.com/drive/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing) 

**Описание**: Регистрирует нового пользователя

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|Email|String |Да|Email пользователя(логин)|
|password|String|Да|Пароль пользователя|
|is\_active|Boolean|Да|Активен ли пользователь|
|is\_superuser|Boolean|Да|Права админа|
|is\_verified|Boolean|Да|Проверен ли пользователь|

**Пример запроса**:
```http
POST /auth/register HTTP/1.1
Host: localhost:9999
Content-Type: application/json
Accept: application/json

{
  "email": "user@example2.com",
  "password": "12345",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
``` 

**Пример ответа**:
```json
{
  "id": "c332c75a-5778-452c-a3c0-7170998458ea",
  "email": "user@example2.com",
  "is_active": true,
  "is_superuser": false,
  "is_verified": false
}
```

### Основные функции сервиса:

**Метод**: POST [/links/shorten](https://colab.research.google.com/drive/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing) 

**Описание**: Cоздает короткую ссылку из url

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|url|String|Да|URL адрес ресурса.|
|custom\_alias|String|Нет|создание кастомной ссылки|
|expires\_at|DateTime|Нет|создание c временем жизни ссылки|

**Пример запроса**:
```http
POST /links/shorten?url=https://dzen.ru/a/Z87t5cZ5tHURGX3q&custom_alias=dzen&expires_at=2025-03-23T15:50 HTTP/1.1
Host: localhost:9999
```

**Пример ответа**:
```json
{
  "status": "success",
  "short_link": "dzen",
  "expires_at": "2025-03-23T15:50:00"
}
```

**Метод**: GET /shorten\_links/links/{short\_code}

**Описание**:  Перенаправляет на оригинальный URL.

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|short\_code|String |Да|Короткая ссылка ресурса.|

**Пример запроса**:
```http
GET /shorten_links/links/dzen HTTP/1.1
Host: localhost:9999
```
**Пример ответа**:
```json
HTTP/1.1 200 OK
Location: https://dzen.ru/a/Z87t5cZ5tHURGX3q
```

**Метод**: DELETE /shorten\_links/links/{short\_code}

**Описание**: Удаляет связь с url и короткую ссылку.

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|short\_code|String |Да|Короткая ссылка ресурса.|

**Пример запроса**:
```http
DELETE /shorten_links/links/dzen HTTP/1.1
Host: localhost:9999
```
**Пример ответа**:
```json
{
  "status": "success deleted",
  "short_link": "dzen"
}
```
**Метод**: PUT /shorten\_links/links/{short\_code}

**Описание**: обновляет у URL короткую ссылку

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|short\_code|String |Да|Короткая ссылка ресурса.|
|new\_short\_code|String |Да|Новая короткая ссылка ресурса.|

**Пример запроса**:
```http
PUT /shorten_links/links/dzen1?new_short_code=dzen2 HTTP/1.1
Host: localhost:9999
```
**Пример ответа**:
```json
{
  "status": "success update",
  "new_short_link": "dzen2"
}
```
**Метод**: GET /links/{short\_code}/stats

**Описание**: Отображает оригинальный URL, возвращает дату создания, количество переходов, дату последнего использования

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|short\_code|String |Да|Короткая ссылка ресурса.|

**Пример запроса**:
```http
GET /shorten_links/links/search/?url=https://dzen1.ru/a/Z87t5cZ5tHURGX3q HTTP/1.1
Host: localhost:9999
```
**Пример ответа**:
```json
{
  "status": "success stats",
  "url": "https://dzen1.ru/a/Z87t5cZ5tHURGX3q",
  "date_create": "2025-03-23T13:04:57.195200",
  "clics_num": "3",
  "last_use_date": "2025-03-23T13:12:41.329115"
}
```
**Метод**: GET /shorten_links/links/search/

**Описание**: Поиск ссылки по оригинальному URL

**Параметры запроса**:

|**Параметр**|**Тип**|**Обязательный**|**Описание**|
| :-: | :-: | :-: | :-: |
|url|String |Да|ссылка на ресурс.|

**Пример запроса**:
```http
GET https://edu.tbank.ru/my-activities/courses/stream/723708e9-716c-4a0d-9060-411569841ec3/practice/40030743-3db4-4424-8210-98c5805ac6e8/overview HTTP/1.1
Host: localhost:9999
```
**Пример ответа**:
```json
{
  "status": "success",
  "short_link": "tb"
}
```

### Коды ответов

|**Код**|**Описание**|
| :-: | :-: |
|200|Успешный запрос.|
|201|Пользователь зарегистрирован|
|400|Неверный запрос (ошибка в данных).|
|401|Неавторизованный доступ.|
|403|Доступ запрещен.|
|404|Ресурс не найден.|
|500|Внутренняя ошибка сервера.|

## Описание БД

### База данных: ` shortening_links_db`

#### Общая информация
- **Версия PostgreSQL**: 17.4
- **Описание**: База данных для сервиса по созданию сокращенных сылок.
- **Владелец**: `postgress`
  
#### Схема: `public`
- **Описание**: Основная схема для хранения данных сервиса.
- **Таблицы**: `alembic_version`, `shorten_links`, `user`

#### Таблицы
##### `alembic_version`
- **Описание**: Содержит информацию о версиях миграций бд.
- **Владелец**: `admin`
- **Столбцы**:
  - `version_num`: ` varchar`, `PRIMARY KEY`, Уникальный идентификатор версии.

##### `shorten_links`
- **Описание**: Содержит информацию о созданных сокращенных ссылках.
- **Столбцы**:
  - `id`: `integer`, `PRIMARY KEY`, Уникальный идентификатор.
  - `url`: `varchar`, `NOT NULL UNIQUE `, Ссылка.
  - `short_link`: `varchar`, `NOT NULL UNIQUE `, Короткая ссылка.
  - `creation_date`: `datetime`, `NOT NULL`, Дата создания ссылки.
  - `last_use_date`: `datetime`, `NOT NULL`, Дата последнего использования ссылки.
  - `expires_at`: `datetime`, `NOT NULL`, Время действия ссылки.
  - `user_id`: `varchar`, `NOT NULL`, Id пользователя, создавшего ссылку.

##### `user`
- **Описание**: Содержит информацию о зарегистрированных пользователях.
- **Столбцы**:
  - `id`: `integer`, `PRIMARY KEY`, Уникальный идентификатор.
  - `email`: `varchar`, `NOT NULL UNIQUE `, Логин.
  - `hashed_password`: `varchar`, `NOT NULL`, Пароль.
  - `registered_at`: `datetime`, `NOT NULL`, Дата регистрации.
  - `is_active`: `boolean`, `NOT NULL`, Активен ли юзер
  - `is_superuser`: `boolean`, `NOT NULL`, Юзер админ
  - `is_verified`: `boolean`, `NOT NULL`, Верифицирован ли юзер


## Описание Redis для хранения подсчета кликов
**1. Общая информация**

Назначение: Redis используется для хранения и быстрого доступа к количеству кликов по коротким ссылкам (short\_link).

Тип хранилища: In-memory key-value хранилище.

Структура данных: Используется структура данных String (строка) для хранения счетчиков.

Ключи: Ключи формируются на основе short\_link.

Значения: Целочисленные значения, представляющие количество кликов.

**2. Функционал:**

- Увеличивает значение счетчика на 1. Если ключ не существует, он создается со значением 0.
- Получение значения счетчика
- Удаление счетчика: если происходит удаление или изменение ссылки, то счетчик обнуляется.

## Инструкция по запуску
1. Клонируем репозиторий
1. Запускаем докер-контейнер командой: docker-compose up –-build
1. Открываем сервис в браузере через Swagger UI: [http://localhost:9999/docs#](http://localhost:9999/docs)
1. Для проверки работы с авторизацией:

   - регистрируемся через ручку POST [/auth/register](https://colab.research.google.com/drive/1_XpbChwNfdSu0k2cBItKDfAX3YOWxU3S?usp=sharing)

   - нажимаем на замочек около ручки POST */shorten\_links/links/shorten* в [**ShortenLinks**](http://localhost:9999/docs#/ShortenLinks) и проходим аутенификацию пользователя.

   - продолжаем использовать различные ручки, удаление и изменение ссылки доступно только для пользователя, который ее создал




