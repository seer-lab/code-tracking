WITH params AS (
    SELECT 8 AS target_student  -- <<< student id to review
),

t3_file_events AS (
    SELECT r."user" AS user_id, d.research_id, d.date
    FROM documentdata AS d
    INNER JOIN researches AS r ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\', '/')) LIKE '%classify_triangle.py%'
    UNION ALL
    SELECT r."user" AS user_id, f.research_id, f.date
    FROM fileeditordata AS f
    INNER JOIN researches AS r ON f.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(f.old_file, ''), '\', '/')) LIKE '%classify_triangle.py%'
       OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\', '/')) LIKE '%classify_triangle.py%'
),
t4_file_events AS (
    SELECT r."user" AS user_id, d.research_id, d.date
    FROM documentdata AS d
    INNER JOIN researches AS r ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\', '/')) LIKE '%process_cart.py%'
    UNION ALL
    SELECT r."user" AS user_id, f.research_id, f.date
    FROM fileeditordata AS f
    INNER JOIN researches AS r ON f.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(f.old_file, ''), '\', '/')) LIKE '%process_cart.py%'
       OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\', '/')) LIKE '%process_cart.py%'
),

task_windows AS (
    SELECT 'Task 3' AS task_label, user_id, research_id, MIN(date) AS task_start, MAX(date) AS task_end
    FROM t3_file_events GROUP BY user_id, research_id
    UNION ALL
    SELECT 'Task 4' AS task_label, user_id, research_id, MIN(date) AS task_start, MAX(date) AS task_end
    FROM t4_file_events GROUP BY user_id, research_id
),

window_intervals AS (
    SELECT
        twd.research_id,
        twd.active_window,
        twd.date AS window_start,
        COALESCE(
            LEAD(twd.date) OVER (PARTITION BY twd.research_id ORDER BY twd.date),
            tw.task_end
        ) AS window_end
    FROM toolwindowdata AS twd
    INNER JOIN task_windows AS tw ON tw.research_id = twd.research_id
    WHERE twd.active_window ILIKE '%continue%'
)

SELECT
    tw.task_label,
    a.date AS event_timestamp,
    a.type,
    a.info,
    a.selected_text
FROM researches AS r
INNER JOIN activitydata AS a ON a.research_id = r.id
INNER JOIN task_windows AS tw
    ON tw.user_id = r."user" AND tw.research_id = r.id
   AND a.date BETWEEN tw.task_start AND tw.task_end
   AND a.date <= tw.task_start + INTERVAL '120 minutes'
CROSS JOIN params AS p
INNER JOIN window_intervals AS wi
    ON wi.research_id = a.research_id
   AND a.date >= wi.window_start AND a.date < wi.window_end
WHERE r."user" = p.target_student
  AND a.type <> 'KeyReleased'
ORDER BY tw.task_label, a.date;