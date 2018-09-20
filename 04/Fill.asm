//Fill.asm
//Gustavo Alves Pacheco
//11821ECP011

// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed.
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(LOOP)
  @i
  M=0 //i = 0

  @SCREEN
  D=A
  @address
  M=D //address = SCREEN

  @8160
  D=A
  @n
  M=D //n = 255

  @24576 //KEYBOARD
  D=M
  @IF
  D;JEQ //if kbd = 0 goto IF

  @24576 //KEYBOARD
  D=M
  @BLACK_SCREEN
  D;JGT //if kbd > 0 goto BLACK_SCREEN

  @LOOP
  0;JMP //goto LOOP

(IF)
  @SCREEN
  D=M
  @LOOP
  D;JEQ //if SCREEN = 0 goto LOOP
  @SCREEN
  D=M
  @WHITE_SCREEN
  D;JNE //if SCREEN != 0 goto WHITE_SCREEN

(WHITE_SCREEN)
  @i
  D=M
  @n
  D=D-M
  @LOOP
  D;JGT //if i > n goto LOOP

  @address
  A=M
  M=0 //RAM[address] = 0

  @address
  M=M+1 //address = address + 1

  @i
  D=M
  M=D+1 //i++

  @WHITE_SCREEN
  0;JMP

(BLACK_SCREEN)
  @i
  D=M
  @n
  D=D-M
  @LOOP
  D;JGT //if i > n goto LOOP

  @address
  A=M
  M=-1 //RAM[address] = -1

  @address
  M=M+1 //address = address + 1

  @i
  D=M
  M=D+1 //i++

  @BLACK_SCREEN
  0;JMP
