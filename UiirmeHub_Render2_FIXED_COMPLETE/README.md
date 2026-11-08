# ÜiirmeHub Pulse — рабочая версия для Render2

Репозиторий: https://github.com/igorbakanov200505-create/Render2
Мониторинг: https://clubium-render.onrender.com/

## Почему вкладка Actions была пустой?

GitHub не запускает файл `monitor.yml`, лежащий в корне. Правильный путь — `.github/workflows/monitor.yml`.
В этом архиве этот файл находится **по правильному пути**.

## Вариант 1: установка на Windows в два клика (предпочтительно)

1. **Распакуйте ZIP ПОЛНОСТЬЮ** в обычную папку (не запускайте файлы внутри ZIP).
2. Если Git не установлен, установите https://git-scm.com/downloads/win (Git for Windows).
3. Дважды нажмите **INSTALL_RENDER2.cmd**.
4. При необходимости войдите в GitHub (Git Credential Manager / окно браузера).
5. После успешной отправки откроется https://github.com/igorbakanov200505-create/Render2/actions
6. В **Settings → Pages** установите **Source: GitHub Actions**.

Установщик загружает существующий Render2, добавляет правильный workflow, обновляет HTML и Python-проверку,
при этом **не перезаписывает существующий** `data/status.json` (история) и `monitor/config.json` (адрес сервера).
GitHub может попросить разрешить вход и запись через Git; никакие токены, пароли и cookies установщик не собирает.

## Вариант 2: без Git и без загрузки скрытой папки

1. Откройте: https://github.com/igorbakanov200505-create/Render2/new/main
2. В поле **Name your file...** введите `.github/workflows/monitor.yml`
3. Откройте в архиве **WORKFLOW_COPY.txt** и скопируйте весь текст в редактор GitHub.
4. Нажмите **Commit changes**. Это создаст правильный путь даже при ошибке “This file is hidden”.
5. Затем откройте https://github.com/igorbakanov200505-create/Render2/actions
6. Нажмите **ÜiirmeHub Pulse • HTTP check and deploy → Run workflow → Run workflow**.
7. В **Settings → Pages** выберите **Source: GitHub Actions** (если ещё не выбрано).

**Не нужно** заново загружать `index.html`, `monitor/check.py`, `monitor/config.json` и `data/status.json`, если они уже находятся в Render2.

## Если не запускается

- **Workflow not visible:** файл отсутствует именно в `.github/workflows/monitor.yml` на ветке `main` либо Actions отключены в Settings → Actions → General.
- **403 во время push:** убедитесь, что вошли в GitHub с доступом к Render2; при необходимости используйте авторизацию через GitHub Desktop.
- **Cannot write data/status.json:** Settings → Actions → General → Workflow permissions → Read and write permissions.
- **Pages deploy failed:** Settings → Pages → Build and deployment → Source → GitHub Actions.
- **Нет данных в панели:** статус загрузится после первого выполнения workflow и публикации Pages.

## Что действительно работает

- **GitHub Actions** без открытой вкладки проверяет настоящий HTTP-статус ~каждые 5 минут и записывает публичную историю в `data/status.json`.
- **HTML-страница** пытается обращаться к Render каждые 30 секунд, но только при активной вкладке и разрешении браузером фоновых таймеров.
- Из-за CORS браузер может не получить HTTP-код; подтверждённый статус берётся из GitHub Actions.
- Все результаты облачных проверок хранятся в GitHub; последний журнал — до 288 записей. Настройки темы сохраняются в браузере.
- GitHub Actions может задерживать/пропускать запуск. Для **надёжной проверки каждые 30 секунд 24/7** нужен постоянно работающий внешний сервис, а не GitHub Pages.

## Безопасность

Проверяется публичный адрес. Нельзя помещать пароли, данные детей, API-токены и секреты в публичный репозиторий. HTTP-доступность URL не доказывает исправность приложения или базы данных.

## Локальная проверка

`python -m unittest discover -s tests -v` — тесты проверки HTTP без доступа к реальному Render.
