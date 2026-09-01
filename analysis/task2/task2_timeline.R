# Task 2 activity timeline
#
# Workflow:
#   1. Query task-specific IDE activity from PostgreSQL.
#   2. Convert events to time intervals and bin them into 10-second windows.
#   3. Assign each bin its duration-weighted dominant activity category.
#      (Execution is excluded from this competition and shown as a marker instead.)
#   4. Merge adjacent bins with the same category.
#   5. Plot one timeline per student, with Execution overlaid as a point marker,
#      and export PNG/PDF figures.

library(data.table)
library(ggplot2)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

BIN_SECONDS <- 10

COLOR_MAP <- c(
  "Inactivity"     = "#FFFFFF",
  "Navigation"     = "#8C510A",  # dark ochre
  "Other"          = "#006D5B",  # dark teal
  "Editing"        = "#D8B4E2",  # light lavender
  "Shortcut"       = "#2C5F8A",  # dark blue
  "Autocompletion" = "#FDE68A",  # light yellow
  "Copy/Paste"     = "#3A8FB7",  # medium blue
  "Terminal"       = "#B8C9D6"   # light blue-grey
  # Note: "Execution" intentionally has no bin fill color. It's excluded from
  # bin-color competition below and shown only as a point marker (see §Plot).
)

# Store the database password outside the script, e.g. in .Renviron:
#   PGPASSWORD=your_password
con <- DBI::dbConnect(
  RPostgres::Postgres(),
  dbname = "csci3060_w26",
  host = "localhost",
  port = 5432,
  user = Sys.getenv("DB_USERNAME"),
  password = Sys.getenv("DB_PASSWORD")
)

# -----------------------------------------------------------------------------
# Query event-level activity
# -----------------------------------------------------------------------------

query <- "
WITH params AS (
    SELECT 10.0 AS inactivity_buffer_seconds
),

task_file_events AS (
    SELECT
        r.\"user\" AS user_id,
        d.research_id,
        d.date
    FROM documentdata AS d
    INNER JOIN researches AS r
        ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\\\\', '/')) LIKE '%summarize_numbers.py%'

    UNION ALL

    SELECT
        r.\"user\" AS user_id,
        f.research_id,
        f.date
    FROM fileeditordata AS f
    INNER JOIN researches AS r
        ON f.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(f.old_file, ''), '\\\\', '/')) LIKE '%summarize_numbers.py%'
       OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\\\\', '/')) LIKE '%summarize_numbers.py%'
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
        a.type,
        a.info,
        CASE
            WHEN a.type = 'KeyPressed' THEN 'Editing'
            WHEN a.type = 'MouseWheel' THEN 'Navigation'
            WHEN a.type = 'MouseMoved' THEN 'Navigation'
            WHEN a.type = 'MouseClicked' THEN 'Navigation'
            WHEN a.type = 'Execution' THEN 'Execution'
            WHEN a.type = 'Shortcut' THEN 'Shortcut'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorChooseLookupItem',
                'EditorChooseLookupItemReplace',
                'InsertInlineCompletionAction',
                'InsertInlineCompletionLineAction',
                'InsertInlineCompletionWordAction',
                'com.intellij.codeInsight.inline.completion.tooltip.InlineCompletionPopupActionGroup',
                'com.intellij.codeInsight.inline.completion.tooltip.InlineCompletionTooltipActionsKt$shortcutActions$shortcutActions$1$1',
                'com.intellij.codeInsight.lookup.impl.actions.ChooseItemAction$FocusedOnly'
            ) THEN 'Autocompletion'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorCopy',
                'EditorCut',
                'EditorPaste',
                '$Copy',
                '$SelectAll'
            ) THEN 'Copy/Paste'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorDelete',
                'EditorDeleteLine',
                'EditorDeleteToWordEnd',
                'EditorDeleteToWordStart',
                'EditorDuplicateLines',
                'EditorEnter',
                'EditorIndentSelection',
                'EditorTab',
                'EditorUnindentSelection',
                '$Delete',
                '$Undo',
                'CommentByLineComment',
                'MoveStatementDown',
                'MoveStatementUp',
                'EditorDownWithSelection',
                'EditorUpWithSelection',
                'EditorLeftWithSelection',
                'EditorRightWithSelection',
                'EditorLineEndWithSelection',
                'EditorLineStartWithSelection',
                'EditorPreviousWordWithSelection',
                'SelectNextOccurrence',
                'EditorBackSpace',
                'OpenFile'
            ) THEN 'Editing'

            WHEN a.type = 'Action' AND a.info IN (
                'Debug',
                'MoreRunToolbarActions',
                'RedesignedRunConfigurationSelector',
                'Run',
                'RunAnything',
                'RunClass',
                'Stop',
                'com.intellij.execution.actions.RunCurrentFileExecutorAction',
                'com.intellij.execution.lineMarker.LineMarkerActionWrapper'
            ) THEN 'Execution'

            WHEN a.type = 'Action' AND a.info IN (
                'EditorDown',
                'EditorLeft',
                'EditorLineEnd',
                'EditorLineStart',
                'EditorNextWord',
                'EditorPageUp',
                'EditorPreviousWord',
                'EditorRight',
                'EditorTextEnd',
                'EditorUp',
                'GotoDeclaration',
                'HideAllWindows',
                'JumpToLastWindow',
                'SearchEverywhere',
                'com.intellij.ide.actions.ToolWindowViewModeAction',
                'com.intellij.toolWindow.ToolWindowHeader$HideAction',
                'com.intellij.toolWindow.ToolWindowHeader$ShowOptionsAction',
                'RevealIn',
                'Switcher',
                'Tablist'
            ) THEN 'Navigation'

            WHEN a.type = 'Action' AND a.info IN (
                'ActivateTerminalToolWindow',
                'Terminal.CommandCompletion.InsertSuggestion',
                'Terminal.OpenInReworkedTerminal',
                'Terminal.Paste',
                'com.intellij.terminal.frontend.action.SendShortcutToTerminalAction'
            ) THEN 'Terminal'

            ELSE 'Other'
        END AS activity_category

    FROM researches AS r
    INNER JOIN activitydata AS a
        ON a.research_id = r.id
    INNER JOIN task_windows AS tw
        ON tw.user_id = r.\"user\"
       AND tw.research_id = r.id
       AND a.date BETWEEN tw.task_start AND tw.task_end
       AND a.date <= tw.task_start + INTERVAL '120 minutes'

    WHERE a.type <> 'KeyReleased'
),

