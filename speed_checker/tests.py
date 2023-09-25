import unittest
from unittest.mock import MagicMock

from speed_checker.core import MyHttpRequestHandler


class TestDoGET(unittest.TestCase):

    def test_do_GET_resource_GET(self) -> None:
        """
        Тестовый пример для GET-запроса к "/resource"

        - Убедитесь, что SQL-запрос выполнен корректно;
        - Убедитесь, что код состояния ответа равен 200;
        - Убедитесь, что в заголовке типа содержимого ответа установлено значение "application/json";
        - Убедитесь, что тело ответа содержит ожидаемые JSON-данные.
        """
        # Set up
        mock_self = MagicMock()
        print(mock_self.requestline)
        mock_self.requestline = "GET /resource"
        mock_cur = MagicMock()
        print(mock_cur)
        mock_cur.fetchall.return_value = [("Dump Truck", "101", 63, 80), ('Dump Truck', '102', 85, 80),
                                          ("Excavator", "Э103", 60, 40), ("Excavator", "Э104", 0, 40)]
        mock_self.send_response = MagicMock()
        mock_self.send_header = MagicMock()
        mock_self.end_headers = MagicMock()
        mock_self.wfile.write = MagicMock()

        # Execute
        MyHttpRequestHandler.do_GET(mock_self)

        # Assert
        mock_cur.execute.assert_called_with(
            "SELECT *, CASE WHEN speed > max_speed THEN ((speed * 100 / max_speed) - 100) ELSE NULL END AS over_speed "
            "FROM construction_equipment")
        mock_cur.fetchall.assert_called_once()
        mock_self.send_response.assert_called_with(200)
        mock_self.send_header.assert_called_with("Content-type", "application/json")
        mock_self.end_headers.assert_called_once()
        mock_self.wfile.write.assert_called_with(b'[[22, "Dump Truck", "101", 63, 80, null], '
                                                 b'[23, "Dump Truck", "102", 85, 80, 6], '
                                                 b'[24, "Excavator", "\u042d103", 60, 40, 50], '
                                                 b'[25, "Excavator", "\u042d104", 0, 40, null]]')

    def test_do_GET_resource_type_equipment_GET(self) -> None:
        """
        Тестовый пример для GET-запроса к "/resource/?type_equipment=<type_equipment>"

        - Убедитесь, что SQL-запрос выполнен корректно; 
        - Убедитесь, что код состояния ответа равен 200; 
        - Убедитесь, что в заголовке типа содержимого ответа установлено значение "application/json"; 
        - Убедитесь, что тело ответа содержит ожидаемые JSON-данные.
        """
        # Set up
        mock_self = MagicMock()
        mock_self.requestline = "GET /resource/?type_equipment=excavator"
        mock_cur = MagicMock()
        mock_cur.fetchall.return_value = [('equipment1', 100, 80, 20), ('equipment2', 120, 100, 20)]
        mock_self.send_response = MagicMock()
        mock_self.send_header = MagicMock()
        mock_self.end_headers = MagicMock()
        mock_self.wfile.write = MagicMock()

        # Execute
        MyHttpRequestHandler.do_GET(mock_self)

        # Assert
        mock_cur.execute.assert_called_with(
            "SELECT *, CASE WHEN speed > max_speed THEN ((speed * 100 / max_speed) - 100) ELSE NULL END AS over_speed "
            "FROM construction_equipment WHERE type_equipment = %s",
            ('excavator',))
        mock_cur.fetchall.assert_called_once()
        mock_self.send_response.assert_called_with(200)
        mock_self.send_header.assert_called_with("Content-type", "application/json")
        mock_self.end_headers.assert_called_once()
        mock_self.wfile.write.assert_called_with(b'[["equipment1", 100, 80, 20], ["equipment2", 120, 100, 20]]')


class TestDoPUT(unittest.TestCase):
    def setUp(self) -> None:
        self.request = MagicMock()

    def test_valid_resource_id_valid_data(self) -> None:
        self.request.path = "/resource/?id=1"
        self.request.headers = {'Content-Length': '50'}
        self.request.rfile.read.return_value = (b'{"type_equipment": "excavator", '
                                                b'"model": "model1", '
                                                b'"speed": 10, '
                                                b'"max_speed": 20}')

        # Call the do_PUT function or the object containing the function
        # and assert the expected response
        # Example: obj.do_PUT()

    def test_valid_resource_id_missing_data(self) -> None:
        self.request.path = "/resource/?id=1"
        self.request.headers = {'Content-Length': '50'}
        self.request.rfile.read.return_value = b'{"model": "model1", "speed": 10}'

        # Call the do_PUT function or the object containing the function
        # and assert the expected response
        # Example: obj.do_PUT()

    def test_invalid_resource_id(self) -> None:
        self.request.path = "/resource/?id=100"
        self.request.headers = {'Content-Length': '50'}
        self.request.rfile.read.return_value = (b'{"type_equipment": "excavator", '
                                                b'"model": "model1", "speed": 10, "max_speed": 20}')

        # Call the do_PUT function or the object containing the function
        # and assert the expected response
        # Example: obj.do_PUT()

    def test_invalid_url_path(self) -> None:
        self.request.path = "/invalid_path"
        self.request.headers = {'Content-Length': '50'}
        self.request.rfile.read.return_value = (b'{"type_equipment": "excavator", "model": "model1", '
                                                b'"speed": 10, "max_speed": 20}')

        # Call the do_PUT function or the object containing the function
        # and assert the


if __name__ == '__main__':
    unittest.main()
