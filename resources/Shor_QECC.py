from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister
from qiskit.circuit.library import StatePreparation
import numpy as np

# Shor Quantum Error Correcting Code Class
#
# Description:
#	Provides Qiskit circuit components for encoding physical qubits and remedying
#	errors under the 9-qubit Shor code.
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
#
# Requirements:
#	QuantumCircuit, QuantumRegister, AncillaRegister, ClassicalRegister from qiskit.circuit
# 	StatePreparation from qiskit.circuit.library
#	numpy as np

class Shor_QECC:

	num_physical_qubits = 9
	num_syndromes = 8
	
	def __init__(self):
		self.__qubits_code = QuantumRegister(size=9, name='code')
		self.__qubits_checks = AncillaRegister(size=8, name='check')
		self.__syndromes = ClassicalRegister(8, name='syndromes')
		
	def get_logical_0_preparer(self):
		preparer_qc = QuantumCircuit(self.__qubits_code, name='Shor Logical 0\nPreparation')
		preparer_qc.cx(self.__qubits_code[0],self.__qubits_code[3])
		preparer_qc.cx(self.__qubits_code[0],self.__qubits_code[6])
		preparer_qc.h(self.__qubits_code[[0,3,6]])
		for i in range(3):
			preparer_qc.cx(self.__qubits_code[3*i], self.__qubits_code[3*i + 1])
			preparer_qc.cx(self.__qubits_code[3*i], self.__qubits_code[3*i + 2])
			
		return preparer_qc.to_gate()
		
	def get_logical_X(self):
		logical_X_qc = QuantumCircuit(self.__qubits_code, name='Shor Logical X')
		logical_X_qc.z(self.__qubits_code[:])
		return logical_X_qc.to_gate()
		
	def __get_error_checker(self):
		checker_qc = QuantumCircuit(
			self.__qubits_code, self.__qubits_checks,
			name='Shor Error Checker'
		)
		
		# X checks
		for i in range(3):
			checker_qc.cx(self.__qubits_code[3*i], self.__qubits_checks[2*i])
			checker_qc.cx(self.__qubits_code[3*i+1], self.__qubits_checks[2*i])
			checker_qc.cx(self.__qubits_code[3*i+1], self.__qubits_checks[2*i+1])
			checker_qc.cx(self.__qubits_code[3*i+2], self.__qubits_checks[2*i+1])
		
		# Z checks
		for i in range(2):
			checker_qc.h(self.__qubits_checks[i+6])
			for j in range(6):
				checker_qc.cx(self.__qubits_checks[i+6], self.__qubits_code[3*i+j])
			checker_qc.h(self.__qubits_checks[i+6])
    
		return checker_qc.to_gate()
	
	def get_error_corrector(self):
		corrector_qc = QuantumCircuit(
			self.__qubits_code, self.__qubits_checks, self.__syndromes,
			name='Shor Corrector'
		)
		
		# add checker circuit and measure syndromes
		corrector_qc.compose(self.__get_error_checker(), inplace=True)
		corrector_qc.barrier()
		corrector_qc.measure(self.__qubits_checks, self.__syndromes)
		corrector_qc.barrier()
		
		# correct Z errors
		with corrector_qc.if_test((self.__syndromes[6],1)):
			with corrector_qc.if_test((self.__syndromes[7],0)):
				corrector_qc.z(self.__qubits_code[0:3])
		with corrector_qc.if_test((self.__syndromes[6],1)):
			with corrector_qc.if_test((self.__syndromes[7],1)):
				corrector_qc.z(self.__qubits_code[3:6])
		with corrector_qc.if_test((self.__syndromes[6],0)):
			with corrector_qc.if_test((self.__syndromes[7],1)):
				corrector_qc.z(self.__qubits_code[6:9])
			
		# correct X errors
		for i in range(3):
			with corrector_qc.if_test((self.__syndromes[2*i],1)):
				with corrector_qc.if_test((self.__syndromes[2*i+1],0)):
					corrector_qc.x(self.__qubits_code[3*i])
			with corrector_qc.if_test((self.__syndromes[2*i],1)):
				with corrector_qc.if_test((self.__syndromes[2*i+1],1)):
					corrector_qc.x(self.__qubits_code[3*i+1])
			with corrector_qc.if_test((self.__syndromes[2*i],0)):
				with corrector_qc.if_test((self.__syndromes[2*i+1],1)):
					corrector_qc.x(self.__qubits_code[3*i+2])
				
		return corrector_qc
