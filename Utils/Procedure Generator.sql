SET TERM ^ ;

create or alter procedure CREATE_TRIGGERS_GENERATOR
as
declare variable TABLENAME varchar(100);
declare variable PKCOLUMN varchar(100);
declare variable UPPERTABLENAME varchar(100);
declare variable GENERATORNAME varchar(100);
declare variable GENERATOREXISTS integer;
declare variable BIGGESTID integer;
declare variable SQLGENERATORTEXT varchar(1000);
declare variable TIPOCOLUMN varchar(50);
BEGIN
    FOR SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS
        WHERE RDB$SYSTEM_FLAG = 0 
          AND RDB$RELATION_NAME != 'REPLICADOR'
        INTO :TABLENAME
    DO
    BEGIN
        UPPERTABLENAME = TRIM(UPPER(TABLENAME));

        FOR SELECT TRIM(RDB$FIELD_NAME)
            FROM RDB$INDEX_SEGMENTS
            WHERE RDB$INDEX_NAME = (
                SELECT RDB$INDEX_NAME
                FROM RDB$RELATION_CONSTRAINTS
                WHERE RDB$RELATION_NAME = :TABLENAME
                  AND RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
            )
            INTO :PKCOLUMN
        DO
        BEGIN

            SELECT
                CASE F.RDB$FIELD_TYPE
                    WHEN 7 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'SMALLINT'
                        WHEN 1 THEN 'NUMERIC(' || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 8 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'INTEGER'
                        WHEN 1 THEN 'NUMERIC('  || F.RDB$FIELD_PRECISION || ', ' || (-F.RDB$FIELD_SCALE) || ')'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 9 THEN 'QUAD'
                    WHEN 10 THEN 'FLOAT'
                    WHEN 12 THEN 'DATE'
                    WHEN 13 THEN 'TIME'
                    WHEN 14 THEN 'CHAR(' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ') '
                    WHEN 16 THEN
                    CASE F.RDB$FIELD_SUB_TYPE
                        WHEN 0 THEN 'BIGINT'
                        WHEN 1 THEN 'NUMERIC'
                        WHEN 2 THEN 'DECIMAL'
                    END
                    WHEN 27 THEN 'DOUBLE'
                    WHEN 35 THEN 'TIMESTAMP'
                    WHEN 37 THEN 'VARCHAR'
                    WHEN 40 THEN 'CSTRING' || (TRUNC(F.RDB$FIELD_LENGTH / CH.RDB$BYTES_PER_CHARACTER)) || ')'
                    WHEN 45 THEN 'BLOB_ID'
                    WHEN 261 THEN 'BLOB SUB_TYPE ' || F.RDB$FIELD_SUB_TYPE
                    ELSE 'RDB$FIELD_TYPE: ' || F.RDB$FIELD_TYPE || '?'
                END as tipo
                FROM RDB$RELATION_FIELDS RF
                JOIN RDB$FIELDS F ON (F.RDB$FIELD_NAME = RF.RDB$FIELD_SOURCE)
                LEFT OUTER JOIN RDB$CHARACTER_SETS CH ON (CH.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID)
                LEFT OUTER JOIN RDB$COLLATIONS DCO ON ((DCO.RDB$COLLATION_ID = F.RDB$COLLATION_ID) AND (DCO.RDB$CHARACTER_SET_ID = F.RDB$CHARACTER_SET_ID))
                WHERE (COALESCE(RF.RDB$SYSTEM_FLAG, 0) = 0) AND RF.RDB$RELATION_NAME = UPPER(:tablename) AND RF.RDB$FIELD_NAME = UPPER(:PKCOLUMN)
                INTO :TIPOCOLUMN;

                IF (TIPOCOLUMN = 'INTEGER' OR (TIPOCOLUMN = 'SMALLINT') OR(TIPOCOLUMN = 'BIGINT')) THEN
                BEGIN
                    GENERATORNAME    = 'GEN_' || UPPERTABLENAME || '_ID';
                    GENERATOREXISTS  = 0;
                    
                    SELECT COUNT(*)
                    FROM RDB$GENERATORS
                    WHERE RDB$GENERATOR_NAME = :GENERATORNAME
                    INTO :GENERATOREXISTS;
                    
                    IF (GENERATOREXISTS = 0) THEN
                    BEGIN
                        SQLGENERATORTEXT  = 'CREATE SEQUENCE ' || GENERATORNAME || ';';
                        EXECUTE STATEMENT :SQLGENERATORTEXT;
                    END 
                END
        END
    END
END^

SET TERM ; ^

/* Existing privileges on this procedure */

GRANT EXECUTE ON PROCEDURE CREATE_TRIGGERS_GENERATOR TO MAXSUPORT;
GRANT EXECUTE ON PROCEDURE CREATE_TRIGGERS_GENERATOR TO MAXSERVICES;