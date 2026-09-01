-- ============================================================================
-- Task 4 timeline validation: EVENT -> SQL CATEGORY -> R BIN -> DOMINANT CATEGORY
--
-- HOW TO USE:
--   1. Run this ENTIRE file. There is no target user to edit.
--   2. Export the single result table to CSV.
--   3. Upload the CSV to ChatGPT for automated validation across all users.
--
-- OUTPUT:
--   * Every Task 4 activity event for every user is retained.
--   * Events are grouped/sorted by user, research session, event, and bin.
--   * Events spanning multiple 10-second bins appear once per overlapping bin.
--   * The output contains the original DB event, SQL category/timing, R bin
--     boundaries/contributions, dominant bin category, and Execution/Continue
--     marker time.
--
-- CATEGORY PLACEMENT NOTES (Task 4): only Continue changed -- it's
-- classified only from its 3 explicit actions (no window-interval
-- inference -- see task4_timeline.R for why) and is excluded from bin-
-- color competition. Every other category is unchanged.
-- ============================================================================

WITH RECURSIVE
params AS (
    SELECT
        10.0::double precision AS inactivity_buffer_seconds,
        10.0::double precision AS bin_seconds
),

-- --------------------------------------------------------------------------
-- 1. Find every process_cart.py file event used to define the task window.
-- --------------------------------------------------------------------------
task_file_events AS (
    SELECT
        r."user" AS user_id,
        d.research_id,
        d.date,
        'documentdata'::text AS file_event_source,
        d.filename::text AS matched_path
    FROM documentdata AS d
    INNER JOIN researches AS r
        ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\\', '/')) LIKE '%process_cart.py%'

    UNION ALL

    SELECT
        r."user" AS user_id,
        f.research_id,
        f.date,
        'fileeditordata'::text AS file_event_source,
        CONCAT_WS(' -> ', NULLIF(f.old_file::text, ''), NULLIF(f.new_file::text, '')) AS matched_path
    FROM fileeditordata AS f
    INNER JOIN researches AS r
        ON f.research_id = r.id
    WHERE (
            LOWER(REPLACE(COALESCE(f.old_file, ''), '\\', '/')) LIKE '%process_cart.py%'
         OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\\', '/')) LIKE '%process_cart.py%'
          )
),

-- --------------------------------------------------------------------------
-- 2. Same task window as the production query.
-- --------------------------------------------------------------------------
task_windows AS (
    SELECT
        user_id,
        research_id,
        MIN(date) AS task_start_timestamp,
        MAX(date) AS task_end_timestamp,
        COUNT(*) AS task_file_event_count
    FROM task_file_events
    GROUP BY user_id, research_id
),