task_activity_timed AS (
    SELECT
        ta.*,

        EXTRACT(
            EPOCH FROM (
                ta.date -
                MIN(ta.date) OVER (
                    PARTITION BY ta.id, ta.research_id
                )
            )
        ) AS time,

        EXTRACT(
            EPOCH FROM (
                LEAD(ta.date) OVER (
                    PARTITION BY ta.id, ta.research_id
                    ORDER BY ta.date
                ) - ta.date
            )
        ) AS duration,

        LEAD(ta.activity_category) OVER (
            PARTITION BY ta.id, ta.research_id
            ORDER BY ta.date
        ) AS next_activity_category

    FROM task_activity AS ta
)

SELECT
    tat.id,
    tat.research_id,
    tat.time,
    tat.duration,
    tat.type,
    tat.info,
    tat.activity_category,

    CASE
        WHEN tat.duration > p.inactivity_buffer_seconds
         AND tat.next_activity_category = tat.activity_category
        THEN 'Inactivity'
        ELSE tat.activity_category
    END AS timeline_category

FROM task_activity_timed AS tat
CROSS JOIN params AS p

ORDER BY
    tat.id,
    tat.research_id,
    tat.time
"

raw <- as.data.table(DBI::dbGetQuery(con, query))
DBI::dbDisconnect(con)

# -----------------------------------------------------------------------------
# Bin activity into fixed-width windows
# -----------------------------------------------------------------------------
# Event-level segments are too narrow to remain legible at print size. For each
# 10-second bin, choose the category occupying the greatest amount of time.
# Execution is excluded from this competition (see §Execution markers below)
# and is instead drawn as an exact-time point marker on top of the timeline.

dt <- raw[!is.na(duration) & duration > 0][order(id, time)]
dt[, `:=`(event_start = time, event_end = time + duration)]

# --- Execution markers -------------------------------------------------------
# Exact execution-event positions for the marker overlay. These come directly
# from the SQL elapsed-time field before any 10-second binning, so they're
# captured from raw (not dt) and are never subject to the duration filter.
execution_markers <- raw[
  activity_category == "Execution",
  .(
    id,
    research_id,
    execution_time_seconds = time,
    execution_time_minutes = time / 60,
    type,
    info
  )
]
execution_markers[, marker_type := "Execution"]

# Non-Execution events only: this is what competes for bin-dominant category.
plot_dt <- dt[timeline_category != "Execution"]

