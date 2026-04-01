def calculate_gpa(results):
    """
    Args:
        results (list): list of (letter_grade, credits) tuples.
                        Valid grades: A, B, C, D, F. Credits must be > 0.
    Returns:
        dict: { 'gpa': float|None, 'classification': str|None,
                'status': 'ok'|'error', 'message': str }
    """
    grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}

    if not results:
        return {'gpa': None, 'classification': None,
                'status': 'error', 'message': 'No results provided'}

    total_points = 0
    total_credits = 0

    for grade, credits in results:
        if grade not in grade_points or credits <= 0:
            return {'gpa': None, 'classification': None,
                    'status': 'error', 'message': 'Invalid grade or credits'}
        total_points += grade_points[grade] * credits
        total_credits += credits

    gpa = total_points / total_credits

    if gpa >= 3.5:
        classification = 'First Class'
    elif gpa >= 2.0:
        classification = 'Second Class'
    else:
        classification = 'Fail'

    return {'gpa': round(gpa, 2), 'classification': classification,
            'status': 'ok', 'message': 'GPA calculated'}