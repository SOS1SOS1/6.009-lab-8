import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.

# Symbol - base class
    # - has dunder methods to allow for expressions to more easily be entered, like Var('x') + Num(3) / Num(2)
    # - includes derivative, simplify, and evalutation methods

# Var - instances of Var represent variables (such as x or y)
    # instance attributes
        # name - variable name

# Num - instances of Num represent numbers within symbolic expressions
    # instance attributes
        # n - number's value

# BinOp (binary operation) - ways of combining primitive symbols (Vars and Nums) together
    # - each instance has two instance attributes, left and right
        # left: a Symbol instance representing the left-hand operand
        # right: a Symbol instance representing the right-hand operand
    # - has four subclasses
        # Add, to represent an addition
        # Sub, to represent a subtraction
        # Mul, to represent a multiplication
        # Div, to represent a division 

class Symbol:
    precedence = None

    def __add__(self, e1):
        return Add(self, e1)
        
    def __radd__(self, e1):
        return Add(e1, self)

    def __sub__(self, e1):
        return Sub(self, e1)
        
    def __rsub__(self, e1):
        return Sub(e1, self)

    def __mul__(self, e1):
        return Mul(self, e1)
        
    def __rmul__(self, e1):
        return Mul(e1, self)

    def __truediv__(self, e1):
        return Div(self, e1)
        
    def __rtruediv__(self, e1):
        return Div(e1, self)

    def deriv(self, name):
        """
        Returns derivative of expression with respect to inputed variable name
        """
        # constant rule
        if type(self) == Num or (type(self) == Var and self.name != name):
            return Num(0)
        elif type(self) == Var and self.name == name:
            return Num(1)
        return self.deriv_helper(name)

    def deriv_helper(self):
        """
        Add, Sub, Mul, and Div subclasses of Symbol override this helper function to 
        handle the different kind of derivatives properly
        """
        pass

    def simplify(self):
        """
        Returns a simplified form of the expression
        """
        # single number or variable always simplifies to itself
        if type(self) == Num or type(self) == Var:
            return self
        left_sim = self.left.simplify()
        right_sim = self.right.simplify()
        return self.simplify_helper(left_sim, right_sim)

    def simplify_helper(self):
        """
        Add, Sub, Mul, and Div subclasses of Symbol override this helper function to 
        handle the different kind of simplification rules properly
        """
        pass

    def eval(self, mapping):
        """
        Plugs in variable's values from mapping and returns a numerical value for the expression
        """
        if type(self) == Num:
            return self.n
        if type(self) == Var:
            # if variable name is in mapping, return its value as Num
            if self.name in mapping:
                return mapping[self.name]
            # otherwise, if variable name is not in mapping, leave that variable in the expression
            return self
        left_eval = self.left.eval(mapping)
        right_eval = self.right.eval(mapping)
        return self.eval_helper(left_eval, right_eval)

    def eval_helper(self):
        """
        Add, Sub, Mul, and Div subclasses of Symbol override this helper function to 
        handle the different kind of evaluations properly
        """
        pass

