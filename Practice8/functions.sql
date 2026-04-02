CREATE OR REPLACE FUNCTION get_contacts_by_pattern(p text)
RETURNS TABLE(first_name TEXT, last_name TEXT, phone TEXT)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.first_name, c.last_name, c.phone
    FROM contacts c
    WHERE c.first_name ILIKE '%' || p || '%'
       OR c.last_name  ILIKE '%' || p || '%'
       OR c.phone      ILIKE '%' || p || '%';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_contacts_paginated(p_limit INT, p_offset INT)
RETURNS TABLE (
    id INT,
    first_name TEXT,
    last_name TEXT,
    phone TEXT
)
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.first_name, c.last_name, c.phone
    FROM contacts c
    ORDER BY c.id
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;