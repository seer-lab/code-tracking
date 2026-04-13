# Test 1: Basic safe - alternating
#   Input:  010101
#   Output: YES

# Test 2: Exactly 7 zeros - dangerous
#   Input:  0000000
#   Output: NO

# Test 3: Exactly 7 ones - dangerous
#   Input:  1111111
#   Output: NO

# Test 4: Exactly 6 zeros - safe (off-by-one mistake)
#   Input:  000000
#   Output: YES

# Test 5: Exactly 6 ones - safe
#   Input:  111111
#   Output: YES

# Test 6: 8 zeros - dangerous
#   Input:  00000000
#   Output: NO

# Test 7: Run of 7 at the start
#   Input:  11111110
#   Output: NO

# Test 8: Run of 7 in the middle
#   Input:  011111110
#   Output: NO

# Test 9: Run of 7 at the end
#   Input:  01111111
#   Output: NO

# Test 10: 7 ones present but only 6 zeros - still dangerous
#   Input:  00000011111110
#   Output: NO

# Test 11: Both 0s and 1s hit 7 in a row
#   Input:  000000011111110
#   Output: NO

# Test 12: Long alternating string (100 chars) - safe
#   Input:  0101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101
#   Output: YES