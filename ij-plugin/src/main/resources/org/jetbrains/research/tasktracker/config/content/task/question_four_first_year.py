# Test 1: Invalid variable name - Y is not X
#   Input:  1
#           Y++
#   Output: (not a valid input per problem rules)

# Test 2: Too many operators - X+++ is not a valid operation
#   Input:  1
#           X+++
#   Output: (not a valid input per problem rules)

# Test 3: Increment then decrement (net zero)
#   Input:  2
#           X++
#           X--
#   Output: 0

# Test 4: Multiple increments
#   Input:  3
#           X++
#           X++
#           X++
#   Output: 3

# Test 5: Multiple decrements
#   Input:  3
#           X--
#           X--
#           X--
#   Output: -3

# Test 6: Mixed prefix and postfix (net zero)
#   Input:  4
#           X++
#           ++X
#           X--
#           --X
#   Output: 0

