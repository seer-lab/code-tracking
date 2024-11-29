const dialogTexts = [
    {
        'key': 'task_solving_error',
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'header': 'Task solving',
                        'description': 'You cannot edit this file until you choose the task. To start or continue solving the %s task, choose it on the task choosing panel in the codetracker plugin and press %s.'
                    }
                }
            ]
    },
    {
        'key': 'successful_submit',
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'header': 'Successful submit',
                        'description': 'The data for the %s task has been submitted successfully.'
                    }
                }
            ]
    },
    {
        'key': 'task_submit_error',
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'header': 'Submit error',
                        'description': 'The data for the %s task has not been submitted. Please, check your internet connection and then try again.'
                    }
                }
            ]
    }
];

module.exports = dialogTexts;
