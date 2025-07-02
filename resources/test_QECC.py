from .five_qubit_QECC import *
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error
from qiskit import transpile

# Test Quantum Error Correcting Code Under Random Pauli Errors
#
# Description:
#	Tests the given error correcting code under random Pauli error. This function
#	generates and simulates a Qiskit circuit which first
#		- places code qubits in the given logical state
# 		- subjects each to a random Pauli gate as an error (The gate is X, Y, or Z, each
#			with probabilities p, and I with probability 1-3*p.)
#		- measures syndromes and attempts to correct the error
#	Then it either A) immediately measures the code qubits (which will be in the given
#	logical state if error correction was successful), or B) decodes the logical state (so
#	that the code qubits should be in the all 0s state) and then measures them. It repeats
#	this procedure for the given number of trials, and reports the fraction of trials
#	 which had successful measurements, i.e.
#		- under option A, measurements which resulted in a component of the desired
#			logical state. Note: this is valid only for some codes, like the 5-qubit code.
#		- under option B, measurements of all 0s.
#
# Inputs:
#	p - probability of each non-trivial Pauli gate. May be a list of values, in which
#		case, the test is repeated for each value.
#	logical_state (optional, default = 0)
#	trails (optional, default = 1000) - the number of trails over which to repeat the
#		procedure 
#	ecc (optional, default = Five_Qubit_ECC()) - class object for the QECC
#	measurement_type (optional, default = "logical") - either "logical" or "decoded" to
#		select between tests A and B, respectively.
#	error_locations (optional, default = "all") - either "all" or a list of non-negative
#		integers, the indicies of the code qubits that are subject to the random error 
#
# Outputs:
#	frac_succesful - the the fraction of trials in which the test was succesful. A list if
#		p is a list.
#
# Requirements:
#	AerSimulator from qiskit_aer
#	NoiseModel, pauli_error from qiskit_aer.noise
#	transpile from qiskit
# 	Five_Qubit_ECC from .five_qubit_ECC

def test_QECC_random_Pauli_errors(
	p, logical_state=0, trials=1000, ecc=Five_Qubit_QECC(), measurement_type='logical',
	error_locations='all'
):

	# build circuit using components from the ECC class
	qubits_code = QuantumRegister(size=ecc.num_physical_qubits, name='code')
	qubits_check = AncillaRegister(size=ecc.num_syndromes, name='check')
	syndromes = ClassicalRegister(size=ecc.num_syndromes, name='syndromes')
	clbits_code = ClassicalRegister(size=ecc.num_physical_qubits, name='code_measurements')

	qecc_qc = QuantumCircuit(qubits_code, qubits_check, syndromes, clbits_code)
	qecc_qc.compose(ecc.get_logical_0_preparer(), inplace=True)

	# flip to logical 1 state, if desired
	if logical_state == 1:
		qecc_qc.compose(ecc.get_logical_X(), inplace=True)

	# introduce identity gates, which will be made noisy
	if error_locations == 'all':
		qecc_qc.id(qubits_code[:])
	else:
		qecc_qc.id(qubits_code[error_locations])

	# add error corrector
	qecc_qc.compose(ecc.get_error_corrector(), inplace=True)

	# add measurement of physical qubits, undoing encoding first if desired
	if measurement_type=='decoded':
		if logical_state == 1:
			qecc_qc.compose(ecc.get_logical_X(), inplace=True)
		qecc_qc.compose(ecc.get_logical_0_preparer().inverse(), inplace=True)
	qecc_qc.measure(qubits_code, clbits_code)
	
	# simulate circuit with noise for each value of p and store results
	
	if type(p) is list:
		pList = p
	else:
		pList = [p]
		
	fracCorrectList = []

	for prob in pList:
		# add noise to the identity gates
		noise_model = NoiseModel()
		noise_model.add_all_qubit_quantum_error(
			pauli_error([('X',prob), ('Y',prob), ('Z',prob), ('I', 1 - 3*prob)]), 
			['id']
		)
	
		# set up and run simulator
		simulator = AerSimulator(noise_model=noise_model)
		compiled_circuit = transpile(qecc_qc, simulator, optimization_level=0)
		job = simulator.run(compiled_circuit, shots=trials)

		# get measurement counts
		counts = job.result().get_counts()

		if measurement_type=='decoded':
			# in this case, find the number of trials where the measurement was all 0's
			count_correct = 0
			for state in counts:
				if state[:ecc.num_physical_qubits] == '0'*ecc.num_physical_qubits:
					count_correct += counts[state]
			fracCorrectList.append(count_correct/trials)
		else:
			# find number of trials where the measurement is a component of the correct
			# logical state. Warning: this assumes that the components of the logical 0 
			# and logical 1 are disjoint! This is a useful statistic for the 5-qubit code,
			# but not many other codes!
			count_correct = [0,0]
			for state in counts:
				if state[:ecc.num_physical_qubits] in ecc.get_logical_0_components():
					count_correct[0] += counts[state]
				else:
					count_correct[1] += counts[state]
			fracCorrectList.append(count_correct[logical_state]/trials)
		
	if type(p) is list:
		return fracCorrectList
	else:
		return fracCorrectList[0]
		
		
