import numpy as np
np.random.seed(0)

import keras
import keras.backend as K
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
from keras.optimizers import RMSprop, SGD
from keras.losses import mean_squared_error

from sklearn import preprocessing

from reader import read_data, read_data_in_sequences, split_data, generate_batches


# the data, shuffled and split between train, validation, and test sets
x, y1, y2, y3 = read_data_in_sequences('train_data/all-tracks.csv', 3, shuffle=True, pca_dims=7)

train_set, valid_set, test_set = split_data(x, y1, y2, y3, 0.8, 0.1)

x_train, y1_train, y2_train, y3_train = train_set
x_valid, y1_valid, y2_valid, y3_valid = valid_set
x_test, y1_test, y2_test, y3_test = test_set

y_train = np.stack((y1_train, y2_train, y3_train), 1)
y_valid = np.stack((y1_valid, y2_valid, y3_valid), 1)
y_test = np.stack((y1_test, y2_test, y3_test), 1)

batch_size = 128
epochs = 70


def mixed_loss(target, output):
    loss1 = K.binary_crossentropy(K.sigmoid(output[:,0]), target[:,0])
    loss2 = K.binary_crossentropy(K.sigmoid(output[:,1]), target[:,1])
    loss3 = mean_squared_error(K.tanh(output[:,2]), target[:,2])

    return loss1 + loss2 + loss3


model = Sequential()
model.add(Dense(512, activation='relu', input_shape=(x_train.shape[1],)))
model.add(Dropout(0.1))
model.add(Dense(512, activation='relu', input_shape=(x_train.shape[1],)))
model.add(Dropout(0.1))
model.add(Dense(3, activation='linear'))
model.summary()

model.compile(loss=mixed_loss,
              optimizer=RMSprop(lr=0.005, decay=1e-3),
              metrics=[])

history = model.fit(x_train, y_train,
                    batch_size=batch_size,
                    epochs=epochs,
                    verbose=1,
                    validation_data=(x_valid, y_valid))

model.save('ff_3out.h5')
score = model.evaluate(x_test, y_test, verbose=0)

print('Test loss:', score[0])
print('Test accuracy:', score[1])
