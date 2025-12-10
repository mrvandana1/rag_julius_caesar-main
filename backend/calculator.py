# app/calculator.py
import math

def sqrt(x):
    x = float(x)
    if x < 0:
        raise ValueError("sqrt: input must be non-negative")
    return math.sqrt(x)

def factorial(n):
    n = int(n)
    if n < 0:
        raise ValueError("factorial: input must be non-negative integer")
    return math.factorial(n)

def ln(x):
    x = float(x)
    if x <= 0:
        raise ValueError("ln: input must be > 0")
    return math.log(x)

def power(x, b):
    x = float(x)
    b = float(b)
    return x ** b