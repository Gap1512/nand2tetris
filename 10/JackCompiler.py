import sys
import os
import re

class JackTokenizer:

    keywords = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char',
                'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while',
                'return'}
    symbols = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '<', '>', '=', '~'}
    keywordsRE = '(?!\w)'.join(keywords) + '(?!\w)'
    symbolsRE = '[' + re.escape('|'.join(symbols)) + ']'
    integersRE = r'\d+'
    stringsRE = r'"[^"\n"]*"'
    identifiersRE = r'[\w]+'
    word = re.compile(keywordsRE    + '|' +
                      symbolsRE     + '|' +
                      integersRE    + '|' +
                      stringsRE     + '|' +
                      identifiersRE        )

    def __init__(self, file):
        self.file = file
        self.currentToken = ''
        self.lines = self.file.read()
        self.removeComments()
        self.tokens = self.tokenize()
        self.tokens = self.replaceSymbols()

    def removeComments(self):
        index = 0
        end = 0
        filter = ''
        while index < len(self.lines):
            char = self.lines[index]
            if char == "/":
                if   self.lines[index + 1] == "/":
                    end = self.lines.find("\n", index + 1)
                    index = end + 1
                    filter += ' '
                elif self.lines[index + 1] == "*":
                    end = self.lines.find("*/", index + 1)
                    index = end + 2
                    filter += ' '
                else:
                    filter += self.lines[index]
                    index += 1
            else:
                filter += self.lines[index]
                index += 1
        self.lines = filter
        return

    def split(self, lines):
        return self.word.findall(lines)

    def tokenize(self):
        words = self.split(self.lines)
        return [self.tokenizeAux(word) for word in words]

    def tokenizeAux(self, word):
        if   word in self.keywords:
            return ("keyword", word)
        elif word in self.symbols:
            return ("symbol", word)
        elif re.match(self.integersRE, word) != None:
            return ("integerConstant", word)
        elif re.match(self.stringsRE, word) != None:
            return ("stringConstant", word)
        else:
            return ("identifier", word)

    def replaceSymbols(self):
        all_tokens = self.tokens
        return [self.replaceSymbolsAux(token) for token in all_tokens]

    def replaceSymbolsAux(self, token):
        value = token[1]
        if   value == '<': return (token[0], '&lt;')
        elif value == '>': return (token[0], '&gt;')
        elif value == '"': return (token[0], '&quot;')
        elif value == '&': return (token[0], '&amp;')
        else:              return (token[0], value)

    def hasMoreTokens(self):
        boolean = self.tokens != []
        return boolean

    def advance(self):
        self.currentToken = self.tokens.pop(0)
        return self.currentToken

    def tokenType(self):
        return self.currentToken[0]

    def tokenValue(self):
        return self.currentToken[1]

    def nextToken(self):
        return self.tokens[0]

