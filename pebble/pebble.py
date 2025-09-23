import sys

# -------------------- Lexer --------------------
class Token:
    def __init__(self, kind, value, line, col):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.kind},{self.value},{self.line}:{self.col})"


class Lexer:
    def __init__(self, src, filename="<stdin>"):
        self.src = src
        self.filename = filename
        self.pos = 0
        self.line = 1
        self.col = 1

    def peek(self):
        return self.src[self.pos] if self.pos < len(self.src) else None

    def advance(self):
        ch = self.peek()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokens(self):
        toks = []
        while self.peek() is not None:
            ch = self.peek()
            if ch.isspace():
                self.advance()
                continue
            if ch.isdigit():
                toks.append(self.number())
                continue
            if ch.isalpha() or ch == "_":
                toks.append(self.ident())
                continue
            if ch in "+-*/=<>{}(),":
                toks.append(Token("PUNC", ch, self.line, self.col))
                self.advance()
                continue
            if ch == '"':
                toks.append(self.string())
                continue
            raise SyntaxError(f"{self.filename}:{self.line}:{self.col}: Unexpected character {ch!r}")
        return toks

    def number(self):
        start_col = self.col
        val = ""
        while self.peek() and self.peek().isdigit():
            val += self.advance()
        return Token("NUM", int(val), self.line, start_col)

    def ident(self):
        start_col = self.col
        val = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            val += self.advance()
        return Token("IDENT", val, self.line, start_col)

    def string(self):
        start_col = self.col
        self.advance()  # skip "
        val = ""
        while self.peek() and self.peek() != '"':
            val += self.advance()
        if self.peek() != '"':
            raise SyntaxError(f"{self.filename}:{self.line}:{self.col}: Unterminated string")
        self.advance()
        return Token("STRING", val, self.line, start_col)


# -------------------- Parser --------------------
class Parser:
    def __init__(self, lexer, filename="<stdin>"):
        self.tokens = lexer.tokens()
        self.pos = 0
        self.filename = filename

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        tok = self.peek()
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek():
            stmts.append(self.statement())
        return ("BLOCK", stmts)

    def statement(self):
        tok = self.peek()
        if tok and tok.kind == "IDENT" and tok.value == "print":
            self.advance()
            exprs = []
            while self.peek():
                exprs.append(self.expr())
            return ("PRINT", exprs)
        elif tok and tok.kind == "IDENT":
            # assignment
            name = tok.value
            self.advance()
            eq = self.advance()
            if not (eq.kind == "PUNC" and eq.value == "="):
                raise SyntaxError(f"{self.filename}:{eq.line}:{eq.col}: Expected '='")
            val = self.expr()
            return ("ASSIGN", name, val)
        else:
            return self.expr()

    def expr(self):
        tok = self.advance()
        if tok.kind == "NUM":
            return ("NUM", tok.value)
        if tok.kind == "STRING":
            return ("STRING", tok.value)
        if tok.kind == "IDENT":
            return ("VAR", tok.value)
        raise SyntaxError(f"{self.filename}:{tok.line}:{tok.col}: Unexpected token {tok}")


# -------------------- Interpreter --------------------
class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.env = {}

    def run(self):
        self.exec_block(self.ast)

    def exec_block(self, block):
        kind, stmts = block
        for s in stmts:
            self.exec_stmt(s)

    def exec_stmt(self, stmt):
        kind = stmt[0]
        if kind == "PRINT":
            values = [self.eval(e) for e in stmt[1]]
            print(*values)
        elif kind == "ASSIGN":
            _, name, expr = stmt
            self.env[name] = self.eval(expr)
        else:
            self.eval(stmt)

    def eval(self, node):
        kind = node[0]
        if kind == "NUM":
            return node[1]
        if kind == "STRING":
            return node[1]
        if kind == "VAR":
            name = node[1]
            if name not in self.env:
                raise NameError(f"Undefined variable {name}")
            return self.env[name]
        return None


# -------------------- Runner --------------------
def run_source(src, filename="<stdin>"):
    lex = Lexer(src, filename)
    parser = Parser(lex, filename)
    ast = parser.parse()
    intr = Interpreter(ast)
    intr.run()


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8-sig") as f:
            src = f.read()
        run_source(src, sys.argv[1])
    else:
        print("Usage: python pebble.py program.peb")


if __name__ == "__main__":
    main()
