\copy public.users(id, pin) FROM 'path/to/users.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')

\copy public.researches(id, name, description, "user", research_unique_id) FROM 'path/to/researches.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')

\copy public.activitydata(id, research_id, date, type, info, selected_text, action_id) FROM 'path/to/activitydata.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')

\copy public.documentdata(id, research_id, date, timestamp, filename, file_hash_code, document_hash_code, fragment, test_mode) FROM 'path/to/documentdata.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')

\copy public.fileeditordata(id, research_id, date, action, old_file, new_file) FROM 'path/to/fileeditordata.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')

\copy public.toolwindowdata(id, research_id, date, action, active_window) FROM 'path/to/toolwindowdata.csv' WITH (FORMAT csv, HEADER, NULL 'NULL', QUOTE '"', ESCAPE '"')