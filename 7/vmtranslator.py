'''
N2T Project 7 Virtual Machine 1, VM Translater
stough F26

The VM Translator takes .vm already compiled to the
virtual machine spec, and translates those codes
(push/pop different segments, compute stack ops) into
the associated Hack assembly mnemonics.

The script's job is to use the Parser and CodeWriter to
perform the translation. No function/call/return/if/goto/label
yet; that's Ch. 8.
'''


from vm_codewriter import CodeWriter
from vm_parser import (CommandType,
                       Parser)
import sys


def vm_translate(inputfile):
    outputfile = inputfile.replace('.vm', '.asm')
    parser = Parser(inputfile=inputfile)
    coder = CodeWriter(outputfile)

    while (parser.hasMoreLines()):
        parser.advance()
        ctype = parser.commandType()

        if ctype == CommandType.C_ARITMETIC:
            coder.writeComment(parser.curLine())
            coder.writeArithmetic(parser.arg1())
        elif ctype in (CommandType.C_PUSH, CommandType.C_POP):
            coder.writeComment(parser.curLine())
            coder.writePushPop(ctype, parser.arg1(), parser.arg2())
        # anything else isn't handled until Ch. 8

    coder.close()


if __name__ == '__main__':
    vm_translate(sys.argv[1])