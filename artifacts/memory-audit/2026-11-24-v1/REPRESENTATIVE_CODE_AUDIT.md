# Representative code and distinguishing-case audit

Posthoc, AI-assisted review sample: first parseable output by task/condition within each model/cross-pass cell. No claim of representative prevalence. Every candidate executes only through the existing restricted subprocess.

## qwen2.5-coder:0.5b / both_fail / HumanEval/1

Source call: 50a3d84b6d1b25231b32c56a07ce46c654def90e911b85ba21e5635b08c60fd7; condition: near_duplicate_1000_beginning.

Alternative: Separate balanced top-level parenthesis groups, ignoring spaces. Return the groups in REVERSE occurrence order, preserving characters inside each group.

```python
from typing import List


def separate_paren_groups(paren_string: str) -> List[str]:
    """Input to this function is a string containing multiple groups of nested parentheses. Your goal is to
    separate those group into separate strings and return the list of those.
    Separate groups are balanced (each open brace is properly closed) and not nested within each other
    Ignore any spaces in the input string.
    >>> separate_paren_groups('( ) (( )) (( )( ))')
    ['()', '(())', '(()())']
    """
    result = []
    current_group = []
    for char in paren_string:
        if char == '(':
            current_group.append(char)
        elif char == ')':
            if current_group:
                result.append(''.join(current_group))
                current_group = []
    if current_group:
        result.append(''.join(current_group))
    return result
```

Expected distinguishing/control cases: [{'args': ['(())()'], 'target_expected': "['(())', '()']", 'alternative_expected': "['()', '(())']"}, {'args': [''], 'target_expected': '[]', 'alternative_expected': '[]'}]

Separate authored witness-suite results: {'target_expected': 'failed', 'alternative_expected': 'failed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.

## qwen2.5-coder:0.5b / distractor_only / HumanEval/0

Source call: 34303c8e4927afd811965083065734287a537b4b782b0c47886aa0bd8a9c6b7d; condition: near_duplicate_1000_beginning.

Alternative: Return whether two distinct list positions have absolute difference less than OR EQUAL TO threshold. Equality is included.

```python
from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if abs(numbers[i] - numbers[j]) <= threshold:
                return True
    return False
```

Expected distinguishing/control cases: [{'args': [[1.0, 2.0], 1.0], 'target_expected': 'False', 'alternative_expected': 'True'}, {'args': [[1.0, 3.0], 1.0], 'target_expected': 'False', 'alternative_expected': 'False'}]

Separate authored witness-suite results: {'target_expected': 'failed', 'alternative_expected': 'passed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.

## qwen2.5-coder:0.5b / target_only / HumanEval/105

Source call: a296c831d393c3c82dc04121c9a4b61eb8649b4c182929905440642b2c1fdeac; condition: near_duplicate_1000_end.

Alternative: Keep integers from 1 through 9 inclusive, sort in ASCENDING order counting duplicates, then replace each by its capitalized English digit name. Ignore all other integers.

```python
def by_length(arr):
    """Keep integers from 1 through 9 inclusive, sort in ASCENDING order counting duplicates, then replace each by its capitalized English digit name. Ignore all other integers."""
    # Create a dictionary to map integers to their corresponding names
    digit_names = {
        1: "One",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine"
    }
    
    # Filter out non-integer values and sort the remaining values
    filtered_sorted = sorted([num for num in arr if num in digit_names])
    
    # Reverse the sorted list
    reversed_sorted = filtered_sorted[::-1]
    
    # Map the reversed list back to integers and return the result
    return [digit_names[num] for num in reversed_sorted]
```

Expected distinguishing/control cases: [{'args': [[2, 1]], 'target_expected': "['Two', 'One']", 'alternative_expected': "['One', 'Two']"}, {'args': [[]], 'target_expected': '[]', 'alternative_expected': '[]'}]

Separate authored witness-suite results: {'target_expected': 'passed', 'alternative_expected': 'failed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.

## qwen2.5-coder:1.5b / both_fail / HumanEval/102

Source call: 37926bb5a84bb034ef48b255cb3ff7b1c7621d52c2deba1319903efea7a9598f; condition: near_duplicate_1000_beginning.

Alternative: Return the largest even integer in [x,y), EXCLUDING upper endpoint y. Return -1 if this half-open interval contains no even integer.

```python
def choose_num(x, y):
    """This function takes two positive numbers x and y and returns the
    biggest even integer number that is in the range [x, y] inclusive. If 
    there's no such number, then the function should return -1.

    For example:
    choose_num(12, 15) = 14
    choose_num(13, 12) = -1
    """
    if x % 2 == 0:
        return x
    elif y % 2 == 0:
        return y
    else:
        return -1
```

Expected distinguishing/control cases: [{'args': [2, 2], 'target_expected': '2', 'alternative_expected': '-1'}, {'args': [2, 4], 'target_expected': '4', 'alternative_expected': '2'}]

Separate authored witness-suite results: {'target_expected': 'failed', 'alternative_expected': 'failed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.

## qwen2.5-coder:1.5b / distractor_only / HumanEval/1

Source call: 5e69117690e279dfb55f7da75a1bcc82eb48554efd0aeb13d328539f34db0a96; condition: near_duplicate_1000_end.

Alternative: Separate balanced top-level parenthesis groups, ignoring spaces. Return the groups in REVERSE occurrence order, preserving characters inside each group.

```python
from typing import List


def separate_paren_groups(paren_string: str) -> List[str]:
    groups = []
    current_group = []
    depth = 0

    for char in paren_string.replace(" ", ""):
        if char == "(":
            depth += 1
            current_group.append(char)
        elif char == ")":
            depth -= 1
            current_group.append(char)
            if depth == 0:
                groups.append("".join(current_group))
                current_group = []

    return groups[::-1]
```

Expected distinguishing/control cases: [{'args': ['(())()'], 'target_expected': "['(())', '()']", 'alternative_expected': "['()', '(())']"}, {'args': [''], 'target_expected': '[]', 'alternative_expected': '[]'}]

Separate authored witness-suite results: {'target_expected': 'failed', 'alternative_expected': 'passed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.

## qwen2.5-coder:1.5b / target_only / HumanEval/0

Source call: ceda75ad2c2bcd49991d1f1b3ec2332377dd17d81367ddb48804d5bfbd92a9b3; condition: near_duplicate_1000_beginning.

Alternative: Return whether two distinct list positions have absolute difference less than OR EQUAL TO threshold. Equality is included.

```python
from typing import List


def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if abs(numbers[i] - numbers[j]) < threshold:
                return True
    return False
```

Expected distinguishing/control cases: [{'args': [[1.0, 2.0], 1.0], 'target_expected': 'False', 'alternative_expected': 'True'}, {'args': [[1.0, 3.0], 1.0], 'target_expected': 'False', 'alternative_expected': 'False'}]

Separate authored witness-suite results: {'target_expected': 'passed', 'alternative_expected': 'failed'}

Both-pass in the original suites does not guarantee agreement on these authored boundaries. Treat coverage discrepancies as oracle sensitivity.
