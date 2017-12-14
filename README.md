# fun-expr
Create a sympy function from an expression

fun-expr provides the possibility to create sympy functions from sympy 
expressions.

To install pip can be used:

`pip install git+https://github.com/wolfgang-302/fun-expr.git`

Then, to use the class `Function_from_Expression` import

```
from sympy import *
init_printing()

from fun_expr.function_from_expression import Function_from_Expression as FE
```

and define i.e. the function `f(x) = x**2` as
```
# define the variable of the function
x = Symbol('x')

# define the function
f = FE(x, x**2)

# show the result
f
```

More examples how to use `Function_from_Expression` can be found in the jupyter-notebooks in the docs.
