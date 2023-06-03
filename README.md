#equations.py

For a given collection of numbers and operations, generate equations that evaluate to a given goal.

##Usage

    solve(goals: int | Iterable[int], numbers: Collection[int], operations: Iterable[str]='+-*/', unary: Callable | None=None, *, singles: bool=False, insert_paras: bool=True, fixed_order: bool=False, max_consecutive_powers: int=1, max_factorials: int=1) -> dict[int, list[str]]
    
For one or more given numeric goals, numbers and operations, return an `int: list` dictionary of all possible equations that can be made from the numbers and operations to make each goal.

`goal` must be an `int` or a collection of `int`s.

`numbers` must be a collection of `int`s.

`operations` must be an iterable of `str` mathemathical symbols. It defaults to `"+-*/"`. The full range of tested operations is `['+', '-', '*', '/', '', '.', '**', '%', '//']`. The empty string concatenates numbers. The period concatenates with a decimal point.

`unary` is an optional unary function eg `abs`, `operator.neg`, `math.floor`, `math.ceil`, `math.sqrt`, `math.factorial`. It defaults to `None`. All permutations of applying it over two or more consecutive operands will be generated. The program can currently only accept one unary function at a time. Also see `singles` parameter.

The following parameters are keyword-only:

If `singles` is `True`, all permutations of applying `unary` to individual operands will also be generated. This boolean option is useful because some unary functions eg `math.floor` and `math.ceil` do not alter integers. It defaults to `False`.

The `insert_paras` bool determines whether to allow parentheses in the generated equations. Parantheses will not be used in the equation if this is `False`, except as required for `unary` with `singles`. It defaults to `True`.

If `fixed_order` is `True`, the numbers will not be rearranged. It defaults to `False`.

Using too many powers (`**`) or too many `math.factorial` functions in equations can cause the program to crash or run for too long. The `max_consecutive_powers` and `max_factorials` `int` parameters (both default=`1`) restrain this issue.
    
##Examples

In:

    numbers = range(1, 4)
    goal = 6
    for eqs in solve(goal, numbers, fixed_order=True).values():
        for eq in eqs:
            print(eq)

Output:

    1+2+3
    (1+2)+3
    1+(2+3)
    1*2*3
    (1*2)*3
    1*(2*3)

In:

    numbers = [100, 23, 56, 40, 6]
    goal = 49
    for eqs in solve(goal, numbers).values():
        for eq in eqs:
            print(eq)

Output:

    (100-23)*(40/56)-6
    ((100-23)*(40/56))-6
    (100-23)*40/56-6
    (((100-23)*40)/56)-6
    ((100-23)*40)/56-6
    ((100-23)*40/56)-6
    (100-23)/56*40-6
    (((100-23)/56)*40)-6
    ((100-23)/56)*40-6
    ((100-23)/56*40)-6
    (100-23)/(56/40)-6
    ((100-23)/(56/40))-6
    40*((100-23)/56)-6
    (40*((100-23)/56))-6
    ((40*(100-23))/56)-6
    (40*(100-23))/56-6
    40*(100-23)/56-6
    (40*(100-23)/56)-6
    (40/56)*(100-23)-6
    (40/56*(100-23))-6
    ((40/56)*(100-23))-6
    40/56*(100-23)-6
    (40/(56/(100-23)))-6
    40/(56/(100-23))-6
