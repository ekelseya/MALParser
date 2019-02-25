import re
from typing import List
from datetime import datetime


class MalRead:
    # Class to open and read MAL files.

    VALID_EXTENSIONS = [".txt", ".mal"]

    def __init__(self, src):
        self.src = src

    # Reads file into list of program lines
    def file_read(self):
        # TODO Check that this opens .mal files
        f = open(self.src, 'r')
        program_lines: List[str] = f.readlines()

        return program_lines

    # Numbers each line of the program
    def add_line_numbers(self):
        program_lines = self.file_read()
        number_lines = []
        i = 0

        while i < len(program_lines):
            number_lines.append(str(i + 1) + '\t' + program_lines[i])
            i += 1

        return number_lines

    # Removes comments
    def remove_comments(self):
        number_lines = self.add_line_numbers()
        no_comments = []
        i = 0
        n = len(number_lines)
        while i < n:
            line = number_lines[i]
            line = re.sub('\s+', ' ', line)
            comment_split = line.split(';')
            line = comment_split[0]
            # TODO Why did I add a newline to the end?
            line = line + '\n'
            no_comments.append(line)
            i += 1

        return no_comments

    def remove_blank_lines(self):
        no_comments = self.remove_comments()
        no_blanks = []
        i = 0
        n = len(no_comments)
        while i < n:
            line = no_comments[i]
            if re.search('[a-zA-Z]', line):
                no_blanks.append(no_comments[i])
            i += 1
        return no_blanks


class MalReport:
    # Class to create report file
    def __init__(self, report_name, number_lines, stripped_lines, lexed_lines):
        self.report_name = report_name
        self.number_lines = number_lines
        self.stripped_lines = stripped_lines
        self.lexed_lines = lexed_lines

    # Creates report file
    def create_report(self):
        # TODO Change report name to source
        rn = self.report_name + '.log'

        header = 'MAL Parser Report \nSource File: ' + self.report_name + '.mal\nReport File: ' \
                 + self.report_name + '.log\n' + datetime.now().strftime("%I:%M%p on %B %d, %Y") \
                 + '\nEryn Kelsey-Adkins\nCS 3210'
        line_sep = '\n\n-------------------------\n'

        f = open(rn, 'w')
        f.writelines(header)
        f.writelines(line_sep)
        f.writelines('\nOriginal MAL program listing:\n\n')
        f.writelines(self.number_lines)
        f.writelines(line_sep)
        f.writelines('\nStripped MAL program listing:\n\n')
        f.writelines(self.stripped_lines)
        f.writelines(line_sep)
        f.writelines('\nError report listing:\n\n')
        f.writelines(self.lexed_lines)
        f.close()


class MalLex:
    # Class to lex program lines into tokens
    def __init__(self, lex_lines):
        self.lex_lines = lex_lines

    # Tokenizes program lines and catches 1st errors
    def lex_tokenizer(self):
        instructions = ['LOAD', 'LOADI', 'STORE', 'ADD', 'INC', 'SUB', 'DEC', 'BEQ', 'BLT', 'BGT', 'BR', 'NOOP', 'END']
        registers = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7']
        tokens = []
        i = 0
        n = len(self.lex_lines)
        while i < n:
            line = self.lex_lines[i].replace(',', '')
            split_line = line.split()
            line_number = split_line[0]
            token_string = line_number
            j = 1
            m = len(split_line)
            while j < m:
                elem = split_line[j]
                if len(elem) <= 6 and elem.endswith(':'):
                    token_string = token_string + ' LABEL:' + elem
                    j += 1
                elif elem in instructions:
                    token_string = token_string + ' ' + elem
                    j += 1
                elif elem in registers:
                    token_string = token_string + ' R'
                    j += 1
                elif len(elem) <= 5 and elem.isalpha():
                    token_string = token_string + ' IDENT:' + elem
                    j += 1
                elif elem.isdigit():
                    x = int(elem)
                    y = x % 10
                    if y <= 8:
                        token_string = token_string + ' OCT'
                    else:
                        token_string = token_string + ' ERROR: NOT OCTAL'
                    j += 1
                else:
                    token_string = token_string + ' ERROR:' + elem
                    j += 1
            tokens.append(token_string)
            i += 1
        return tokens


