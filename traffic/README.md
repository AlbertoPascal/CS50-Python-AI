# Experiment Notes

The first convolutional neural network that I tried was based on the class's example:

- Convolutional layer with 32 filters in 3x3
- 2x2 Max pooling
- Flattening
- Hidden layer with 128 neurons
- 0.5 dropout
- output layer with a softmax activation

# Initial Results:
| Attempt #| Accuracy |  Loss  |
|    0     | 0.6230   | 1.1958 |

# Improvement attempts:

My following attempts are described below:

## Attempt 1:

Modifications:

- Changed Convolutional layer's size from 3x3 to 2x2
- Changed max pooling size from 2x2 to 3x3
- Changed hidden layer size from 128 neurons to 256 neurons

## Attempt 1 results:

| Attempt #| Accuracy |  Loss  |
|    1     | 0.0572   | 3.4987 |

## Observations:

It seems that these results were much worse than expected and worse than the base model. I suspect it is due to the max pooling size mainly since the filters being applied in 2x2 instead of 3x3 would make them be applied more often only.

## Attempt 2:

Modifications:
- Reverted the convolutional layer's size to 3x3
- Reverted the max pooling size to 2x2
- Increased the number of filters from 32 to 64

## Attempt 2 results:

| Attempt #| Accuracy |  Loss  |
|    2     | 0.7214   | 0.9436 |

## Observations:

Huge improvement when increasing the number of filters but returning to the base model. Even though the accuracy can still improve a lot, trying out many more different inputs (filters) results in possibly having many more different outputs. 

## Attempt 3:

Modifications:
- Added a second convolutional layer after max pooling. This layer contains only 32 filters
- Added a second max pooling layer, keeping the 2x2 size.

## Observations:

Adding more convolutional layers was a huge improvement. This probably allowed to identify the objects within my images with much more precision.  

## Attempt 3 results:

| Attempt #| Accuracy |  Loss  |
|    3     | 0.8926   | 0.3701 |

## Attempt 4:

Modifications:
- Increased first convolutional layer filters to 128
- Increased second covolutional layer filters to 64
- Increased Dropout to 0.75

## Attempt 4 results:

| Attempt #| Accuracy |  Loss  |
|    4     | 0.0565   | 3.5053 |

## Observations:

These changes were completely bad. Most likely due to the fact that even though I added many more neurons, many more were also discarded on the dropout mechanic

## Attempt 5:

Modifications:
- Reverted dropout rate to 0.5

## Attempt 5 results:

| Attempt #| Accuracy |  Loss  |
|    5     | 0.9333   | 0.2949 |

## Observations:

It seems that having a dropout of 50% might be the best approach. Increasing the dropout would result in less neurons being tested and decreasing it might also mean the results could be over-fit. 

## Attempt 6:

Modifications:
- Added second hidden layer with 128 neurons and relu activation

## Attempt 6 results:

| Attempt #| Accuracy |  Loss  |
|    6     | 0.9245   | 0.2752 |

## Observations:

It seems that adding an additional hidden layer did not increase the accuracy. However, it did decrease the loss. It is probably better to play with the number of available neurons or decrease this number when adding new hidden layers.

##Attempt 7:

Modifications:
- Reduced the number of neurons from the first hidden layer to 128
- moved the dropout mechanic to after the second hidden layer. 

## Attempt 7 results:

| Attempt #| Accuracy |  Loss  |
|    7     | 0.9172   | 0.2844 |

## Observations:

Reducing the amount of neurons from the first hidden layer resulted in a little decrease in accuracy and an increase of the loss. 

## Attempt 8:

- Removed the second hidden layer
- Increased the hidden layer's neurons up to 552

## Attempt 8 results:

| Attempt #| Accuracy |  Loss  |
|    8     | 0.9239   |  0.3005 |

## Observations:

Overly increasing the number of neurons doesn't provide the best results either. Even though the accuracy did increase, so did the loss, meaning there is more variation in the results. 

## Attempt 9:

Modifications:
- Reduced the hidden layer's neurons back to 256. 
- added a third convolutional layer with, once again, half the filters than the last one: 32. 

## Attempt 9 results:

| Attempt #| Accuracy |  Loss  |
|    9     | 0.0549   |  3.5051 |


## Observations: 

Increasing the number of convolutional layers does not help at all. It seems that decreasing too much the image's pixels with the max-pooling also results in a very poor accuracy. 

## Attempt 10:

Modifications:
- Removed the third convolutional layer
- decreased the dropout to 0.25. 

## Attempt 10 results:

| Attempt #| Accuracy |  Loss  |
|    10    | 0.9107   |  0.3874 |

## Observations: 

Decreasing the dropout seemed to work at first. The accuracy between epochs was higher than expected. However, this may have been a result of over-fitting since at the end, the accuracy diminished. 

## Attempt 11:

Modifications:
- changed the first convolutional network size from 3x3 to 5x5
- Increased dropout to 0.45

## Attempt 11 results:

| Attempt #| Accuracy |  Loss  |
|    11    | 0.0558   | 3.4950 |

## Observations: 

Changing the convolutional network's size has a negative impact on the image (when increasing). This is probably due to the loss of quality/detail from the pixels. Reducing it might help

## Attempt 12:

Modifications:
- Reduced the convolutional's network size to 2x2. 
- Increased dropout to 0.5

## Attempt 12 results:

| Attempt #| Accuracy |  Loss  |
|    12    | 0.8507   | 0.5213 |

## Observations: 

Changing the convolutional network's size to a lower value did not help at all. It is certainly better than increasing the convolution size but it is still not as accurate as 3x3. 

## Attempt 13:

Modifications:
- Changed the convolutional networks' size back to 3x3
- Changed the activation function from the convultion networks to Selu. 

## Attempt 13 results:

| Attempt #| Accuracy |  Loss  |
|    13    | 0.9275   | 0.2600 |

## Observations: 

Changing the activation type from Relu to Selu did have an effect. The values were pretty close to the Relu accuary at first but with a slower growth. At the end, the results were probably the second best obtained in terms of accuracy and the best yet in terms of loss. 

## Attempt 14:

Modifications:
- Changed back the first convolutional network's activation function to relu

## Attempt 14 results:

| Attempt #| Accuracy |  Loss  |
|    14    | 0.9524   |  0.2021 |

## Observations: 

With the combination of activation functions, the values obtained where the best so far. The loss was minimized to a value of 0.2021 while the accuracy went to its all-time high with a value of 0.9524.