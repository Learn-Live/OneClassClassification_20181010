"""
    load features data from txt
"""


def load_data(input_data='', norm_flg=True, train_val_test_percent=[0.7 * 0.9, 0.7 * 0.1, 0.3]):
    """

    :param input_data:
    :param norm_flg: default True
    :param train_val_test_percent: train_set = 0.7*0.9, val_set = 0.7*0.1, test_set = 0.3
    :return:
    """
    if 'mnist' in input_data:
        from utils.Mnist_data_loader import MNIST_DataLoader
        # load input_data with input_data loader
        dataset = MNIST_DataLoader(ad_experiment=1)
        train_set, val_set, test_set = (dataset._X_train, dataset._y_train), (dataset._X_val, dataset._y_val), (
            dataset._X_test, dataset._y_test)
    elif 'csv' in input_data:
        # train_set, val_set, test_set = csv_dataloader(input_data,norm_flg)
        (X, y) = csv_dataloader(input_data)
        if norm_flg:
            X = normalizate_data(X)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=train_val_test_percent[-1], random_state=1)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=train_val_test_percent[1],
                                                          random_state=1)
        train_set, val_set, test_set = (X_train, y_train), (X_val, y_val), (X_test, y_test)

    else:
        print('error dataset.')
        return -1

    # if norm_flg:
    #     train_set = (normalizate_data(train_set[0]),train_set[1]) # X, y
    #     val_set=(normalizate_data(val_set[0]),val_set[1])
    #     test_set=(normalizate_data(test_set[0]),test_set[1])

    return train_set, val_set, test_set


def load_data_with_new_principle(input_data='', norm_flg=True, train_val_test_percent=[0.7 * 0.9, 0.7 * 0.1, 0.3]):
    """
    Case1:
        sess_normal_0 + sess_TDL4_HTTP_Requests_0
    Case2:
        sess_normal_0  + sess_Rcv_Wnd_Size_0_0

    Case1 and Case 2:
        Train set : (0.7 * all_normal_data)*0.9
        Val_set: (0.7*all_normal_data)*0.1 + 0.1*all_abnormal_data
        Test_set: 0.3*all_normal_data+ 0.9*all_abnormal_data

    :param input_data:
    :param norm_flg: default True
    :param train_val_test_percent: train_set = 0.7*0.9, val_set = 0.7*0.1, test_set = 0.3
    :return:
    """
    if 'mnist' in input_data:
        from utils.Mnist_data_loader import MNIST_DataLoader
        # load input_data with input_data loader
        dataset = MNIST_DataLoader(ad_experiment=1)
        train_set, val_set, test_set = (dataset._X_train, dataset._y_train), (dataset._X_val, dataset._y_val), (
            dataset._X_test, dataset._y_test)
    elif 'csv' in input_data:
        # train_set, val_set, test_set = csv_dataloader(input_data,norm_flg)
        (X, y) = csv_dataloader(input_data)
        if norm_flg:
            X = normalizate_data(X)

        lab = Counter(y)
        len_normal, len_abnormal = lab[0], lab[1]
        # X_normal=[]
        # y_normal=[]
        # X_abnormal=[]
        # y_abnormal=[]
        X_train = []
        y_train = []
        X_val = []
        y_val = []
        X_test = []
        y_test = []
        train_set_size = 0
        val_set_size = 0
        test_set_size = 0
        for i in range(len(y)):
            if y[i] == 1:
                # X_abnormal.append(X[i])
                # y_abnormal.append(y[i])
                if test_set_size < int(len_abnormal * 0.9):
                    X_test.append(X[i])
                    y_test.append(y[i])
                    test_set_size += 1
                else:
                    X_val.append(X[i])
                    y_val.append(y[i])
            elif y[i] == 0:
                # X_normal.append(X[i])
                # y_normal.append(y[i])
                if train_set_size < int(len_normal * 0.7 * 0.9):
                    X_train.append(X[i])
                    y_train.append(y[i])
                    train_set_size += 1
                elif val_set_size < int(len_normal * 0.7 * 0.1):
                    X_val.append(X[i])
                    y_val.append(y[i])
                    val_set_size += 1
                else:
                    X_test.append(X[i])
                    y_test.append(y[i])
            else:
                pass
        X_train = np.asarray(X_train, dtype=float)
        y_train = np.asarray(y_train, dtype=int)
        X_val = np.asarray(X_val, dtype=float)
        y_val = np.asarray(y_val, dtype=int)
        X_test = np.asarray(X_test, dtype=float)
        y_test = np.asarray(y_test, dtype=int)
        #
        # len_train_set = int(len(y_normal)*0.7)
        # len_val_set = int(len_train_set * 0.1)
        # X_train = np.asarray(X_normal[:len_train_set-len_val_set],dtype=float)
        # y_train = np.asarray(y_normal[:len_train_set-len_val_set], dtype = int)
        # len_test_set = int(len(y_abnormal)*0.9)
        # X_test = np.asarray(X_abnormal[:len_test_set].extend(X_normal[len_train_set:]), dtype=float)
        # y_test = np.asarray(y_abnormal[:len_test_set].extend(y_normal[len_train_set:]),dtype=int)
        # X_val = np.asarray(X_normal[len_train_set-len_val_set:len_train_set].extend(X_abnormal[len_test_set:]),dtype=float)
        # y_val = np.asarray(y_normal[len_train_set-len_val_set:len_train_set].extend(y_abnormal[len_test_set:]), dtype=int)

        # X_train, X_test, y_train, y_test = train_test_split(X_normal, y_normal, test_size=train_val_test_percent[-1], random_state=1)
        # train_set = (X_train,y_train)
        # X_val, X_test, y_val, y_test = train_test_split(X_abnormal, y_abnormal, test_size=0.9,random_state=1)
        # test_set=(test_set+)

        train_set, val_set, test_set = (X_train, y_train), (X_val, y_val), (X_test, y_test)

    else:
        print('error dataset.')
        return -1

    # if norm_flg:
    #     train_set = (normalizate_data(train_set[0]),train_set[1]) # X, y
    #     val_set=(normalizate_data(val_set[0]),val_set[1])
    #     test_set=(normalizate_data(test_set[0]),test_set[1])

    return train_set, val_set, test_set


