from functools import lru_cache


@lru_cache()
def factorial(n):
    """
    Calculate the factorial of an input using memoization
    :param n: int
    :rtype value: int
    """
    assert n >= 0
    return 1 if (n in (0, 1)) else (n * factorial(n-1))


@lru_cache()
def C(n, k):
    """Choose k elements from a set of n elements."""
    return 0 if k > n else factorial(n) // (factorial(k) * factorial(n-k))


def combos_sum_total(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total with n_dice each with n_sides.

    """
    combos = 0
    for i in range(0, n_dice+1):
        combos += pow(-1, i) * C(n_dice, i) * C(total - i*n_sides - 1, n_dice - 1)
    return combos

def combos_sum_total_or_more(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total or more with n_dice each with n_sides.

    """
    max_total = n_dice * n_sides
    from_total = min(total, max_total + 1)

    print(f"max total {max_total}")
    print(f"from total {from_total}")
    # print(f"to total {to_total}")

    combos = 0
    #for t in range(from_total, to_total):
    for t in range(from_total, max_total + 1):
        combos += combos_sum_total(t, n_dice, n_sides)
    return combos


def combos_sum_total_or_less(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total or less with n_dice each with n_sides.

    """
    max_total = n_dice * n_sides
    from_total = n_dice
    to_total = min(total, max_total)

    combos = 0
    for t in range(from_total, to_total + 1):
        combos += combos_sum_total(t, n_dice, n_sides)
    return combos


def prob_sum_total(total, n_dice, n_sides):
    """
    Return the chance of rolling exactly total with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total(total, n_dice, n_sides) / float(total_combos)


def prob_sum_total_or_more(total, n_dice, n_sides):
    """
    Return the chance of rolling total or more with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total_or_more(total, n_dice, n_sides) / float(total_combos)


def prob_sum_total_or_less(total, n_dice, n_sides):
    """
    Return the chance of rolling total or less with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total_or_less(total, n_dice, n_sides) / float(total_combos)



x = 15

# print("--")
print(combos_sum_total_or_more(x, 2, 6))
print(prob_sum_total_or_more(x, 2, 6))
#print(prob_sum_total_or_more(15, 2, 6))


