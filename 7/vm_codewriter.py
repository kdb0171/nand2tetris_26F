'''
N2T VM Translator, Project 7, CodeWriter class
stough F26

Following the API specified in N2T Ch 7.
'''

import os
from vm_parser import (CommandType,
                        arithmetic_all,
                        arithmetic_comp,
                        arithmetic_binary,
                        arithmetic_unary)

# push D onto the stack
standard_pushd = '@SP\nA=M\nM=D\n@SP\nM=M+1\n'

# segments addressed through a base pointer: addr = RAM[base] + index
pointer_segments = {
    'local': 'LCL',
    'argument': 'ARG',
    'this': 'THIS',
    'that': 'THAT',
}

# binary ops: after gettwo, D = y, M = x. Result is stored back in M.
binary_ops = {
    'add': 'M=D+M\n',
    'sub': 'M=M-D\n',
    'and': 'M=D&M\n',
    'or':  'M=D|M\n',
}

unary_ops = {
    'neg': 'M=-M\n',
    'not': 'M=!M\n',
}

# comparison jumps, applied to D = x - y
comp_jumps = {
    'eq': 'JEQ',
    'gt': 'JGT',
    'lt': 'JLT',
}


class CodeWriter(object):

    def __init__(self, outfile=None):
        if outfile is None:
            outfile = './Garbage.asm'
            print(f'CodeWriter: default outfile {outfile}.')
        self._outfile = outfile
        with open(self._outfile, 'w') as f:
            f.write(f'// CodeWriter Hack assembly output file {outfile}\n\n')
        # keep track of comparison counts for the logic ops lt, gt, eq
        self.comp_counts = {
            'lt': 0,
            'eq': 0,
            'gt': 0
        }
        self.static_count = 0
        self.static_name = self.extract_static_name(self._outfile)

    def _write(self, s: str):
        with open(self._outfile, 'a') as f:
            f.write(s)

    def writeArithmetic(self, command: str):
        '''
        Write asm for the arithmetic op. all of these ops require
        one or two stack operands, perform an op, then push the result
        back on the stack.
        '''
        assert command in arithmetic_all, \
            f'CodeWriter writeArithmetic: unknown command {command}'
        if command in arithmetic_binary:
            # pop y into D, x stays in M, compute in place; SP ends one above the result slot
            self._write(self.gettwo() + binary_ops[command])
        elif command in arithmetic_unary:
            self._write(self.getone() + unary_ops[command])
        else:  # comparison command
            n = self.comp_counts[command]
            self.comp_counts[command] += 1
            true_label = f'{command.upper()}_TRUE_{n}'
            end_label = f'{command.upper()}_END_{n}'
            s = self.gettwo()
            s += 'D=M-D\n'                      # D = x - y
            s += f'@{true_label}\nD;{comp_jumps[command]}\n'
            s += '@SP\nA=M-1\nM=0\n'            # false
            s += f'@{end_label}\n0;JMP\n'
            s += f'({true_label})\n'
            s += '@SP\nA=M-1\nM=-1\n'           # true
            s += f'({end_label})\n'
            self._write(s)

    def writePushPop(self, command: CommandType, segment: str, index: int):
        '''
        Write asm for the push or pop command.
        '''
        assert command in [CommandType.C_PUSH, CommandType.C_POP], \
            f'CodeWriter writePushPop: unknown command {command}'

        if segment == 'static':
            self.staticPushPop(command, index)
            return

        s = ''
        if command == CommandType.C_PUSH:
            if segment == 'constant':
                s += f'@{index}\nD=A\n'
            elif segment in pointer_segments:
                s += f'@{index}\nD=A\n@{pointer_segments[segment]}\nA=D+M\nD=M\n'
            elif segment == 'temp':
                s += f'@{5 + index}\nD=M\n'
            elif segment == 'pointer':
                s += f'@{"THIS" if index == 0 else "THAT"}\nD=M\n'
            else:
                raise ValueError(f'CodeWriter: unknown segment {segment}')
            s += standard_pushd
        else:  # pop
            if segment in pointer_segments:
                s += f'@{index}\nD=A\n@{pointer_segments[segment]}\nD=D+M\n'
                s += '@R13\nM=D\n'                       # save target address
                s += '@SP\nAM=M-1\nD=M\n'                # pop into D
                s += '@R13\nA=M\nM=D\n'                  # store at target
            elif segment == 'temp':
                s += f'@SP\nAM=M-1\nD=M\n@{5 + index}\nM=D\n'
            elif segment == 'pointer':
                s += f'@SP\nAM=M-1\nD=M\n@{"THIS" if index == 0 else "THAT"}\nM=D\n'
            else:
                raise ValueError(f'CodeWriter: cannot pop to segment {segment}')
        self._write(s)

    def staticPushPop(self, command, index):
        '''
        'push static i' / 'pop static i' become variables of the form @File.i
        '''
        varname = f'{self.static_name}.{index}'
        if command == CommandType.C_PUSH:
            self._write(f'@{varname}\nD=M\n' + standard_pushd)
        else:
            self._write(f'@SP\nAM=M-1\nD=M\n@{varname}\nM=D\n')

    def gettwo(self):
        '''
        Returns asm that pops the stack once, leaving D = y and M = x (at A),
        with SP pointing just above x.
        '''
        return '@SP\nAM=M-1\nD=M\nA=A-1\n'

    def getone(self):
        '''
        Returns asm leaving M = x (the top), SP unchanged.
        '''
        return '@SP\nA=M-1\n'

    def extract_static_name(self, filename):
        base, file = os.path.split(filename)
        name, ext = os.path.splitext(file)
        return name

    def close(self):
        # finish with an infinite loop.
        with open(self._outfile, 'a') as f:
            f.write('(END)\n@END\n0;JMP\n')

    def writeComment(self, comment):
        # Writes the comment into the file, for debugging.
        with open(self._outfile, 'a') as f:
            f.write(f'\n//{comment}\n')