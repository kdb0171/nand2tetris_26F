// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.
@SCREEN
D=A
@addr
M=D
@i
M=0

(LOOP)
    @KBD
    D=M
    @NOKEYPRESS
    D;JEQ
    @KEYPRESS
    0;JMP

(KEYPRESS)
    @addr
    A=M
    M=-1
    @addr
    M=M+1
    @i
    M=M+1
    D=M

    //RESET SCREEN IF FULL
    @8192
    D=D-A
    @RESET
    D;JEQ

    //CHECK IF KEYBOARD IS PRESSED STILL
    @KBD
    D=M
    @RESET
    D;JEQ

    @KEYPRESS
    0;JMP

(NOKEYPRESS)
    @addr
    A=M
    M=0
    @addr
    M=M+1
    @i
    M=M+1
    D=M

    //RESET SCREEN IF FULL
    @8192
    D=D-A
    @RESET
    D;JEQ

    //CHECK IF KBD IS PRESSED
    @KBD
    D=M
    @RESET
    D;JNE

    @NOKEYPRESS
    0;JMP

(RESET)
    @SCREEN
    D=A
    @addr
    M=D
    @i
    M=0
    @LOOP
    0;JMP