-- --------------------------------------------------------------------------
-- 3. EVERY activity event for this user's task window, with the exact category
--    mapping from the production SQL.
-- --------------------------------------------------------------------------
task_activity AS (
    SELECT
        tw.user_id AS id,
        tw.research_id,
        tw.task_start_timestamp,
        tw.task_end_timestamp,
        tw.task_file_event_count,
        a.date AS original_timestamp,
        a.type AS original_type,
        a.info AS original_info,

        CASE
            WHEN a.type = 'KeyPressed' THEN 'Editing'
            WHEN a.type IN ('MouseWheel', 'MouseMoved', 'MouseClicked') THEN 'Navigation'
            WHEN a.type = 'Execution' THEN 'Execution'
            WHEN a.type = 'Shortcut' THEN 'Shortcut'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorChooseLookupItem', 'EditorChooseLookupItemReplace',
                'InsertInlineCompletionAction', 'InsertInlineCompletionLineAction',
                'InsertInlineCompletionWordAction',
                'com.intellij.codeInsight.inline.completion.tooltip.InlineCompletionPopupActionGroup',
                'com.intellij.codeInsight.inline.completion.tooltip.InlineCompletionTooltipActionsKt$shortcutActions$shortcutActions$1$1',
                'com.intellij.codeInsight.lookup.impl.actions.ChooseItemAction$FocusedOnly'
            ) THEN 'Autocompletion'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorCopy', 'EditorCut', 'EditorPaste', '$Copy', '$SelectAll'
            ) THEN 'Copy/Paste'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorDelete', 'EditorDeleteLine', 'EditorDeleteToWordEnd',
                'EditorDeleteToWordStart', 'EditorDuplicateLines', 'EditorEnter',
                'EditorIndentSelection', 'EditorTab', 'EditorUnindentSelection',
                '$Delete', '$Undo', 'CommentByLineComment', 'MoveStatementDown',
                'MoveStatementUp', 'EditorDownWithSelection', 'EditorUpWithSelection',
                'EditorLeftWithSelection', 'EditorRightWithSelection',
                'EditorLineEndWithSelection', 'EditorLineStartWithSelection',
                'EditorPreviousWordWithSelection', 'SelectNextOccurrence',
                'EditorBackSpace', 'OpenFile'
            ) THEN 'Editing'

            WHEN a.type = 'Action' AND a.info IN (
                'Debug', 'MoreRunToolbarActions', 'RedesignedRunConfigurationSelector',
                'Run', 'RunAnything', 'RunClass', 'Stop',
                'com.intellij.execution.actions.RunCurrentFileExecutorAction',
                'com.intellij.execution.lineMarker.LineMarkerActionWrapper'
            ) THEN 'Execution'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorDown', 'EditorLeft', 'EditorLineEnd', 'EditorLineStart',
                'EditorNextWord', 'EditorPageUp', 'EditorPreviousWord',
                'EditorRight', 'EditorTextEnd', 'EditorUp', 'GotoDeclaration',
                'HideAllWindows', 'JumpToLastWindow', 'SearchEverywhere',
                'com.intellij.ide.actions.ToolWindowViewModeAction',
                'com.intellij.toolWindow.ToolWindowHeader$HideAction',
                'com.intellij.toolWindow.ToolWindowHeader$ShowOptionsAction',
                'RevealIn', 'Switcher', 'Tablist'
            ) THEN 'Navigation'

            WHEN a.type = 'Action' AND a.info IN (
                'ActivateTerminalToolWindow', 'Terminal.CommandCompletion.InsertSuggestion',
                'Terminal.OpenInReworkedTerminal', 'Terminal.Paste',
                'com.intellij.terminal.frontend.action.SendShortcutToTerminalAction'
            ) THEN 'Terminal'

            WHEN a.type = 'Action' AND a.info IN (
                'continue.reloadPage', 'continue.openConfigPage', 'continue.newContinueSession'
            ) THEN 'Continue'

            ELSE 'Other'
        END AS activity_category

    FROM researches AS r
    INNER JOIN activitydata AS a
        ON a.research_id = r.id
    INNER JOIN task_windows AS tw
        ON tw.user_id = r."user"
       AND tw.research_id = r.id
       AND a.date BETWEEN tw.task_start_timestamp AND tw.task_end_timestamp
       AND a.date <= tw.task_start_timestamp + INTERVAL '120 minutes'
    WHERE a.type <> 'KeyReleased'
),

-- --------------------------------------------------------------------------
-- 4. Exact timing fields produced by the SQL query.
--    event_seq is only a convenient validation row number.
-- --------------------------------------------------------------------------
task_activity_timed AS (
    SELECT
        ta.*,
        ROW_NUMBER() OVER (
            PARTITION BY ta.id, ta.research_id
            ORDER BY ta.original_timestamp
        ) AS event_seq,

        MIN(ta.original_timestamp) OVER (
            PARTITION BY ta.id, ta.research_id
        ) AS first_activity_timestamp,

        EXTRACT(EPOCH FROM (
            ta.original_timestamp
            - MIN(ta.original_timestamp) OVER (
                PARTITION BY ta.id, ta.research_id
              )
        ))::double precision AS time_seconds,

        LEAD(ta.original_timestamp) OVER (
            PARTITION BY ta.id, ta.research_id
            ORDER BY ta.original_timestamp
        ) AS next_original_timestamp,

        EXTRACT(EPOCH FROM (
            LEAD(ta.original_timestamp) OVER (
                PARTITION BY ta.id, ta.research_id
                ORDER BY ta.original_timestamp
            ) - ta.original_timestamp
        ))::double precision AS duration_seconds,

        LEAD(ta.activity_category) OVER (
            PARTITION BY ta.id, ta.research_id
            ORDER BY ta.original_timestamp
        ) AS next_activity_category,

        COUNT(*) OVER (
            PARTITION BY ta.id, ta.research_id, ta.original_timestamp
        ) AS events_at_same_timestamp

    FROM task_activity AS ta
),

