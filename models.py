from keras.layers import Dense, SimpleRNN, LSTM, Dropout, TimeDistributed, Activation, Flatten, GRU
from keras.models import Sequential
from keras.optimizers import Adam


def simple_rnn(data_shape):
    adam = Adam(lr=0.00001)
    model = Sequential()
    model.add(SimpleRNN(units=32, input_shape=(data_shape), activation="relu", return_sequences=True))
    model.add(SimpleRNN(units=16))
    model.add(Dense(8, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    return model

def LSTM_rnn(data_shape):
    adam = Adam(lr=0.00001)
    model = Sequential()
    model.add(LSTM(units=32, input_shape=(data_shape), return_sequences=True))
    model.add(LSTM(units=16, return_sequences=False))
    model.add((Dense(1)))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    return model

def LSTM_rnn_2(data_shape, use_dropout):
    adam = Adam(lr=0.00001)
    model = Sequential()
    model.add(LSTM(units=32, input_shape=(data_shape), return_sequences=True))
    model.add(LSTM(units=16, return_sequences=True))
    if use_dropout:
        model.add(Dropout(0.3))
    model.add(TimeDistributed(Dense(1)))
    model.add(Flatten())
    model.add((Dense(1)))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    return model

def GRU_rnn(data_shape):
    adam = Adam(lr=0.00001)
    model = Sequential()
    model.add(GRU(units=32, input_shape=(data_shape), return_sequences=True))
    model.add(SimpleRNN(units=128))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=['accuracy'])
    return model
