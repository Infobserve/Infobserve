/*
 * This is the PostgreSQL schema that Infobserve uses to store processed events
 */

CREATE TABLE IF NOT EXISTS EVENTS (
  ID SERIAL PRIMARY KEY,
  SOURCE VARCHAR(256), -- The service in which the event was found
  RAW_CONTENT TEXT, -- The raw text of the event
  FILENAME VARCHAR(64), -- The name of the file in which the event was found
  CREATOR VARCHAR(64), -- The name of the user that created the post that contained the event
  TIME_CREATED TIMESTAMPTZ, -- The time and date the event was created
  TIME_DISCOVERED TIMESTAMPTZ -- The time and date the event was discovered
);
CREATE TABLE IF NOT EXISTS MATCHES (
  ID SERIAL PRIMARY KEY,
  EVENT_ID INTEGER REFERENCES EVENTS(ID), -- A reference to the event in which the rule matched
  RULE_MATCHED VARCHAR(128), -- The name of the yara rule that matched
  TAGS_MATCHED TEXT [] -- The tags of the rule that matched
);
CREATE TABLE IF NOT EXISTS BINARY_MATCH (
  ID SERIAL PRIMARY KEY,
  MATCH_ID INTEGER REFERENCES MATCHES(ID),
  MATCHED_DATA BYTEA, -- The binary string that matched
  MATCHED_DATA_HASH TEXT -- Auto-calculated hash of the matched binary string
);
CREATE TABLE IF NOT EXISTS ASCII_MATCH (
  ID SERIAL PRIMARY KEY,
  MATCH_ID INTEGER REFERENCES MATCHES(ID),
  MATCHED_STRING TEXT -- The matched ASCII string
);
CREATE TABLE IF NOT EXISTS INDEX_CACHE (
  ID SERIAL PRIMARY KEY,
  SOURCE TEXT,
  SOURCE_ID TEXT, -- The Reason is each kind of source could have different definition of a unique id format.
  CACHED_TIME TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION expire_cached_rows() RETURNS trigger
  LANGUAGE plpgsql
  AS $$
BEGIN
  DELETE FROM INDEX_CACHE WHERE CACHED_TIME < NOW() - INTERVAL '8 hours';
  RETURN NULL;
END;
$$;


DROP TRIGGER IF EXISTS trigger_expire_cached_rows
  ON PUBLIC.INDEX_CACHE;
CREATE TRIGGER trigger_expire_cached_rows
  AFTER INSERT ON INDEX_CACHE
  EXECUTE PROCEDURE expire_cached_rows();
