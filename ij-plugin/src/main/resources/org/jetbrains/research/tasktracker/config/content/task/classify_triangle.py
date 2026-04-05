def classify_triangle(a, b, c):
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"

    if a + b <= c or a + c <= b or b + c <= a:
        return "invalid"

    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "scalene"