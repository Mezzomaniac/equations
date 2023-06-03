# equations.py - For a given collection of numbers, generate equations that evaluate to a given goal

from collections import defaultdict
from collections.abc import Callable, Collection, Iterable
from functools import lru_cache
import itertools
from math import ceil, factorial, floor, sqrt
from operator import neg
import more_itertools

@lru_cache(maxsize=None)
def parentheses_combos(last: int, first: int=0) -> set[frozenset[tuple[int]]]:
    '''For a `last` number of operands, return the set of all possible combinations (frozensets) of pairs (tuples) of positions relative to the operands where parentheses could go in a mathematical equation.
    
    `first` should not be used directly. It is used internally when the function calls itself to find nested sets of parentheses.
    
    It is cached to improve the efficiency of recursive calls.
    
    Eg parentheses_combos(4) -> {frozenset({(0, 2), (2, 4)}), frozenset({(1, 4)}), frozenset({(1, 3), (1, 4)}), frozenset({(2, 4)}), frozenset({(1, 3)}), frozenset({(2, 4), (1, 4)}), frozenset({(0, 3)}), frozenset({(0, 2), (0, 3)}), frozenset({(0, 3), (1, 3)}), frozenset(), frozenset({(0, 2)})}'''
    
    size = last - first
    combos = {frozenset()}  # Include the empty set ie no parentheses
    # Find all possible groupings, initially without nesting
    for partition in more_itertools.partitions(range(first, last)):
        # No groupings with only 1-element or all-element groups
        if not 1 < len(partition) < size:
            continue
        alternatives = []
        for group in partition:
            # Groups must contain at least 2 elements
            if len(group) < 2:
                continue
            left = group[0]
            right = group[-1] + 1  # The ')' goes on the far side of the element
            alternatives.append({frozenset({(left, right)})})
            # Groups of at least 3 elements can have nested groups - find those subcombos
            if len(group) > 2:
                for subcombo in parentheses_combos(right, left):
                    alternatives[-1].add(frozenset({(left, right)} | subcombo))
        # Include all combos of each subcombo with each other group
        for combo in itertools.product(*alternatives):
            combos.add(frozenset.union(*combo))
    return combos


def equations(numbers: Collection[int], operations: Iterable[str]='+-*/', unary: Callable | None=None, *, singles: bool=False, insert_paras: bool=True, fixed_order: bool=False, max_consecutive_powers: int=1, max_factorials: int=1) -> list[str]:
    '''For given iterables of `numbers` and `operations` return a list of all possible ways they can be arranged in a str mathematical equation, optionally taking into account all possible arrangements of parentheses.
    
    Takes all the same parameters as solve() (with the same defaults) except for that function's /goal/ parameter. See the solve() documentation for more detail.'''
    
    length = len(numbers)
    number_combos = more_itertools.distinct_permutations(str(number) for number in numbers) if not fixed_order else [[str(number) for number in numbers]]
    operations_combos = list(itertools.product(operations, repeat=length-1))
    para_combos = parentheses_combos(length) if insert_paras else {frozenset()}
    
    whole = {(0, length)}  # Used if unary
    single_positions = frozenset((i, i + 1) for i in range(length))  # Used if unary and singles
    
    eqs = []
    for number_combo in number_combos:
        for operations_combo in operations_combos:
            if ('**',) * (max_consecutive_powers + 1)  in more_itertools.windowed(operations_combo, max_consecutive_powers + 1):
                continue
            for para_combo in para_combos:
                if not unary:
                    eq = list(more_itertools.roundrobin(number_combo, operations_combo))
                    paras = parentheses(para_combo)
                    for index, para in paras:
                        eq.insert(index, para)
                    eq = ''.join(eq)
                    #print(eq)
                    eqs.append(eq)
                    continue
                elif not singles:
                    # TODO: exclude whole if insert_paras is False
                    para_combos2 = more_itertools.powerset(para_combo | whole)
                else:
                    # TODO: exclude whole if insert_paras is False
                    para_combos2 = more_itertools.powerset(para_combo | whole | single_positions)
                # para_combos2 is the powerset of all combinations of places where unary can be inserted
                for para_combo2 in para_combos2:
                    if unary is factorial and len(para_combo2) > max_factorials:
                        continue
                    eq = list(more_itertools.roundrobin(number_combo, operations_combo))
                    paras = parentheses_with_unary(para_combo, para_combo2, unary, length, single_positions)
                    for index, para in paras:
                        eq.insert(index, para)
                    eq = ''.join(eq)
                    #print(eq)
                    eqs.append(eq)
    return eqs


