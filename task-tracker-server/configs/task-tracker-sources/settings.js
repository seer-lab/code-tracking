const settings = {
    'descriptions':
        [
            {
                'language': 'en',
                'info': {
                    'surveyPane': {
                        'program': 'Program of Study',
                        'year': 'Year',
                        'experience': 'Programming Experience',
                        // 'difficulty': 'How difficult do you think unit testing your project is?',
                        'years': 'Full years',
                        'months': 'Months',
                        'startSession': 'Start the session',
                        'programmingLanguage': 'Programming language'
                    },
                    'taskChoosingPane': {
                        'chooseTask': 'Choose the task',
                        'finishSession': 'Finish the session',
                        'startSolving': 'Start solving',
                        'description': 'After you choose the task and press %s, a file will be created in the codding-assistant folder in the root of the project where you should write the code. When you are finished, press %s to submit your solution.\n' +
                            '\n' +
                            'Note: we only track the changes in the files created by the plugin, other files are not considered. The data will not be sent until you press %s.'
                    },
                    'taskSolvingPane': {
                        'inputData': 'Input data',
                        'outputData': 'Output data',
                        'submit': 'Submit',
                        'hint': 'Get a hint'
                    },
                    'finalPane': {
                        'praise': 'Nicely done!',
                        'backToSurvey': 'Back to the survey',
                        'finalMessage': 'Do not forget to uninstall the TaskTracker plugin',
                    },
                    'commonText': {
                        'backToTasks': 'Back to the tasks'
                    },
                    'successPane': {
                        'successMessage': 'The solution for the %s task has been submitted successfully'
                    }
                }
            },
        ]
};

module.exports = settings;
