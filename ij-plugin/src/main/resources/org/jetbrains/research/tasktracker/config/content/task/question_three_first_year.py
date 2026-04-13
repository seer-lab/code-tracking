# Test 1: Basic mixed word
#   Input:  tour
#   Output: .t.r

# Test 2: Mixed case word
#   Input:  CodeForces
#   Output: .c.d.f.r.c.s

# Test 3: All uppercase vowels - empty output
#   Input:  AEIOU
#   Output: (empty)

# Test 4: All lowercase vowels - empty output
#   Input:  aeiou
#   Output: (empty)

# Test 5: All uppercase consonants - lowercased with dots
#   Input:  BCDFG
#   Output: .b.c.d.f.g

# Test 6: All lowercase consonants
#   Input:  bcdfg
#   Output: .b.c.d.f.g

# Test 7: Lowercase y is a vowel - empty output
#   Input:  y
#   Output: (empty)

# Test 8: Both y and Y are vowels - empty output
#   Input:  yY
#   Output: (empty)

# Test 9: Y at start of word is removed as vowel (common mistake)
#   Input:  Yes
#   Output: .s

# Test 10: Y between consonants - Y removed
#   Input:  zYz
#   Output: .z.z

# Test 11: Single consonant
#   Input:  b
#   Output: .b