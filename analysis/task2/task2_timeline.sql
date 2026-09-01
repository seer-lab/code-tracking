WITH params AS (
    SELECT 10.0 AS inactivity_buffer_seconds
),

task_file_events AS (
    SELECT
        r."user" AS user_id,
        d.research_id,
        d.date
    FROM documentdata AS d
    INNER JOIN researches AS r
        ON d.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(d.filename, ''), '\\', '/')) LIKE '%summarize_numbers.py%'

    UNION ALL

    SELECT
        r."user" AS user_id,
        f.research_id,
        f.date
    FROM fileeditordata AS f
    INNER JOIN researches AS r
        ON f.research_id = r.id
    WHERE LOWER(REPLACE(COALESCE(f.old_file, ''), '\\', '/')) LIKE '%summarize_numbers.py%'
       OR LOWER(REPLACE(COALESCE(f.new_file, ''), '\\', '/')) LIKE '%summarize_numbers.py%'
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
        ON tw.user_id = r."user"
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
    tat.time;