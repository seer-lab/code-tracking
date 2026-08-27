WITH code_snapshots AS (
    SELECT
        r."user" AS id,
        d.research_id,
        d.date,
        LENGTH(COALESCE(d.fragment, '')) AS total_code_size
    FROM documentdata AS d
    INNER JOIN researches AS r
        ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\', '/'))
          LIKE '%grade_scale.py%'
),

timed_snapshots AS (
    SELECT
        id,
        research_id,
        date,
        total_code_size,

        MIN(date) OVER (
            PARTITION BY id, research_id
        ) AS start_time,

        MAX(date) OVER (
            PARTITION BY id, research_id
        ) AS end_time,

        LEAD(date) OVER (
            PARTITION BY id, research_id
            ORDER BY date
        ) AS next_time

    FROM code_snapshots
)

SELECT
    id,
    research_id,

    -- Normalized x-axis: 0% to 100% for every student
    100.0 *
    EXTRACT(EPOCH FROM (date - start_time))
    /
    NULLIF(
        EXTRACT(EPOCH FROM (end_time - start_time)),
        0
    ) AS time_percentage,

    -- Actual number of seconds until the next snapshot
    EXTRACT(EPOCH FROM (next_time - date)) AS duration,

    total_code_size

FROM timed_snapshots

ORDER BY
    id,
    research_id,
    time_percentage;