-- --------------------------------------------------------------------------
-- 5. Apply exact inactivity rule from production SQL.
-- --------------------------------------------------------------------------
event_level AS (
    SELECT
        tat.*,
        tat.time_seconds AS event_start_seconds,
        tat.time_seconds + tat.duration_seconds AS event_end_seconds,

        CASE
            WHEN tat.duration_seconds > p.inactivity_buffer_seconds
             AND tat.next_activity_category = tat.activity_category
            THEN 'Inactivity'
            ELSE tat.activity_category
        END AS timeline_category,

        CASE
            WHEN tat.duration_seconds IS NULL THEN
                'Excluded from R bins: duration is NULL (last event)'
            WHEN tat.duration_seconds <= 0 THEN
                'Excluded from R bins: duration <= 0'
            WHEN tat.duration_seconds > p.inactivity_buffer_seconds
             AND tat.next_activity_category = tat.activity_category THEN
                'Inactivity: gap > 10s and next category is the same'
            ELSE
                'Keeps activity category'
        END AS category_decision

    FROM task_activity_timed AS tat
    CROSS JOIN params AS p
),

-- --------------------------------------------------------------------------
-- 6. These are exactly the events that survive the R line:
--      raw[!is.na(duration) & duration > 0]
-- --------------------------------------------------------------------------
r_events AS (
    SELECT *
    FROM event_level
    WHERE duration_seconds IS NOT NULL
      AND duration_seconds > 0
),

-- --------------------------------------------------------------------------
-- 7. R total_time and 10-second bins. For one target user, this mirrors:
--      bins <- dt[, .(total_time = max(event_end)), by = id]
-- --------------------------------------------------------------------------
r_total AS (
    SELECT
        id,
        MAX(event_end_seconds) AS total_time_seconds,
        MIN(first_activity_timestamp) AS plot_origin_timestamp
    FROM r_events
    GROUP BY id
),

bins AS (
    SELECT
        rt.id,
        gs::double precision AS bin_start_seconds,
        LEAST(gs::double precision + p.bin_seconds, rt.total_time_seconds) AS bin_end_seconds,
        ROW_NUMBER() OVER (
            PARTITION BY rt.id
            ORDER BY gs
        ) AS bin_number,
        rt.plot_origin_timestamp
    FROM r_total AS rt
    CROSS JOIN params AS p
    CROSS JOIN LATERAL generate_series(
        0::numeric,
        GREATEST(rt.total_time_seconds - 1e-9, 0)::numeric,
        p.bin_seconds::numeric
    ) AS gs
),

-- --------------------------------------------------------------------------
-- 8. Pair every surviving event with every bin it overlaps, exactly like the
--    data.table non-equi join in the R script.
-- --------------------------------------------------------------------------
event_bin_overlap AS (
    SELECT
        e.id,
        e.research_id,
        e.event_seq,
        b.bin_number,
        b.bin_start_seconds,
        b.bin_end_seconds,
        b.plot_origin_timestamp,
        e.timeline_category,
        GREATEST(
            0::double precision,
            LEAST(e.event_end_seconds, b.bin_end_seconds)
            - GREATEST(e.event_start_seconds, b.bin_start_seconds)
        ) AS overlap_seconds
    FROM r_events AS e
    INNER JOIN bins AS b
        ON b.id = e.id
       AND e.event_start_seconds < b.bin_end_seconds
       AND e.event_end_seconds > b.bin_start_seconds
),

-- --------------------------------------------------------------------------
-- 9. Same category-seconds calculation used to choose the dominant colour.
--    Execution and Continue are excluded from colour competition because
--    the R plot represents both as exact-time markers instead. Terminal is
--    UNCHANGED and remains eligible for the dominant colour, same as ever.
--    If an Execution/Continue event was converted to Inactivity by the SQL
--    rule, that Inactivity interval remains eligible for the bin colour.
-- --------------------------------------------------------------------------
bin_category_totals AS (
    SELECT
        id,
        bin_number,
        bin_start_seconds,
        bin_end_seconds,
        timeline_category,
        SUM(overlap_seconds) AS category_seconds_in_bin
    FROM event_bin_overlap
    WHERE overlap_seconds > 0
      AND timeline_category NOT IN ('Execution', 'Continue')
    GROUP BY
        id, bin_number, bin_start_seconds, bin_end_seconds, timeline_category
),

