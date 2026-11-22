"""Authored computational alternatives; references/tests never enter model prompts.

Expected values below are hand-specified validation fixtures, not model results.
All execution of these reference bodies is through the restricted test worker.
"""

import ast
import copy


def alternative_catalog() -> dict:
    """One meaningful change per original fixed task, with explicit boundary witnesses."""
    result = {}

    def add(n, description, edits, cases, *, body=None):
        result[f"HumanEval/{n}"] = {
            "description": description,
            "edits": edits,
            "body": body,
            "witnesses": [
                {"args": args, "target_expected": repr(a), "alternative_expected": repr(b)}
                for args, a, b in cases
            ],
        }

    add(
        0,
        (
            "Return whether two distinct list positions have "
            "absolute difference less than OR EQUAL TO threshold. "
            "Equality is included."
        ),
        [(" < threshold", " <= threshold")],
        [(([1.0, 2.0], 1.0), False, True), (([1.0, 3.0], 1.0), False, False)],
    )
    add(
        1,
        (
            "Separate balanced top-level parenthesis groups, "
            "ignoring spaces. Return the groups in REVERSE "
            "occurrence order, preserving characters inside each "
            "group."
        ),
        [("return results", "return results[::-1]")],
        [(("(())()",), ["(())", "()"], ["()", "(())"]), (("",), [], [])],
    )
    add(
        11,
        (
            "For two equal-length binary strings return bitwise "
            "XNOR as a string: a position is 1 when its two input "
            "bits are equal, otherwise 0."
        ),
        [],
        [(("010", "110"), "100", "011"), (("", ""), "", "")],
        body='\n    return "".join("1" if x == y else "0" for x, y in zip(a, b))\n',
    )
    add(
        13,
        (
            "Return the nonnegative LEAST COMMON MULTIPLE of "
            "integers a and b. Return 0 if either input is zero."
        ),
        [
            (
                "return query_gcd(a, b)",
                "return 0 if a == 0 or b == 0 else abs(a * b) // abs(query_gcd(a, b))",
            )
        ],
        [((6, 8), 2, 24), ((0, 5), 5, 0)],
    )
    add(
        14,
        (
            "Return all prefixes from shortest to longest, "
            "INCLUDING the empty prefix and the full input. Empty "
            "input therefore returns a list containing one empty "
            "string."
        ),
        [],
        [(("abc",), ["a", "ab", "abc"], ["", "a", "ab", "abc"]), (("",), [], [""])],
        body="\n    return [string[:i] for i in range(len(string) + 1)]\n",
    )
    add(
        24,
        (
            "For integer n greater than 1, return its SMALLEST "
            "divisor greater than 1. Include n itself, so a prime "
            "input returns n."
        ),
        [],
        [((15,), 5, 3), ((2,), 1, 2)],
        body="\n    for i in range(2, n + 1):\n        if n % i == 0:\n            return i\n",
    )
    add(
        29,
        (
            "Retain strings starting with prefix in input order, "
            "but EXCLUDE a string equal to prefix itself. Only "
            "strictly longer matches qualify."
        ),
        [("x.startswith(prefix)", "x.startswith(prefix) and len(x) > len(prefix)")],
        [((["a", "ab", "b"], "a"), ["a", "ab"], ["ab"]), (([], "a"), [], [])],
    )
    add(
        39,
        (
            "Return the prime Fibonacci number at ZERO-BASED index "
            "n: index 0 is 2, index 1 is 3. n is nonnegative; "
            "count prime Fibonacci values in increasing order."
        ),
        [("    c_prime = 0", "    n += 1\n    c_prime = 0")],
        [((1,), 2, 3), ((2,), 3, 5)],
    )
    add(
        43,
        (
            "Return whether two list values sum to zero, ALLOWING "
            "reuse of the same list position for both values. Thus "
            "a single zero qualifies."
        ),
        [("i != j and ", "")],
        [(([0],), False, True), (([1, -1],), True, True)],
    )
    add(
        46,
        (
            "Compute the four-term recurrence without recursion, "
            "with initial values 0, 0, ONE, 0 at indices 0,1,2,3; "
            "later terms sum the preceding four values."
        ),
        [("return 2", "return 1"), ("0, 0, 2, 0", "0, 0, 1, 0")],
        [((2,), 2, 1), ((5,), 4, 2)],
    )
    add(
        53,
        "Return x MINUS y for the two integer inputs, preserving their argument order.",
        [("x + y", "x - y")],
        [((2, 3), 5, -1), ((0, 0), 0, 0)],
    )
    add(
        55,
        (
            "Return Fibonacci(n+1) for nonnegative n, where "
            "Fibonacci(0)=0 and Fibonacci(1)=1. The indexing is "
            "shifted forward by one."
        ),
        [("    if n == 0", "    n += 1\n    if n == 0")],
        [((0,), 0, 1), ((3,), 2, 3)],
    )
    add(
        57,
        (
            "Return whether the list is STRICTLY increasing or "
            "STRICTLY decreasing. Equal adjacent values violate "
            "both directions. Lists of length zero or one qualify."
        ),
        [("l[i] > l[i + 1]", "l[i] >= l[i + 1]"), ("l[i] < l[i + 1]", "l[i] <= l[i + 1]")],
        [(([1, 1],), True, False), (([1, 2],), True, True)],
    )
    add(
        73,
        (
            "Count ALL indices i whose value differs from the "
            "mirrored value arr[len(arr)-1-i]. Count both members "
            "of every mismatched pair, rather than minimum edits."
        ),
        [("range(len(arr) // 2)", "range(len(arr))")],
        [(([1, 2],), 1, 2), (([1, 2, 1],), 0, 0)],
    )
    add(
        74,
        (
            "Return the list with fewer total characters across "
            "its strings. When character totals tie, return the "
            "SECOND list."
        ),
        [("c1 <= c2", "c1 < c2")],
        [((["a"], ["b"]), ["a"], ["b"]), (([], ["b"]), [], [])],
    )
    add(
        76,
        (
            "Return whether x equals n raised to a POSITIVE "
            "integer exponent. Exponent zero is forbidden. In "
            "particular 1 only qualifies for bases 1 and -1."
        ),
        [("if x == 1: return True", "if x == 1: return n in (1, -1)")],
        [((1, 4), True, False), ((8, 2), True, True)],
    )
    add(
        89,
        (
            "Rotate lowercase ASCII letters forward THREE places "
            "with wraparound. Leave all other characters unchanged."
        ),
        [("+ 4)", "+ 3)")],
        [(("az",), "ed", "dc"), (("!",), "!", "!")],
    )
    add(
        90,
        (
            "Return the second element of the sorted integer list "
            "COUNTING DUPLICATES. Return None if the input has "
            "fewer than two elements."
        ),
        [],
        [(([1, 1],), None, 1), (([],), None, None)],
        body="\n    return sorted(lst)[1] if len(lst) >= 2 else None\n",
    )
    add(
        92,
        (
            "Return whether any one of x,y,z equals the sum of the "
            "other two. Allow real-valued numeric inputs; do NOT "
            "require integer types. Use ordinary exact numeric "
            "equality."
        ),
        [("    if type(x) != int or type(y) != int or type(z) != int: return False\n", "")],
        [((2.0, 3.0, 5.0), False, True), ((1, 1, 3), False, False)],
    )
    add(
        94,
        (
            "Find the SMALLEST prime in the integer list and "
            "return the sum of its decimal digits. Return None if "
            "no prime is present."
        ),
        [("sorted(lst)[::-1]", "sorted(lst)")],
        [(([2, 13],), 4, 2), (([4, 6],), None, None)],
    )
    add(
        96,
        (
            "Return all prime integers LESS THAN OR EQUAL TO "
            "nonnegative n, in increasing order. Include n when n "
            "is prime."
        ),
        [("range(2, n)", "range(2, n + 1)"), ("range(i + i, n, i)", "range(i + i, n + 1, i)")],
        [((2,), [], [2]), ((5,), [2, 3], [2, 3, 5])],
    )
    add(
        101,
        (
            "Split the input string on whitespace ONLY. Commas "
            "remain literal characters inside words; do not treat "
            "commas as separators."
        ),
        [('(s.replace(",", " ")).split()', "s.split()")],
        [(("a,b c",), ["a", "b", "c"], ["a,b", "c"]), (("",), [], [])],
    )
    add(
        102,
        (
            "Return the largest even integer in [x,y), EXCLUDING "
            "upper endpoint y. Return -1 if this half-open "
            "interval contains no even integer."
        ),
        [],
        [((2, 2), 2, -1), ((2, 4), 4, 2)],
        body="\n    z = y - 1\n    if z % 2:\n        z -= 1\n    return z if z >= x else -1\n",
    )
    add(
        105,
        (
            "Keep integers from 1 through 9 inclusive, sort in "
            "ASCENDING order counting duplicates, then replace "
            "each by its capitalized English digit name. Ignore "
            "all other integers."
        ),
        [("sorted(arr)[::-1]", "sorted(arr)")],
        [(([2, 1],), ["Two", "One"], ["One", "Two"]), (([],), [], [])],
    )
    add(
        115,
        (
            "Water may be pooled across all wells into shared "
            "buckets of the given positive capacity. Return the "
            "minimum number of bucket loads to remove the total "
            "water; partial loads can combine different rows."
        ),
        [],
        [(([[1], [1]], 2), 2, 1), (([[0], [0]], 2), 0, 0)],
        body="\n    return math.ceil(sum(sum(row) for row in grid) / capacity)\n",
    )
    add(
        116,
        (
            "Sort integers by DESCENDING count of ones in "
            "bin(value). For equal counts, sort by ascending "
            "integer value. The minus sign in negative bin "
            "representations is not counted."
        ),
        [],
        [(([1, 3, 7],), [1, 3, 7], [7, 3, 1]), (([1, 2],), [1, 2], [1, 2])],
        body='\n    return sorted(arr, key=lambda x: (-bin(x).count("1"), x))\n',
    )
    add(
        117,
        (
            "Return words containing AT LEAST n consonants, in "
            "occurrence order. Input contains letters and spaces, "
            "vowels are aeiou ignoring case, and an empty string "
            "yields an empty list."
        ),
        [("c_cnt == n", "c_cnt >= n")],
        [(("cat dogs", 2), ["cat"], ["cat", "dogs"]), (("", 2), [], [])],
    )
    add(
        122,
        (
            "Among the first k array elements sum only integers "
            "with EXACTLY two decimal digits in their absolute "
            "value, from 10 through 99. Ignore the sign when "
            "counting digits."
        ),
        [("digits(x) <= 2", "digits(x) == 2")],
        [(([1, 12, 100], 3), 13, 12), (([-12, 3], 2), -9, -12)],
    )
    add(
        127,
        (
            "For two closed integer intervals, count INTEGER "
            "POINTS in their intersection, including endpoints. "
            "Return YES iff that count is prime, otherwise NO. "
            "Disjoint intervals have count zero."
        ),
        [("is_prime(r - l)", "is_prime(r - l + 1)")],
        [(((1, 2), (1, 2)), "NO", "YES"), (((1, 4), (1, 4)), "YES", "NO")],
    )
    add(
        128,
        (
            "Return sum of absolute values multiplied by the "
            "product of signs of NONZERO elements. Ignore zero "
            "elements when determining the sign. Empty input "
            "returns None; an all-zero nonempty list returns 0."
        ),
        [
            ("    if 0 in arr: return 0\n", ""),
            ("    for x in arr:\n", "    for x in arr:\n        if x == 0: continue\n"),
        ],
        [(([0, -2, 3],), 0, -5), (([],), None, None)],
    )
    add(
        133,
        (
            "Round each number DOWN to its floor integer, square "
            "that integer, and return the sum. Use floor rather "
            "than ceiling, including for negative numbers."
        ),
        [("math.ceil(x)", "math.floor(x)")],
        [(([1.2],), 4, 1), (([-1.2],), 1, 4)],
    )
    add(
        140,
        (
            "Replace each run of TWO OR MORE ordinary spaces by "
            "one hyphen. Replace each isolated ordinary space by "
            "an underscore. Preserve all other characters."
        ),
        [("range(len(text), 2, -1)", "range(len(text), 1, -1)")],
        [(("a  b",), "a__b", "a-b"), (("a b",), "a_b", "a_b")],
    )
    add(
        143,
        (
            "Retain words whose lengths are COMPOSITE integers "
            "(greater than one and not prime), preserving order "
            "and joining with single spaces. Do not retain words "
            "of length zero or one."
        ),
        [("is_prime(len(word))", "len(word) > 1 and not is_prime(len(word))")],
        [(("This is a test",), "is", "This test"), (("a is",), "is", "")],
    )
    add(
        144,
        (
            "Inputs x and n are valid positive fractions "
            "numerator/denominator. Return whether x DIVIDED BY n "
            "is a whole number, rather than multiplying the "
            "fractions."
        ),
        [("(x1 * n1) % (x2 * n2)", "(x1 * n2) % (x2 * n1)")],
        [(("1/2", "1/2"), False, True), (("1/2", "2/1"), True, False)],
    )
    add(
        148,
        (
            "Return the tuple of planets from the closer endpoint "
            "to the farther endpoint in solar order, INCLUDING "
            "BOTH endpoint planets. Invalid names yield an empty "
            "tuple; identical valid names yield a one-element "
            "tuple."
        ),
        [("planets[i1 + 1 : i2]", "planets[i1 : i2 + 1]")],
        [
            (("Earth", "Mercury"), ("Venus",), ("Mercury", "Venus", "Earth")),
            (("Mars", "Mars"), (), ("Mars",)),
        ],
    )
    add(
        150,
        (
            "Return y when n is prime, otherwise return x. Values "
            "below 2 are not prime. This reverses which branch "
            "selects each value."
        ),
        [("return x if is_prime(n) else y", "return y if is_prime(n) else x")],
        [((7, 3, 5), 3, 5), ((4, 3, 5), 5, 3)],
    )
    add(
        156,
        (
            "Convert integer 1..1000 to lowercase ADDITIVE Roman "
            "numerals. Use descending m,d,c,l,x,v,i symbols "
            "repeatedly; never use subtractive pairs such as iv or "
            "ix."
        ),
        [],
        [((4,), "iv", "iiii"), ((9,), "ix", "viiii")],
        body=(
            '\n    answer = ""\n    for value, symbol in '
            '[(1000,"m"),(500,"d"),(100,"c"),(50,"l"),(10,"x"),(5,"'
            'v"),(1,"i")]:\n        answer += symbol * (number // '
            "value)\n        number %= value\n    return answer\n"
        ),
    )
    add(
        158,
        (
            "Return a word with the largest number of unique "
            "characters. Break ties by the LEXICOGRAPHICALLY LAST "
            "word. Empty input returns an empty string."
        ),
        [("word < ans", "word > ans")],
        [((["ab", "ba"],), "ab", "ba"), (([],), "", "")],
    )
    add(
        160,
        (
            "Evaluate the supplied operators and nonnegative "
            "operands STRICTLY LEFT TO RIGHT, without ordinary "
            "precedence. Support +,-,*,//,**; assume valid "
            "operations and no division by zero."
        ),
        [],
        [((["+", "*"], [2, 3, 4]), 14, 20), ((["-", "*"], [6, 2, 2]), 2, 8)],
        body=(
            "\n    result = operand[0]\n    for op, value in "
            'zip(operator, operand[1:]):\n        if op == "+": '
            'result += value\n        elif op == "-": result -= '
            'value\n        elif op == "*": result *= value\n        '
            'elif op == "//": result //= value\n        elif op == '
            '"**": result **= value\n    return result\n'
        ),
    )
    add(
        162,
        (
            "Return the lowercase hexadecimal MD5 of UTF-8 text "
            "for EVERY string, INCLUDING the empty string. Do not "
            "return None for empty text."
        ),
        [('    if text == "": return None\n', "")],
        [
            (("",), None, "d41d8cd98f00b204e9800998ecf8427e"),
            (("a",), "0cc175b9c0f1b6a831c399e269772661", "0cc175b9c0f1b6a831c399e269772661"),
        ],
    )
    return result


