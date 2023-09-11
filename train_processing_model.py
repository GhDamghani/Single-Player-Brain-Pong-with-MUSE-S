import numpy as np
from EEGprocessing import preprocess_func
from scipy.fft import rfft
from os.path import isfile
from sklearn.neural_network import MLPClassifier

if not(isfile('train.npz') and isfile('test.npz')):

    

    data_parameters = np.load('data.npz')
    time_ser = data_parameters['time_ser']
    signal = data_parameters['signal']
    modes = data_parameters['modes']
    N_blocks_per_mode = data_parameters['N_blocks_per_mode']
    window_time = data_parameters['window_time'].item()
    decision_time = data_parameters['decision_time'].item()
    N_samples = data_parameters['N_samples'].item()
    N_blocks = data_parameters['N_blocks'].item()
    N_samples_per_block = int(N_samples//N_blocks)

    y = []
    for m_ix, m_val in enumerate(modes):
        y += N_blocks_per_mode[m_ix]*[m_val]
    
    mypreprocessor = preprocess_func(sfreq = 256)

    def processing_line(data, data_shape):
        data_preprocessed = mypreprocessor(data)
        data_reshaped = data_preprocessed.reshape(data_shape)
        data_rfft = rfft(data_reshaped, axis=1)
        data_rfft_abs = np.abs(data_rfft)
        x = data_rfft_abs/np.sum(data_rfft_abs, 1, keepdims=True)
        return x

    def processing_line(data, data_shape):
        data_preprocessed = mypreprocessor(data)
        data_reshaped = data_preprocessed.reshape(data_shape)
        x_t = data_reshaped - np.mean(data_reshaped, 1, keepdims=True)
        x_t = x_t.reshape(data_shape[0], data_shape[1]*data_shape[2])

        data_rfft = rfft(data_reshaped, axis=1)
        data_rfft_abs = np.abs(data_rfft)
        x_f = data_rfft_abs/np.sum(data_rfft_abs, 1, keepdims=True)
        x_f_shape = x_f.shape
        x_f = x_f.reshape(x_f_shape[0], x_f_shape[1]*x_f_shape[2])

        return np.concatenate((x_t, x_f), 1)

    signal_shape_raw = signal.shape
    x_shape = (N_blocks, signal_shape_raw[0]//N_blocks, *signal_shape_raw[1:])

    x = processing_line(signal, x_shape)
    y = np.array(y)

    # N_blocks = N_blocks//2

    # x = x[N_blocks:]
    # y = y[N_blocks:]

    train_n = int(N_blocks*0.8)
    test_n = N_blocks - train_n

    ind = np.arange(N_blocks)
    np.random.shuffle(ind)

    x = x[ind]
    y = y[ind]

    x_train, x_test = x[:train_n], x[train_n:]
    y_train, y_test = y[:train_n], y[train_n:]

    print(x.shape, x_train.shape, x_test.shape)
    print(y.shape, y_train.shape, y_test.shape)

    np.savez('train', x_train=x_train, y_train=y_train)
    np.savez('test', x_test=x_test, y_test=y_test)

else:
    train = np.load('train.npz')
    x_train = train['x_train']
    y_train = train['y_train']
    test = np.load('test.npz')
    x_test = test['x_test']
    y_test = test['y_test']

    train_n = y_train.shape[0]
    test_n = y_test.shape[0]

    x_train = x_train.reshape(train_n, x_train.size//train_n)
    x_test = x_test.reshape(test_n, x_test.size//test_n)

    print('Shape of data')
    print(x_train.shape, x_test.shape)
    print(y_train.shape, y_test.shape)

    print('Distribution of data')
    print(np.histogram(y_train, bins=np.arange(-1.5, 2, 0.5), density=True, range=(-1, 1)))
    print(np.histogram(y_test, bins=np.arange(-1.5, 2, 0.5), density=True, range=(-1, 1)))
    
    
    # N_layers = np.geomspace(260, 50, 10, True, int)
    # N_layers = [200, 200, 200, 150, 100]
    # print(N_layers)
    clf = MLPClassifier((500, 500, 200), max_iter=5000)

    clf.fit(x_train, y_train)

    sc = clf.score(x_test, y_test)
    print('After Training Accuracy', sc)

    ind = np.arange(test_n)
    np.random.shuffle(ind)

    for i in range(4):
        x_ran = x_test[ind[i]]
        y_ran = y_test[ind[i]]

        y0 = clf.predict(x_ran[np.newaxis])
        print(f'Random sampling, predict: {y0[0]:2} Correct answer: {y_ran:2}')
    
    from joblib import dump, load

    dump(clf, 'MLP.joblib')

    clf2 = load('MLP.joblib')

    sc = clf2.score(x_test, y_test)
    print('Pretrained Accuracy', sc)
