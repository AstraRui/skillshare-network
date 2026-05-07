-- Protection from accidental destructive operations by non-admin DB users.
-- The app user is not a superuser and cannot drop the database.

ALTER ROLE skillshare_app NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE skillshare_db FROM PUBLIC;
GRANT CONNECT ON DATABASE skillshare_db TO skillshare_app;
GRANT USAGE ON SCHEMA public TO skillshare_app;

CREATE OR REPLACE FUNCTION block_dangerous_ddl()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF current_user <> 'postgres' THEN
        RAISE EXCEPTION 'Dangerous DDL is blocked for user %', current_user;
    END IF;
END;
$$;

DROP EVENT TRIGGER IF EXISTS trg_block_dangerous_ddl;
CREATE EVENT TRIGGER trg_block_dangerous_ddl
    ON ddl_command_start
    WHEN TAG IN ('DROP TABLE', 'DROP SCHEMA', 'DROP TYPE', 'TRUNCATE TABLE')
    EXECUTE FUNCTION block_dangerous_ddl();