class MalParse:
    # Parses tokens
    def __init__(self, parse_lines):
        self.parse_lines = parse_lines

    def parse_label(self, lbl_elem):
        label_list = []
        lbl = lbl_elem.split(':')
        label_list.append(lbl[1])
        return label_list

    def parse_load(self, load_line, counter):
        counter += 1
        if load_line[counter] == 'R':
            counter += 1
            if load_line[j].startswith('IDENT'):
                break
            else:
                error_string = f'Error line {int(line_number)}: Expected Memory Location\n'
                error_lines.append(error_string)
                break
        else:
            error_string = f'Error line {int(line_number)}: Expected Register\n'
            error_lines.append(error_string)
            break

    # Reads tokens and compares to proper syntax for error detection
    def token_parser(self):
        labels = []
        branch_labels = []
        error_lines = []

        i = 0
        n = len(self.parse_lines)
        while i < n:
            line = self.parse_lines[i]
            split_line = line.split()
            line_number = split_line[0]

            j = 1
            m = len(split_line)
            if split_line[1].startswith('LABEL'):
                labels = self.parse_label(split_line[1])
                j += 1
            while j < m:
                elem = split_line[j]
                if elem == 'LOAD':
                    #parse_load(split_line, j)
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j].startswith('IDENT'):
                            break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Memory Location\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                if elem == 'STORE':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j].startswith('IDENT'):
                            break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Memory Location\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'LOADI':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'OCT':
                            break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Octal\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'ADD':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'R':
                            j += 1
                            if split_line[j] == 'R':
                                break
                            else:
                                error_string = f'Error line {int(line_number)}: Expected Register\n'
                                error_lines.append(error_string)
                                break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Register\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'SUB':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'R':
                            j += 1
                            if split_line[j] == 'R':
                                break
                            else:
                                error_string = f'Error line {int(line_number)}: Expected Register\n'
                                error_lines.append(error_string)
                                break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Register\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'INC':
                    j += 1
                    if split_line[j] == 'R':
                        break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'DEC':
                    j += 1
                    if split_line[j] == 'R':
                        break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'BEQ':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'R':
                            j += 1
                            if split_line[j].startswith('IDENT'):
                                brn = split_line[j].split(':', 1)
                                branch_labels.append(brn[1])
                                break
                            else:
                                error_string = f'Error line {line_number}: {split_line[j]}: Expected Label \n'
                                error_lines.append(error_string)
                                break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Register\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'BLT':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'R':
                            j += 1
                            if split_line[j].startswith('IDENT'):
                                brn = split_line[j].split(':', 1)
                                branch_labels.append(brn[1])
                                break
                            else:
                                error_string = f'Error line {line_number}: {split_line[j]}: Expected Label \n'
                                error_lines.append(error_string)
                                break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Register\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'BGT':
                    j += 1
                    if split_line[j] == 'R':
                        j += 1
                        if split_line[j] == 'R':
                            j += 1
                            if split_line[j].startswith('IDENT'):
                                brn = split_line[j].split(':', 1)
                                branch_labels.append(brn[1])
                                break
                            else:
                                error_string = f'Error line {line_number}: {split_line[j]}: Expected Label \n'
                                error_lines.append(error_string)
                                break
                        else:
                            error_string = f'Error line {int(line_number)}: Expected Register\n'
                            error_lines.append(error_string)
                            break
                    else:
                        error_string = f'Error line {int(line_number)}: Expected Register\n'
                        error_lines.append(error_string)
                        break
                elif elem == 'BR':
                    j += 1
                    if split_line[j].startswith('IDENT'):
                        brn = split_line[j].split(':')
                        branch_labels.append(brn[1])
                        break
                    else:
                        error_string = f'Error line {line_number}: {split_line[j]}: Expected Label \n'
                        error_lines.append(error_string)
                        break
                elif elem == 'NOOP':
                    break
                elif elem == 'END':
                    if split_line[j] == split_line[-1]:
                        break
                    else:
                        error_string = f'Error line {line_number}: END must be at the end of the program\n'
                        error_lines.append(error_string)
                        break
                elif elem.startswith('IDENT'):
                    iden = split_line[j].split(':')
                    id_string = iden[1]
                    error_string = f'Error line {line_number}: {id_string}: Expected instruction\n'
                    error_lines.append(error_string)
                    break
                else:
                    error_string = f'Error line {line_number}: unknown error\n'
                    error_lines.append(error_string)
                    break
            i += 1

        if not bool(set(branch_labels).intersection(labels)):
            error_lines.append('Error: branch error may exist\n')

        return error_lines


def main():
    read = MalRead('NoError.txt')

    line_numbers = read.add_line_numbers()

    no_blanks = read.remove_blank_lines()

    lex = MalLex(no_blanks)

    lex_lines = lex.lex_tokenizer()

    parse = MalParse(lex_lines)

    error_lines = parse.token_parser()

    report_file = MalReport('report', line_numbers, no_blanks, error_lines)

    report_file.create_report()


if __name__ == '__main__':
    main()