-- Alphabetical timeline_category breaks exact ties, matching setorder(...)
-- followed by .SD[1] in the R script.
bin_ranked AS (
    SELECT
        bct.*,
        ROW_NUMBER() OVER (
            PARTITION BY bct.id, bct.bin_number
            ORDER BY bct.category_seconds_in_bin DESC, bct.timeline_category ASC
        ) AS category_rank_in_bin
    FROM bin_category_totals AS bct
),

bin_winner AS (
    SELECT
        id,
        bin_number,
        bin_start_seconds,
        bin_end_seconds,
        timeline_category AS dominant_category,
        category_seconds_in_bin AS dominant_category_seconds
    FROM bin_ranked
    WHERE category_rank_in_bin = 1
),

-- --------------------------------------------------------------------------
-- 10. Main validation result.
--     LEFT JOIN means EVERY activity event remains visible, even if R drops it.
--     Events spanning multiple bins appear on multiple rows.
-- --------------------------------------------------------------------------
validation AS (
    SELECT
        -- ======================================================================
        -- ESSENTIAL VALIDATION COLUMNS ONLY
        -- ======================================================================

        -- WHO / EVENT
        e.id AS user_id,
        e.research_id,
        e.event_seq,

        -- ORIGINAL DATABASE ACTIVITY
        e.original_timestamp,
        e.original_type,
        e.original_info,

        -- SQL CLASSIFICATION
        e.activity_category,
        e.timeline_category,
        e.next_activity_category,
        e.category_decision,

        -- EXACT TIMING USED BY THE PLOT PIPELINE
        e.time_seconds,
        e.time_seconds / 60.0 AS time_minutes,
        e.duration_seconds,
        e.duration_seconds / 60.0 AS duration_minutes,

        -- R 10-SECOND BIN
        o.bin_number,
        o.bin_start_seconds,
        o.bin_end_seconds,
        o.bin_start_seconds / 60.0 AS bin_start_minutes,
        o.bin_end_seconds / 60.0 AS bin_end_minutes,
        o.plot_origin_timestamp + (o.bin_start_seconds * INTERVAL '1 second')
            AS bin_start_timestamp,
        o.plot_origin_timestamp + (o.bin_end_seconds * INTERVAL '1 second')
            AS bin_end_timestamp,

        -- HOW MUCH THIS EVENT / CATEGORY CONTRIBUTED TO THE BIN
        o.overlap_seconds AS this_event_seconds_in_bin,
        bct.category_seconds_in_bin AS this_category_total_seconds_in_bin,

        -- FINAL CATEGORY CHOSEN FOR THE BIN
        bw.dominant_category,
        bw.dominant_category_seconds,

        -- MARKER POSITIONS (Execution and Continue only -- Terminal unchanged)
        CASE WHEN e.activity_category = 'Execution' THEN TRUE ELSE FALSE END
            AS is_execution_marker,
        CASE WHEN e.activity_category = 'Execution' THEN e.time_seconds / 60.0 END
            AS execution_marker_time_minutes,
        CASE WHEN e.activity_category = 'Continue' THEN TRUE ELSE FALSE END
            AS is_continue_marker,
        CASE WHEN e.activity_category = 'Continue' THEN e.time_seconds / 60.0 END
            AS continue_marker_time_minutes

    FROM event_level AS e
    LEFT JOIN event_bin_overlap AS o
        ON o.id = e.id
       AND o.research_id = e.research_id
       AND o.event_seq = e.event_seq
    LEFT JOIN bin_category_totals AS bct
        ON bct.id = o.id
       AND bct.bin_number = o.bin_number
       AND bct.timeline_category = e.timeline_category
    LEFT JOIN bin_winner AS bw
        ON bw.id = o.id
       AND bw.bin_number = o.bin_number
)

SELECT *
FROM validation
ORDER BY
    user_id,
    research_id,
    event_seq,
    bin_number NULLS LAST;