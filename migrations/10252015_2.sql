-- MIGRATE THE DATA
-- popuplate the matched track table
BEGIN;
INSERT INTO echonest_matchedtrack (track_id, found_on)
  (
    SELECT DISTINCT
      ei.track_id,
     (select max(ei2.uploaded_on) from echonest_ingested ei2 where ei.track_id = ei2.track_id)
    FROM echonest_ingested ei
    WHERE ei.match = true
  )
;

-- build out the table of actual ingested<->tracks
INSERT INTO echonest_ingested_tracks (ingested_id, matchedtrack_id) (
  SELECT ei.id, mt.id
  FROM echonest_ingested ei
  JOIN echonest_matchedtrack mt ON ei.track_id = mt.track_id
  WHERE ei.match = true
)
;

END;