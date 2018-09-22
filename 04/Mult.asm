//Mult.asm
//Gustavo Alves Pacheco
//11821ECP011

// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)

//PseudoCode:
//a = RAM[0]
//flip = a
//n = RAM[1]
//aux = n
//i = 0
//acc = 0
//
//FLIP:
//  if a >= n goto LOOP
//  flip = a
//  a = n
//  n = flip
//  goto FLIP
//
//LOOP:
//  if i > n goto RESULT
//  acc = acc + a
//  i = i + 1
//  goto LOOP
//
//RESULT:
//  RAM[2] = acc
//  goto END
//
//END:
//  goto END

  @R0
  D=M
  @a //a = RAM[0]
  M=D

  @R0
  D=M
  @flip //if a < n, flip values
  M=D

  @R1
  D=M
  @n //n = RAM[1] (How Many Times Is Going To Sum)
  M=D

  @R1
  D=M
  @aux //aux variable for flip
  M=D

  @0
  D=A
  @R2 //RAM[2] = 0
  M=D

  @i
  M=1 //i = 1

  @acc
  M=0 //acc = 0

(FLIP)
  @a
  D=M
  @aux
  D=D-M
  @LOOP
  D;JGE //if a > n goto LOOP

  @a
  D=M
  @flip
  M=D //flip = a
  @n
  D=M
  @a
  M=D //a = n
  @flip
  D=M
  @n
  M=D //n = flip

  @FLIP
  0;JMP //if a < n goto FLIP

(LOOP)
  @i
  D=M
  @n
  D=D-M
  @RESULT
  D;JGT //if i > n goto RESULT

  @a
  D=M
  @acc //acc = acc + a
  M=M+D

  @i
  M=M+1 //i++

  @LOOP
  0;JMP //goto LOOP

(RESULT)
  @acc
  D=M
  @R2
  M=D //RAM[2] = acc

  @END
  0;JMP //End The Program

(END)
  @END
  0;JMP
