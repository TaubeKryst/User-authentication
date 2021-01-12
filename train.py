from dataLoader import DataLoader
from collections import Counter
from keras.callbacks import EarlyStopping
from keras.models import load_model

import matplotlib.pyplot as plt
import numpy as np
import time
import models

SIGN = 'sign_1'
ZU = 'ZU1'
train = True
save_model = False
plot_acc_loss = False
model_id = 1  # [1,2,3,4]
iteration = 1  # [1,2,3,4,5,6,7,8,9,10]
batch_size = 64
epochs = 250

base_path = 'data/csv/' + SIGN + '/data_13_09_2020-' + SIGN
train_file_path = base_path + '-general.csv'
test_file_path = base_path + '-test_data.csv'
shifted_pos_file_path = base_path + '-shifted_pos.csv'
shifted_time_file_path = base_path + '-shifted_time.csv'
rotated_file_path = base_path + '-rotated_gyr_y_acc_y.csv'
removed_samples_file_path = base_path + '-removed_delta_a=15-delta_d=60-delta_v=1.6.csv'
augmented_data = False

if not ZU == 'ZU0':
    augmented_data = True
    if ZU == 'ZU1':
        augmented_data_sets = [shifted_pos_file_path]
    elif ZU == 'ZU2':
        augmented_data_sets = [shifted_pos_file_path, shifted_time_file_path]
    elif ZU == 'ZU3':
        augmented_data_sets = [rotated_file_path]
    elif ZU == 'ZU4':
        augmented_data_sets = [removed_samples_file_path]
    elif ZU == 'ZU5':
        augmented_data_sets = [shifted_pos_file_path, shifted_time_file_path, rotated_file_path, removed_samples_file_path]

# ==================train/valid data==============================
data_loader = DataLoader(train_file_path, width=140)

if not augmented_data:
    in_array, out_array, in_augmented_array, out_augmented_array = data_loader.get_data()
    train_size = 300
else:
    in_array, out_array, in_augmented_array, out_augmented_array = data_loader.get_data(augmented_data_sets)
    train_size = 650

if len(in_augmented_array):
    in_array, out_array = np.concatenate((in_array, in_augmented_array), axis=0), np.concatenate((out_array, out_augmented_array), axis=0)

indices = np.arange(in_array.shape[0])
np.random.shuffle(indices)
in_array, out_array = in_array[indices], out_array[indices]

train_x, train_y = in_array[:train_size], out_array[:train_size]
valid_x, valid_y = in_array[train_size:], out_array[train_size:]

print(f"train shape: {train_x.shape}")
print(f"valid shape: {valid_x.shape}")
print(f"correct & incorrect proportions (train+valid): {Counter(out_array)}", end="\n")

# ==================test data==============================
data_loader = DataLoader(test_file_path)
test_x, test_y, _, _ = data_loader.get_data()
print(f"test shape: {test_x.shape}")
print(f"correct & incorrect proportions (test): {Counter(test_y)}")

indices = np.arange(in_array.shape[0])
np.random.shuffle(indices)
in_array, out_array = in_array[indices], out_array[indices]

train_x, train_y = in_array[:train_size], out_array[:train_size]
valid_x, valid_y = in_array[train_size:], out_array[train_size:]

if train:
    if model_id == 1:
        model = models.simple_rnn(train_x[0].shape)
    elif model_id == 2:
        model = models.LSTM_rnn(train_x[0].shape)
    elif model_id == 3:
        model = models.LSTM_rnn_2(train_x[0].shape, use_dropout=True)
    elif model_id == 4:
        model = models.GRU_rnn(train_x[0].shape)

    model.summary()
    early_stop = EarlyStopping(monitor='val_loss', patience=20)
    start = time.time()
    history = model.fit(train_x, train_y, validation_data=(valid_x, valid_y), shuffle=True, validation_split=0.6,
                        epochs=epochs, batch_size=batch_size, callbacks=[early_stop])
    end = time.time()
    learning_duration = end - start

    if plot_acc_loss:
        # Plot training & validation accuracy values
        plt.plot(history.history['accuracy'])
        plt.plot(history.history['val_accuracy'])
        plt.title('Model accuracy')
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Valid'], loc='upper left')
        plt.show()

        # Plot training & validation loss values
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('Model loss')
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        plt.legend(['Train', 'Valid'], loc='upper left')
        plt.show()

else:
    model = load_model(f"data/models/{SIGN}/model_{ZU}_{model_id}_{iteration}.h5")
    model.summary()

incorrect_signs = []
for i, (x, y) in enumerate(zip(test_x, test_y)):
    z = np.expand_dims(x, axis=0)
    predicted = model.predict(z)
    predicted_round = predicted.round()

    if predicted_round[0][0] != y:
        incorrect_signs.append(i)
        print(f"Sign id:{i} Should be:{y} Predicted:{predicted}", end="\n")

# Final evaluation of the model
scores = model.evaluate(test_x, test_y, verbose=0)

print(f"ZU: {ZU}\nModel id: {model_id}")
print("Accuracy: %.2f%%" % (scores[1] * 100))
if train:
    print("Learning duration [s]: ", round(learning_duration))
    print("Epochs number: ", len(history.history['accuracy']))
print("Incorrectly predicted signs: ", incorrect_signs)

if save_model:
    model.save(f"data/models/{SIGN}/model_{ZU}_{model_id}_{iteration}.h5")

