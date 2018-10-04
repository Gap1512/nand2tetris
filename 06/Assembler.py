import sys

filename = sys.argv[1]
source = open(filename, "r")
new_filename = filename[:-3] + 'hack'
destiny = open(new_filename, "w")

counter = 16
symbol_table = {
    'R0' : 0,
    'R1' : 1,
    'R2' : 2,
    'R3' : 3,
    'R4' : 4,
    'R5' : 5,
    'R6' : 6,
    'R7' : 7,
    'R8' : 8,
    'R9' : 9,
    'R10': 10,
    'R11': 11,
    'R12': 12,
    'R13': 13,
    'R14': 14,
    'R15': 15,
    'SCREEN' : 16384,
    'KBD' : 24576,
    'SP' : 0,
    'LCL' : 1,
    'ARG' : 2,
    'THIS' : 3,
    'THAT' : 4
}

def is_not_a_symbol(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def acommand(text):
    value = text.strip('@')
    if is_not_a_symbol(value):
        value = int(value)
        acommand = '0' + bin(value)[2:].zfill(15) + "\n"
        destiny.write(acommand)
    else:
        global counter
        if value in symbol_table:
            address = symbol_table[value]
            acommand = '0' + bin(address)[2:].zfill(15) + "\n"
            destiny.write(acommand)
        else:
            symbol_table[value] = counter
            counter += 1
            acommand = '0' + bin(symbol_table[value])[2:].zfill(15) + "\n"
            destiny.write(acommand)

def ccommand(text):
    comp_table = {
        '0'  : '0101010',
        '1'  : '0111111',
        '-1' : '0111010',
        'D'  : '0001100',
        'A'  : '0110000',
        'M'  : '1110000',
        '!D' : '0001101',
        '!A' : '0110001',
        '!M' : '1110001',
        '-D' : '0001111',
        '-A' : '0110011',
        '-M' : '1110011',
        'D+1': '0011111',
        'A+1': '0110111',
        'M+1': '1110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'M-1': '1110010',
        'D+A': '0000010',
        'D+M': '1000010',
        'D-A': '0010011',
        'D-M': '1010011',
        'A-D': '0000111',
        'M-D': '1000111',
        'D&A': '0000000',
        'D&M': '1000000',
        'D|A': '0010101',
        'D|M': '1010101'
    }
    dest_table = {
        'null'  : '000',
        'M'     : '001',
        'D'     : '010',
        'MD'    : '011',
        'A'     : '100',
        'AM'    : '101',
        'AD'    : '110',
        'AMD'   : '111'
    }
    jump_table = {
        'null': '000',
        'JGT' : '001',
        'JEQ' : '010',
        'JGE' : '011',
        'JLT' : '100',
        'JNE' : '101',
        'JLE' : '110',
        'JMP' : '111'
    }

    if   (text.find('=') != -1) and (text.find(';') != -1):
        comp = text[(text.find('=')) + 1:(text.find(';'))]
    elif (text.find('=') != -1) and (text.find(';') == -1):
        comp = text[(text.find('=')) + 1:]
    elif (text.find('=') == -1) and (text.find(';') != -1):
        comp = text[0:(text.find(';'))]
    else:
        comp = text

    dest = 'null' if (text.find('=') == -1) else text[0:(text.find('='))]
    jump = 'null' if (text.find(';') == -1) else text[(text.find(';'))+1:]

    ccommand = '111' + comp_table[comp] + dest_table[dest] + jump_table[jump] + "\n"
    destiny.write(ccommand)

def label(text, i):
    label = text.strip('(').strip(')')
    symbol_table[label] = i

def format_file(content):
    remove_empty_counter = 0

    while (remove_empty_counter < len(content)):
        if content[remove_empty_counter] == '':
            del content[remove_empty_counter]
        elif content[remove_empty_counter].startswith('//'):
            del content[remove_empty_counter]
        else:
            index = content[remove_empty_counter].find('//')
            if (index != -1):
                content[remove_empty_counter] = content[remove_empty_counter][:index]
            remove_empty_counter += 1

def instruction_type(content):
    i = 0

    for text in content:
        text = (text.lstrip()).rstrip()
        if text.startswith('@'):
            i += 1
        elif text.startswith('('):
            label(text, i)
        else:
            i += 1

    for text in content:
        text = (text.lstrip()).rstrip()
        if text.startswith('@'):
            acommand(text)
        elif text.startswith('('):
            pass
        else:
            ccommand(text)

def main():
    content = source.readlines()
    content = [x.strip() for x in content]

    format_file(content)
    instruction_type(content)

    source.close()
    destiny.close()

if __name__ == '__main__':
    main()
