# Speed checker

![Python](https://img.shields.io/badge/-Python-05122A?style=flat&logo=python)&nbsp;
![Docker](https://img.shields.io/badge/-Docker-05122A?style=flat&logo=Docker)&nbsp;
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-05122A?style=flat&logo=PostgreSQL)&nbsp;

Для быстрого запуска:
 - клонировать репозиторий `git clone https://github.com/UsefulSan/speed_checker.git`
 - запустить `docker-compose up --build`

Примеры реализованных методов:
 -  GET:\
-- http://localhost:8000/resource \
-- http://localhost:8000/resource/?type_equipment=Excavator (фильтр)
 - POST: \
-- http://localhost:8000/ {"type_equipment": "123", "model": "1", "speed": 1, "max_speed": 2}
 - DELETE:
-- http://localhost:8000/resource/?id=1,2,3
 - PUT: \
-- http://localhost:8000/resource/?id=1,2,3