import sys
import os
import re

class SymbolTable:

    def __init__(self):
        self.symbol_table = {}
        return

    def startSubroutine(self):
        self.symbol_table.clear()
        return

    def define(self, name, type, kind):
        self.symbol_table[name] = [type, kind, self.varCount(kind)]
        return

    def varCount(self, kind):
        counter = 0
        for x in self.symbol_table.values():
            if x[1] == kind:
                counter += 1
        return counter

    def kindOf(self, name):
        return self.symbol_table[name][1]

    def typeOf(self, name):
        return self.symbol_table[name][0]

    def indexOf(self, name):
        return self.symbol_table[name][2]

class VMWriter:

    def __init__(self, destiny):
        self.destiny = open(destiny, 'w')

    def writePush(self, segment, index):
        self.destiny.write("push " + segment + " " + str(index) + "\n")
        return

    def writePop(self, segment, index):
        self.destiny.write("pop " + segment + " " + str(index) + "\n")
        return

    def writeArithmetic(self, command):
        self.destiny.write(command + "\n")
        return

    def writeLabel(self, label):
        self.destiny.write("label L" + str(label) + "\n")
        return

    def writeGoto(self, label):
        self.destiny.write("goto L" + str(label) + "\n")
        return

    def writeIf(self, label):
        self.destiny.write("if-goto L" + str(label) + "\n")
        return

    def writeCall(self, name, nArgs):
        self.destiny.write("call " + name + " " + str(nArgs) + "\n")
        return

    def writeFunction(self, name, nLocals):
        self.destiny.write("function " + name + " " + str(nLocals) + "\n")
        return

    def writeReturn(self):
        self.destiny.write("return" + "\n")
        return

    def writeString(self, string):
        counter = 0
        for char in string:
            if char != '\"':
                counter += 1
        self.writePush('constant', counter)
        self.writeCall("String.new", 1)
        for char in string:
            if char != '\"':
                self.writePush('constant', ord(char))
                self.writeCall("String.appendChar", 2)

    def close(self):
        self.destiny.close()
        return

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

    binaryOperations  = {'+', '-', '*', '/', '|', '=', '&lt;', '&gt;', '&amp;'}
    unaryOperations   = {'-', '~'}
    keywords          = {'true', 'false', 'null', 'this'}
    fBinaryOperations = {'+' : 'add', '-' : 'sub', '*' : 'call Math.multiply 2',
                         '/' : 'call Math.divide 2', '|' : 'or', '=' : 'eq',
                         '&lt;' : 'lt', '&gt;' : 'gt', '&amp;' : 'and'}
    fUnaryOperations   = {'-' : 'neg', '~' : 'not'}

    def __init__ (self, source, destiny):
        self.tokenizer = JackTokenizer(open(source, 'r'))
        self.parsedRules = []
        #self.destiny = open(destiny, 'w')
        self.writer = VMWriter(destiny[:-4] + ".vm")
        self.classSymbolTable = SymbolTable()
        self.subroutineSymbolTable = SymbolTable()
        self.className = ''
        self.labelCounter = 0
        self.labelList = []

    '''
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
    '''

    def advance(self):
        token = self.tokenizer.advance()
        #self.writeLine(token)
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
        #self.writeStartRule('class')
        self.advance() #class
        self.className = self.tokenizer.nextToken()[1]
        self.advance() #name
        self.advance() #{
        while self.existClassVarDec():
            self.compileClassVarDec()
        while self.existSubroutine():
            self.compileSubroutine()
        self.advance() #}
        #self.writeEndRule()
        #self.destiny.close()
        self.writer.close()
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

    def setIdentifierKind(self):
        if self.tokenizer.nextToken()[1] == 'field':
            self.identifierKind = 'this'
        else:
            self.identifierKind = self.tokenizer.nextToken()[1]
        return

    def setIdentifierType(self):
        self.identifierType = self.tokenizer.nextToken()[1]
        return

    def setIdentifierName(self):
        self.identifierName = self.tokenizer.nextToken()[1]
        return

    def registerClassIdentifier(self):
        self.classSymbolTable.define(self.identifierName, self.identifierType, self.identifierKind)
        #print(self.classSymbolTable.symbol_table)
        return

    def registerSubroutineIdentifier(self):
        self.subroutineSymbolTable.define(self.identifierName, self.identifierType, self.identifierKind)
        #print(self.subroutineSymbolTable.symbol_table)
        return

    def compileClassVarDec(self):
        #self.writeStartRule('classVarDec')
        self.setIdentifierKind()
        self.advance()
        self.setIdentifierType()
        self.advance()
        self.setIdentifierName()
        self.advance()
        self.registerClassIdentifier()
        while self.nextValueIs(","):
            self.advance()
            self.setIdentifierName()
            self.advance()
            self.registerClassIdentifier()
        self.advance()
        #self.writeEndRule()
        return

    def setFunctionName(self):
        self.functionName = self.className + "." + self.tokenizer.nextToken()[1]
        return

    def setFunctionType(self):
        self.functionType = self.tokenizer.nextToken()[1]

    def setSubroutineType(self):
        self.subroutineType = self.tokenizer.nextToken()[1]

    def compileSubroutine(self):
        self.subroutineSymbolTable.startSubroutine()
        self.setSubroutineType()
        if self.subroutineType == 'method':
            self.subroutineSymbolTable.define('this', self.className, 'argument')
        #self.writeStartRule('subroutineDec')
        self.advance() #function/method/constructor
        self.setFunctionType()
        self.advance() #type
        self.setFunctionName()
        self.advance() #name
        self.advance() #(
        self.compileParameterList()
        self.advance() #)
        self.compileSubroutineBody()
        #self.writeEndRule()
        return

    def compileParameterList(self):
        #self.writeStartRule('parameterList')
        self.identifierKind = 'argument'
        while self.existParameter():
            self.setIdentifierType()
            self.advance()
            self.setIdentifierName()
            self.advance()
            self.registerSubroutineIdentifier()
            if self.nextValueIs(","):
                self.advance()
        #self.writeEndRule()
        return

    def compileSubroutineBody(self):
        #self.writeStartRule('subroutineBody')
        self.advance() #{
        while self.existVarDec():
            self.compileVarDec()
        self.writer.writeFunction(self.functionName, self.subroutineSymbolTable.varCount('local'))
        if   self.subroutineType == 'method':
            self.writer.writePush('argument', 0)
            self.writer.writePop('pointer', 0)
        elif self.subroutineType == 'constructor':
            self.writer.writePush('constant', self.classSymbolTable.varCount('this'))
            self.writer.writeCall('Memory.alloc', 1)
            self.writer.writePop('pointer', 0)
        self.compileStatements()
        self.advance() #}
        #self.writeEndRule()
        return

    def compileVarDec(self):
        #self.writeStartRule('varDec')
        self.identifierKind = 'local'
        self.advance()
        self.setIdentifierType()
        self.advance()
        self.setIdentifierName()
        self.advance()
        self.registerSubroutineIdentifier()
        while self.nextValueIs(","):
            self.advance()
            self.setIdentifierName()
            self.advance()
            self.registerSubroutineIdentifier()
        self.advance()
        #self.writeEndRule()
        return

    def compileStatements(self):
        #self.writeStartRule('statements')
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
        #self.writeEndRule()
        return

    def compileDo(self):
        #self.writeStartRule('doStatement')
        self.advance() #do
        self.compileTerm()
        self.advance() #;
        self.writer.writePop("temp", 0)
        #self.writeEndRule()
        return

    def compileExpressionList(self):
        #self.writeStartRule('expressionList')
        if self.existExpression():
            self.functionArgCounter += 1
            self.compileExpression()
        while self.nextValueIs(","):
            self.functionArgCounter += 1
            self.advance()
            self.compileExpression()
        #self.writeEndRule()
        return

    def bArithmetic(self, operation):
        return self.fBinaryOperations[operation]

    def uArithmetic(self, operation):
        return self.fUnaryOperations[operation]

    def compileExpression(self):
        #self.writeStartRule('expression')
        self.compileTerm()
        while self.nextValueIsIn(self.binaryOperations):
            self.advance()
            operation = self.bArithmetic(self.tokenizer.currentToken[1])
            self.compileTerm()
            self.writer.writeArithmetic(operation)
        #self.writeEndRule()
        return

    def setFunctionCall(self, firstName):
        self.functionCall = firstName + "." + self.tokenizer.nextToken()[1]
        self.functionArgCounter = 0
        return

    def setClassFunctionCall(self):
        self.functionCall = self.className + "." + self.tokenizer.currentToken[1]
        self.functionArgCounter = 1
        return

    def setMethodCall(self, varClassName):
        self.functionCall = varClassName + "." + self.tokenizer.nextToken()[1]
        self.functionArgCounter = 0
        return

    def compileTerm(self):
        #self.writeStartRule('term')
        if   self.nextTokenIs("integerConstant"):
            self.advance() #number
            self.writer.writePush('constant', self.tokenizer.currentToken[1])
        elif  self.nextTokenIs("stringConstant"):
            self.advance() #string
            self.writer.writeString(self.tokenizer.currentToken[1])
        elif self.nextValueIsIn(self.keywords):
            self.advance() #keyword
            keyword = self.tokenizer.currentToken[1]
            if   keyword == 'null' or keyword == 'false':
                self.writer.writePush('constant', 0)
            elif keyword == 'true':
                self.writer.writePush('constant', 0)
                self.writer.writeArithmetic('not')
            elif keyword == 'this':
                self.writer.writePush('pointer', 0)
        elif self.nextTokenIs("identifier"):
            self.advance()
            varName = self.tokenizer.currentToken[1]
            if varName in self.subroutineSymbolTable.symbol_table:
                self.writer.writePush(self.subroutineSymbolTable.kindOf(varName), self.subroutineSymbolTable.indexOf(varName))
                if self.nextValueIs("."):
                    varClassName = self.subroutineSymbolTable.typeOf(self.tokenizer.currentToken[1])
                    self.advance() #.
                    self.setMethodCall(varClassName)
                    #self.writer.writePush(self.subroutineSymbolTable.kindOf(firstName), self.subroutineSymbolTable.indexOf(firstName))
                    self.advance() #method name
                    self.advance() #(
                    self.compileExpressionList()
                    self.advance() #)
                    self.writer.writeCall(self.functionCall, self.functionArgCounter + 1)
                elif   self.nextValueIs("["):
                    self.writeArrayIndex()
                    self.writer.writePop('pointer', 1)
                    self.writer.writePush('that', 0)
            else:
                if varName in self.classSymbolTable.symbol_table:
                    self.writer.writePush(self.classSymbolTable.kindOf(varName), self.classSymbolTable.indexOf(varName))
                    if self.nextValueIs("."):
                        varClassName = self.classSymbolTable.typeOf(self.tokenizer.currentToken[1])
                        self.advance() #.
                        self.setMethodCall(varClassName)
                        #self.writer.writePush(self.subroutineSymbolTable.kindOf(firstName), self.subroutineSymbolTable.indexOf(firstName))
                        self.advance() #method name
                        self.advance() #(
                        self.compileExpressionList()
                        self.advance() #)
                        self.writer.writeCall(self.functionCall, self.functionArgCounter + 1)
                    elif   self.nextValueIs("["):
                        self.writeArrayIndex()
                        self.writer.writePop('pointer', 1)
                        self.writer.writePush('that', 0)
                else:
                    if self.nextValueIs("("):
                        if self.subroutineType == 'constructor' or self.subroutineType == 'method':
                            self.writer.writePush('pointer', 0)
                        self.setClassFunctionCall()
                        self.advance()
                        self.compileExpressionList()
                        self.advance()
                        self.writer.writeCall(self.functionCall, self.functionArgCounter)
                    elif self.nextValueIs("."):
                        firstName = self.tokenizer.currentToken[1]
                        self.advance() #.
                        self.setFunctionCall(firstName)
                        self.advance()
                        self.advance() #(
                        self.compileExpressionList()
                        self.advance() #)
                        self.writer.writeCall(self.functionCall, self.functionArgCounter)
        elif self.nextValueIsIn(self.unaryOperations):
            self.advance()
            operation = self.uArithmetic(self.tokenizer.currentToken[1])
            self.compileTerm()
            self.writer.writeArithmetic(operation)
        elif self.nextValueIs("("):
            self.advance()
            self.compileExpression()
            self.advance()
        #self.writeEndRule()
        return

    def compileLet(self):
        #self.writeStartRule('letStatement')
        self.advance() #let
        self.advance() #varName
        varName = self.tokenizer.currentToken[1]
        if self.nextValueIs("["):
            if varName in self.classSymbolTable.symbol_table:
                self.writer.writePush(self.classSymbolTable.kindOf(varName), self.classSymbolTable.indexOf(varName))
            elif varName in self.subroutineSymbolTable.symbol_table:
                self.writer.writePush(self.subroutineSymbolTable.kindOf(varName), self.subroutineSymbolTable.indexOf(varName))
            self.writeArrayIndex()
            self.advance() #=
            self.compileExpression()
            self.writer.writePop('temp', 0)
            self.writer.writePop('pointer', 1)
            self.writer.writePush('temp', 0)
            self.writer.writePop('that', 0)
            self.advance() #;
        else:
            self.advance() #=
            self.compileExpression()
            if varName in self.subroutineSymbolTable.symbol_table:
                segment = self.subroutineSymbolTable.kindOf(varName)
                index = self.subroutineSymbolTable.indexOf(varName)
            else:
                segment = self.classSymbolTable.kindOf(varName)
                index = self.classSymbolTable.indexOf(varName)
            self.writer.writePop(segment, index)
            self.advance() #;
        #self.writeEndRule()
        return

    def writeArrayIndex(self):
        self.advance() #[
        self.compileExpression()
        self.writer.writeArithmetic('add')
        self.advance() #]
        return

    def increaseLabelCounter(self):
        self.labelCounter += 1
        return

    def addLabel(self):
        self.increaseLabelCounter()
        self.labelList.insert(0, self.labelCounter)
        self.increaseLabelCounter()
        self.labelList.insert(1, self.labelCounter)
        return

    def removeLabel(self):
        del self.labelList[1]
        del self.labelList[0]

    def compileWhile(self):
        #self.writeStartRule('whileStatement')
        self.advance() #while
        self.advance() #(
        self.addLabel()
        self.writer.writeLabel(self.labelList[0])
        self.compileExpression()
        self.writer.writeArithmetic('not')
        self.advance() #)
        self.advance() #{
        self.writer.writeIf(self.labelList[1])
        self.compileStatements()
        self.writer.writeGoto(self.labelList[0])
        self.advance() #}
        self.writer.writeLabel(self.labelList[1])
        self.removeLabel()
        #self.writeEndRule()
        return

    def compileIf(self):
        #self.writeStartRule('ifStatement')
        self.advance() #if
        self.advance() #(
        self.addLabel()
        self.compileExpression()
        self.writer.writeArithmetic('not')
        self.advance() #)
        self.writer.writeIf(self.labelList[0])
        self.advance() #{
        self.compileStatements()
        self.advance() #}
        self.writer.writeGoto(self.labelList[1])
        self.writer.writeLabel(self.labelList[0])
        if self.nextValueIs("else"):
            self.advance() #else
            self.advance() #{
            self.compileStatements()
            self.advance() #}
            #self.writeEndRule()
        self.writer.writeLabel(self.labelList[1])
        self.removeLabel()
        return

    def compileReturn(self):
        #self.writeStartRule('returnStatement')
        self.advance()
        if self.existExpression():
            self.compileExpression()
        self.advance()
        if  self.functionType == 'void':
            self.writer.writePush('constant', 0)
        self.writer.writeReturn()
        #self.writeEndRule()
        return

class JackCompiler:

    @staticmethod
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
                    #print("Classe compilada", filename)
        elif os.path.isfile(source):
            source = source.split(".")[0]
            compilation = CompilationEngine(source + ".jack", source + ".xml")
            compilation.compileClass()
        else:
            raise Exception("Invalid Source")

        return

if __name__ == '__main__':
    JackCompiler.main()
