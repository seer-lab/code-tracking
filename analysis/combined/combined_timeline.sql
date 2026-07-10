-- Unfiltered baseline: no file-touch filter.
-- TEMP CAP: hard 120-minute ceiling from the first activity row of each
-- (user, research_id), same reasoning as the per-task queries.

WITH session_bounds AS (
    SELECT
        r."user" AS user_id,
        r.id     AS research_id,
        MIN(a.date) AS session_start
    FROM researches AS r
             INNER JOIN activitydata AS a
                        ON a.research_id = r.id
    GROUP BY
        r."user",
        r.id
)
SELECT
    sb.user_id AS id,
    sb.research_id,
    EXTRACT(EPOCH FROM (
        a.date - MIN(a.date) OVER (
            PARTITION BY sb.user_id, sb.research_id
            )
        )) AS time,
    EXTRACT(EPOCH FROM (
                LEAD(a.date) OVER (
            PARTITION BY sb.user_id, sb.research_id
            ORDER BY a.date
            ) - a.date
        )) AS duration,
    a.type
FROM session_bounds AS sb
         INNER JOIN activitydata AS a
                    ON a.research_id = sb.research_id
                        AND a.date <= sb.session_start + INTERVAL '120 minutes'
ORDER BY
    id,
    research_id,
    a.date;
