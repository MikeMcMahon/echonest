-- Alter the DB to add the new columns and create the new table
BEGIN;
CREATE TABLE "echonest_matchedtrack" (
    "id" serial NOT NULL PRIMARY KEY,
    "track_id" text NOT NULL,
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

-- MIGRATE THE DATA
-- popuplate the matched track table
INSERT INTO echonest_matchedtrack (track_id, found_on)
  (
    SELECT DISTINCT
      ei.track_id,
      ei.uploaded_on
    FROM echonest_ingested ei
    WHERE ei.match = 1
  )
;

-- build out the table of actual ingested<->tracks
INSERT INTO echonest_ingested_tracks (ingested_id, matchedtrack_id) (
  SELECT ei.id, mt.id
  FROM echonest_ingested ei
  JOIN echonest_matchedtrack mt ON ei.track_id = mt.track_id
  WHERE ei.match = 1
)
;
-- REMOVE THE OFFENDING COLUMN
ALTER TABLE echonest_ingested DROP COLUMN IF EXISTS track_id;