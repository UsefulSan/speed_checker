import psycopg2


def create_db() -> None:
    """
    Создает новую базу данных с именем "resources" в PostgreSQL.

    Эта функция устанавливает соединение с сервером PostgreSQL, используя указанные имя базы данных, имя пользователя,
    пароль и хост. Затем создается новая база данных с именем "resources", если она еще не существует.

    Raises:
     - psycopg2.errors.DuplicateDatabase: Если база данных с именем "resources" уже существует.
    """
    try:
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="postgres")
        cursor = conn.cursor()

        conn.autocommit = True
        sql = "CREATE DATABASE resources"

        cursor.execute(sql)
        print("База данных успешно создана")

        cursor.close()
        conn.close()
    except psycopg2.errors.DuplicateDatabase:
        print("База данных уже существует")


def create_table() -> None:
    """
    Создает в базе данных "resources" новую таблицу "construction_equipment", если она еще не существует.

    Эта функция устанавливает соединение с базой данных с использованием предоставленных учетных данных и создает объект
     курсора для выполнения SQL-запросов.
    Выполняется SQL-запрос для создания таблицы "construction_equipment", если она еще не существует. 
    Таблица содержит следующие столбцы: 
    - id: SERIAL PRIMARY KEY 
    - type_equipment: VARCHAR(50) 
    - model: VARCHAR(50) 
    - speed: SMALLINT 
    - max_speed: SMALLINT

    После выполнения запроса изменения фиксируются в базе данных. Выводится сообщение о том, что таблица создана.

    Наконец, объекты курсора и соединения закрываются, чтобы освободить ресурсы. 
    """
    conn = psycopg2.connect(dbname="resources", user="postgres", password="123456", host="postgres")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS construction_equipment "
                   "(id SERIAL PRIMARY KEY, "
                   "type_equipment VARCHAR(50), "
                   "model VARCHAR(50), "
                   "speed SMALLINT, "
                   "max_speed SMALLINT)")

    conn.commit()
    print("Таблица создана")

    cursor.close()
    conn.close()


def fill_table() -> None:
    """
    Заполняет таблицу 'construction_equipment' в базе данных 'resources' заданными данными об оборудовании.
    Для взаимодействия с базой данных используется соединение с PostgreSQL.
    """
    conn = psycopg2.connect(dbname="resources", user="postgres", password="123456", host="postgres")
    cursor = conn.cursor()

    equipment = [('Dump Truck', '101', 63, 80),
                 ('Dump Truck', '102', 85, 80),
                 ('Excavator', 'Э103', 60, 40),
                 ('Excavator', 'Э104', 0, 40)]

    for eq in equipment:
        type_equipment, model, speed, max_speed = eq
        cursor.execute("SELECT COUNT(model) FROM construction_equipment WHERE model = %s", (model,))
        count = cursor.fetchone()[0]

        if count == 0:
            cursor.execute("INSERT INTO construction_equipment (type_equipment, model, speed, max_speed) "
                           "VALUES (%s, %s, %s, %s)", (type_equipment, model, speed, max_speed))

    conn.commit()

    print("Таблица успешно заполнена")
    cursor.close()
    conn.close()


if __name__ == '__main__':
    create_db()
    create_table()
    fill_table()
