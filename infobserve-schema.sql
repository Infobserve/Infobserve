/*
 * This is the PostgreSQL schema that Infobserve uses to store processed events
 */

CREATE TABLE EVENTS
(
    ID SERIAL PRIMARY KEY,
    SOURCE VARCHAR(256), -- The service in which the event was found
    RAW_CONTENT TEXT, -- The raw text of the event
    FILENAME VARCHAR(64), -- The name of the file in which the event was found
    CREATOR VARCHAR(64), -- The name of the user that created the post that contained the event
    TIME_CREATED TIMESTAMPTZ, -- The time and date the event was created
    TIME_DISCOVERED TIMESTAMPTZ -- The time and date the event was discovered
);

CREATE TABLE MATCHES
(
    ID SERIAL PRIMARY KEY,
    EVENT_ID INTEGER REFERENCES EVENTS(ID), -- A reference to the event in which the rule matched
    RULE_MATCHED VARCHAR(128), -- The name of the yara rule that matched
    TAGS_MATCHED TEXT[] -- The tags of the rule that matched
);

CREATE TABLE BINARY_MATCH
(
    ID SERIAL PRIMARY KEY,
    MATCH_ID INTEGER REFERENCES MATCHES(ID),
    MATCHED_DATA BYTEA, -- The binary string that matched
    MATCHED_DATA_HASH TEXT -- Auto-calculated hash of the matched binary string
);

CREATE TABLE ASCII_MATCH
(
    ID SERIAL PRIMARY KEY,
    MATCH_ID INTEGER REFERENCES MATCHES(ID),
    MATCHED_STRING TEXT -- The matched ASCII string
);

CREATE TABLE INDEX_CACHE
(
    ID SERIAL PRIMARY KEY,
    SOURCE TEXT,
    UUID CHAR(36)
);