# Create bins independently for each student. total_time is computed from the
# full event set (dt) so the last bin still reflects the true session length,
# even if the session's final event happens to be an Execution.
bins <- dt[, .(total_time = max(event_end)), by = id][
  , {
    starts <- seq(0, total_time - 1e-9, by = BIN_SECONDS)
    .(
      bin_start = starts,
      bin_end = pmin(starts + BIN_SECONDS, total_time)
    )
  },
  by = id
]
bins[, bin_id := .I]

# Non-equi join: pair each non-Execution event with every time bin it overlaps.
overlaps <- plot_dt[
  bins,
  on = .(id, event_start < bin_end, event_end > bin_start),
  allow.cartesian = TRUE,
  nomatch = 0,
  .(
    id = x.id,
    bin_id = i.bin_id,
    bin_start = i.bin_start,
    bin_end = i.bin_end,
    timeline_category = x.timeline_category,
    event_start = x.event_start,
    event_end = x.event_end
  )
]

# Measure the actual amount of each event falling inside each bin.
overlaps[, overlap_seconds :=
           pmin(event_end, bin_end) - pmax(event_start, bin_start)]

# Sum overlap by category, then keep the dominant category in each bin.
# Alphabetical category order breaks exact ties, matching the original Python
# sorted(set(...)) + argmax behavior.
binned <- overlaps[
  overlap_seconds > 0,
  .(category_seconds = sum(overlap_seconds)),
  by = .(id, bin_id, bin_start, bin_end, timeline_category)
]
setorder(binned, id, bin_id, -category_seconds, timeline_category)
binned <- binned[, .SD[1], by = .(id, bin_id)]

# Convert to minutes and merge consecutive bins with the same category.
binned[, bin_duration := (bin_end - bin_start) / 60]
binned[, bin_start := bin_start / 60]
setorder(binned, id, bin_start)
binned[, run_id := rleid(timeline_category), by = id]

timeline <- binned[, .(
  elapsed_start = min(bin_start),
  duration_minutes = sum(bin_duration)
), by = .(id, run_id, timeline_category)]
setorder(timeline, id, elapsed_start)

# -----------------------------------------------------------------------------
# Plot
# -----------------------------------------------------------------------------
# Only students represented in the task data receive a row. Inactivity is white,
# so every segment gets a thin black border to keep those intervals visible.
# Execution events are overlaid as triangle markers, nudged slightly above each
# row so they don't obscure the bin colors beneath them.

student_levels <- rev(sort(unique(timeline$id)))
timeline[, student := factor(id, levels = student_levels)]
execution_markers[, student := factor(id, levels = student_levels)]

fig_height <- max(2.2, uniqueN(timeline$id) * 0.32 + 1.0)

p <- ggplot(
  timeline,
  aes(
    x = elapsed_start + duration_minutes / 2,
    y = student,
    width = duration_minutes,
    fill = timeline_category
  )
) +
  geom_tile(height = 0.5, color = "black", linewidth = 0.15) +
  geom_point(
    data = execution_markers,
    aes(
      x = execution_time_minutes,
      y = student,
      shape = marker_type
    ),
    inherit.aes = FALSE,
    position = position_nudge(y = 0.48),  # lift marker just above the shorter tile
    fill = "black",
    color = "black",
    size = 1.6,
    stroke = 0.3
  ) +
  scale_fill_manual(
    values = COLOR_MAP,
    breaks = sort(unique(timeline$timeline_category)),
    name = "Categories"
  ) +
  scale_shape_manual(
    values = c("Execution" = 25),  # filled triangle pointing down = a tick
    name = "Markers"
  ) +
  scale_x_continuous(
    breaks = scales::breaks_width(5),
    minor_breaks = scales::breaks_width(1),
    expand = expansion(mult = c(0, 0.01))
  ) +
  scale_y_discrete(expand = expansion(add = 0.7)) +  # room for nudged markers on edge rows
  labs(
    x = "Elapsed Active Time (Minutes)",
    y = "Students"
  ) +
  guides(
    fill = guide_legend(nrow = 2, byrow = TRUE, order = 1),
    shape = guide_legend(order = 2)
  ) +
  theme_minimal(base_size = 8) +
  theme(
    panel.grid.major.y = element_blank(),
    panel.grid.minor.y = element_blank(),
    legend.position = "bottom"
  )

print(p)

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------

ggsave(
  "task2_timeline.png", p,
  width = 10, height = fig_height, units = "in", dpi = 300
)