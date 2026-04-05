def summarize_numbers(numbers):
    if not numbers:
        return None

    total = 0
    negatives = 0
    largest = numbers[0]

    for n in numbers:
        total += n
        if n < 0:
            negatives += 1
        if n > largest:
            largest = n

    average = total / len(numbers)

    if average > 0:
        trend = "positive"
    elif average < 0:
        trend = "negative"
    else:
        trend = "neutral"

    return {"average": average, "negatives": negatives, "largest": largest, "trend": trend}