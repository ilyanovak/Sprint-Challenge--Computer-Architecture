"""CPU functionality."""

import sys

# Instructions
LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""

        self.ram = [0] * 256            # Memory is 256 bytes
        self.reg = {}                   # Create register
        self.reg = [0] * 8              # Register has 8 slots
        self.pc = 0                     # Program Counter, address of the currently executing instruction
        self.running = True             # Program is initialized as running = False, and changes to False with HLT instruction
        self.reg[7] = len(self.ram) - 1 # Register slot 7 is reserved as the stack pointer and set to last byte in memory
        self.fl = 0b00000000            # Flag register is set to default = False.

        # self.count = 0


    def ram_read(self, memory_address_register):
        """Accepts an address and returns the value stored there"""

        return self.ram[memory_address_register]

    def ram_write(self, memory_address_register, memory_data_register):
        """Accepts a value to write and the address to write to it"""

        self.ram[memory_address_register] = memory_data_register


    def load(self, filename):
        """Load a program into memory."""

        print('--- Instructions ---')
        with open(filename, 'r') as file:
            address = 0
            for line in file:
                if line[0].isdigit():
                    instruction = int(line[0:8], 2)
                    self.ram_write(address, instruction)
                    address += 1
                    print(line[0:8])
        print('--- Program ---')


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()


    def bit_mask(self, instruction):
        '''Performs bit masking on a given instruction and returns the number of operands'''

        return ((instruction >> 6) & 0b11) + 1


    def run(self):
        """Run the CPU."""

        while self.running:
            instruction = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            num_operands = self.bit_mask(instruction)

            if instruction == LDI:
                self.reg[operand_a] = operand_b
                self.pc += num_operands

            elif instruction == PRN:
                print(self.reg[operand_a])
                self.pc += num_operands

            elif instruction == HLT:
                self.running = False
                print('Register:', self.reg)
                print('Memory:', self.ram)
                self.pc += num_operands

            elif instruction == MUL:
                product = self.reg[operand_a] * self.reg[operand_b]
                self.reg[operand_a] = product
                self.pc += num_operands

            elif instruction == PUSH:
                self.ram_write(self.reg[7], self.reg[operand_a])
                self.reg[7] -= 1
                self.pc += num_operands

            elif instruction == POP:
                self.reg[7] += 1
                self.reg[operand_a] = self.ram_read(self.reg[7])
                self.pc += num_operands

            elif instruction == CALL:
                self.ram_write(self.reg[7], self.pc + 2)
                self.reg[7] -= 1
                self.pc = self.reg[operand_a]

            elif instruction == RET:
                self.reg[7] += 1
                self.pc = self.ram_read(self.reg[7])

            elif instruction == ADD:
                sum = self.reg[operand_a] + self.reg[operand_b]
                self.reg[operand_a] = sum
                self.pc += num_operands

            elif instruction == CMP:
                if self.reg[operand_a] < self.reg[operand_b]:
                    bit_mask = (self.fl | 0b00000100) & 0b00000100
                    self.fl = bit_mask
                elif self.reg[operand_a] > self.reg[operand_b]:
                    bit_mask = (self.fl | 0b00000010) & 0b00000010
                    self.fl = bit_mask
                else:
                    bit_mask = (self.fl | 0b00000001) & 0b00000001
                    self.fl = bit_mask
                self.pc += num_operands

            elif instruction == JEQ:
                if self.fl == 0b00000001:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += num_operands

            elif instruction == JNE:
                bit_mask = self.fl & 0b00000001
                if bit_mask == 0:
                    self.pc = self.reg[operand_a]
                else:
                    self.pc += num_operands

            elif instruction == JMP:
                self.pc = self.reg[operand_a]

            else:
                print(f'Unknown instructions: {instruction}')

            # print('Instruction:', instruction)
            # print('self.pc:', self.pc)
            # print('self.fl:', self.fl)
            # print('register:', self.reg)
            # print('memory:', self.ram)

            # self.count += 1
            # if self.count > 50:
            #     self.running = False
