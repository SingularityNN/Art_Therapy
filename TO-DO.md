- Джанго:
  1) Модели
  2) Скрипты добавления записей

## Как хранить записи об экспериментах?
- ### В двух таблицах
  ### Front
    - ID (text field, pk)
    - Drawing
    - Analyzer_res_image
    - Psych_test_image
  
  ### Back
    - ID (fk)
    - Analyzer_res_json
    - Psych_test_json

- ### В одной
    - ID (text field, pk)
    - Drawing
    - Analyzer_res_image
    - Psych_test_image
    - Analyzer_res_json
    - Psych_test_json