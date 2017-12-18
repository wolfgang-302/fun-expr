#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 14:02:06 2017

run unittest:
>>> python -m unittest <this-test.py>

@author: wolfgang
"""

import unittest

from sympy import (
        #Symbol, 
        symbols, 
        Lambda, 
        Expr, 
        sin,
        cos,
        lambdify,
        FiniteSet, 
        Tuple, 
        S,
        )

from fun_expr import Function_from_Expression as FE

a,b,c,x,y,z = symbols('a,b,c,x,y,z')

i = FE(x,x)
f = FE(x, a*x+b)
g = FE(x, a*x**2)
h = FE((x,y,z), a*x*y*z+b)

fun_lst = [i,f,g,h]

class Test_FE(unittest.TestCase):
    def test_type_of_FE(self):
        for fun in fun_lst:
            for t in (FE, Lambda, Expr):
                assert isinstance(fun, t)
                assert isinstance(fun.diff(x), t)
                assert isinstance(fun.integrate(x, as_function=True), t)
                
        assert isinstance(f.diff(x, as_function=False), FE) == False
        assert isinstance(f.diff(x, as_function=False), Lambda) == False        
        assert isinstance(fun.diff(x, as_function=False), Expr) 

        assert isinstance(fun.integrate(x), FE) == False
        assert isinstance(fun.integrate(x), Lambda) == False
        assert isinstance(fun.integrate(x), Expr) 
        
        self.assertRaises(TypeError, lambda: f.integrate((x,0,1),as_function=True))
        
    def test_variables_symbols_expr_of_f(self):
        assert f.variables == Tuple(x)
        assert f.free_symbols == FiniteSet(a,b)
        assert f.expr == a*x+b
        assert f(x) == f.expr
        assert f.subs({a: S.One, b:0}) == i
        
    def test_variables_symbols_expr_of_h(self):
        assert h.variables == Tuple(x,y,z)
        assert h.free_symbols == FiniteSet(a,b)
        assert h.expr == a*x*y*z+b
        assert h.diff(y,z) == FE((x,y,z),a*x)
        
    def test_limit(self):
        x,x_0 = symbols('x,x_0')
        m_s = FE((x,x_0), (g(x)-g(x_0))/(x-x_0))
        assert m_s.limit(x,x_0) == g.diff(x)(x_0)
        
    def test_composition(self):
        self.assertEqual(f(sin(x)).diff(x), a*cos(x))
        self.assertEqual(sin(f(x)).diff(x), a*cos(a*x+b))