# Brief: transactions (held-out round)

Design the transaction history screen of a personal finance application.
Name: «Операции». Language: Russian. iOS light, 390 × 844 logical pixels,
including safe areas; Adaptive profile, system blue accent and neutral
surfaces. No account balance, investment, budgeting or payment features.

Capabilities: browse transaction history, search merchant, filter all/income/
expense, filter by date range, sort newest/oldest, open transaction details.
Show amounts in ₽ and distinguish income from expenses without color alone.

Same populated sample for both concepts, newest first:
- 24 ноября: Супермаркет −2 480 ₽; Кофейня −320 ₽
- 23 ноября: Зарплата +85 000 ₽; Метро −65 ₽
- 22 ноября: Аптека −1 290 ₽; Возврат покупки +1 600 ₽

Initial state: all transactions, newest first, no search/date filter.
Primary job: understand recent money movements and locate a specific one.
Do not add unrelated charts, branding, accounts, data fields or features.
Map all requested interactions; static mockups do not implement them.

Follow RUN.md in this directory.
