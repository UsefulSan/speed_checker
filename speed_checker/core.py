import http.server
import json
import os
import re

import psycopg2
from dotenv import load_dotenv

load_dotenv()

host = "postgres" if os.environ.get("EXECUTION_ENVIRONMENT") == "DOCKER" else "localhost"

conn = psycopg2.connect(
    host=host,
    database="resources",
    user="postgres",
    password="123456")

cur = conn.cursor()



class MyHttpRequestHandler(http.server.CGIHTTPRequestHandler):
    def do_GET(self) -> None:
        """
        Обрабатывает метод запроса GET.

        Получает данные из таблицы construction_equipment в базе данных в соответствии с указанным путем и методом.
        Если путь - "/resource", а метод - "GET", то извлекаются все строки таблицы и добавляется колонка "over_speed",
        в которой показан % превышения максимальной скорости.
        Если путь имеет вид "/resource/?type_equipment=<type_equipment>", а метод - "GET", то из таблицы извлекаются
        строки, соответствующие шаблону type_equipment, и добавляется колонка "over_speed".
        Наконец, она отправляет ответ с кодом состояния 200, устанавливает в заголовке "Content-type" значение
        "application/json" и записывает в тело ответа полученные строки в виде JSON-строки.

        Эта функция не принимает никаких параметров и ничего не возвращает.
        """
        lst = self.requestline.split()
        method, path = lst[0], lst[1]
        if path == "/resource" and method == "GET":
            cur.execute("SELECT *, CASE WHEN speed > max_speed THEN ((speed * 100 / max_speed) - 100) ELSE NULL "
                        "END AS over_speed FROM construction_equipment")

        elif path.split('=')[0] == "/resource/?type_equipment" and method == "GET":
            type_equipment_pattern = path.split('=')[1]
            cur.execute("SELECT *, CASE WHEN speed > max_speed THEN ((speed * 100 / max_speed) - 100) ELSE NULL END "
                        "AS over_speed FROM construction_equipment WHERE type_equipment = %s",
                        (type_equipment_pattern,))

        rows = cur.fetchall()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(rows), "utf8"))

    def do_POST(self) -> None:
        """
        Обработка POST-запроса.
        Этот метод вызывается при поступлении на сервер POST-запроса.
        Он считывает тело запроса, проверяет данные и вставляет их в таблицу 'construction_equipment' в базе данных.
        """
        try:
            self.send_header("Content-type", "application/json")
            self.end_headers()
            content_length = self.headers.get('Content-Length')
            if isinstance(content_length, str):
                content_length = int(content_length)
                request_body = self.rfile.read(content_length)
                data = json.loads(request_body)
                if (isinstance(data["type_equipment"], str)
                        and isinstance(data["model"], str)
                        and isinstance(data["speed"], int)
                        and isinstance(data["max_speed"], int)):
                    cur.execute("INSERT INTO construction_equipment (type_equipment, model, speed, max_speed) "
                                "VALUES (%s, %s, %s, %s)",
                                (data["type_equipment"],
                                 data["model"],
                                 data["speed"],
                                 data["max_speed"]))
                    conn.commit()
                    self.send_response(201)
        except json.decoder.JSONDecodeError:
            self.send_error(400, "Bad request")

    def do_DELETE(self) -> None:
        """
        Отправляет на сервер запрос DELETE на удаление ресурса.

        Эта функция отправляет на сервер запрос DELETE на удаление ресурса на основе предоставленного идентификатора
        ресурса (идентификаторов). Она устанавливает для заголовка "Content-type" значение "application/json" и
        завершает заголовки запроса.
        """
        self.send_header("Content-type", "application/json")
        self.end_headers()
        resource_id_pattern = re.compile(r'^\/resource\/\?id=((\d+)?(,\d+)*)')
        match = resource_id_pattern.match(self.path)
        if match:
            resource_id = match.group(1)
            resource_id = resource_id.split(',')
            placeholders = ', '.join(resource_id)
            cur.execute(f"SELECT id FROM construction_equipment WHERE id IN ({placeholders})")
            result = cur.fetchall()
            if result:
                cur.execute(f"DELETE FROM construction_equipment WHERE id IN ({placeholders})")
                conn.commit()
                self.send_response(204)
            else:
                self.send_response(404, "Not found")

    def do_PUT(self) -> None:
        """
        Обрабатывает метод запроса PUT.

        Эта функция отвечает за обработку метода запроса PUT. Она извлекает идентификатор ресурса из пути URL и
        проверяет, существует ли ресурс в базе данных. Если ресурс существует, то на основе данных тела запроса
        происходит обновление соответствующих полей. В зависимости от успеха или неудачи операции обновления функция
        возвращает соответствующий код ответа.
        """
        resource_id_pattern = re.compile(r'^\/resource\/\?id=((\d+)?(,\d+)*)')
        match = resource_id_pattern.match(self.path)
        if match:
            resource_id = match.group(1)
            resource_id = resource_id.split(',')
            content_length = self.headers.get('Content-Length')
            if isinstance(content_length, str):
                content_length = int(content_length)
                request_body = self.rfile.read(content_length)
                data = json.loads(request_body)

            cur.execute(f"SELECT EXISTS(SELECT 1 FROM construction_equipment WHERE id = {resource_id[0]})")
            count = cur.fetchone()[0]
            if count == 0:
                self.send_response(400, "Bad request: No resource with the given ID")
                return

            updates = []
            update_values = []

            if isinstance(data.get("type_equipment"), str):
                updates.append("type_equipment = %s")
                update_values.append(data["type_equipment"])

            if isinstance(data.get("model"), str):
                updates.append("model = %s")
                update_values.append(data["model"])

            if isinstance(data.get("speed"), int):
                updates.append("speed = %s")
                update_values.append(data["speed"])

            if isinstance(data.get("max_speed"), int):
                updates.append("max_speed = %s")
                update_values.append(data["max_speed"])

            if updates:
                query = f"UPDATE construction_equipment SET {', '.join(updates)} WHERE id = %s"
                update_values.append(resource_id[0])
                cur.execute(query, tuple(update_values))
                conn.commit()
                self.send_response(201)
            else:
                self.send_response(400, "Bad request")
        else:
            self.send_response(404, "Not found")


if __name__ == "__main__":
    host = ''
    port = 8000
    handler = MyHttpRequestHandler
    httpd = http.server.HTTPServer((host, port), handler)
    print(f"Server running on port http://localhost:{port}/resource")
    httpd.serve_forever()

    # Закрытие соединения с базой данных
    cur.close()
    conn.close()
