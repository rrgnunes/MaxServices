CREATE OR ALTER PROCEDURE CREATE_TRIGGERS
AS
DECLARE VARIABLE tableName VARCHAR(100);
DECLARE VARIABLE pkColumn VARCHAR(100);
DECLARE VARIABLE upperTableName VARCHAR(100);
DECLARE VARIABLE triggerExists INTEGER;
DECLARE VARIABLE triggerName VARCHAR(100);
DECLARE VARIABLE sqlText VARCHAR(1000);
BEGIN
    FOR SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS
        WHERE RDB$SYSTEM_FLAG = 0 
          AND RDB$RELATION_NAME != 'REPLICADOR' 
        INTO :tableName
    DO
    BEGIN
        upperTableName = TRIM(UPPER(:tableName));
        
        FOR SELECT TRIM(RDB$FIELD_NAME)
            FROM RDB$INDEX_SEGMENTS
            WHERE RDB$INDEX_NAME = (
                SELECT RDB$INDEX_NAME
                FROM RDB$RELATION_CONSTRAINTS
                WHERE RDB$RELATION_NAME = :tableName
                  AND RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
            )
            INTO :pkColumn
        DO
        BEGIN
            -- Nome do gatilho
            triggerName = 'TR_' || upperTableName || '_I_U_D';

            -- Verifica se o gatilho já existe
            triggerExists = 0;
            SELECT COUNT(*)
            FROM RDB$TRIGGERS
            WHERE RDB$TRIGGER_NAME = :triggerName
            INTO :triggerExists;

            IF (triggerExists = 0) THEN
            BEGIN
                -- Monta a instrução SQL para criar o gatilho
                sqlText = 'CREATE TRIGGER ' || triggerName || ' FOR ' || upperTableName || '
                ACTIVE AFTER INSERT OR UPDATE OR DELETE POSITION 0
                AS
                BEGIN
                    IF (CURRENT_USER = ''MAXSUPORT'') THEN
                    BEGIN
                        IF (INSERTING) THEN
                            INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE)
                            VALUES (''' || upperTableName || ''', ''I'', NEW.' || pkColumn || ');

                        IF (UPDATING) THEN
                            INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE)
                            VALUES (''' || upperTableName || ''', ''U'', NEW.' || pkColumn || ');

                        IF (DELETING) THEN
                            INSERT INTO REPLICADOR (TABELA, ACAO, CHAVE)
                            VALUES (''' || upperTableName || ''', ''D'', OLD.' || pkColumn || ');
                    END
                END';

                EXECUTE STATEMENT :sqlText;
            END
        END
    END
END
