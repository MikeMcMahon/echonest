-- Alter the DB to add the new columns and create the new table
BEGIN;
CREATE TABLE "echonest_matchedtrack" (
    "id" serial NOT NULL PRIMARY KEY,
    "track_id" text NOT NULL UNIQUE,
    "found_on" date NOT NULL
)
;
CREATE TABLE "echonest_ingested_tracks" (
    "id" serial NOT NULL PRIMARY KEY,
    "ingested_id" integer NOT NULL,
    "matchedtrack_id" integer NOT NULL REFERENCES "echonest_matchedtrack" ("id"),
    UNIQUE ("ingested_id", "matchedtrack_id")
)
;

CREATE INDEX "echonest_ingested_tracks_8336a855" ON "echonest_ingested_tracks" ("ingested_id");
CREATE INDEX "echonest_ingested_tracks_cacbcceb" ON "echonest_ingested_tracks" ("matchedtrack_id");
END;