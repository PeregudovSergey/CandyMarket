def mining_time():
  connection = sqlite3.connect('../concurrency.db')
  cursor = connection.cursor()
  query = """
    CREATE OR REPLACE FUNCTION time_generator(start_time TIMESTAMP)
    RETURNS TABLE (serial_generator TIMESTAMP) AS $$
    DECLARE
        cur_pos INTEGER := start_time;
    BEGIN
        WHILE cur_pos < last_val_ex LOOP
            serial_generator := cur_pos;
            cur_pos := cur_pos + 1;
            RETURN NEXT;
        END LOOP;
    END;
    $$ LANGUAGE plpgsql;

    """
  df = pd.read_sql(query, connection)
  connection.close()
  return df