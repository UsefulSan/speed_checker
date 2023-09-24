import psycopg2


def create_db():
    try:
        conn = psycopg2.connect(dbname="postgres", user="postgres", password="123456", host="localhost")
        cursor = conn.cursor()

        conn.autocommit = True
        sql = "CREATE DATABASE resources"

        cursor.execute(sql)
        print("База данных успешно создана")

        cursor.close()
        conn.close()
    except psycopg2.errors.DuplicateDatabase:
        print("База данных уже существует")


def create_table():
    conn = psycopg2.connect(dbname="resources", user="postgres", password="123456", host="localhost")
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


def fill_table():
    conn = psycopg2.connect(dbname="resources", user="postgres", password="123456", host="localhost")
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