def split_normal2train_val_test_from_files(file_list, norm_flg=True,
                                           train_val_test_percent=[0.7, 0.1, 0.2], shuffle_flg=False):
    """
        only split normal_data to train, val, test (only includes 0.2*normal and not normlized in this function, )
    :param files_dict:  # 0 is normal, 1 is abnormal
    :param norm_flg:
    :param train_val_test_percent: train_set=0.7*normal, val_set = 0.1*normal, test_set = 0.2*normal,
    :return:
    """
    np.set_printoptions(suppress=True)  # Suppresses the use of scientific notation for small numbers in numpy array
    print('file_list:', file_list)
    X_normal = []
    y_normal = []
    for normal_file in file_list:
        X_tmp, y_tmp = open_file(normal_file, label='0')
        X_tmp_new = []
        y_tmp_new = []
        cnt = 0
        i = 0
        for x in X_tmp:
            if x[-3] == '0' or x[0] == '17':  # is_new: 1 or prtl = 17
                X_tmp_new.append(x)
                # y_tmp_new.append(y)
                cnt += 1
                print('i = %d, x=%s' % (i, ','.join(x)))
            i += 1
        print('is_new ==0,the cnt data is %d' % (cnt))
        X_normal.extend(X_tmp)
        y_normal.extend(y_tmp)
    X_normal = np.asarray(X_normal, dtype=np.float64)
    y_normal = np.asarray(y_normal, dtype=int)
    print('normal_data:', X_normal.shape)

    if shuffle_flg:
        print('not implement yet.')
    else:
        if norm_flg:
            # train set only includes 0.7*normal_data
            train_set_len = int(len(y_normal) * train_val_test_percent[0])
            X_train_normal = X_normal[:train_set_len, :]
            u_normal = np.mean(X_train_normal, axis=0)
            std_normal = np.std(X_train_normal, axis=0)
            print('u_normal:', u_normal)
            print('std_normal:', std_normal)
            for i in range(std_normal.shape[0]):
                if std_normal[i] == 0:
                    std_normal[i] += 10e-4
            print('std_normal_modified:', std_normal)
            X_train_normal = (X_train_normal - u_normal) / std_normal
            y_train_normal = y_normal[:train_set_len]
            train_set = (X_train_normal, y_train_normal)

            # val set only includes 0.1* normal_data
            val_set_len = int(len(y_normal) * train_val_test_percent[1])
            X_val_normal = (X_normal[train_set_len:train_set_len + val_set_len, :] - u_normal) / std_normal
            val_set = (X_val_normal, y_normal[train_set_len:train_set_len + val_set_len])

            X_normal_test = X_normal[train_set_len + val_set_len:, :]
            y_normal_test = y_normal[train_set_len + val_set_len:]
            test_normal_set = (X_normal_test, y_normal_test)

            cnt = 0
            i = 0
            for x in X_normal_test:
                if x[-3] == 0.0 or x[0] == 17.0:  # is_new: 1 or prtl = 17
                    # X_tmp_new.append(x)
                    # y_tmp_new.append(y)
                    cnt += 1
                    # print('i = %d, x=%s' % (i, ','.join(x)))
                i += 1
            print('normal_test is_new ==0 and prtl == 17,the cnt data is %d' % (cnt))

    return train_set, val_set, test_normal_set, u_normal, std_normal


