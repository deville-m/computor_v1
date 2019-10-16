#!/usr/bin/env python3
import re
import sys
import functools

TERM_REG = r"\d+(?:\.\d+)?\*X\^\d+"
EXPR_REG = r"^-?{0}(?:[-+]?{0})*=-?{0}(?:[-+]?{0})*$".format(TERM_REG)
FULL_TERM = r"([-+]?{})".format(TERM_REG)

print_stderr = functools.partial(print, file=sys.stderr)

class ParseError(Exception):
    def __init__(self, msg, statement):
        self.msg = msg
        self.statement = statement

def print_exception(e):
    print_stderr(sys.argv[0], ":", e.msg, ":", e.statement)
    sys.exit(1)

def usage(msg):
    print_stderr(msg)
    print_stderr("usage:", sys.argv[0], "\"expression\"")
    sys.exit(1)

def transform(lst):
    res = dict()
    for elem in lst:
        matches = re.findall(r"-?\d+(?:\.\d+)?", elem)
        try:
            coef = int(matches[0])
        except ValueError:
            coef = float(matches[0])
        exp = int(matches[1])
        res[exp] = coef if exp not in res else coef + res[exp]
    return res

def print_reduced(expr):
    def to_str(coef, exp):
        return str(abs(coef)) + " * X^" + str(exp)
    if all(not v for v in expr.values()):
        print("Everything is a solution.")
        return False
    s = ""
    for k, v in expr.items():
        if v:
            if not s:
                s += " " if v > 0 else " - "
            else:
                s += " + " if v > 0 else " - "
            s += to_str(v, k)
    s += " = 0"
    print("Reduced form:" + s)
    for i in range(3):
        if i not in expr:
            expr[i] = 0
    return True

def parse_expr(expr):
    expr = expr.replace(" ", "")
    m = re.match(EXPR_REG, expr)
    if not m:
        raise ParseError("Malformed expression", expr)
    left, right = tuple(expr.split("="))
    left = re.findall(FULL_TERM, left)
    right = re.findall(FULL_TERM, right)
    left = transform(left)
    right =  transform(right)
    for k, v in right.items():
        if k not in left:
            left[k] = 0
        left[k] -= v
    return left

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

def second_degree(expr):
    def print_complex(c):
        r, i = c
        if r:
            print(r, "+" if i > 0 else "-", abs(i), "* i")
        else:
            print(i, "* i")

    c, b, a = expr[0], expr[1], expr[2]
    discr = b * b - 4 * a * c
    if discr < 0:
        print("Discriminant is strictly negative, the two solutions are:")
        discr = -discr
        x1 = (-b / (2 * a), -sqrt(discr) / (2 * a))
        x2 = (-b / (2 * a), +sqrt(discr) / (2 * a))
        print_complex(x1)
        print_complex(x2)
    elif discr > 0:
        print("Discriminant is strictly positive, the two solutions are:")
        x1 = (-b + sqrt(discr)) / (2 * a)
        x2 = (-b - sqrt(discr)) / (2 * a)
        print(x1)
        print(x2)
    else:
        print("Discriminant is zero, the solution is:")
        x = -b / (2 * a)

def eval_expr(expr):
    if not print_reduced(expr):
        return
    degree = -1
    for k, v in expr.items():
        if v and k > degree:
            degree = k
    print("Polynomial degree:", degree)
    if degree == 0:
        print("There is no solution.")
    elif degree == 1:
        print("There is one solution:")
        print(-expr[0]/expr[1])
    elif degree == 2:
        second_degree(expr)
    else:
        print("The polynomial degree is strictly greater than 2, I can't solve.".format(degree))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage("Need exactly one argument")
    try:
        expr = parse_expr(sys.argv[1])
    except ParseError as e:
        print_exception(e)
    eval_expr(expr)
