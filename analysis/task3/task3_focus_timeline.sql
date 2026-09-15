-- ============================================================================
-- Task 3: Focus timeline -- Code vs Continue vs Neither (v2)
--
-- Rebuilt on the SAME architecture as the main activity timeline: every
-- activitydata event is the backbone (dense -- fires on every keystroke,
-- mouse move, etc.), classified by whichever tool-window-focus span it
-- falls into.
--
-- window_intervals is built from toolwindowdata alone, using the same
-- LEAD-over-ALL-rows-then-classify technique already validated in Task 2:
-- compute the next window-focus change first, THEN split into Continue vs
-- everything else -- never filter before computing LEAD.
--
-- 'Code' is the DEFAULT state, not something with its own explicit signal:
-- if an activitydata event's timestamp doesn't fall inside any known
-- tool-window-focus span, the student is assumed to be in the code editor.
--
-- CAP: each toolwindowdata row's interval is capped at 90 seconds. Without
-- this, window_intervals is wall-to-wall by construction (window_end of one
-- row = window_start of the next, via LEAD), so there are literally never
-- any gaps for 'Code' to default into after the first toolwindowdata row of
-- a session -- confirmed directly: a 5m52s gap after a Continue row was
-- entirely swallowed as Continue before this cap was added. 90 seconds is
-- informed by the same gap-distribution check used for the Continue
-- category on the main timeline: genuine sustained engagement showed gaps
-- under ~97s; anything longer looks like a stale/background window, not
-- continued attention.
--
-- IMPORTANT NUANCE ON WHAT THE CAP ACTUALLY DOES: it limits how far a
-- window_interval can extend for classifying FUTURE activitydata events --
-- it does NOT retroactively split the DURATION of an event that's already
-- been classified. An event's duration is time-until-the-next-activitydata-
-- event. If a student generates no activitydata at all during a pause (e.g.
-- reading an AI response without typing), the one event right before that
-- silence still carries its FULL duration under whatever category it was
-- classified as -- even if that silent gap is much longer than 90 seconds.
-- Confirmed directly: two students with 90%+ Continue share had raw
-- toolwindowdata gaps of 138s and 242s (both over the cap), yet each
-- showed under 3 seconds of Code total -- because there was simply no
-- activitydata during those gaps for the cap to hand back to Code. The cap
-- protects against misclassifying NEW events after a long gap; it does not
-- shrink an already-assigned event's duration mid-gap.
WITH task_file_events AS (
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

task_windows AS (
    SELECT user_id, research_id, MIN(date) AS task_start, MAX(date) AS task_end
    FROM task_file_events
    GROUP BY user_id, research_id
),

window_intervals AS (
    SELECT
        twd.research_id,
        twd.active_window,
        twd.date AS window_start,
        LEAST(
            COALESCE(
                LEAD(twd.date) OVER (PARTITION BY twd.research_id ORDER BY twd.date),
                tw.task_end
            ),
            twd.date + INTERVAL '90 seconds'
        ) AS window_end
    FROM toolwindowdata AS twd
    INNER JOIN task_windows AS tw
        ON tw.research_id = twd.research_id
),

focus_activity AS (
    SELECT
        tw.user_id AS id,
        a.research_id,
        a.date,
        CASE
            WHEN wi.active_window ILIKE '%continue%' THEN 'Continue'
            WHEN wi.active_window IS NOT NULL THEN 'Neither'
            ELSE 'Code'
        END AS focus_type
    FROM researches AS r
    INNER JOIN activitydata AS a
        ON a.research_id = r.id
    INNER JOIN task_windows AS tw
        ON tw.user_id = r."user"
       AND tw.research_id = r.id
       AND a.date BETWEEN tw.task_start AND tw.task_end
       AND a.date <= tw.task_start + INTERVAL '120 minutes'
    LEFT JOIN window_intervals AS wi
        ON wi.research_id = a.research_id
       AND a.date >= wi.window_start
       AND a.date < wi.window_end
    WHERE a.type <> 'KeyReleased'
),

focus_timed AS (
    SELECT
        fa.*,
        EXTRACT(EPOCH FROM (
            fa.date - MIN(fa.date) OVER (PARTITION BY fa.id, fa.research_id)
        )) AS time,
        EXTRACT(EPOCH FROM (
            LEAD(fa.date) OVER (PARTITION BY fa.id, fa.research_id ORDER BY fa.date) - fa.date
        )) AS duration
    FROM focus_activity AS fa
)

SELECT
    id,
    research_id,
    time,
    duration,
    focus_type
FROM focus_timed
ORDER BY id, research_id, time;
