# -*- coding: utf-8 -*-
"""
    "Using one class classification (ocsvm) to detect abnormal traffic"
    # 0 is normal, 1 is abnormal

     process:
        1) After training, then save model firstly.
        2) Then laod model, test on different attack data.

    Case4:
        Normal data:
            sess_normal_0

        Attack data:
            sess_DDoS_Excessive_GET_POST
            sess_DDoS_Multi_VERB_Single_Request
            sess_DDoS_Recursive_GET
            sess_DDoS_Slow_POST_Two_Arm_HTTP_server_wait
            sess_DDoS_SlowLoris_Two_Arm_HTTP_server_wait


    Case4:  (no shuffle)
        Train set : (0.7 * all_normal_data)
        Val_set:  (0.1*all_normal_data)
        Test_set: (0.2*all_normal_data+ 1.0*all_abnormal_data)


     Created at :
        2018/10/04

    Version:
        0.3.0

    Requirements:
        python 3.x
        Sklearn 0.20.0

    Author:

"""

import argparse
import os
import time
from collections import Counter

import numpy as np
from sklearn import svm
from sklearn.metrics import roc_auc_score, confusion_matrix
from sklearn.metrics.pairwise import pairwise_distances
from sys_path_export import *  # it is no need to do in IDE environment, however, it must be done in shell/command environment

from utilities.CSV_Dataloader import open_file
from utilities.common_funcs import dump_model, load_model, split_normal2train_val_test_from_files


