#!/usr/bin/env python3
import sys
import re

FLOAT = r"\d+(?:\.\d+)?"

def usage(err):
    print(err, file=sys.stderr)
    print("usage: {} equation".format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)


def parse_expr(expr):
    """Finds every members like 5*X^0 and parses the coefficients"""
    res = dict()

    pattern = r"^(-?{0}\*X\^{0})([-\+]{0}\*X\^{0})*$".format(FLOAT)
    reg = re.fullmatch(pattern, expr)
    if reg is None:
        usage("malformed equation")

    prog = re.compile(r"([-+]?{0})\*X\^(-?{0})".format(FLOAT))

    for term in prog.finditer(expr):
        reg = prog.match(term.group(0))
        if reg is None:
            usage("malformed term: {}".format(term))

        groups = reg.groups()
        if len(groups) != 2:
            usage("malformed numbers")

        try:
            coef = int(groups[0])
        except ValueError:
            coef = float(groups[0])
        try:
            exponent = int(groups[1])
            if exponent < 0:
                raise
        except ValueError:
            usage("The exponent {} must be an non-negative integer")
        res[exponent] = res.get(exponent, 0) + coef

    return res


def sqrt(nb):
    if int(nb) == nb:
        nb = int(nb)
        for i in range(nb // 2 + 1):
            if i * i == nb:
                return i
    x_n = 1
    for x in range(10):
        x_n = 0.5 * (x_n + (nb / x_n))
    return x_n


def print_reduced(reduced):
    s = ""
    for k, v in reduced.items():
        if s == "" and v > 0:
            s += "{} * X^{} ".format(v, k)
        elif v > 0:
            s += "+ {} * X^{} ".format(v, k)
        else:
            s += "- {} * X^{} ".format(-v, k)
    print("Reduced form:", s, end='')
    print("= 0")
    print("Polynomial degree:", max(reduced))


def solve(reduced):
    coefs = []
    for exp in range(2, -1, -1):
        coefs.append(reduced.get(exp, 0))
    if max(reduced) > 2:
        print("The polynomial degree is stricly greater than 2, I can't solve.")

    discriminant = coefs[1] ** 2 - 4 * coefs[0] * coefs[2]
    print("𝚫 = {}".format(discriminant))

    if discriminant > 0:
        print("Discriminant is strictly positive, the two solutions are:")
        print((-coefs[1] + sqrt(discriminant))/(2 * coefs[0]))
        print((-coefs[1] - sqrt(discriminant))/(2 * coefs[0]))
    elif discriminant == 0:
        print("Discriminant is equal to zero, the solution is:")
        print(-coefs[1]/(2 * coefs[0]))
    else:
        imaginary = sqrt(-discriminant) / (2 * coefs[0])
        if imaginary < 0:
            imaginary = -imaginary
        print("Discriminant is negative, the two complex solutions are:")
        print(-coefs[1]/(2 * coefs[0]), "+", imaginary, "* i")
        print(-coefs[1]/(2 * coefs[0]), "-", imaginary, "* i")


def computor(expr):
    """Entry point for computor_v1"""
    expr = expr.split('=')
    if len(expr) != 2:
        usage("expecting exactly one =")
    left_side = parse_expr(expr[0])
    right_side = parse_expr(expr[1])

    for k, v in right_side.items():
        left_side[k] = left_side.get(k, 0) - v
        if left_side[k] == 0:
            del left_side[k]

    print_reduced(left_side)
    solve(left_side)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage("expecting exactly one parameter")

    computor(sys.argv[1].replace(" ", ""))
