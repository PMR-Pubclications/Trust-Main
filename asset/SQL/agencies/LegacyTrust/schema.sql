SELECT * FROM operational_records;

SELECT record_id, title, intake_timestamp 
FROM operational_records 
WHERE security_tag = 'PUBLIC';