class OCSVM(object):

    def __init__(self, kernel='rbf', grid_search_cv_flg=False, **kwargs):
        """

        :param kernel:
        :param grid_search_cv_flg:
        :param kwargs:
        """
        self.kernel = kernel
        self.nu = 0.5  # nu : An upper bound on the fraction of training errors and a lower bound of the fraction of support vectors. Should be in the interval (0, 1]. By default 0.5 will be taken.
        self.gamma = 0.9  # Kernel coefficient for ‘rbf’, ‘poly’ and ‘sigmoid’.
        self.grid_search_cv_flg = grid_search_cv_flg
        self.show_flg = True
        self.results = {'val_set': {'acc': [0.0], 'auc': [0.0]}, 'test_set': {'acc': [0.0], 'auc': [0.0]}}

    def train(self, train_set, val_set):
        """

                :param train_set:
                :param val_set:
                :return:
                """
        if len(train_set) == 0 or len(val_set) == 0:
            print('data set is not right.')
            return -1
        print('train_set shape is %s, val_set size is %s' % (train_set[0].shape, val_set[0].shape))

        X_train = train_set[0]
        self.loss = []
        if self.grid_search_cv_flg:
            # parameters={'kernel':('linear','rbf'),'nu':[0.01,0.99],'gamma':[0,1]}
            # self.ocsvm=svm.OneClassSVM()
            # clf = GridSearchCV(self.ocsvm,parameters,cv=5,scoring="accuracy")
            # clf.fit(X_train)
            cv_auc = 0.0
            cv_acc = 0.0
            for nu in np.logspace(-10, -0.001, num=3, base=2):
                for gamma in np.logspace(-10, -0.001, num=3, base=2):  # log2
                    # train on selected gamma
                    print('\nnu:', nu, ', gamma:', gamma)
                    self.ocsvm = svm.OneClassSVM(kernel=self.kernel, nu=nu, gamma=gamma)
                    self.ocsvm.fit(X_train)
                    # predict on small hold-out set
                    auc, acc, cm = self.evaluate(val_set, name='val_set')
                    # save model if AUC on hold-out set improved
                    # if self.diag['val_set']['auc'][0] > cv_auc:
                    if acc > cv_acc:
                        self.best_ocsvm = self.ocsvm  # save the best results
                        self.nu = nu
                        self.gamma = gamma
                        cv_auc = auc
                        cv_acc = acc
                        self.auc = auc
                        self.acc = acc
                        self.cm = cm

            self.ocsvm = self.best_ocsvm
            # save results of best cv run
            self.results['val_set']['auc'] = self.auc
            self.results['val_set']['acc'] = self.acc

            # if self.show_flg:
            #     show_data_3d(self.results['val_set']['acc'], x_label='epochs', y_label='acc', fig_label='acc',
            #               title='val_set evaluation accuracy on training process')

            print('---The best accuracy on \'val_set\' is %.2f%% when nu and gamma are %.5f and %.5f respectively' % (
                self.acc, self.nu, self.gamma))
            print('---Confusion matrix:\n', self.cm)
        else:
            # if rbf-kernel, re-initialize svm with gamma minimizing the numerical error
            try:
                max_distance = (np.max(pairwise_distances(X_train)) ** 2)
            except:
                # self.gamma = self.gamma
                print('use default gamma.')
                pass
            else:
                self.gamma = 1 / max_distance
            print('gamma:', self.gamma)
            self.ocsvm = svm.OneClassSVM(kernel=self.kernel, nu=self.nu, gamma=self.gamma)  # construction function
            self.ocsvm.fit(X_train)

            self.auc, self.acc, self.cm = self.evaluate(val_set, name='val_set')
            print('\'val_set\' accuracy is %.2f%% when nu and gamma are %.5f and %.5f respectively' % (
                self.acc, self.nu, self.gamma))
            print('---Confusion matrix:\n', self.cm)

    def evaluate(self, test_set, name='test_set', **kwargs):
        """

        :param test_set: 0 is normal, 1 is abnormal
        :param name:
        :param kwargs:
        :return:
        """
        print('Evaluating input_data is \'%s\'.' % name)

        X = test_set[0]
        y = test_set[1]
        self.false_alarm_lst = []
        # Step 1. predict output values
        # For an one-class model, +1 (inlier) or -1 (outlier) is returned.
        # change label (-1 (abnormal) and +1 (normal)) outputed by ocsvm to '1 and 0' (-1->1, +1->0)
        y_pred = (self.ocsvm.predict(X) == -1) * 1  # -1=>True, 0=>False, then True=>1, False=>0

        for i in range(len(y_pred)):
            if y_pred[i] == 1 and y[i] == 0:  # save predict error: normal are recognized as attack
                self.false_alarm_lst.append([i, 0, X[i]])

        # Step 2. achieve the evluation standards.
        cm = confusion_matrix(y, y_pred)
        print(name + ' confusion matrix:\n', cm)
        acc = 100.0 * sum(y == y_pred) / len(y)
        print(name + ' Acc: %.2f%% ' % (acc))
        # self.results[name]['acc'][0] = acc
        if len(list(Counter(y))) > 1:
            y_pred_scores = (-1.0) * self.ocsvm.decision_function(X)  # Signed distance to the separating hyperplane.
            # auc = roc_auc_score(y, y_pred_scores.flatten(),pos_label=0) # label 0 is considered as positive and others are considered as negative
            auc = roc_auc_score(y, y_pred_scores.flatten())  # not very clear, if possible, please do not use it.
        else:  # Only one class present in y_true. ROC AUC score is not defined in that case.
            auc = -1

        return auc, acc, cm


def evaluate_model_new(model, test_set_without_abnormal_data, u_normal, std_normal, test_files_lst):
    """

    :param AE_model:
    :param test_set_without_abnormal_data:
    :param u_normal:
    :param std_normal:
    :param test_files_lst:
    :return:
    """
    idx_f = 1
    for test_file_tmp in test_files_lst:
        print('\n[%d/%d] test_file:%s' % (idx_f, len(test_files_lst), test_file_tmp))
        (X_attack_data, y_attack_data) = test_set_without_abnormal_data
        (X_tmp, y_tmp) = open_file(test_file_tmp, label='1')
        X_attack_data = np.concatenate((X_attack_data, np.asarray(X_tmp, dtype=float)), axis=0)
        y_attack_data = np.concatenate(
            (np.reshape(y_attack_data, (len(y_attack_data))), np.reshape(np.asarray(y_tmp, dtype=int), (len(y_tmp)))))
        test_set_original = (X_attack_data, y_attack_data)
        print('\'test_set\' includes 0.2 normal_data (%d) + 1.0*attack_data (%d) which comes from \'%s\'' % (
            len(test_set_without_abnormal_data[1]), len(X_attack_data), test_file_tmp))
        test_set = ((X_attack_data - u_normal) / std_normal, y_attack_data)
        print('test_set:%s' % Counter(test_set_without_abnormal_data[1]))
        model.evaluate(test_set, name='test_set')

        # step 4.2 out predicted values in descending order
        false_samples_lst = sorted(model.false_alarm_lst, key=lambda l: l[1],
                                   reverse=True)  # for second dims, sorted(li,key=lambda l:l[1], reverse=True)
        num_print = 10
        print('The normal samples are recognized as attack samples are as follow in the first %d samples:', num_print)
        if len(false_samples_lst) < num_print:
            num_print = len(false_samples_lst)
        np.set_printoptions(suppress=True)  # Suppresses the use of scientific notation for small numbers in numpy array
        for i in range(num_print):
            v_by_std_u = np.asarray(false_samples_lst[i][2].data.tolist(), dtype=float) * std_normal + u_normal
            print('i=%d' % i, ' <index in test_set, distance_error, norm_vale>', false_samples_lst[i], ' v*std+u:',
                  v_by_std_u, '=>original vaule in test set:', test_set_original[0][false_samples_lst[i][0]],
                  test_set_original[1][false_samples_lst[i][0]])

        idx_f += 1


