import sys
import os
import pathlib
import itertools

function_counter = {}

filename = ((sys.argv[-1:][0].split("\\"))[-1:])[0]

directory = ''.join(ch for ch, _ in itertools.groupby([' '.join(sys.argv[1:])]))

if sys.argv[-1:][0][-3:] == '.vm':
    type = 1
else:
    type = 0

eq_counter = 0
lt_counter = 0
gt_counter = 0
file_counter = 0

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
    elif symbol_i.startswith('static'):
        symbol = '@' + filename + '.' + symbol_i.replace('static', '')
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
    elif symbol_i.startswith('pointer'):
        i = '@' + str(3 + int(symbol_i.replace('pointer', '')))
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
    elif symbol_i.startswith('pointer'):
        i = '@' + str(3 + int(symbol_i.replace('pointer', '')))
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

def label_generator(label_name, destiny):
    label = '(' + filename + '.' + label_name + ')'
    list = [label]
    for i in list:
        destiny.write(i+'\n')

def if_goto(label_name, destiny):
    label = '@' + filename + '.' + label_name
    list = ['@SP', 'M=M-1', 'D=M', 'A=D', 'D=M', label, 'D;JNE']
    for i in list:
        destiny.write(i+'\n')

def goto(label_name, destiny):
    label = '@' + filename + '.' + label_name
    list = [label, '0;JMP']
    for i in list:
        destiny.write(i+'\n')

def function_label(list, destiny):
    global filename
    local_variables = []
    label = '(' + filename + '.' + list[1] + ')'
    local_variables.append(label)
    local_variables.append('@SP')
    local_variables.append('A=M')
    x = 0
    while (x < int(list[2])):
        local_variables.append('M=0')
        local_variables.append('A=A+1')
        x += 1
    local_variables.append('D=A')
    local_variables.append('@SP')
    local_variables.append('M=D')
    list = local_variables
    for i in list:
        destiny.write(i+'\n')

def function_return(destiny):
    list = ['@LCL', 'D=M', '@FRAME', 'M=D', '@5', 'A=D-A', 'D=M',
            '@RET', 'M=D',
            '@SP', 'M=M-1', 'A=M', 'D=M', '@ARG', 'A=M', 'M=D',
            '@ARG', 'D=M+1', '@SP', 'M=D',
            '@FRAME', 'D=M', '@1', 'D=D-A', 'A=D', 'D=M', '@THAT', 'M=D',
            '@FRAME', 'D=M', '@2', 'D=D-A', 'A=D', 'D=M', '@THIS', 'M=D',
            '@FRAME', 'D=M', '@3', 'D=D-A', 'A=D', 'D=M', '@ARG', 'M=D',
            '@FRAME', 'D=M', '@4', 'D=D-A', 'A=D', 'D=M', '@LCL', 'M=D',
            '@RET', 'A=M', '0;JMP']
    for i in list:
        destiny.write(i+'\n')

def function_call(list, destiny):
    global filename
    global function_counter

    function_name = list[1].replace('.', '$')

    if function_name in function_counter:
        function_counter[function_name] += 1
    else:
        function_counter[function_name] = 0

    retaddr_name = filename + '.' + list[1].replace('.', '$') + '.' + str(function_counter[function_name])
    at_retaddr = '@' + retaddr_name
    retaddr_label = '(' + retaddr_name + ')'
    n = '@' + list[2]
    f = '@' + filename + '.' + list[1]
    list = [at_retaddr, 'D=A', '@SP', 'M=M+1', 'A=M-1', 'M=D',
            '@LCL', 'D=M', '@SP', 'M=M+1', 'A=M-1', 'M=D',
            '@ARG', 'D=M', '@SP', 'M=M+1', 'A=M-1', 'M=D',
            '@THIS', 'D=M', '@SP', 'M=M+1', 'A=M-1', 'M=D',
            '@THAT', 'D=M', '@SP', 'M=M+1', 'A=M-1', 'M=D',
            '@SP', 'D=M', n, 'D=D-A', '@5', 'D=D-A', '@ARG', 'M=D',
            '@SP', 'D=M', '@LCL', 'M=D',
            f, '0;JMP', retaddr_label]
    for i in list:
        destiny.write(i+'\n')

def translate_line(line, destiny):
    if line.startswith('push'):
        symbol_i = line.replace('push', '')
        push(symbol_i, destiny)
    elif line.startswith('pop'):
        symbol_i = line.replace('pop', '')
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
    elif line.startswith('label'):
        symbol_i = line.replace('label', '')
        label_generator(symbol_i, destiny)
    elif line.startswith('if-goto'):
        symbol_i = line.replace('if-goto', '')
        if_goto(symbol_i, destiny)
    elif line.startswith('goto'):
        symbol_i = line.replace('goto', '')
        goto(symbol_i, destiny)
    elif line.startswith('function'):
        line = line.split(" ")
        function_label(line, destiny)
    elif line.startswith('call'):
        line = line.split(" ")
        function_call(line, destiny)
    elif line.startswith('return'):
        function_return(destiny)

def submain(filename, destinyname):
    global directory
    global type
    global file_counter

    source = open(filename + '.vm', 'r')
    if type == 1:
        destiny = open(destinyname + '.asm', 'w')
    else:
        destiny = open(destinyname + '.asm', 'a')
        if file_counter == 0:
            list = ['@256', 'D=A', '@SP', 'M=D']
            for i in list:
                destiny.write(i+'\n')
            translate_line('call Sys.init 0', destiny)

    lines = source.readlines()
    i = 0

    for x in lines:
        if x.startswith('function') or x.startswith('call'):
            lines[i] = x.strip()
        else:
            lines[i] = x.strip().replace(" ", "")
        i += 1

    content = format_file(lines)

    for line in content:
        destiny.write('//' + line + '\n')
        translate_line(line, destiny)

    source.close()
    destiny.close()
    file_counter += 1

def main():
    global filename
    global directory
    global type

    if type == 1:
        filename = filename[:-3]
        submain(filename, filename)
    else:
        list_of_files = os.listdir(directory)
        file_name = directory + '\\' + filename

        if os.path.exists(file_name + '.asm'):
            os.remove(file_name + '.asm')

        for file in list_of_files:
            file_path = directory + "/" + file
            file_extension = pathlib.Path(file_path).suffix
            if file_extension == '.vm':
                name = directory + '\\' + file[:-3]
                submain(name, file_name)

if __name__ == '__main__':
    main()
