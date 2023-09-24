import http.server
import json
import re

import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="resources",
    user="postgres",
    password="123456")

# Создание запроса
cur = conn.cursor()


class MyHttpRequestHandler(http.server.CGIHTTPRequestHandler):
    def do_GET(self):
        cur.execute("SELECT * FROM construction_equipment;")
        rows = cur.fetchall()

        lst = self.requestline.split()
        method, path = lst[0], lst[1]
        if path == "/resource" and method == "GET":
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(bytes(json.dumps(rows), "utf8"))
            self.send_response(200)

    def do_POST(self) -> None:
        try:
            self.send_header("Content-type", "application/json")
            self.end_headers()
            content_length = int(self.headers.get('Content-Length'))
            request_body = self.rfile.read(content_length)
            data = json.loads(request_body)
            if (isinstance(data["type_equipment"], str) and isinstance(data["model"], str)
                    and isinstance(data["speed"], int) and isinstance(data["max_speed"], int)):
                cur.execute("INSERT INTO construction_equipment (type_equipment, model, speed, max_speed) "
                            "VALUES (%s, %s, %s, %s)", (data["type_equipment"], data["model"], data["speed"],
                                                        data["max_speed"]))
                conn.commit()
                self.send_response(201)
            else:
                self.send_error(400, "Bad request")
        except json.decoder.JSONDecodeError:
            self.send_error(400, "Bad request")

    def do_DELETE(self) -> None:
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
        self.send_header("Content-type", "application/json")
        self.end_headers()
        resource_id_pattern = re.compile(r'^\/resource\/\?id=((\d+)?(,\d+)*)')
        match = resource_id_pattern.match(self.path)
        if match:
            resource_id = match.group(1)
            resource_id = resource_id.split(',')
            if len(resource_id) == 1:
                cur.execute(f"UPDATE construction_equipment SET id FROM construction_equipment "
                            f"WHERE id = {resource_id[0]}")
                conn.commit()
                self.send_response(201)
            else:
                self.send_response(404, "Bad request")


if __name__ == "__main__":
    host = 'localhost'
    port = 8000
    handler = MyHttpRequestHandler
    httpd = http.server.HTTPServer((host, port), handler)
    print(f"Server running on port http://{host}:{port}")
    httpd.serve_forever()

    # Закрытие соединения с базой данных
    cur.close()
    conn.close()
