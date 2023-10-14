import sqlite3

#numerate public_key 
def create_triger():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  cursor.execute('''-- Триггер на изменение в таблице block_info, он считает время между блоками в блокчейне
  CREATE OR REPLACE FUNCTION record() RETURNS TRIGGER AS $user_insert_trigger$
    BEGIN
        --
        -- Добавление строки в базу данных time_block, которая отображает разницу времени между майнингом блоков
        --
        IF (TG_OP = 'INSERT') THEN
            INSERT INTO time_block SELECT NOW() - NEW.date
            RETURN NEW;
        END IF;
        RETURN NULL;
    END;
  $user_insert_trigger$ LANGUAGE plpgsql;


  CREATE TRIGGER user_insert_trigger
  BEFORE INSERT ON block_info
  FOR EACH ROW
  EXECUTE FUNCTION record();
                    
  ''')

  connection.commit()
  connection.close()

create_triger()