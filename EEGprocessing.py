
import numpy as np
from scipy.signal import firwin, convolve
from scipy.fft import rfft
from joblib import dump, load


def processing_func(sfreq, decision_window):
    # f_res = 1/decision_window
    n_samples_decision = int(sfreq * decision_window)
    # f_ser = np.arange(0, (n_samples_decision//2+1)*f_res, f_res)

    # delta_mask = np.logical_and(0.5 < f_ser, f_ser <= 4)
    # theta_mask = np.logical_and(4 < f_ser, f_ser <= 8)
    # alpha_mask = np.logical_and(8 < f_ser, f_ser <= 12)
    # beta_mask = np.logical_and(12 < f_ser, f_ser <= 30)

    # print('Masks Created')
    clf = load('MLP.joblib')
    """ def processing(data, time_ser):
        data = data[-n_samples_decision:, :]
        data_f = rfft(data, axis=0)
        data_f_abs = np.abs(data_f)
        data_f_normal = data_f_abs/np.sum(data_f_abs, 0, keepdims=True)
        data_f_unravel = data_f_normal.reshape(1, data_f_normal.size)
        return clf.predict(data_f_unravel)[0] # activation(data_f_alpha[3], data_f_alpha[0]) """
    
    def processing(data, time_ser):
        data = data[-n_samples_decision:, :]

        x_t = data - np.mean(data, 0, keepdims=True)
        x_t = x_t.reshape(1, x_t.size)

        data_f = rfft(data, axis=0)
        data_f_abs = np.abs(data_f)
        data_f_normal = data_f_abs/np.sum(data_f_abs, 0, keepdims=True)
        x_f = data_f_normal.reshape(1, data_f_normal.size)
        
        x = np.concatenate((x_t, x_f), 1)

        return clf.predict(x)[0] # activation(data_f_alpha[3], data_f_alpha[0])
    
    # print('Processing Function Defined')
    return processing


def preprocess_func(sfreq):
    
    numtaps = 400
    f1, f2 = 0.5, 70
    LTI_filter_coeff = firwin(numtaps, [f1, f2], pass_zero=False, fs=sfreq)
    LTI_filter_coeff = np.expand_dims(LTI_filter_coeff, -1)

    def preprocess(data):
        # print('Preprocess Started')
        # Average Referencing
        data = data - np.mean(data, 0)

        # Basic Filtering
        filt_samples = convolve(data, LTI_filter_coeff, mode='same')
        # print('Preprocess Ended')
        return filt_samples
    return preprocess