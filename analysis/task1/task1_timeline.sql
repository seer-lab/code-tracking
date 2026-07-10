-- TODO: CREATE GROUPINGS FOR RELATED COLUMNS. SEE PAST WORK FOR REFERENCE
-- TODO: UPDATE SCRIPT TO FOCUS ON SEPARATE TASKS - CURRENTLY DOES IT ACROSS ALL WORK

-- SQL script for code timelines
SELECT
    u.id,
    EXTRACT(EPOCH FROM (
        a.date - MIN(a.date) OVER (
            PARTITION BY u.id
            )
        )) AS time,
    EXTRACT(EPOCH FROM (
                LEAD(a.date) OVER (
            PARTITION BY u.id
            ORDER BY a.date
            ) - a.date
        )) AS duration,
    a.type
FROM users AS u
         INNER JOIN researches AS r
                    ON u.id = r."user"
         INNER JOIN activitydata AS a
                    ON a.research_id = r.id
ORDER BY
    u.id,
    a.date;