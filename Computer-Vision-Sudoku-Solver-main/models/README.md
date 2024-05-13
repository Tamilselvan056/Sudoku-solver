### Digit Classifier

CNN takes in 28x28 pixel values in the range [0,1] and consists of three sets of convolutional and max-pooling layers, followed by fully connected layers with ReLU activations and dropout layers to prevent overfitting. The output layer uses softmax activation for multi-class classification, and the model is trained with categorical cross-entropy loss and the Adam optimizer.

Trained on the MNIST dataset from tensorflow.keras.datasets. On the training set an accuracy of 100% is achieved and for the test set this is >99%.

### Solver

CNN takes in 9x9 values signifying the Sudoku puzzle. The digits in the puzzle are divided by 9 and subtracted with 0.5 (for normalization). Initial empty cells will now be represented with -0.5. The CNN consists of 9 (seemed appropriate for Sudoku's) convolutional layers with 512 filters (as in https://cs230.stanford.edu/files_winter_2018/projects/6939771.pdf), followed by batch normalization. The output is flattened, passed through a dense layer (81*9 neurons) with dropout and layer normalization, and reshaped back into the grid shape. The model is trained using categorical cross-entropy loss, Adam optimizer, and softmax activation.

The training set consists of 1,000,000 Sudoku puzzles and solutions (https://www.kaggle.com/datasets/bryanpark/sudoku). The training set accuracy was above 95% and for the test set above 98%. Furthermore, the performance was tested on 1,000 Sudoku's generated with [generate_puzzle(difficult=False)](../src/generate.py), here an accuracy of 100% was obtained. However, at least on a CPU, the CNN approach is much slower than the backtracking approach.

To improve the model [a 9 times larger dataset](https://www.kaggle.com/datasets/rohanrao/sudoku) could be used, also increasing the number of epochs can increase performance since there is no sign of overfitting the training data. It would be interesting to find a NN that is faster than the backtracking algorithm.
