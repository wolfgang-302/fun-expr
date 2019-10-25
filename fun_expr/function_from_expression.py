# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 18:30:58 2017

@author: wolfgang-302

MIT License

Copyright (c) 2017 wolfgang_302

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from sympy import lambdify, Lambda, Expr, Tuple, sympify, FiniteSet, latex
from sympy.utilities.iterables import iterable
from IPython.display import Math


class Function_from_Expression(Lambda):
    """ 
    Define a function with respect to an expression.
    
    Usage:
    f = Function_from_Expression(variables, expr)
    
    where
        variables: symbol or tuple of symbols
        expr: a valid sympy expression
        
    returns an anonymous function derived from sympy.Lambda
    
    Examples:
    >>> from sympy import *
    >>> from fun-expr import Function_from_Expression as FE
    >>> x = Symbol('x')
    >>> a = Symbol('a')
    >>> f = FE(x, x**2 + x)
    >>> f(0)
    0
    >>> f(1)
    2
    >>> f(-1)
    0
    >>> f.diff(x)
    ((x) \mapsto 2*x + 1)
    >>> f.diff(x)(a)
    2*a + 1
    """
    
    def __new__(cls, variables, expr, name=None):
        """
        Create the body of the class.
        
        __new__ must be redefined in order to avoid to
        return the IdentityFunction. The IdentityFunction is 
        not of type Function_from_Expression, so there are no 
        methods of this class available.
        """
        
        # see source of Lambda for the next lines
        #from sympy.utilities.iterables import iterable
        v = list(variables) if iterable(variables) else [variables]
        for i in v:
            if not getattr(i, 'is_Symbol', False):
                raise TypeError('variable is not a symbol: %s' % i)
        obj = Expr.__new__(cls, Tuple(*v), sympify(expr))
        obj.nargs = FiniteSet(len(v))
        obj.name = name
        return obj

    def subs(self, *args, **kwargs):
        """
        return a new function with *args and **kwargs
        substituted into the expression of this function
        """
        return Function_from_Expression(self.variables, 
                                        self.expr.subs(*args, **kwargs),
                                        self.name)        
    
    def diff(self, *symbols, name=None, **assumptions):
        """
        Differentiate function w.r.t. symbols.
        
        Returns a function with the variables of this function.
        
        If as_function=False then return result as expression
        
        Example:
        >>> from sympy import *
        >>> from myfunction import Function_from_Expression as FE
        >>> a,x = symbols('a,x')
        >>> f = FE(x, a*x**2)
        >>> f.diff() # returns error
        >>> f.diff(x)
        ((x) \mapsto 2*a*x)
        >>> f.diff(x, as_function = False)
        2*a*x
        """
        as_function = assumptions.pop('as_function',True)
        expr = self.expr.diff(*symbols, **assumptions)
        if as_function:
            return Function_from_Expression(self.variables, expr,name)
        return expr
        
    def integrate(self, *args, name=None, **kwargs):
        """
        integrate returns the result as expression
        
        If as_function=True return result as function
        of the remaining variables. If no variables are left,
        raise TypeError('no variable left to define a function')
        
        Example:
        >>> from sympy import *
        >>> from myfunction import Function_from_Expression as FE
        >>> a,x = symbols('a,x')
        >>> f = FE(x, a*x**2)
        >>> f.integrate(x)
        a*x**3/3
        >>> x_0, x_1 = symbols('x_0,x_1')
        >>> f.integrate((x,x_0,x_1))
        -a*x_0**3/3 + a*x_1**3/3
        >>> f.integrate(x,as_function=True)
        ((x) \mapsto a*x**3/3)
        >>> f.integrate((x,1,2), as_function=True) # raises TypeError
        """
        as_function = kwargs.pop('as_function', False)
        expr = self.expr.integrate(*args, **kwargs)
        
        if as_function:
            free_symbols = expr.free_symbols
            new_variables = tuple(v for v in self.variables if v in free_symbols)
            if new_variables:
                return Function_from_Expression(new_variables, expr, name)
            else:
                raise TypeError('no variable left to define a function')
        
        return expr
    
    def limit(self, *args, **kwargs):
        """limit returns an expression"""
        return self.expr.limit(*args, **kwargs)
                
    def lambdify(self, *args, **kwargs):
        """
        lambdify self
        Example:
        if f is defined as
        >>> x = Symbol('x')
        >>> f = FE(x,2*x**2)
        and x must be plotted for 0<x<3
        you can write
        >>> lx = np.linspace(0,3)
        >>> lf = f.lambdify()
        >>> plt.plot(lx,lf(lx))
        """         
        return lambdify(self.variables, self.expr, *args, **kwargs)    

    def lambdified(self, *apply_to, **kwargs):
        """
        lambdify self and apply the result to values given by *apply_to
        
        Example:
        if f is defined as
        
        >>> x = Symbol('x')
        >>> f = FE(x,x**2)
        
        and must be plottet for 0<x<3
        you can write
        
        >>> lx = np.linspace(0,3)
        >>> plt.plot(lx,f.lambdified(lx))
        
        if g is a parameterfunction defined as
        
        >>> a,x = symbols('a,x')
        >>> g = FE((x,a), a*x**2)
        
        and you must plot g for 0<3<x, a in [0,1,3]
        you can write
        
        >>> lx = np.linspace(0,3)
        >>> [plt.plot(lx,g.lambdied(lx,a) for a in [0,1,3])
        """

        # if self.var has only one variable and
        # self.expr does not depend on self.var,
        # i.e. self.expr.is_constant(self.var)
        # then lambdify() fails.
        # This case must be tested and treated separately:
        # if apply_to has length 1 and its first element
        # is iterable, a numpy array is returned.
        if 1 in self.nargs\
        and self.expr.is_constant(*self.variables)\
        and len(apply_to) == 1\
        and iterable(*apply_to):
            import numpy as np
            return float(self.expr)*np.ones(np.shape(*apply_to))

        
        lambdified = lambdify(self.variables, self.expr, **kwargs)
        return lambdified(*apply_to)
    
    def equation(self,name=None):
        """ return the equation for this function
            
            The preferred way is to use `name` from
            this function call. If no name is specified
            then `self.name` is tried. If `self.name` is
            not specified, an error is raised.
        """

        
        name = name if name else getattr(self,'name',None)
        if not name:
            message = f'No name has been specified for \n{self.__repr__()}'
            raise Exception(message)
            
        arg_str = fr'\left({",".join(latex(v) for v in self.variables)}\right)'
        expr_str = fr'{latex(self.expr)}'
        
        from IPython.display import Math
        return Math(f'{latex(name)}{arg_str} = {expr_str}')


class Named_Function_from_Expression(Function_from_Expression):
    """just a convienience class """
    
    def __new__(cls, name, variables, expr):
        return Function_from_Expression.__new__(cls, variables, expr, name=name)
