CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_label        VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    cid INT;
BEGIN
    SELECT id INTO cid
    FROM contacts
    WHERE first_name = p_contact_name
    LIMIT 1;

    IF cid IS NULL THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    INSERT INTO phones (contact_id, number, label)
    VALUES (cid, p_phone, p_label);
END;
$$;


CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql
AS $$
DECLARE
    cid INT;
    gid INT;
BEGIN
    SELECT id INTO cid
    FROM contacts
    WHERE first_name = p_contact_name
    LIMIT 1;

    IF cid IS NULL THEN
        RAISE EXCEPTION 'Contact not found';
    END IF;

    SELECT id INTO gid
    FROM groups
    WHERE name = p_group_name;

    IF gid IS NULL THEN
        INSERT INTO groups(name)
        VALUES (p_group_name)
        RETURNING id INTO gid;
    END IF;

    UPDATE contacts
    SET group_id = gid
    WHERE id = cid;
END;
$$;


CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id INT,
    first_name VARCHAR,
    last_name VARCHAR,
    email VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.first_name,
        c.last_name,
        c.email,
        p.number
    FROM contacts c
    LEFT JOIN phones p ON p.contact_id = c.id
    WHERE
        c.first_name ILIKE '%' || p_query || '%'
        OR c.last_name ILIKE '%' || p_query || '%'
        OR c.email ILIKE '%' || p_query || '%'
        OR p.number ILIKE '%' || p_query || '%';
END;
$$;