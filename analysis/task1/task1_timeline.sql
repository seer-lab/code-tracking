-- TODO: Add activity groupings
-- SQL script for code timelines -- task: grade_scale.py / test_grade_scale.py
-- TEMP CAP: hard 120-minute ceiling on each task window, measured from
-- task_start. Any activity beyond that is excluded -- guards against
-- stray reopens days/weeks later inflating the window. Revisit later
-- with a more general gap-based outlier guard if this keeps coming up.

WITH task_file_events AS (
    SELECT
        r."user" AS user_id,
        d.research_id,
        d.date
    FROM documentdata AS d
             INNER JOIN researches AS r
                        ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\', '/')) LIKE '%grade_scale.py%'

    UNION ALL

    SELECT
        r."user" AS user_id,
        f.research_id,
        f.date
    FROM fileeditordata AS f
             INNER JOIN researches AS r
                        ON f.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(f.old_file, ''), '\', '/')) LIKE '%grade_scale.py%'
       OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\', '/')) LIKE '%grade_scale.py%'
),
     task_windows AS (
         SELECT
             user_id,
             research_id,
             MIN(date) AS task_start,
             MAX(date) AS task_end
         FROM task_file_events
         GROUP BY
             user_id,
             research_id
     ),
     task_activity AS (
         SELECT
             tw.user_id AS id,
             tw.research_id,
             a.date,
             a.type
         FROM researches AS r
                  INNER JOIN activitydata AS a
                             ON a.research_id = r.id
                  INNER JOIN task_windows AS tw
                             ON tw.user_id = r."user"
                                 AND tw.research_id = r.id
                                 AND a.date BETWEEN tw.task_start AND tw.task_end
                                 AND a.date <= tw.task_start + INTERVAL '120 minutes'
     )
SELECT
    id,
    research_id,
    EXTRACT(EPOCH FROM (
        date - MIN(date) OVER (
            PARTITION BY id, research_id
            )
        )) AS time,
    EXTRACT(EPOCH FROM (
                LEAD(date) OVER (
            PARTITION BY id, research_id
            ORDER BY date
            ) - date
        )) AS duration,
    type
FROM task_activity
ORDER BY
    id,
    research_id,
    date;
