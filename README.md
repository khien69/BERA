
Данный код делает депозит в берачейн через стейкстон.

Код учитывает газ эфира, пропускает кошелек, если там недостаточно эфира и имеет гибкую настройку.

Реккомендую пополнять кошелек не меньше чем на  0.005 эфира. Контракт биры тупой и если мало баксов на счету тупо делает пустую транзу...

Настройка:

1. Укажите приватные ключи в файл private_keys . КАЖДЫЙ КОШЕЛЕК С НОВОЙ СТРОКИ!!!!! ПУСТЫЕ СТРОКИ НЕ ОСТАВЛЯЙТЕ

2. Пришите в теримнал pip install -r requirements.txt

3. В файле main.py указываете максимальный газ, задержку и сумму депозита

4. Запускаете в пучарм или же в консоли python main.py   / для МАК python3 main.py


Подпишись на автора https://t.me/gaincryptolox
