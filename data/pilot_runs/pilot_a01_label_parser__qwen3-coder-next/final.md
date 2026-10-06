All tests pass. The implementation correctly:

1. **Splits by semicolon** to get individual entries
2. **Trims whitespace** from both keys and values using `.strip()`
3. **Preserves additional `=` characters** in values by using `split("=", 1)` 
4. **Ignores entries** with no `=`, empty keys, or empty values
5. **Preserves the public function signature** `def parse_labels(text: str) -> dict[str, str]`

The fix addresses all the issues in the original implementation:
- Original used `item.split("=")` which would fail on values containing `=`
- Original didn't trim whitespace from keys/values  
- Original didn't validate for empty keys/values after trimming