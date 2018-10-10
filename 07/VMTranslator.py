import sys

filename = sys.argv[1][:-3]
eq_counter = 0
lt_counter = 0
gt_counter = 0

def format_file(list):
    line_counter = 0

    while (line_counter < len(list)):
        if list[line_counter] == '':
            del list[line_counter]
        elif list[line_counter].startswith('//'):
            del list[line_counter]
        else:
            index = list[line_counter].find('//')
            if (index != -1):
                list[line_counter] = list[line_counter][:index]
            line_counter += 1

    return list

def push(symbol_i, destiny):
    list = []
    global filename

    if symbol_i.startswith('local'):
        symbol = '@LCL'
        i = '@' + symbol_i.strip('local')
        list = [i, 'D=A', symbol, 'A=M+D', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('argument'):
        symbol = '@ARG'
        i = '@' + symbol_i.strip('argument')
        list = [i, 'D=A', symbol, 'A=M+D', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('tatic'): #tatic = static
        symbol = '@' + filename + '.' + symbol_i.strip('tatic') #tatic = static
        list = [symbol, 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('constant'):
        i = '@' + symbol_i.strip('constant')
        list = [i, 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('this'):
        symbol = '@THIS'
        i = '@' + symbol_i.strip('this')
        list = [i, 'D=A', symbol, 'A=M+D', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('that'):
        symbol = '@THAT'
        i = '@' + symbol_i.strip('that')
        list = [i, 'D=A', symbol, 'A=M+D', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('ointer'): #ointer = pointer
        i = '@' + str(3 + int(symbol_i.strip('ointer'))) #ointer = pointer
        list = [i, 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']
    elif symbol_i.startswith('temp'):
        i = '@' + str(5 + int(symbol_i.strip('temp')))
        list = [i, 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

    for i in list:
        destiny.write(i+'\n')

def pop(symbol_i, destiny):
    list = []
    global filename

    if symbol_i.startswith('local'):
        symbol = '@LCL'
        i = '@' + symbol_i.strip('local')
        list = [i, 'D=A', symbol, 'D=M+D', '@R13', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@R13', 'A=M', 'M=D']
    elif symbol_i.startswith('argument'):
        symbol = '@ARG'
        i = '@' + symbol_i.strip('argument')
        list = [i, 'D=A', symbol, 'D=M+D', '@R13', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@R13', 'A=M', 'M=D']
    elif symbol_i.startswith('static'):
        symbol = '@' + filename + '.' + symbol_i.strip('static')
        list = ['@SP', 'M=M-1', 'A=M', 'D=M', symbol, 'M=D']
    elif symbol_i.startswith('this'):
        symbol = '@THIS'
        i = '@' + symbol_i.strip('this')
        list = [i, 'D=A', symbol, 'D=M+D', '@R13', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@R13', 'A=M', 'M=D']
    elif symbol_i.startswith('that'):
        symbol = '@THAT'
        i = '@' + symbol_i.strip('that')
        list = [i, 'D=A', symbol, 'D=M+D', '@R13', 'M=D', '@SP', 'M=M-1', 'A=M', 'D=M', '@R13', 'A=M', 'M=D']
    elif symbol_i.startswith('inter'): #inter = pointer
        i = '@' + str(3 + int(symbol_i.strip('inter'))) #inter = pointer
        list = ['@SP', 'M=M-1', 'A=M', 'D=M', i, 'M=D']
    elif symbol_i.startswith('temp'):
        i = '@' + str(5 + int(symbol_i.strip('temp')))
        list = ['@SP', 'M=M-1', 'A=M', 'D=M', i, 'M=D']

    for i in list:
        destiny.write(i+'\n')

def add(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'M=D+M']
    for i in list:
        destiny.write(i+'\n')

def sub(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'M=M-D']
    for i in list:
        destiny.write(i+'\n')

def eq(destiny):
    global eq_counter

    equal_i = '@EQUAL' + str(eq_counter)
    nequal_i = '@NEQUAL' + str(eq_counter)
    end_eq_i = '@ENDEQ' + str(eq_counter)
    label_equal_i = '(EQUAL' + str(eq_counter) + ')'
    label_nequal_i = '(NEQUAL' + str(eq_counter) + ')'
    label_endeq_i = '(ENDEQ' + str(eq_counter) + ')'

    list = [
        '@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'D=M-D',
        equal_i, 'D;JEQ',
        nequal_i, 'D;JNE',
        label_equal_i, '@SP', 'A=M-1', 'M=-1', end_eq_i, '0;JMP',
        label_nequal_i, '@SP', 'A=M-1', 'M=0', end_eq_i, '0;JMP',
        label_endeq_i
    ]
    for i in list:
        destiny.write(i+'\n')

    eq_counter += 1

def gt(destiny):
    global gt_counter

    greater_i = '@GREATER' + str(gt_counter)
    ngreater_i = '@NGREATER' + str(gt_counter)
    end_gt_i = '@ENDGT' + str(gt_counter)
    label_greater_i = '(GREATER' + str(gt_counter) + ')'
    label_ngreater_i = '(NGREATER' + str(gt_counter) + ')'
    label_endgt_i = '(ENDGT' + str(gt_counter) + ')'

    list = [
        '@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'D=M-D',
        greater_i, 'D;JGT',
        ngreater_i, 'D;JLE',
        label_greater_i, '@SP', 'A=M-1', 'M=-1', end_gt_i, '0;JMP',
        label_ngreater_i, '@SP', 'A=M-1', 'M=0', end_gt_i, '0;JMP',
        label_endgt_i
    ]
    for i in list:
        destiny.write(i+'\n')

    gt_counter += 1

def lt(destiny):
    global lt_counter

    lesser_i = '@LESSER' + str(lt_counter)
    nlesser_i = '@NLESSER' + str(lt_counter)
    end_lt_i = '@ENDLT' + str(lt_counter)
    label_lesser_i = '(LESSER' + str(lt_counter) + ')'
    label_nlesser_i = '(NLESSER' + str(lt_counter) + ')'
    label_endlt_i = '(ENDLT' + str(lt_counter) + ')'

    list = [
        '@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'D=M-D',
        lesser_i, 'D;JLT',
        nlesser_i, 'D;JGE',
        label_lesser_i, '@SP', 'A=M-1', 'M=-1', end_lt_i, '0;JMP',
        label_nlesser_i, '@SP', 'A=M-1', 'M=0', end_lt_i, '0;JMP',
        label_endlt_i
    ]
    for i in list:
        destiny.write(i+'\n')

    lt_counter += 1

def asmand(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'M=M&D']
    for i in list:
        destiny.write(i+'\n')

def asmor(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'D=M', 'A=A-1', 'M=M|D']
    for i in list:
        destiny.write(i+'\n')

def neg(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'M=-M', '@SP', 'M=M+1']
    for i in list:
        destiny.write(i+'\n')

def asmnot(destiny):
    list = ['@SP', 'M=M-1', 'A=M', 'M=!M', '@SP', 'M=M+1']
    for i in list:
        destiny.write(i+'\n')

def translate_line(line, destiny):
    if line.startswith('push'):
        symbol_i = line.strip('push')
        push(symbol_i, destiny)
    elif line.startswith('pop'):
        symbol_i = line.strip('pop')
        pop(symbol_i, destiny)
    elif line.startswith('add'):
        add(destiny)
    elif line.startswith('sub'):
        sub(destiny)
    elif line.startswith('neg'):
        neg(destiny)
    elif line.startswith('eq'):
        eq(destiny)
    elif line.startswith('gt'):
        gt(destiny)
    elif line.startswith('lt'):
        lt(destiny)
    elif line.startswith('and'):
        asmand(destiny)
    elif line.startswith('or'):
        asmor(destiny)
    elif line.startswith('not'):
        asmnot(destiny)

def main():
    global filename

    source = open(filename+'.vm', 'r')
    destiny = open(filename+'.asm', 'w')

    content = format_file([x.strip().replace(" ", "") for x in source.readlines()])
    for line in content:
        destiny.write('//' + line + '\n')
        translate_line(line, destiny)

    source.close()
    destiny.close()

if __name__ == '__main__':
    main()