class Var(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Var(' + repr(self.name) + ')'


class Num(Symbol):
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return 'Num(' + repr(self.n) + ')'

class BinOp(Symbol):
    def __init__(self, left, right):
        """
        Initializer.  
            left: a Symbol instance representing the left-hand operand
            right: a Symbol instance representing the right-hand operand
        """
        self.left = left if isinstance(left, Symbol) else Var(left) if type(left) == str else Num(left)
        self.right = right if isinstance(right, Symbol) else Var(right) if type(right) == str else Num(right)

    # prints human readable representation of expression with paratheses as needed
    def __str__(self):
        left = str(self.left)
        right = str(self.right)
        # add paratheses around left operand, if B.left/B.right represent expressions with lower precedence than B
        if self.left.precedence and self.left.precedence > self.precedence:
            left = "(" + left + ")"
        # for right operand, also add paratheses if B represents - or / and B.right is an expression w/ the same precedence
        if self.right.precedence and ((self.right.precedence > self.precedence) or ((self.operation == "Sub" or self.operation == "Div") and self.precedence == self.right.precedence)):
            right = "(" + right + ")"
        return left + " " + self.operand + " " + right

    def __repr__(self):
        return self.operation + "(" + repr(self.left) + ", " + repr(self.right) + ")"

class Add(BinOp):
    operand = "+"
    operation = "Add"
    precedence = 2

    def deriv_helper(self, name):
        # sum rule
        return self.left.deriv(name) + self.right.deriv(name)

    def simplify_helper(self, left, right):
        # any binary operation on two numbers should simplify to a single number containing the result
        if type(left) == Num and type(right) == Num:
            return Num(left.n + right.n)
        # adding 0 to (or subtracting 0 from) any expression E should simplify to E
        elif type(left) == Num and left.n == 0:
            return right
        elif type(right) == Num and right.n == 0:
            return left
        return left + right

    def eval_helper(self, left, right):
        return left + right


class Sub(BinOp):
    operand = "-"
    operation = "Sub"
    precedence = 2

    def deriv_helper(self, name):
        # difference rule
        return self.left.deriv(name) - self.right.deriv(name)

    def simplify_helper(self, left, right):
        # any binary operation on two numbers should simplify to a single number containing the result
        if type(left) == Num and type(right) == Num:
            return Num(left.n - right.n)
        # adding 0 to (or subtracting 0 from) any expression E should simplify to E
        elif type(right) == Num and right.n == 0:
            return left
        return left - right

    def eval_helper(self, left, right):
        return left - right

class Mul(BinOp):
    operand = "*"
    operation = "Mul"
    precedence = 1

    def deriv_helper(self, name):
        # product rule
        return self.left * self.right.deriv(name) + self.right * self.left.deriv(name)

    def simplify_helper(self, left, right):
        # any binary operation on two numbers should simplify to a single number containing the result
        if type(left) == Num and type(right) == Num:
            return Num(left.n * right.n)
        # multiplying any expression E by 1 should simplify to E
        elif type(left) == Num and left.n == 1:
            return right
        elif type(right) == Num and right.n == 1:
            return left
        # multiplying any expression E by 0 should simplify to 0
        elif ((type(left) == Num and left.n == 0) or type(right) == Num and right.n == 0):
            return Num(0)
        return left * right

    def eval_helper(self, left, right):
        return left * right

class Div(BinOp):
    operand = "/"
    operation = "Div"
    precedence = 1

    def deriv_helper(self, name):
        # quotient rule
        return (self.right * self.left.deriv(name) - self.left * self.right.deriv(name)) / (self.right * self.right)

    def simplify_helper(self, left, right):
        # any binary operation on two numbers should simplify to a single number containing the result
        if type(left) == Num and type(right) == Num:
            return Num(left.n / right.n)
        # dividing any expression E by 1 should simplify to E
        elif type(right) == Num and right.n == 1:
            return left
        # dividing 0 by any expression E should simplify to 0
        elif type(left) == Num and left.n == 0:
            return Num(0)
        return left / right

    def eval_helper(self, left, right):
        return left / right

def tokenize(text):
    """
    Takes a string as input and returns a list of meaningful tokens (parentheses, 
    variable names, numbers, or operands)
    """
    tokens = []
    last_char = ''
    for idx, c in enumerate(text):
        if c == '(' or c == ')' or c in {'*', '/', '+', '-'}:
            # symbol
            tokens.append(c)
        elif c != ' ':
            if not last_char or last_char == " " or last_char == "(":
                # variable name
                tokens.append(c)
            else:
                # negative number and/or number with more than one digit
                tokens[-1] = tokens[-1] + c
        last_char = c
    return tokens

def parse(tokens):
    """
    Takes the output of tokenize and convert it into an appropriate instance of 
    Symbol (or some subclass thereof)
    """
    def parse_expression(index):
        """
        Takes in an index into the tokens list and returns the expression found 
        starting at the location given by index (an instance of one of the Symbol subclasses)
        and the index beyond where this expression ends
        """
        token = tokens[index]
        if token.isalpha():
            # token represents a variable name
            return Var(token), index+1
        elif token == '(':
            # recursively parses the two subexpressions and combines them into an appropriate 
            # instance of a subclass of BinOp (determined by op)
            lhs, end_index = parse_expression(index+1)
            op = tokens[end_index]
            rhs, end_index = parse_expression(end_index+1)
            if op == "+":
                operation = Add(lhs, rhs)
            elif op == "-":
                operation = Sub(lhs, rhs)
            elif op == "*":
                operation = Mul(lhs, rhs)
            else:
                operation = Div(lhs, rhs)
            return operation, end_index+1
        else:
            # token represents an integer
            return Num(int(token)), index+1
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def sym(text_expr):
    """
    Parses strings into symbolic expressions
    """
    tokens = tokenize(text_expr)
    return parse(tokens)

if __name__ == '__main__':
    doctest.testmod()
    # t = tokenize("(x * (-200 + 3))")
    # print(t)

    # t = tokenize('20')
    # print(repr(sym('20')))

    # "(x * (2 + 3))"
    # t = tokenize("(x * (2 + 3))")
    # # print(t)
    # print(repr(sym("(x * (2 + 3))")))

    # "(x * (-302 + 3))"
    t = tokenize("(x * (-302 + 3))")
    print(t)

    # "(x * (30 - 3))"
    t = tokenize("(x * (30 - 3))")
    print(t)

    result = Mul(-1, Div( Mul(Num(6), Sub(Num(0), Var('e')) ), Add(Var('N'), Var('t')) ) )
    print(result)
    result = result.eval({'e': 7, 'N': 3, 't': 9})



    # print(result)
