CREATE OR REPLACE PROCEDURE upsert_user(p_first_name TEXT, p_phone TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE first_name = p_first_name) THEN
        UPDATE contacts
        SET phone = p_phone
        WHERE first_name = p_first_name;
    ELSE
        INSERT INTO contacts(first_name, phone)
        VALUES (p_first_name, p_phone);
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE upsert_many_users(
    p_names TEXT[],
    p_phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
    v_name TEXT;
    v_phone TEXT;
BEGIN
    -- таблица для неправильных данных
    CREATE TEMP TABLE IF NOT EXISTS invalid_data (
        name TEXT,
        phone TEXT,
        reason TEXT
    ) ON COMMIT DROP;

    FOR i IN 1..array_length(p_names, 1) LOOP
        v_name := p_names[i];
        v_phone := p_phones[i];

        -- проверка телефона (только цифры и + в начале)
        IF v_phone ~ '^\+?[0-9]{10,15}$' THEN

            -- UPSERT логика
            IF EXISTS (SELECT 1 FROM contacts WHERE first_name = v_name) THEN
                UPDATE contacts
                SET phone = v_phone
                WHERE first_name = v_name;
            ELSE
                INSERT INTO contacts(first_name, phone)
                VALUES (v_name, v_phone);
            END IF;

        ELSE
            INSERT INTO invalid_data(name, phone, reason)
            VALUES (v_name, v_phone, 'Invalid phone format');
        END IF;

    END LOOP;

    -- вернуть неправильные данные
    RAISE NOTICE 'Invalid rows stored in temp table invalid_data';
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_name TEXT DEFAULT NULL, p_phone TEXT DEFAULT NULL)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM contacts
    WHERE (p_name IS NOT NULL AND first_name = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);
END;
$$;