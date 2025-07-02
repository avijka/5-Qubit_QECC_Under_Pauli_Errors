from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister
from qiskit.circuit.library import StatePreparation
import numpy as np

# 5-Qubit Quantum Error Correcting Code Class
#
# Description:
#	Provides Qiskit circuit components for encoding physical qubits and remedying
#	errors under the 5-qubit code.
#
# Inputs:
#	<none>
#
# Attributes (self-explanatory):
#	num_physical_qubits, num_syndromes
#
# Methods:
#	get_logical_0_preparer - Returns a gate that transforms the all 0's state on the
#		physical qubits to the logical 0 state for this code.
#	get_logical_X - Returns a gate that acts on the physical qubits and executes the
#		logical X for this code. 
#	get_error_corrector - Returns a circuit that acts on the physical qubits, the syndrome
#		ancilla qubits, and the syndrome classical bits to check and correct for errors.
#	get_logical_0_components - Returns a list of bit strings that correspond to the
#		elements of the computational basis that appear in the logical 0
#		state.
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister from qiskit.circuit
# 	StatePreparation from qiskit.circuit.library
#	numpy as np

class Five_Qubit_QECC:

	num_physical_qubits = 5
	num_syndromes = 4
	__logical0_coef_pos = ['00000','00101','01010','10100','01001','10010']
	__logical0_coef_neg = [
		'00011','00110','01100','11000','10001','01111','11110','11101','11011','10111'
	]
	
	def __init__(self):
		self.__qubits_code = QuantumRegister(size=5, name='code')
		self.__qubits_checks = AncillaRegister(size=4, name='check')
		self.__syndromes = ClassicalRegister(4, name='syndromes')
		
	def get_logical_0_preparer(self):
		logical0_coefficients = np.zeros((2**5))
		logical0_coefficients[[int(c,2) for c in self.__logical0_coef_pos]] = 1/4
		logical0_coefficients[[int(c,2) for c in self.__logical0_coef_neg]] = -1/4
		return StatePreparation(
			logical0_coefficients, normalize=True, label='5-Qubit Logical 0\nPreparation'
		)
		
	def get_logical_X(self):
		logical_X_qc = QuantumCircuit(self.__qubits_code, name='5-Qubit Logical X')
		logical_X_qc.x(self.__qubits_code[:])
		return logical_X_qc.to_gate()
		
	def __get_error_checker(self):
		checker_qc = QuantumCircuit(
			self.__qubits_code, self.__qubits_checks,
			name='5-Qubit Error Checker'
		)
		
		checker_qc.h(self.__qubits_checks[:])
		for i in range(4): 
		# i=0: XZZXI -> i=1: IXZZX -> i=2: XIXZZ -> i=3: ZXIXZ
			checker_qc.cx(self.__qubits_checks[i], self.__qubits_code[i%5])
			checker_qc.cz(self.__qubits_checks[i], self.__qubits_code[(i+1)%5])
			checker_qc.cz(self.__qubits_checks[i], self.__qubits_code[(i+2)%5])
			checker_qc.cx(self.__qubits_checks[i], self.__qubits_code[(i+3)%5])
		checker_qc.h(self.__qubits_checks[:])
		
		return checker_qc.to_gate()
	
	def get_error_corrector(self):
		corrector_qc = QuantumCircuit(
			self.__qubits_code, self.__qubits_checks, self.__syndromes,
			name='5-Qubit Corrector'
		)
		
		# add checker circuit and measure syndromes
		corrector_qc.compose(self.__get_error_checker(), inplace=True)
		corrector_qc.barrier()
		corrector_qc.measure(self.__qubits_checks, self.__syndromes)
		corrector_qc.barrier()
		
		# correct X errors
		for j in range(5): # ... on qubit j
			syndromes_int = 2**((j-1)%5) + 2**((j-2)%5)  # integer for syndrome bit string
			syndromes_int = syndromes_int % (2**4) # drop most significant bit
			with corrector_qc.if_test((self.__syndromes, syndromes_int)):
				corrector_qc.x(self.__qubits_code[j])
		
		# correct Z errors
		for j in range(5):
			syndromes_int = 2**(j%5) + 2**((j-3)%5)
			syndromes_int = syndromes_int % (2**4)
			with corrector_qc.if_test((self.__syndromes, syndromes_int)):
				corrector_qc.z(self.__qubits_code[j])
				
		# correct Y errors
		for j in range(5):
			syndromes_int = 31 - 2**((j-4)%5)
			syndromes_int = syndromes_int % (2**4)
			with corrector_qc.if_test((self.__syndromes, syndromes_int)):
				corrector_qc.y(self.__qubits_code[j])
				
		return corrector_qc
	
	def get_logical_0_components(self):
		return self.__logical0_coef_pos + self.__logical0_coef_neg
		
