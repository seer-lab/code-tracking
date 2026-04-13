# Test 1: Normal short word - no change
#   Input:  word
#   Output: word

# Test 2: Normal long word - abbreviate
#   Input:  localization
#   Output: l10n

# Test 3: Exactly 10 characters - should NOT abbreviate (common off-by-one mistake)
#   Input:  abcdefghij
#   Output: abcdefghij

# Test 4: Exactly 11 characters - should abbreviate (boundary)
#   Input:  abcdefghijk
#   Output: a9k

# Test 5: First and last letter are the same
#   Input:  abcdefghija
#   Output: a9a

# Test 6: All same letter (11 chars)
#   Input:  aaaaaaaaaaa
#   Output: a9a

# Test 7: Very long word
#   Input:  internationalization
#   Output: i18n
