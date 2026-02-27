ALTER TABLE lap_summaries 
ADD COLUMN duration_sector_1 FLOAT,
ADD COLUMN duration_sector_2 FLOAT,
ADD COLUMN duration_sector_3 FLOAT,
ADD COLUMN is_pit_out_lap BOOLEAN,
ADD COLUMN is_pit_in_lap BOOLEAN;