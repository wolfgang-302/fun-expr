#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 22:41:05 2017

@author: wolfgang
"""

from sympy import (Symbol, symbols, Lambda, Expr, sin, lambdify,
                   FiniteSet, Tuple, S)

from sympy.utilities.pytest import XFAIL, raises

from fun_expr import Function_from_Expression as FE

a,b,c,x,y,z = symbols('a,b,c,x,y,z')

i = FE(x,x)
f = FE(x, a*x+b)
g = FE(x, a*x**2)
h = FE((x,y,z), a*x*y*z+b)

fun_lst = [i,f,g,h]

def test_type_of_FE():
    for fun in fun_lst:
        for t in (FE, Lambda, Expr):
            assert isinstance(fun, t)
            assert isinstance(fun.diff(x), t)
            assert isinstance(fun.integrate(x, as_function=True), t)
            assert isinstance(fun.integrate((x,0,1), as_function=True), t)
            
        for t in (FE, Lambda):
            assert isinstance(fun.diff(x, as_function=False), t) == False
            assert isinstance(fun.integrate(), t) == False

def test_variables_symbols_expr_of_f():
    assert f.variables == Tuple(x)
    assert f.free_symbols == Tuple(a,b)
    assert f.expr == a*x+b
    assert f(x) == f.expr
    assert f.subs({a: S.One, b:0}) == i
    
def test_variables_symbols_expr_of_h():
    assert h.variables == Tuple(x,y,z)
    assert h.free_symbols == Tuple(a,b)
    assert h.expr == a*x*y*z+b
    assert h.diff(y,z) == FE((x,y,z),a*x)
    
def test_limit():
    x,x_0 = symbols('x,x_0')
    m_s = FE((x,x_0), (g(x)-g(x_0))/(x-x_0))
    assert m_s.limit(x,x_0) == g.diff(x)(x_0)
    