def ocsvm_main(input_files_dict, kernel='rbf', out_dir='./log', **kwargs):
    """

    :param input_files_dict:
    :param kernel:
    :param out_path:
    :param kwargs:
    :return:
    """
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    st = time.time()
    print('It starts at ', start_time)

    # step 1 load input_data and do preprocessing
    train_set_without_abnormal_data, val_set_without_abnormal_data, test_set_without_abnormal_data, u_normal, std_normal = split_normal2train_val_test_from_files(
        input_files_dict['normal_files'], norm_flg=True, train_val_test_percent=[0.7, 0.1, 0.2], shuffle_flg=False)
    print('train_set:%s,val_set:%s,test_set:%s' % (
        Counter(train_set_without_abnormal_data[1]), Counter(val_set_without_abnormal_data[1]),
        Counter(test_set_without_abnormal_data[1])))

    # step 2.1 initialize OC-SVM
    ocsvm = OCSVM(kernel=kernel, grid_search_cv_flg=True)

    # step 2.2 train OC-SVM model
    print('\nTraining begins ...')
    ocsvm.train(train_set_without_abnormal_data, val_set_without_abnormal_data)
    print('Train finished.')

    # step 3.1 dump model
    model_file = dump_model(ocsvm, os.path.join(out_dir, 'ocsvm_model.p'))

    # step 3.2 load model
    ocsvm_model = load_model(model_file)

    # step 4 evaluate model
    # ocsvm_model.evaluate(val_set_without_abnormal_data, name='val_set')
    print('\nEvaluting ...', end='')
    # ocsvm_model.evaluate(test_set, name='test_set')
    evaluate_model_new(ocsvm_model, test_set_without_abnormal_data, u_normal, std_normal,
                       test_files_lst=input_files_dict['attack_files'])
    print('Evaluation finished.')

    end_time = time.strftime('%Y-%h-%d %H:%M:%S', time.localtime())
    print('\nIt ends at ', end_time)
    print('All takes %.4f s' % (time.time() - st))


def parse_params():
    parser = argparse.ArgumentParser(prog='OCSVM_Case4')
    parser.add_argument('-i', '--input_files_dict', type=str, dest='input_files_dict',
                        help='{\'normal_files\': [normal_file,...], \'attack_files\': [attack_file_1, attack_file_2,...]}',
                        default='../input_data/normal_demo.txt',
                        required=True)  # '-i' short name, '--input_dir' full name
    parser.add_argument('-k', '--kernel', dest='kernel', help="kernel", default='rbf')
    parser.add_argument('-o', '--out_dir', dest='out_dir', help="the output information of this scripts",
                        default='../log')
    args = vars(parser.parse_args())

    return args


if __name__ == '__main__':
    # input_files_dict={'normal_files': ['../input_data/sess_normal_0.txt'], 'attack_files': ['../input_data/sess_TDL4_HTTP_Requests_0.txt', '../input_data/sess_Rcv_Wnd_Size_0_0.txt']}
    args = parse_params()
    input_files_dict = eval(args['input_files_dict'])
    kernel = args['kernel']
    out_dir = args['out_dir']
    print('args:%s\n' % args)
    ocsvm_main(input_files_dict, kernel=kernel, out_dir='../log')