def achieve_train_val_test_from_files(files_dict={'normal_files': [], 'attack_files': []}, norm_flg=True,
                                      train_val_test_percent=[0.7, 0.1, 0.2], shuffle_flg=False):
    """

    :param files_dict:  # 0 is normal, 1 is abnormal
    :param norm_flg:
    :param train_val_test_percent: train_set=0.7*normal, val_set = 0.1*normal test_set = (0.2*normal +1*abnormal),
    :return:
    """
    X_normal = []
    y_normal = []
    for normal_file in files_dict['normal_files']:
        X_tmp, y_tmp = open_file(normal_file, label='0')
        X_normal.extend(X_tmp)
        y_normal.extend(y_tmp)
    X_attack = []
    y_attack = []
    for attack_file in files_dict['attack_files']:
        X_tmp, y_tmp = open_file(attack_file, label='1')
        X_attack.extend(X_tmp)
        y_attack.extend(y_tmp)

    print('normal_data:', len(X_normal), ', attack_data:', len(X_attack))
    X_normal = np.asarray(X_normal, dtype=float)
    y_normal = np.asarray(y_normal, dtype=int)
    if shuffle_flg:
        print('not implement yet.')
    else:
        if norm_flg:
            # train set only includes 0.7*normal_data
            train_set_len = int(len(y_normal) * train_val_test_percent[0])
            X_train_normal = X_normal[:train_set_len, :]
            u_normal = np.mean(X_train_normal, axis=0)
            std_normal = np.std(X_train_normal, axis=0)
            print('u_normal:', u_normal)
            print('std_normal:', std_normal)
            for i in range(std_normal.shape[0]):
                if std_normal[i] == 0:
                    std_normal[i] += 10e-4
            print('std_normal_modified:', std_normal)
            X_train_normal = (X_train_normal - u_normal) / std_normal
            y_train_normal = y_normal[:train_set_len]
            train_set = (X_train_normal, y_train_normal)

            # val set only includes 0.1* normal_data
            val_set_len = int(len(y_normal) * train_val_test_percent[1])
            X_val_normal = (X_normal[train_set_len:train_set_len + val_set_len, :] - u_normal) / std_normal
            val_set = (X_val_normal, y_normal[train_set_len:train_set_len + val_set_len])

            # test set includes (0.2*normal_data + 1*abnormal_data)
            # test_set_len = len(y_normal)-train_set_len-val_set_len
            X_test_normal = X_normal[train_set_len + val_set_len:, :]
            X_test = np.concatenate((X_test_normal, np.asarray(X_attack, dtype=float)), axis=0)
            y_test = np.concatenate((np.reshape(y_normal[train_set_len + val_set_len:], (-1, 1)),
                                     np.reshape(np.asarray(y_attack, dtype=int), (len(y_attack), 1))))
            test_set_original = (X_test, y_test.flatten())
            X_test = (X_test - u_normal) / std_normal
            test_set = (X_test, y_test.flatten())

    return train_set, val_set, test_set, u_normal, std_normal, test_set_original


def dump_model(model, out_file):
    """
        save model to disk
    :param model:
    :param out_file:
    :return:
    """
    out_dir = os.path.split(out_file)[0]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    with open(out_file, 'wb') as f:
        pickle.dump(model, f)

    print("Model saved in %s" % out_file)

    return out_file


def load_model(input_file):
    """

    :param input_file:
    :return:
    """
    print("Loading model...")
    with open(input_file, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded.")

    return model


def show_data(data, x_label='epochs', y_label='y', fig_label='', title=''):
    plt.figure()
    plt.plot(data, 'r', alpha=0.5, label=fig_label)
    plt.legend(loc='upper right')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def show_data_2(data1, data2, x_label='epochs', y_label='mean loss', title=''):
    plt.figure()
    plt.plot(data1, 'r', alpha=0.5, label='train_loss in each epoch')
    plt.plot(data2, 'b', alpha=0.5, label='val loss in each epoch')
    # plt.plot(new_decision_data[:, 2], 'g', alpha=0.5, label='D_G_fake')
    plt.legend(loc='upper right')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()


def get_variable_name(data_var):
    """
        get variable name as string
    :param data_var:
    :return:
    """
    name = ''
    keys = locals().keys()
    for key, val in locals().items():
        # if id(key) == id(data_var):
        print(key, id(key), id(data_var), key is data_var)
        # if id(key) == id(data_var):
        if val == data_var:
            name = key
            break

    return name