@lru_cache(maxsize=None)
def parentheses(para_combo: frozenset[tuple[int]]) -> list[tuple[int]]:
    '''Generate the parentheses to be inserted into the equation. This is necessary due to potentially needing stacks of parentheses.
    
    Takes an iterable of left & right pairs of positions for parentheses relative to the operands and turns it into a reverse-sorted list of 2-tuple pairs of positions in the equation and the parentheses stack strings to be inserted.'''
    
    paras = defaultdict(str)
    for left, right in para_combo:
        paras[left * 2] += '('
        paras[right * 2 - 1] += ')'
    return list(reversed(sorted(paras.items())))


@lru_cache(maxsize=None)
def parentheses_with_unary(para_combo: frozenset[tuple[int]], para_combo2: tuple[frozenset[tuple[int]]], unary: Callable, length: int, single_positions: frozenset[tuple[int]]) -> list[tuple[int]]:
    '''Generate unary function strings to be inserted into the equation, including required supporting parentheses.
    
    Returns a reverse-sorted list of 2-tuple pairs of positions in the equation and strings of the unary function name with associated parentheses strings to be inserted.'''
    
    paras = defaultdict(str)
    for pair in para_combo:
        left, right = pair
        paras[left * 2] += f'{unary.__name__}(' if pair in para_combo2 else '('
        paras[right * 2 - 1] += ')'
    if (0, length) in para_combo2:
        paras[0] = f'{unary.__name__}(' + paras[0]
        paras[length * 2 - 1] += ')'
    for pair in single_positions & set(para_combo2):
        left, right = pair
        paras[left * 2] += f'{unary.__name__}('
        paras[right * 2 - 1] = ')' + paras[right * 2 - 1]
    return list(reversed(sorted(paras.items())))


def solve(goals: int | Iterable[int], numbers: Collection[int], operations: Iterable[str]='+-*/', unary: Callable | None=None, *, singles: bool=False, insert_paras: bool=True, fixed_order: bool=False, max_consecutive_powers: int=1, max_factorials: int=1) -> dict[int, list[str]]:
    '''For one or more given numeric goals, numbers and operations, return a int: list dictionary of all possible equations that can be made from the numbers and operations to make each goal.
    
    `goal` must be an int or a collection of ints.
    
    `numbers` must be a collection of ints.
    
    `operations` must be an iterable of str mathemathical symbols. It defaults to "+-*/". The full range of tested operations is ['+', '-', '*', '/', '', '.', '**', '%', '//']. The empty string concatenates numbers. The period concatenates with a decimal point.
    
    `unary` is an optional unary function eg abs, operator.neg, math.floor, math.ceil, math.sqrt, math.factorial. It defaults to None. All permutations of applying it over two or more consecutive operands will be generated. The program can currently only accept one unary function at a time. Also see `singles` parameter.

    The following parameters are keyword-only:
    
    If `singles` is True, all permutations of applying `unary` to individual operands will also be generated. This boolean option is useful because some unary functions eg math.floor and math.ceil do not alter integers. It defaults to False.

    The `insert_paras` bool determines whether to allow parentheses in the generated equations. Parantheses will not be used in the equation if this is False, except as required for `unary` with `singles`. It defaults to True.
    
    If `fixed_order` is True, the numbers will not be rearranged. It defaults to False.
    
    Using too many powers ("**") or too many math.factorial functions in equations can cause the program to crash or run for too long. The `max_consecutive_powers` and `max_factorials` int parameters (both default=1) restrain this issue.'''
    
    try:
        iter(goals)
    except TypeError:
        goals = [goals]
    
    hits = {goal: [] for goal in goals}
    for equation in equations(numbers, operations, unary, insert_paras=insert_paras, fixed_order=fixed_order, singles=singles, max_consecutive_powers=max_consecutive_powers, max_factorials=max_factorials):
        try:
            result = eval(equation)
            # TODO: disable SyntaxWarning
        except (ZeroDivisionError, SyntaxError, TypeError, ValueError, OverflowError, AttributeError):
            continue
        if result in goals:
            hits[result].append(equation)
    return hits
    

if __name__ == '__main__':
    '''numbers = range(1, 4)
    goal = 6
    for goal, eqs in solve(goal, numbers, fixed_order=True).items():
        print(goal)
        for eq in eqs:
            print(eq)
        print()'''
    
    '''numbers = [100, 23, 56, 40, 6]
    goal = 49
    for goal, eqs in solve(goal, numbers).items():
        print(goal)
        for eq in eqs:
            print(eq)
        print()'''
    
    '''numbers = '4444'
    operations = ['+', '-', '*', '/', '', '.', '**', '%', '//']
    for goal, eqs in sorted(solve(range(21), numbers, operations=operations, unary=sqrt, singles=True).items()):
        print(goal)
        for eq in eqs:
            print(eq)
        print()'''
