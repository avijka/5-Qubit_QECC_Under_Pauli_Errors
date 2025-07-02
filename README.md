## The 5 Qubit Quantum Error Correcting Code Under Random Pauli Errors
This repository investigates the performance of the 5 qubit code, first introduced in ([Laflamme et al. 1996](https://arxiv.org/abs/quant-ph/9602019)) and ([Bennett et al. 1996](https://arxiv.org/abs/quant-ph/9604024)). The main focus here is to build a circuit in Qiskit that 
- encodes 5 qubits into a logical state,
- randomly subjects each of the 5 code qubits to a Pauli gate according to a probability $p$, as a model for noise,
- measures syndromes and attempts to correct the error,
- and finally measures the code qubits.
  
We repeat this procedure for a number of trials and report the fraction of trials which had successful final measurements, i.e. measurements of the code qubits which reflect a component of the correct logical state.

### Basic Usage Example
The main function is `test_QECC_random_Pauli_errors`, which takes in the probability and, optionally, a boolean for the desired logical state and a number of trials. For example:

```python
from resources.test_QECC import test_QECC_random_Pauli_errors

probability = .1
test_QECC_random_Pauli_errors(probability, logical_state=1, trials=10000)
```

There are additional options and functionality, but, by default, this function will run the above-described experiment. The output for the above call to `test_QECC_random_Pauli_errors` is a success rate of around $0.7$.

### Implementation Details and More
For implementation details, visualizations of performance as a function of $p$, exploration of the additional functionality beyond that described above, and a comparison with another classic code, Shor's code, see [the iPython notebook](https://github.com/avijka/5-Qubit_QECC_Under_Pauli_Errors/blob/main/5-Qubit_QECC_Under_Pauli_Errors.ipynb) in this repository.
