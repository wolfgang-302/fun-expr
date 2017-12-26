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


#import sympy

#from IPython.display import display_latex


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
    
    def __new__(cls, variables, expr):
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
        return obj

    def subs(self, *arg, **kwargs):
        """
        Substitution should not be allowed on variables.
        So the result of a subst is testet, if
        variables have changed. In this case, a 
        ValueError is thrown.
        
        Example:
        >>> from sympy import *
        >>> from fun_expr import Function_as_Expression as FE
        >>> a,x,y = symbols('a,x,y')
        >>> f = FE((x,y), a*x*y**2)
        >>> f.subs(a,x) # returns x**2*y**2
        >>> f.subs(x,y) # throws ValueError since x is a variable of f
        >>> f.subs(x,a) # throws ValueError since x is a variable of f
        """
        obj = super().subs(*arg, **kwargs)
        if False in [u==v for u,v in zip(self.variables,obj.variables)]:
            raise ValueError(
                    "Substitution of variables is not valid: {}".format(arg) 
                    )
        return obj
        
    
    def diff(self, *symbols, **assumptions):
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
            return Function_from_Expression(self.variables, expr)
        return expr
        
    def integrate(self, *args, **kwargs):
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
                return Function_from_Expression(new_variables, expr)
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
    

class Named_Function_from_Expression(Function_from_Expression):
    """
    Create a named function from an expression.
    
    Example fo use:
    >>> from sympy import *
    >>> from fun_expr import (
            Function_from_Expression as FE,
            Named_Function_from_Expression as NFE,
            )
    >>> f = NFE("f", x, x**2)
    >>> f.displ()
    '$f(x) = x^{2}$'
    >>> f_1 = f.diff(x,name="f'")
    >>> f_1.displ()
    "$f'(x) = 2 x$"
    >>> f_1 = f.diff(x)
    '((x) \mapsto 2\,x)'
    >>> print(type(f_1))
    fun_expr.function_from_expression.Function_from_Expression
    >>> f.displ(2)
    '$f(2) = 4$'
    """
    
    def __new__(cls, name, variables, expr):
        obj = Function_from_Expression.__new__(cls, variables, expr)
        obj.name = name
        return obj
    
    def displ(self, *values, par="$", n=False, simplify=False, **kwargs):
        """
        This is a convenience function to display the equation 
        
          $f(x_1,x_2,...) = rhs$
          or 
          $$f(x_1,x_2,...) = rhs$$ # if par='$$'
          
        in latex-notation. 

        If values == (): replace rhs by self.expr
        instead. If values are specified, exactly one 
        value for every variable of this function is 
        expected.
        
        If n ist True, replace the rhs by rhs.n().
        If n is an integer number replace the rhs by rhs.n(n).
        
        If simplify is true, simplify rhs.
        
        Here rhs always is the right hand side of the equation.
        """
        
        # there are exactly two possibilities:
        #    either there is no value at all, values == ()
        #    or there are exactly len(self.variables) values.
        #    if there are no values, set rhs to self.expr
        #    else calculate rhs = f(*values)
        if values is not ():
            vals = values 
            rhs = super().__call__(*values, **kwargs) 
        else:
            vals = self.variables
            rhs = self.expr
        
        # n can be None, bool or int.
        # if n is None do nothing
        # if n is bool and n is True, replace rhs by rhs.n()
        # if n is bool and n is False, do nothing
        # if n is int replace rhs by rhs.n(n)
        if n is not None:
            if isinstance(n, bool):
                if n:
                    rhs = rhs.n()
            else:
                rhs = rhs.n(n)
        
        # simplify can be True or False
        # if simplfiy ist True, the rhs is simplified
        if simplify:
            rhs = rhs.simplify()
        
        # create output as 
        #    f(x_1,x_2,...) = rhs
        # in latex notation
        ret_val = par 
        ret_val += latex(self.name)
        ret_val += r"\left({vars}\right) = ".format(vars=','.join(latex(v) for v in vals))
        ret_val += latex(rhs) 
        ret_val += par
        return ret_val
    
    def diff(self, *symbols, **assumptions):
        """
        If a name is specified, as_function is set to True.
        In this case, a Named_Function_of_Expression is retured.
        If no name is specified, the result depends on as_function
        """
        name = assumptions.pop('name',None)
        as_function = assumptions.pop('as_function', True) or name is not None 
        # let my parent do the hard part 
        res = super().diff(*symbols, as_function=as_function, **assumptions)
        if name is not None:
            return Named_Function_from_Expression(name, res.variables, res.expr)
        else:
            return res
        
    def integrate(self, *args, **kwargs):
        """
        If a name is specified, as_function is set to True.
        In this case, a Named_Function_of_Expression is returned.
        If no name is specified, the result depends on as_function
        """
        name = kwargs.pop('name',None)
        as_function = kwargs.pop('as_function', False) or name is not None
        # let my parent do the hard part
        res = super().integrate(*args, as_function=as_function, **kwargs)
        if name is not None:
            return Named_Function_from_Expression(name, res.variables, res.expr)
        else:
            return res