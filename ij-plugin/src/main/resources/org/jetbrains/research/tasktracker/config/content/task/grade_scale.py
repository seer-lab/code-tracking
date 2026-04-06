def grade_scale(test1, test2, test3):

    average = (test1 + test2 + test3) / 3

    if average < 0 or average > 100:
        return "invalid"

    if average >= 80:
        grade = "A"
    elif average >= 70:
        grade = "B"
    elif average >= 60:
        grade = "C"
    elif average >= 50:
        grade = "D"
    else:
        grade = "F"

    return grade