def specification(task: dict, description: str, *, background: bool) -> str:
    """Only signature/imports and authored prose, never reference or test fixtures."""
    lines = task["prompt"].splitlines(keepends=True)
    node = next(n for n in ast.parse(task["prompt"]).body if isinstance(n, ast.FunctionDef))
    prefix = "".join(lines[: node.body[0].lineno - 1])
    if background:
        prefix = prefix.replace(
            "def " + task["entry_point"] + "(", "def " + task["entry_point"] + "_alternative("
        )
    return prefix + '    """' + description + '"""\n'


def variant_row(task: dict, definition: dict) -> dict:
    """Build the hidden oracle separately from its description-only stimulus."""
    row = copy.deepcopy(task)
    body = definition["body"]
    if body is None:
        body = task["canonical_solution"]
        for old, new in definition["edits"]:
            if old not in body:
                raise ValueError(f"Missing declared reference edit for {task['task_id']}: {old}")
            body = body.replace(old, new)
    row["prompt"] = specification(task, definition["description"], background=False)
    row["canonical_solution"] = body
    # Ensure cross-pass is tested on the boundary witnesses, even if upstream
    # generated argument suites happen not to contain that exact boundary.
    for witness in definition["witnesses"]:
        if witness["args"] not in row["base_input"]:
            row["base_input"].append(witness["args"])
    return row
