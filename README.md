# ÜiirmeHub Pulse — ТОЛЬКО GITHUB + TELEGRAM

Целевой репозиторий: **https://github.com/igorbakanov200505-create/Render2**
Проверяемый сервер: **https://clubium-render.onrender.com/**

## Важное отличие от предыдущей версии

- Монитор запускается **на серверах GitHub Actions**, не на домашнем ПК.
- GitHub Pages отображает графики и историю; он не выполняет серверный Python.
- Отправка Telegram-уведомлений и обработка Telegram-команд происходят **в GitHub Actions**.
- **Минимальный интервал GitHub Actions — 5 минут**, расписание может опаздывать или пропускать запуски. Поэтому 30 секунд / гарантированное 24/7 / мгновенные ответы Telegram-бота при использовании только GitHub обеспечить нельзя.
- Это не замена профессиональному uptime-мониторингу. Бесплатный Render может перезапускаться или иметь лимиты.

## Загрузка на GitHub — БЕЗ ПРОГРАММ НА КОМПЬЮТЕРЕ

Хорошая новость: в твоём `Render2` **уже существуют** `index.html`, `monitor/check.py`, `monitor/config.json` и `data/status.json`.
Поэтому для первого запуска достаточно **одного файла**:

1. Открой **https://github.com/igorbakanov200505-create/Render2/new/main**
2. В поле **Name your file...** вставь `.github/workflows/monitor.yml` — **точка в начале обязательна**.
3. Открой из этого архива `WORKFLOW_COPY.txt` и **целиком** скопируй его содержимое в большую текстовую область GitHub.
4. Нажми **Commit changes** и ещё раз подтверди.
5. Открой **https://github.com/igorbakanov200505-create/Render2/settings/pages** → **Build and deployment → Source: GitHub Actions**.
6. Открой **https://github.com/igorbakanov200505-create/Render2/settings/actions** → **Workflow permissions → Read and write permissions** (если доступно); сохрани. Разреши запуск Actions, если GitHub просит.
7. Открой **https://github.com/igorbakanov200505-create/Render2/actions** и слева выбери **UiirmeHub Pulse - GitHub cloud monitor + Telegram** → **Run workflow** → **Run workflow**.
8. Дождись зелёной галочки. Адрес сайта: **https://igorbakanov200505-create.github.io/Render2/** после публикации.

Если нужно обновить внешний вид без браузерных запросов:
- Открой **https://github.com/igorbakanov200505-create/Render2/edit/main/index.html**
- Замени содержимое на `index.html` из этого архива и нажми Commit changes. Панель будет исключительно отображать результаты GitHub, её открывать необязательно.

Если создаёшь другой новый репозиторий, загружай **все** файлы из архива с сохранением путей; для Render2 уже всё необходимое присутствует, кроме workflow.

## Настройка Telegram бота

1. Открой **https://t.me/BotFather** и отправь `/newbot`.
2. Введи имя и уникальный username бота с окончанием `bot`. BotFather выдаст **BOT TOKEN** (секрет).
3. Открой созданного бота и отправь `/start` **до первого успешного запуска GitHub Actions**.
4. Узнай **числовой Chat ID** своего диалога с ботом. Для этого открой в своём браузере `https://api.telegram.org/botВАШ_ТОКЕН/getUpdates` (подставь токен без пробелов), затем найди в JSON объект `"chat":{"id": ЧИСЛО, ...}`. Токен содержит пароль от бота: **не отправляй ссылку и токен никому**. Если `result` пуст, напиши боту ещё одно сообщение и обнови страницу; отключи ранее установленный webhook, если он есть. Для групп Chat ID может быть отрицательным.
5. Открой **https://github.com/igorbakanov200505-create/Render2/settings/secrets/actions**.
6. **New repository secret** → Name: `TELEGRAM_BOT_TOKEN` → Secret: токен от BotFather → Add secret.
7. Создай ещё один **New repository secret** → Name: `TELEGRAM_CHAT_ID` → Secret: твой числовой Chat ID → Add secret.
8. Вернись в **Actions** и ещё раз **Run workflow**. Бот ответит на `/start` при ближайшем запуске; если хочешь проверить, отправь ему `/status`.

Никогда не записывай токен в `monitor.yml`, `index.html`, README или комментарий GitHub. GitHub Secrets не видны посетителям страницы.

## Telegram-команды (обрабатываются по расписанию GitHub)

- `/start` — справка и подключение.
- `/status` — последнее состояние HTTP.
- `/history` — последние 8 проверок.
- `/check` — сведения о проверке, уже выполненной данным запуском GitHub Actions.
- `/help` — справка.

Бот отвечает **только** на `TELEGRAM_CHAT_ID`; остальные чаты игнорируются. Спустя **две подряд ошибки** бот отправляет предупреждение. Когда доступ вернётся, бот один раз сообщит о восстановлении. Между командами и ответом может пройти больше пяти минут из-за задержек Actions; реального постоянного процесса или Telegram webhook нет.

## Что и где хранится

- `monitor/config.json`: HTTPS-адрес, тайм-аут и ожидаемые HTTP-коды.
- `data/status.json`: публичная история последних 288 проверок и накопительная статистика. GitHub сам сохраняет изменения коммитами; старые значения можно найти в истории коммитов.
- `data/bot_state.json`: только счётчик ошибок, флаг отправленного предупреждения и номер последней обработанной Telegram-команды. **Токен и Chat ID не сохраняются в файлах репозитория**.
- Telegram Secrets хранятся зашифрованно в настройках GitHub Actions.
- В `index.html` только публичные данные, никаких логинов учащихся и персональных данных.

## Не запускается?

- Пустая Actions? Проверь точный путь `.github/workflows/monitor.yml` **на ветке `main`**. Файл `monitor.yml` в **корне** репозитория не запускается!
- GitHub пишет `Resource not accessible` / `403` при сохранении статуса? Установи **Read and write permissions** в Settings → Actions → General (если этот пункт доступен); проверь защиту ветки.
- Ошибка Pages? **Settings → Pages → Source: GitHub Actions**.
- Telegram молчит? Проверь имена двух Secrets, отправь `/status` боту, дождись следующего Action; проверь, что getUpdates не блокируется установленным webhook.
- Данные устарели? У GitHub расписание не гарантирует точное выполнение. В публичных репозиториях расписание может отключаться после 60 дней без активности; GitHub может задерживать и пропускать запуски.

## Для разработчика

`python -m unittest discover -s tests -v` — 9 тестов без интернета.
В `WORKFLOW_COPY.txt` код Telegram уже встроен внутрь YAML; **дополнительный файл `monitor/telegram_bot.py` в Render2 загружать не требуется**.