class CompilationEngine:

    binaryOperations = {'+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;'}
    unaryOperations  = {'-', '~'}
    keywords          = {'true', 'false', 'null', 'this'}

    def __init__ (self, source, destiny):
        self.tokenizer = JackTokenizer(open(source, 'r'))
        self.parsedRules = []
        self.destiny = open(destiny, 'w')

    def writeStartRule(self, rule):
        self.destiny.write("<" + rule + ">\n")
        rule = self.parsedRules.append(rule)
        return

    def writeEndRule(self):
        rule = self.parsedRules.pop()
        self.destiny.write("</" + rule + ">\n")
        return

    def writeLine(self, token):
        self.destiny.write("<" + token[0] + "> " + token[1] + " </" + token[0] + ">\n")
        return

    def advance(self):
        token = self.tokenizer.advance()
        self.writeLine(token)
        return

    def nextValueIsIn(self, list):
        token = self.tokenizer.nextToken()
        return token[1] in list

    def nextTokenIs(self, token_aux):
        token = self.tokenizer.nextToken()
        return token[0] == token_aux

    def nextValueIs(self, token_aux):
        token = self.tokenizer.nextToken()
        return token[1] == token_aux

    def compileClass(self):
        self.writeStartRule('class')
        self.advance()
        self.advance()
        self.advance()
        while self.existClassVarDec():
            self.compileClassVarDec()
        while self.existSubroutine():
            self.compileSubroutine()
        self.advance()
        self.writeEndRule()
        self.destiny.close()
        return

    def existClassVarDec(self):
        return self.nextValueIs("static") or self.nextValueIs("field")

    def existSubroutine(self):
        return self.nextValueIs("constructor") or self.nextValueIs("method") or self.nextValueIs("function")

    def existParameter(self):
        return not self.nextTokenIs("symbol")

    def existVarDec(self):
        return self.nextValueIs("var")

    def existStatement(self):
        return self.nextValueIs("let")    or \
               self.nextValueIs("if")     or \
               self.nextValueIs("while")  or \
               self.nextValueIs("do")     or \
               self.nextValueIs("return")

    def existExpression(self):
        return self.nextTokenIs("integerConstant")      or \
               self.nextTokenIs("stringConstant")       or \
               self.nextTokenIs("identifier")           or \
               self.nextValueIsIn(self.unaryOperations) or \
               self.nextValueIsIn(self.keywords)        or \
               self.nextValueIs('(')

    def compileClassVarDec(self):
        self.writeStartRule('classVarDec')
        self.advance()
        self.advance()
        self.advance()
        while self.nextValueIs(","):
            self.advance()
            self.advance()
        self.advance()
        self.writeEndRule()
        return

    def compileSubroutine(self):
        self.writeStartRule('subroutineDec')
        self.advance()
        self.advance()
        self.advance()
        self.advance()
        self.compileParameterList()
        self.advance()
        self.compileSubroutineBody()
        self.writeEndRule()
        return

    def compileParameterList(self):
        self.writeStartRule('parameterList')
        while self.existParameter():
            self.advance()
            self.advance()
            if self.nextValueIs(","):
                self.advance()
        self.writeEndRule()
        return

    def compileSubroutineBody(self):
        self.writeStartRule('subroutineBody')
        self.advance()
        while self.existVarDec():
            self.compileVarDec()
        self.compileStatements()
        self.advance()
        self.writeEndRule()
        return

    def compileVarDec(self):
        self.writeStartRule('varDec')
        self.advance()
        self.advance()
        self.advance()
        while self.nextValueIs(","):
            self.advance()
            self.advance()
        self.advance()
        self.writeEndRule()
        return

    def compileStatements(self):
        self.writeStartRule('statements')
        while self.existStatement():
            if self.nextValueIs("let"):
                self.compileLet()
            elif self.nextValueIs("if"):
                self.compileIf()
            elif self.nextValueIs("while"):
                self.compileWhile()
            elif self.nextValueIs("do"):
                self.compileDo()
            elif self.nextValueIs("return"):
                self.compileReturn()
        self.writeEndRule()
        return

    def compileDo(self):
        self.writeStartRule('doStatement')
        self.advance()
        self.compileSubroutineCall()
        self.advance()
        self.writeEndRule()
        return

    def compileSubroutineCall(self):
        self.advance()
        if self.nextValueIs("."):
            self.advance()
            self.advance()
        self.advance()
        self.compileExpressionList()
        self.advance()
        return

    def compileExpressionList(self):
        self.writeStartRule('expressionList')
        if self.existExpression():
            self.compileExpression()
        while self.nextValueIs(","):
            self.advance()
            self.compileExpression()
        self.writeEndRule()
        return

    def compileExpression(self):
        self.writeStartRule('expression')
        self.compileTerm()
        while self.nextValueIsIn(self.binaryOperations):
            self.advance()
            self.compileTerm()
        self.writeEndRule()
        return

    def compileTerm(self):
        self.writeStartRule('term')
        if   self.nextTokenIs("integerConstant") or self.nextTokenIs("stringConstant") or self.nextValueIsIn(self.keywords):
            self.advance()
        elif self.nextTokenIs("identifier"):
            self.advance()
            if   self.nextValueIs("["):
                self.writeArrayIndex()
            elif self.nextValueIs("("):
                self.advance()
                self.compileExpressionList()
                self.advance()
            elif self.nextValueIs("."):
                self.advance()
                self.advance()
                self.advance()
                self.compileExpressionList()
                self.advance()
        elif self.nextValueIsIn(self.unaryOperations):
            self.advance()
            self.compileTerm()
        elif self.nextValueIs("("):
            self.advance()
            self.compileExpression()
            self.advance()
        self.writeEndRule()
        return

    def compileLet(self):
        self.writeStartRule('letStatement')
        self.advance()
        self.advance()
        if self.nextValueIs("["):
            self.writeArrayIndex()
        self.advance()
        self.compileExpression()
        self.advance()
        self.writeEndRule()
        return

    def writeArrayIndex(self):
        self.advance()
        self.compileExpression()
        self.advance()

    def compileWhile(self):
        self.writeStartRule('whileStatement')
        self.advance()
        self.advance()
        self.compileExpression()
        self.advance()
        self.advance()
        self.compileStatements()
        self.advance()
        self.writeEndRule()
        return

    def compileReturn(self):
        self.writeStartRule('returnStatement')
        self.advance()
        if self.existExpression():
            self.compileExpression()
        self.advance()
        self.writeEndRule()
        return

    def compileIf(self):
        self.writeStartRule('ifStatement')
        self.advance()
        self.advance()
        self.compileExpression()
        self.advance()
        self.advance()
        self.compileStatements()
        self.advance()
        if self.nextValueIs("else"):
            self.advance()
            self.advance()
            self.compileStatements()
            self.advance()
        self.writeEndRule()
        return

def main():
    try:
        source = sys.argv[1]
    except:
        raise Exception("Invalid Source")
        return

    if   os.path.isdir(source):
        if not source.endswith("/"):
            source += "/"
        files = os.listdir(source)
        for file in files:
            if file.endswith('.jack'):
                filename = file.split(".")[0]
                compilation = CompilationEngine(source + file, source + filename + ".xml")
                compilation.compileClass()
    elif os.path.isfile(source):
        source = source.split(".")[0]
        compilation = CompilationEngine(source + ".jack", source + ".xml")
        compilation.compileClass()
    else:
        raise Exception("Invalid Source")
    return

if __name__ == '__main__':
    main()
