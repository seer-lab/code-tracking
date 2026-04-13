# Test 1: Two words not separated by WUB - they become one word
#   Input:  WUBWUBHELLOWORLDWUB
#   Output: HELLOWORLD


# Test 1: Example from problem
#   Input:  WUBWUBIWUBAMWUBWUBX
#   Output: I AM X

# Test 2: Leading and trailing WUBs
#   Input:  WUBHELLOWUBWORLDWUB
#   Output: HELLO WORLD

# Test 3: Multiple WUBs only - empty output
#   Input:  WUBWUBWUB
#   Output: (empty)

# Test 4: No WUBs at all - word printed as-is
#   Input:  HELLO
#   Output: HELLO

# Test 5: Two words not separated by WUB - become one word (common mistake)
#   Input:  WUBWUBHELLOWORLDWUB
#   Output: HELLOWORLD

# Test 6: Single word wrapped in WUBs
#   Input:  WUBHELLOWUB
#   Output: HELLO

# Test 7: WUB splits two single letters
#   Input:  AWUBB
#   Output: A B

# Test 8: Multiple single letter words
#   Input:  WUBAWUBBWUBCWUB
#   Output: A B C