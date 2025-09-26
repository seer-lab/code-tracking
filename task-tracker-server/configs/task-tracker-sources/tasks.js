const tasks = [
    {
        'key': 'Task 1: Simple Debugging and Fixing a Syntax Error',
        'examples':
            [
                {
                    'input': '10\n' +
                        '15\n' +
                        '2',
                    'output': '20 30'
                },
                {
                    'input': '2\n' +
                        '50\n' +
                        '4',
                    'output': '10 0'
                },
                {
                    'input': '2\n' +
                        '50\n' +
                        '0',
                    'output': '0 0'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Task 1: Simple Debugging and Fixing a Syntax Error',
                        'description': 'You are given the following code that is meant to calculate the sum of all even numbers in a list. However, there is a syntax error. Fix the code to make it work.',
                        'input': 'The program receives a list of numbers as an input.',
                        'output': 'Returns the sum of all even numbers in the input list.'
                    }
                }
            ]
    },
    {
        'key': 'max_3',
        'examples':
            [
                {
                    'input': '1\n' +
                        '2\n' +
                        '3',
                    'output': '3'
                },
                {
                    'input': '5\n' +
                        '5\n' +
                        '5',
                    'output': '5'
                },
                {
                    'input': '2\n' +
                        '1\n' +
                        '1',
                    'output': '1'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Max 3',
                        'description': 'Print the largest of three numbers in the input.',
                        'input': 'The program receives three numbers as an input',
                        'output': 'Print the largest number. If there are several largest among the three numbers, print only one of them.'
                    }
                }
            ]
    },
    {
        'key': 'is_zero',
        'examples':
            [
                {
                    'input': '3\n' +
                        '0\n' +
                        '1',
                    'output': 'YES'
                },
                {
                    'input': '3\n' +
                        '-15\n' +
                        '1',
                    'output': 'NO'
                },
                {
                    'input': '2\n' +
                        '0\n' +
                        '0',
                    'output': 'YES'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Is zero',
                        'description': 'Check if there are zeros among numbers in the input.',
                        'input': 'The program receives several numbers as an input:\n' +
                            'N - how many numbers do you need to input;\n' +
                            'N numbers to check.',
                        'output': 'Print YES if there are zeros among numbers in the input and NO otherwise. You must enter all N numbers and only after that the inscription YES or NO should appear.'
                    }
                }
            ]
    },
    {
        'key': 'max_digit',
        'examples':
            [
                {
                    'input': '11111111',
                    'output': '1'
                },
                {
                    'input': '123034655943',
                    'output': '9'
                },
                {
                    'input': '4',
                    'output': '4'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Max digit',
                        'description': 'Given a string containing only digits, find and print the largest digit.',
                        'input': 'The program receives a string containing only digits.',
                        'output': 'Print the largest digit that occurs more often in the string.'
                    }
                }
            ]
    },
    {
        'key': 'voting',
        'examples':
            [
                {
                    'input': '0 0 1',
                    'output': '0'
                },
                {
                    'input': '1 1 1',
                    'output': '1'
                },
                {
                    'input': '1 0 1',
                    'output': '1'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Voting',
                        'description': 'Given three numbers, each of them being 1 or 0, determine which one occurs more often — 1 or 0.',
                        'input': 'The program receives three numbers as an input, each being 1 or 0.',
                        'output': 'Print out the number that occurs more often.'
                    }
                }
            ]
    },
    {
        'key': 'brackets',
        'examples':
            [
                {
                    'input': 'example',
                    'output': 'e(x(a(m)p)l)e'
                },
                {
                    'input': 'card',
                    'output': 'c(ar)d'
                },
                {
                    'input': 'ab',
                    'output': 'ab'
                }
            ],
        'descriptions':
            [
                {
                    'language': 'en',
                    'info': {
                        'name': 'Brackets',
                        'description': 'Place the opening and the closing brackets into the input string like this:\nfor odd length\n' +
                            'example → e(x(a(m)p)l)e,\n' +
                            'for even length\n' +
                            'card → c(ar)d, but not c(a()r)d.',
                        'input': 'The program receives a string of English letters (lowercase and uppercase) as an input.',
                        'output': 'Print out the string with the brackets added.'
                    }
                }
            ]
    }
];

module.exports = tasks;
