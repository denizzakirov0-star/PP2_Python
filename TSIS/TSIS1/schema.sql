CREATE TABLE IF NOT EXISTS groups (
    id          SERIAL          PRIMARY KEY,
    name        VARCHAR(100)    NOT NULL UNIQUE,
    color       VARCHAR(7)      DEFAULT '#6366f1',   -- hex color for UI
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS contacts (
    id          SERIAL          PRIMARY KEY,
    first_name  VARCHAR(100)    NOT NULL,
    last_name   VARCHAR(100),
    email       VARCHAR(255)    UNIQUE,
    birthday    DATE,
    group_id    INT             REFERENCES groups(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS phones (
    id          SERIAL          PRIMARY KEY,
    contact_id  INT             NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    number      VARCHAR(30)     NOT NULL,
    label       VARCHAR(50)     DEFAULT 'mobile',    
    is_primary  BOOLEAN         NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_phones_primary
    ON phones (contact_id)
    WHERE is_primary = TRUE;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_contacts_updated_at ON contacts;
CREATE TRIGGER trg_contacts_updated_at
    BEFORE UPDATE ON contacts
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

INSERT INTO groups (name, color) VALUES
    ('Семья',    '#ef4444'),
    ('Работа',   '#3b82f6'),
    ('Друзья',   '#22c55e')
ON CONFLICT (name) DO NOTHING;

INSERT INTO contacts (first_name, last_name, email, birthday, group_id) VALUES
    ('Алия',    'Сейткали',  'aliya@example.com',  '1990-03-15', 1),
    ('Данияр',  'Ахметов',   'daniyar@example.com','1985-07-22', 2),
    ('Жанар',   'Нурланова', NULL,                  NULL,         3)
ON CONFLICT (email) DO NOTHING;

INSERT INTO phones (contact_id, UNIQUE (number), label, is_primary)
SELECT id, '+7 701 123 4567', 'mobile', TRUE  FROM contacts WHERE email = 'aliya@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO phones (contact_id, UNIQUE (number), label, is_primary)
SELECT id, '+7 702 987 6543', 'mobile', TRUE  FROM contacts WHERE email = 'daniyar@example.com'
ON CONFLICT DO NOTHING;