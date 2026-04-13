# Test 1: Basic - 1 digit divisible by 2
#   Input:  1 2
#   Output: 2

# Test 2: Basic - 3 digits divisible by 4
#   Input:  3 4
#   Output: 100

# Test 3: t=1, every number works - smallest n-digit number
#   Input:  1 1
#   Output: 1

# Test 4: t=1 with 2 digits
#   Input:  2 1
#   Output: 10

# Test 5: t=1 with 3 digits
#   Input:  3 1
#   Output: 100

# Test 6: Last single digit (9)
#   Input:  1 9
#   Output: 9

# Test 7: No single digit divisible by 10 - must print -1 (common mistake to skip -1 case)
#   Input:  1 10
#   Output: -1

# Test 8: No single digit divisible by 11
#   Input:  1 11
#   Output: -1

# Test 9: 2-digit number divisible by 10
#   Input:  2 10
#   Output: 10

# Test 10: 2-digit number, t equals the number itself
#   Input:  2 99
#   Output: 99

# Test 11: 2-digit prime as t
#   Input:  2 97
#   Output: 97

# Test 12: t larger than any n-digit number
#   Input:  1 97
#   Output: -1