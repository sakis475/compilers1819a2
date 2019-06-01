import plex  

class ParseError (Exception):
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

    def create_scanner(self, fp):
        """ Creates a plex scanner for a particular grammar 
        to operate on file object fp. """
        self.scanner = plex.Scanner(self.lexicon, fp)
        self.la, self.text = self.next_token()
    
    def next_token(self):
        """ Returns tuple (next_token,matched-text). """
        return self.scanner.read()

    def position(self):
        """ Utility function that returns position in text in case of errors.
        Here it simply returns the scanner position. """
        
        return self.scanner.position()

    

    def match(self, token):
        """ Consumes (matches with current lookahead) an expected token.
        Raises ParseError if anything else is found. Acquires new lookahead. """ 
        print(token),
        if self.la == token:
            self.la, self.text = self.next_token()
        else:
            raise ParseError("Expected self.la == token in match()")

    def parse(self, fp):
        self.create_scanner(fp)
        self.expression_list()

    def expression_list(self):
        if self.la == 'id' or self.la == 'print':
            self.expression()
            self.expression_list()
        elif self.la == None:
            return
        else:
            raise ParseError('Expected id or print in expression_list()')

    def expression(self):
        if self.la == 'print':
            self.match('print')
            self.definition()

        elif self.la == 'id':
              self.match('id')
              self.match('=')
              self.definition()
        else:
            raise ParseError('Expected id or print in expression()')

    def definition(self):
        if self.la == 'id' or self.la == 'binary' or self.la == '(':
            self.atom()
            self.atom_tail()
        else:
            raise ParseError('Expected id or binary or ( in definition()')
    
    def atom_tail(self):
        if self.la == 'xor':
            self.match('xor')
            self.atom()
            self.atom_tail()
        elif self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
            return
        else:
            raise ParseError('Expected xor in atom_tail()')
    
    def atom(self):
        if self.la == '(' or self.la == 'id' or self.la == 'binary':
            self.term()
            self.term_tail()
        else:
            raise ParseError('Expected ( or id or binary in term()')

    def term_tail(self):
        if self.la == 'or':
            self.match('or')
            self.term()
            self.term_tail()
        elif self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
            return
        else:
            raise ParseError('Expected or in term_tail()')

    def term(self):
        if self.la == '(' or self.la == 'id' or self.la == 'binary':
            self.factor()
            self.factor_tail()
        else:
            raise ParseError('Expected ( or id or binary in term()')
    
    def factor_tail(self):
        if self.la == 'and':
            self.match('and')
            self.factor()
            self.factor_tail()
        elif self.la == 'xor' or self.la == 'or' or self.la == 'id' or self.la == 'print' or self.la == None or self.la == ')':
            return
        else:
            raise ParseError('Expected and in factor_tail()')

    def factor(self):
        if self.la == '(':
            self.match('(')
            self.definition()
            self.match(')')
        elif self.la == 'id':
            self.match('id')
        elif self.la == 'binary':
            self.match('binary')
        else:
            raise ParseError('Expected ( or id or binary in factor()')

parser = myParser()
with open('testing.txt', 'r') as fp:
    parser.parse(fp)