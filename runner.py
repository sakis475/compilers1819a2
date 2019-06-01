import plex  

class ParseError (Exception):
    pass

class RunError (Exception):
    pass

class myParser:
    def __init__(self):
        #ta pattern pou xreiazomaste
        
        string = plex.Range("azAZ")
        token_equals = plex.Str('=')
        token_leftParenthesis = plex.Str('(')
        token_rightParenthesis = plex.Str(')')
        number = plex.Range('01')
        space = plex.Any(' \n\t')
        token_xor = plex.Str('xor')
        token_or = plex.Str('or')
        token_and = plex.Str('and')
        identifier = string + plex.Rep(string|number)
        binary = plex.Rep1(number)
        token_print = plex.Str('print')
        #to scanner leksiko
        self.lexicon = plex.Lexicon([
            (token_xor, 'xor'),
            (token_or, 'or'),
            (token_and, 'and'),
            (token_leftParenthesis, '('),
            (token_rightParenthesis, ')'),
            (token_equals, '='),
            (binary, 'binary'),
            (token_print, 'print'),
            (identifier, 'id'),
            (space, plex.IGNORE),
        ])
        self.st = {}

    def create_scanner(self, fp):
        """ Creates a plex scanner for a particular grammar 
        to operate on file object fp. """
        self.scanner = plex.Scanner(self.lexicon, fp)
        self.la, self.text = self.next_token()
    
    def next_token(self):
        """ Returns tuple (next_token,matched-text). """
        return self.scanner.read()

    def parse(self, fp):
        self.create_scanner(fp)
        self.expression_list()

    def match(self, token):
        """ Consumes (matches with current lookahead) an expected token.
        Raises ParseError if anything else is found. Acquires new lookahead. """ 
        if self.la == token:
            self.la, self.text = self.next_token()
        else:
            raise ParseError("Expected self.la == token in match()")

    def expression_list(self):
        if self.la == 'id' or self.la == 'print':
            self.expression()
            self.expression_list()
        elif self.la == None:
            return
        else:
            raise ParseError('Expected id or print in expression_list()')

    def expression(self):
        if self.la == 'id':
            varname = self.text
            self.match('id')
            self.match('=')
            e = self.definition()
            self.st[varname] = e
        elif self.la == 'print':
            self.match('print')
            print('{:b}'.format(self.definition()))
        else:
            raise ParseError('Expected id or print in expression()')

    def definition(self):
        if self.la == '(' or self.la == 'id' or self.la == 'binary':
            a = self.atom()
            while self.la == 'xor':
                self.match('xor')
                a ^= self.atom()
            if self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
                return a
            raise ParseError('Expected xor in atom()')
        else:
            raise ParseError('Expected ( or id or binary in definition()')
   
    def atom(self):
        if self.la == '(' or self.la == 'id' or self.la == 'binary':
            t = self.term()
            while self.la == 'or':
                self.match('or')
                t |= self.term()
            if self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
                return t
            raise ParseError('Expected or in atom()')
        else:
            raise ParseError('Expected ( or id or binary in atom()')

    def term(self):
        if self.la == '(' or self.la == 'id' or self.la == 'binary':
            f = self.factor()
            while self.la == 'and':
                self.match('and')
                f &= self.factor()
            if self.la == 'xor' or self.la == 'or' or self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
                return f
            raise ParseError('Expected and in term()')
        else:
            raise ParseError('Expected ( or id or binary in term()')

    def factor(self):
        if self.la == '(':
            self.match('(')
            e = self.definition()
            self.match(')')
            return e
        elif self.la == 'id':
            varname = self.text
            self.match('id')
            if varname in self.st:
                return self.st[varname]
            raise RunError("lathos sto factor")
        elif self.la == 'binary':
            value = int(self.text, 2)
            self.match('binary')
            return value
        else:
            raise ParseError('Expected ( or id or binary in factor()')

parser = myParser()
with open('testing.txt', 'r') as fp:
    parser.parse(fp)