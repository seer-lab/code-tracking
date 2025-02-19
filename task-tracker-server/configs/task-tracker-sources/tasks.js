const tasks = [
    {
        'key': 'Statement Coverage',
        'examples':
            [
                {
                    'input': 'TBD',
                    'output': 'TBD'
                },
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Statement Coverage',
                        'description': 'Causes every statement in the program to be executed at least once, ' +
                            'giving us confidence that every statement is at least capable of executing correctly.\n\n' +
                            'System: Make a test case for each statement in the program, independent of the others.\n\n' +
                            'Completion criterion: A test case for every statement.\n\n' +
                            'Note: You only need to do statement coverage for the provided code for this study.',
                        'input': 'TBD',
                        'output': 'TBD'
                    }
                }
            ]
    },
    {
        'key': 'Branch Coverage',
        'examples':
            [
                {
                    'input': 'TBD',
                    'output': 'TBD'
                },
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Branch Coverage',
                        'description': 'Causes every decision (if, switch, while, etc.) in the program to be made both ways ' +
                            '(or every possible way for switch).\n\n' +
                            'System: Design a test case to exercise each decision in the program each way (true/false).\n\n' +
                            'Completion criterion: A test case for each side of each decision.\n\n' +
                            'Note: You only need to do branch coverage for the provided code for this study.',
                        'input': 'TBD',
                        'output': 'TBD'
                    }
                }
            ]
    },
    {
        'key': 'Path Coverage',
        'examples':
            [
                {
                    'input': 'TBD',
                    'output': 'TBD'
                },
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Path Coverage',
                        "description": "Ensures that every unique path through the program, from start to finish, is executed at least once.\n\n" +
                            "System: Design test cases to cover all possible paths in the control flow graph of the program.\n\n" +
                            "Completion criterion: A test case for every distinct control flow path.\n\n" +
                            "Note: You only need to do path coverage for the provided code for this study.",
                        'input': 'TBD',
                        'output': 'TBD'
                    }
                }
            ]
    },
    // {
    //     'key': 'brackets',
    //     'examples':
    //         [
    //             {
    //                 'input': 'example',
    //                 'output': 'e(x(a(m)p)l)e'
    //             },
    //             {
    //                 'input': 'card',
    //                 'output': 'c(ar)d'
    //             },
    //             {
    //                 'input': 'ab',
    //                 'output': 'ab'
    //             }
    //         ],
    //     'descriptions':
    //         [
    //             {
    //                 'language': 'en',
    //                 'info': {
    //                     'name': 'Brackets',
    //                     'description': 'Place the opening and the closing brackets into the input string like this:\nfor odd length\n' +
    //                         'example → e(x(a(m)p)l)e,\n' +
    //                         'for even length\n' +
    //                         'card → c(ar)d, but not c(a()r)d.',
    //                     'input': 'The program receives a string of English letters (lowercase and uppercase) as an input.',
    //                     'output': 'Print out the string with the brackets added.'
    //                 }
    //             }
    //         ]
    // }
];

module.exports = tasks;
