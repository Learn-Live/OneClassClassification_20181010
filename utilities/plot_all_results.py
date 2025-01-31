import os

import numpy as np
from matplotlib.ticker import FormatStrFormatter
from sklearn.utils import shuffle
from sklearn import metrics

import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib import rcParams
from sklearn.manifold import TSNE
from sklearn.metrics import roc_curve
import scikitplot as skplt
from joblib import dump, load
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

rcParams.update({'figure.autolayout': True})


#
# def plotHist(data, labels, case, feat):
#     _, dist = test_AE(data, labels, case, feat)
#     print(np.amax(dist))
#     bins = np.linspace(0, 2, 100)
#     plt.hist(dist, bins=bins)
#     plt.xlabel('Reconstruction Loss')
#     plt.ylabel('Count')
#     plt.savefig('Figures/reconstruct_loss_attack.eps', format='eps', dpi=1500)
#     plt.show()

def plot_3d_feature_selection(input_file):
    x = []
    y = []
    z = []
    with open(input_file, 'r') as hdr:
        line = hdr.readline()
        while line != '':
            if line.startswith('3d'):
                line = hdr.readline()
                continue
            line_arr = line.split(',')
            x.append(float(line_arr[0]))
            y.append(float(line_arr[1]))
            z.append(float(line_arr[2]))

            line = hdr.readline()

    fig = plt.figure()
    ax = plt.axes(projection='3d')

    # # Data for a three-dimensional line
    # zline = np.linspace(0, 15, 1000)
    # xline = np.sin(zline)
    # yline = np.cos(zline)
    # ax.plot3D(xline, yline, zline, 'gray')

    # # Data for three-dimensional scattered points
    # zdata = 15 * np.random.random(100)
    # xdata = np.sin(zdata) + 0.1 * np.random.randn(100)
    # ydata = np.cos(zdata) + 0.1 * np.random.randn(100)
    # ax.scatter3D(xdata, ydata, zdata, c=zdata, cmap='Greens')

    # Data for three-dimensional scattered points
    xdata = x  # number of features
    ydata = y  # FPR and FNR
    zdata = z  # AE_optimal_thres_lst
    ax.scatter3D(xdata, ydata, zdata)

    plt.show()


def plot_loss(train_loss, val_loss, title_flg=True, title=f'case_loss'):
    fig, ax = plt.subplots()
    ax.plot(train_loss, 'r*-', label='train_loss')
    ax.plot(val_loss, 'k*-', label='val_loss')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend(loc='upper right')

    if title_flg:
        plt.title(title)

    # output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    # out_file = output_pre_path + '_ROC.pdf'
    # print(f'out_file:{out_file}')
    # plt.savefig(out_file)  # should use before plt.show()

    plt.show()


def plot_features_selection_results(input_file, title_flg=True, title=f'features_selection'):
    # features_descended_dict = OrderedDict()
    data_lst = []
    corr_thres_lst = []
    with open(input_file, 'r') as hdl:
        line = hdl.readline()
        while line != '':
            if line.startswith('features_descended_dict: <key=corr_thres, value=sub_features> '):
                line = hdl.readline()
                continue
            line_arr = line.split(':')
            data_lst.append(int(line_arr[1]))
            corr_thres_lst.append(float(line_arr[0]))
            line = hdl.readline()

    fig, ax = plt.subplots()
    ax.plot(corr_thres_lst, data_lst, 'b*-', label='')
    # ax.plot(val_loss, 'k*-', label='val_loss')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    plt.xlabel('Correlation threshold')
    plt.ylabel('Number of features')
    # plt.legend(loc='upper right')

    if title_flg:
        plt.title(title)

    sub_dir = os.path.split(input_file)[0]
    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_features_number.pdf')
    print(f'features_number: out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    plt.show()


def plot1(test_label, pred_label):
    fpr, tpr, thresholds = roc_curve(test_label, pred_label[:, 1], pos_label=1)
    auc = "%.2f" % metrics.auc(fpr, tpr)

    title = 'ROC Curve, AUC = ' + str(auc)

    with plt.style.context(('ggplot')):
        fig, ax = plt.subplots()
        ax.plot(fpr, tpr, "#000099", label='ROC curve')
        ax.plot([0, 1], [0, 1], 'k--', label='Baseline')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.legend(loc='lower right')
        plt.title(title)
        plt.show()


def plot_roc(input_file, y_test_pred_labels_dict={}, balance_data_flg=True, title_flg=True, title=''):
    """

    :param y_test_pred_labels_lst: {'AE':(y_label, y_preds),'PCA':(), ...}
    :param balance_data_flg:
    :return:
    """
    print(f'input_file:{input_file}')
    y_test_pred_labels_dict = {'AE': [], 'DT': [], 'PCA': [], 'IF': [], 'OCSVM': []}
    with open(input_file, 'r') as in_hdl:
        # line = 'model-y_true[0]:y_preds[0], y_true[1]:y_preds[1],....'
        line = in_hdl.readline()
        while line != '':
            if line.startswith('model'):
                line = in_hdl.readline()
                continue

            line_arr = line.split('@')
            model_name = line_arr[0]
            values = line_arr[1].split(',')
            y_true = []
            y_preds = []
            # print(values)
            for va in values:
                # print(va)
                y_t, y_p = va.split(':')
                # print(y_t, y_p, flush=True)
                y_true.append(float(y_t))
                y_preds.append(float(y_p))
            y_test_pred_labels_dict[model_name] = (y_true, y_preds)
            line = in_hdl.readline()

    # with plt.style.context(('ggplot')):
    fig, ax = plt.subplots()
    colors = {'AE': 'r', 'DT': 'm', 'PCA': 'C1', 'IF': 'b', 'OCSVM': 'g'}
    # for idx, (key, value) in enumerate(y_test_pred_labels_dict.items()):
    for idx, (key, values) in enumerate(y_test_pred_labels_dict.items()):
        if key == 'DT' or len(values) <= 0:
            continue
        (y_test, y_preds) = values
        if key == 'PCA':
            lw = 4
        else:
            lw = 2
        fpr, tpr, thresholds = roc_curve(y_test, y_preds,
                                         pos_label=1)  # pos_label = 1 (y_preds should be the probabilities of y = 1),
        # IMPORTANT: first argument is true values, second argument is predicted probabilities
        auc = "%.5f" % metrics.auc(fpr, tpr)
        # title = 'ROC Curve, AUC = ' + str(auc)
        print(f'key={key}, auc={auc}, fpr={fpr}, tpr={tpr}')
        ax.plot(fpr, tpr, colors[key], label=key, lw=lw, alpha=1, linestyle='--')

    ax.plot([0, 1], [0, 1], 'k--', label='Baseline', alpha=0.9)
    plt.xlim([0.0, 1.0])
    plt.ylim([0., 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')

    sub_dir = os.path.split(input_file)[0]
    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_ROC.pdf')
    print(f'ROC:out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()


def plot_roc_with_scikit_plot(input_file, y_test_pred_labels_dict={}, balance_data_flg=True, title_flg=True, title=''):
    """

    :param y_test_pred_labels_lst: {'AE':(y_label, y_preds),'PCA':(), ...}
    :param balance_data_flg:
    :return:
    """
    y_test_pred_labels_dict = {'AE': [], 'DT': [], 'PCA': [], 'IF': [], 'OCSVM': []}
    with open(input_file, 'r') as in_hdl:
        # line = 'model-y_true[0]:y_preds[0], y_true[1]:y_preds[1],....'
        line = in_hdl.readline()
        while line != '':
            if line.startswith('model'):
                line = in_hdl.readline()
                continue

            line_arr = line.split('@')
            model_name = line_arr[0]
            values = line_arr[1].split(',')
            y_true = []
            y_preds = []
            for va in values:
                y_t, y_p = va.split(':')
                # print(y_t, y_p, flush=True)
                y_true.append(float(y_t))
                y_preds.append(float(y_p))
            y_test_pred_labels_dict[model_name] = (y_true, y_preds)
            line = in_hdl.readline()

    # with plt.style.context(('ggplot')):
    fig, ax = plt.subplots()
    colors = {'AE': 'r', 'DT': 'm', 'PCA': 'C1', 'IF': 'b', 'OCSVM': 'g'}
    # for idx, (key, value) in enumerate(y_test_pred_labels_dict.items()):
    for idx, (key, values) in enumerate(y_test_pred_labels_dict.items()):
        if key == 'DT' or len(values) <= 0:
            continue
        (y_test, y_preds) = values
        if key == 'PCA':
            lw = 4
        else:
            lw = 2
        # fpr, tpr, thresholds = roc_curve(y_test, y_preds, pos_label=1)
        # auc = "%.2f" % metrics.auc(fpr, tpr)
        # title = 'ROC Curve, AUC = ' + str(auc)
        # print(f'key={key}, auc={auc}, fpr={fpr}, tpr={tpr}')
        # ax.plot(fpr, tpr, colors[key], label=key, lw=lw, alpha=1, linestyle='--')
        skplt.metrics.plot_roc(y_test, y_preds)

    ax.plot([0, 1], [0, 1], 'k--', label='Baseline', alpha=0.9)
    plt.xlim([0.0, 1.0])
    plt.ylim([0., 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend(loc='lower right')

    sub_dir = os.path.split(input_file)[0]
    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_ROC.pdf')
    print(f'ROC:out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()


def plot_reconstruction_errors_basic(dist_data, x_label='Reconstruction loss of normal samples',
                                     out_file='Figures/{case}_reconstruct_loss_normal.pdf', case='', feat='',
                                     title_flg=True, title='', max_val=''):
    print(f'*len(data):{len(dist_data)}, the maximize reconstrcution error is {max(dist_data)} for {x_label}')
    # bins = np.linspace(0, max(dist_data), 100)
    if max_val == '':
        max_val = max(dist_data)
    bins = np.linspace(0, max_val, 15)
    fig, ax = plt.subplots()
    counts, bins, patches = ax.hist(dist_data, bins=bins, align='mid')  # facecolor='yellow', edgecolor='gray'
    # plt.hist(dist_data, bins=bins, range=[0, max_val], align='mid')  # facecolor='blue',

    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.1f'))

    plt.xlabel(x_label)
    plt.ylabel('Num. of samples')

    # plt.savefig('Figures/reconstruct_loss_attack.eps', format='eps', dpi=1500)
    sub_dir = os.path.split(out_file)[0]
    output_pre_path = os.path.split(out_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_rescon.pdf')
    # out_file= 'normal.pdf'
    print(f'Reconstr: out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()

    print(f'*the maximize reconstrcution error is {max(dist_data)} for {x_label} in samples\' order')
    plt.plot(range(len(dist_data)), dist_data, 'b*-')
    plt.xlabel(x_label)
    plt.ylabel('reconstruction error value.')
    # plt.savefig('Figures/reconstruct_loss_attack.eps', format='eps', dpi=1500)
    # plt.savefig(out_file)  # should use before plt.show()
    plt.show()


def plot_reconstruction_errors(dist_data, x_label='Reconstruction errors of normal samples',
                               out_file='Figures/{case}_reconstruct_loss_normal.pdf', case='', feat='', title_flg=True,
                               title='', max_val=''):
    print(f'*len(data):{len(dist_data)}, the maximize reconstrcution error is {max(dist_data)} for {x_label}')
    # bins = np.linspace(0, max(dist_data), 100)
    if max_val == '':
        max_val = max(dist_data)
    bins = np.linspace(0, max_val, 30)
    fig, ax = plt.subplots()
    counts, bins, patches = ax.hist(dist_data, bins=bins, align='mid')  # facecolor='yellow', edgecolor='gray'
    # plt.hist(dist_data, bins=bins, range=[0, max_val], align='mid')  # facecolor='blue',

    # Set the ticks to be at the edges of the bins.
    ax.set_xticks(bins)
    # Set the xaxis's tick labels to be formatted with 1 decimal place...
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.f'))

    percent_flg = False
    if percent_flg:
        # Change the colors of bars at the edges...
        twentyfifth, seventyfifth = np.percentile(dist_data, [25, 75])
        for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
            if rightside < twentyfifth:
                patch.set_facecolor('green')
            elif leftside > seventyfifth:
                patch.set_facecolor('red')

        # Label the raw counts and the percentages below the x-axis...
        bin_centers = 0.5 * np.diff(bins) + bins[:-1]
        for count, x in zip(counts, bin_centers):
            # # Label the raw counts
            # ax.annotate(str(count), xy=(x, 0), xycoords=('data', 'axes fraction'),
            #             xytext=(0, -18), textcoords='offset points', va='top', ha='center')

            # Label the percentages
            percent = '%0.0f%%' % (100 * float(count) / counts.sum())
            if percent_flg:
                if x < 1:
                    print(f'bin_center={x},percent={percent}')
            ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
                        xytext=(0, -32), textcoords='offset points', va='top', ha='center')

    plt.ylabel('Num. of samples')

    # Give ourselves some more room at the bottom of the plot
    plt.subplots_adjust(bottom=0.15)
    plt.xlabel(x_label)

    # plt.savefig('Figures/reconstruct_loss_attack.eps', format='eps', dpi=1500)
    sub_dir = os.path.split(out_file)[0]
    output_pre_path = os.path.split(out_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_rescon.pdf')
    # out_file= 'normal.pdf'
    print(f'Reconstr: out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()

    print(f'*the maximize reconstrcution error is {max(dist_data)} for {x_label} in samples\' order')
    plt.plot(range(len(dist_data)), dist_data, 'b*-')
    plt.xlabel(x_label)
    plt.ylabel('reconstruction error value.')
    # plt.savefig('Figures/reconstruct_loss_attack.eps', format='eps', dpi=1500)
    # plt.savefig(out_file)  # should use before plt.show()
    plt.show()


def plot_reconstruction_errors_from_txt(input_file, output_pre_path='', balance_data_flg=True, random_state=42,
                                        title_flg=True, title='', max_val=''):
    """

    :param input_file:   f'Figures/{case}_recon_err_of_{str(num_features)}_features.txt'
    :param output_pre_path:
    :param balance_data_flg:
    :return:
    """
    reconst_errors_dict = {'normal': [], 'attack': []}
    with open(input_file, 'r') as in_hdl:
        line = in_hdl.readline()
        while line != '':
            if line.startswith('recon'):
                line = in_hdl.readline()
                continue
            line_arr = line.split(',')
            if '1' in line_arr[1]:  # '1': normal data ; '0': attack data
                reconst_errors_dict['normal'].append(float(line_arr[0]))
            else:
                reconst_errors_dict['attack'].append(float(line_arr[0]))
            line = in_hdl.readline()

    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    print(f'output_pre_path:{output_pre_path}')
    if balance_data_flg:
        min_size = len(reconst_errors_dict['normal'])
        if min_size > len(reconst_errors_dict['attack']):
            min_size = len(reconst_errors_dict['attack'])
            plot_reconstruction_errors(shuffle(reconst_errors_dict['normal'], random_state=random_state)[:min_size],
                                       x_label='Reconstruction errors of normal samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
            plot_reconstruction_errors(reconst_errors_dict['attack'], x_label='Reconstruction errors of attack samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
        else:
            plot_reconstruction_errors(reconst_errors_dict['normal'],
                                       x_label='Reconstruction errors of normal samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
            plot_reconstruction_errors(shuffle(reconst_errors_dict['attack'], random_state=random_state)[:min_size],
                                       x_label='Reconstruction errors of attack samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
    else:
        plot_reconstruction_errors(reconst_errors_dict['normal'],
                                   x_label='Reconstruction errors of normal samples',
                                   out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                   feat='', title_flg=title_flg, title=title, max_val=max_val)
        plot_reconstruction_errors(shuffle(reconst_errors_dict['attack'], random_state=random_state),
                                   x_label='Reconstruction errors of attack samples',
                                   out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                   feat='', title_flg=title_flg, title=title, max_val=max_val)


def plot_reconstruction_errors_from_txt_less_than_5(input_file, output_pre_path='', balance_data_flg=True,
                                                    random_state=42, title_flg=True, title='', max_val=5):
    """

    :param input_file:   f'Figures/{case}_recon_err_of_{str(num_features)}_features.txt'
    :param output_pre_path:
    :param balance_data_flg:
    :return:
    """
    reconst_errors_dict = {'normal': [], 'attack': []}
    with open(input_file, 'r') as in_hdl:
        line = in_hdl.readline()
        while line != '':
            if line.startswith('recon'):
                line = in_hdl.readline()
                continue
            line_arr = line.split(',')
            if float(line_arr[0]) < 10:
                if '1' in line_arr[1]:  # '1': normal data ; '0': attack data
                    reconst_errors_dict['normal'].append(float(line_arr[0]))
                else:
                    reconst_errors_dict['attack'].append(float(line_arr[0]))
            line = in_hdl.readline()

    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    print(f'output_pre_path:{output_pre_path}')
    if balance_data_flg:
        min_size = len(reconst_errors_dict['normal'])
        if min_size > len(reconst_errors_dict['attack']):
            min_size = len(reconst_errors_dict['attack'])
            plot_reconstruction_errors(shuffle(reconst_errors_dict['normal'], random_state=random_state)[:min_size],
                                       x_label='Reconstruction loss of normal samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
            plot_reconstruction_errors(reconst_errors_dict['attack'], x_label='Reconstruction loss of attack samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
        else:
            plot_reconstruction_errors(reconst_errors_dict['normal'],
                                       x_label='Reconstruction loss of normal samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
            plot_reconstruction_errors(shuffle(reconst_errors_dict['attack'], random_state=random_state)[:min_size],
                                       x_label='Reconstruction loss of attack samples',
                                       out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                       feat='', title_flg=title_flg, title=title, max_val=max_val)
    else:
        plot_reconstruction_errors(reconst_errors_dict['normal'],
                                   x_label='Reconstruction loss of normal samples',
                                   out_file=f'Figures/{output_pre_path}_reconstruct_loss_normal_data.pdf', case='',
                                   feat='', title_flg=title_flg, title=title, max_val=max_val)
        plot_reconstruction_errors(shuffle(reconst_errors_dict['attack'], random_state=random_state),
                                   x_label='Reconstruction loss of attack samples',
                                   out_file=f'Figures/{output_pre_path}_reconstruct_loss_attack_data.pdf', case='',
                                   feat='', title_flg=title_flg, title=title, max_val=max_val)


def plot_sub_features_metrics(input_file='Figures/{case}_num_features_res_metrics.txt', title_flg=True, title=''):
    res_metrics_lst = {'tpr': [], 'fnr': [], 'fpr': [], 'tnr': [], 'acc': []}
    thres_lst = []
    num_features_list = []
    with open(input_file, 'r') as in_hdl:
        line = in_hdl.readline()

        while line != '':
            if line.startswith('thres'):
                num_features_list.append(int(line.split('=')[1].split(',')[0]))
                line = in_hdl.readline()
                continue

            line_arr = line.split(',')
            thres_lst.append(float(line_arr[0]))
            res_metrics_lst['tpr'].append(float(line_arr[1]))
            res_metrics_lst['fnr'].append(float(line_arr[2]))
            res_metrics_lst['fpr'].append(float(line_arr[3]))
            res_metrics_lst['tnr'].append(float(line_arr[4]))
            res_metrics_lst['acc'].append(float(line_arr[5]))

            line = in_hdl.readline()

    fig, ax = plt.subplots()
    ax.plot(num_features_list, res_metrics_lst['fpr'], 'r*-', label='FPR')
    ax.plot(num_features_list, res_metrics_lst['fnr'], 'b*-', label='FNR')
    # ax.plot(num_features_list, res_metrics_lst['tpr'], 'g*-', label='TPR')
    # ax.plot(num_features_list, res_metrics_lst['tnr'], 'c*-', label='TNR')
    # plt.xlim([0.0, 1.0])
    # plt.ylim([0.0, 1.05])
    plt.xlabel('Number of features')
    plt.ylabel('Rate')
    plt.legend(loc='upper right')
    # plt.title(title)

    sub_dir = os.path.split(input_file)[0]
    output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    out_file = os.path.join(sub_dir, output_pre_path + '_num_features.pdf')
    print(f'different Num_features: out_file:{out_file}')
    plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()


def plot_AE_thresholds_metrics(input_file='Figures/{case}_thres_res_metrics.txt', title_flg=True, title='',
                               only_FRP_flg=False):
    res_metrics_lst = {'tpr': [], 'fnr': [], 'fpr': [], 'tnr': [], 'acc': []}
    thres_lst = []

    with open(input_file, 'r') as in_hdl:
        line = in_hdl.readline()

        while line != '':
            if line.startswith('thres'):
                line = in_hdl.readline()
                continue

            line_arr = line.split(',')
            thres_lst.append(float(line_arr[0]))
            res_metrics_lst['tpr'].append(float(line_arr[1]))
            res_metrics_lst['fnr'].append(float(line_arr[2]))
            res_metrics_lst['fpr'].append(float(line_arr[3]))
            res_metrics_lst['tnr'].append(float(line_arr[4]))
            res_metrics_lst['acc'].append(float(line_arr[5]))

            line = in_hdl.readline()

    fig, ax = plt.subplots()

    if only_FRP_flg:
        ax.plot(thres_lst, res_metrics_lst['fpr'], 'r*-', label='FPR')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        plt.xlabel('Reconstruction errors')
        plt.ylabel('False Positive Rate')
        # plt.legend(loc='upper right')
        # plt.title(title)

        sub_dir = os.path.split(input_file)[0]
        output_pre_path = os.path.split(input_file)[-1].split('.')[0]
        out_file = os.path.join(sub_dir, output_pre_path + '_AE_thres_for_paper.pdf')
        print(f'AE_thres: out_file:{out_file}')
        plt.savefig(out_file)  # should use before plt.show()

    else:
        ax.plot(thres_lst, res_metrics_lst['fpr'], 'r*-', label='FPR')
        ax.plot(thres_lst, res_metrics_lst['fnr'], 'b*-', label='FNR')
        # ax.plot(thres_lst, res_metrics_lst['tpr'], 'g*-', label='TPR')
        # ax.plot(thres_lst, res_metrics_lst['tnr'], 'c*-', label='TNR')
        # plt.xlim([0.0, 1.0])
        # plt.ylim([0.0, 1.05])
        plt.xlabel('AE Thresholds')
        plt.ylabel('Rate')
        plt.legend(loc='upper right')
        # plt.title(title)

        sub_dir = os.path.split(input_file)[0]
        output_pre_path = os.path.split(input_file)[-1].split('.')[0]
        out_file = os.path.join(sub_dir, output_pre_path + '_AE_thres.pdf')
        print(f'AE_thres: out_file:{out_file}')
        plt.savefig(out_file)  # should use before plt.show()

    if title_flg:
        plt.title(title)

    plt.show()


def plot_point(tp, tn, fp, fn):
    tp = np.array(tp[0:250])
    tn = np.array(tn[0:250])
    fp = np.array(fp[0:250])
    fn = np.array(fn[0:250])

    diff = tp - tn
    for i in range(10):
        print(diff[i])

    print(tp.shape)
    # tp = tp[:,2:]
    # tn = tn[:,2:]
    # fp = fp[:,2:]
    # fn = fn[:,2:]

    data_fin = np.concatenate([tp, tn, fp, fn])

    # pca = PCAS(n_components=2, svd_solver='full')
    # pca.fit(data_fin)
    # data_fin = pca.transform(data_fin)
    data_fin = TSNE(n_components=2, verbose=2).fit_transform(data_fin)

    tp = data_fin[:250]
    tn = data_fin[250:500]
    fp = data_fin[500:750]
    fn = data_fin[750:]

    x = tp[:, 0]
    y = tp[:, 1]
    # z = tp[:,2]
    # print(x,y)

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # ax.scattacker(x, y, z, c='red')
    # ax.scattacker(tn[:,0],tn[:,1],tn[:,2],c='blue')
    # ax.scattacker(fp[:,0],fp[:,1],fp[:,2],c='green')
    # ax.scattacker(fn[:,0],fn[:,1],fn[:,2],c='yellow')

    plt.scattacker(x, y, color='red')
    plt.scattacker(tn[:, 0], tn[:, 1], color='blue')
    plt.scattacker(fp[:, 0], fp[:, 1], color='green')
    plt.scattacker(fn[:, 0], fn[:, 1], color='yellow')

    plt.show()


def show_feature_selection_data(input_file):
    #
    # fig, ax = plt.subplots()
    # ax.plot(num_features_list, res_metrics_lst['fpr'], 'r*-', label='FPR')
    # ax.plot(num_features_list, res_metrics_lst['fnr'], 'b*-', label='FNR')
    # # plt.xlim([0.0, 1.0])
    # # plt.ylim([0.0, 1.05])
    # plt.xlabel('Number of features')
    # plt.ylabel('Rate')
    # plt.legend(loc='upper right')
    # # plt.title(title)
    #
    # sub_dir = os.path.split(input_file)[0]
    # output_pre_path = os.path.split(input_file)[-1].split('.')[0]
    # out_file = os.path.join(sub_dir, output_pre_path + '_num_features.pdf')
    # print(f'Num_features: out_file:{out_file}')
    # plt.savefig(out_file)  # should use before plt.show()
    #
    # if title_flg:
    #     plt.title(title)
    #
    # plt.show()

    pass


# To plot some findings
def showFindings(case, title, data):
    weight = np.ones_like(data) / data.shape
    bin = np.linspace(0, 40, 2500)
    print("\nFor ", title, " Case : ", case)
    print("Max : ", np.round(np.amax(data), 4), "\nMin : ", np.round(np.amin(data), 4), "\nMean : ",
          np.round(np.mean(data), 4))
    '''
    n, bins, patches = plt.hist(data, weights = weight, bins = bin, cumulative=False)
    plt.title("For " + title + " Case : " + str(case))
    plt.show()
    '''

    n, bins, patches = plt.hist(data, weights=weight, bins=bin, cumulative=True, histtype='step')
    plt.title("For " + title + " Case : " + str(case))
    plt.show()


def get_features_from_idx(sub_features_idx_lst=[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 25]):
    # ts, sip, dip, sport, dport, proto, dura, orig_pks, reply_pks, orig_bytes, reply_bytes, orig_min_pkt_size, orig_max_pkt_size, reply_min_pkt_size, reply_max_pkt_size, orig_min_interval, orig_max_interval, reply_min_interval, reply_max_interval, orig_min_ttl, orig_max_ttl, reply_min_ttl, reply_max_ttl, urg, ack, psh, rst, syn, fin, is_new, state, prev_state

    features_lst = ['ts', 'sip', 'dip', 'sport', 'dport', 'proto', 'dura', 'orig_pks', 'reply_pks', 'orig_bytes',
                    'reply_bytes', 'orig_min_pkt_size', 'orig_max_pkt_size', 'reply_min_pkt_size', 'reply_max_pkt_size',
                    'orig_min_interval', 'orig_max_interval', 'reply_min_interval', 'reply_max_interval',
                    'orig_min_ttl',
                    'orig_max_ttl', 'reply_min_ttl', 'reply_max_ttl', 'urg', 'ack', 'psh', 'rst', 'syn', 'fin',
                    'is_new',
                    'state', 'prev_state']

    result_lst = []
    for i in sub_features_idx_lst:  # the first one (0) starts from 'proto'
        result_lst.append(features_lst[i + 5])
        print(f'feature_idx:{i}, {features_lst[i+5]}')
    print('result_lst:', result_lst)

    return result_lst


if __name__ == '__main__':
    flg = '5'

    if flg == '1':  # AE_thresholds
        input_file = "Figures/uSc1C2_z-score_20_14_thres_res_metrics_of_27_features.txt"
        input_file = "Figures/uSc1C2_z-score_thres_res_metrics_of_27_features.txt"
        input_file = 'Figures/uSc1C2_z-score_thres_res_metrics_of_27_features.txt'
        plot_AE_thresholds_metrics(input_file, title_flg=True, title='', only_FRP_flg=False)

    elif flg == '2':  # econstruction_errors
        input_file = 'Figures/uSc1C1_z-score_20_14_recon_err_of_27_features.txt'
        input_file = 'Figures/uSc1C2_z-score_recon_err_of_27_features.txt'
        # input_file = '../Experiment_1_Results_20190617_19_30.txt'
        plot_reconstruction_errors_from_txt(input_file, output_pre_path='', balance_data_flg=True, random_state=42,
                                            title_flg=True, title='', max_val='')

        # plot_reconstruction_errors_from_txt_less_than_5(input_file, output_pre_path='', balance_data_flg=True, random_state=42,
        #                                     title_flg=True, title='',max_val = '')
    elif flg == '3':  # sub_features
        input_file = "Figures/uSc1C2_z-score_num_features_res_metrics.txt"
        input_file = "Figures/uSc1C1_z-score_all_num_features_res_metrics.txt"
        plot_sub_features_metrics(input_file, title_flg=True, title='')
        get_features_from_idx(sub_features_idx_lst=[0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 19, 25])

    elif flg == '4':  # feature selection
        input_file = "Figures/uSc1C2_z-score_sub_features_list.txt"
        input_file = "Figures/uSc1C1_z-score_sub_features_list.txt"
        plot_features_selection_results(input_file, title_flg=True, title='')
    elif flg == '5':  # ROC
        # input_file = "Figures/uSc1C1_z-score_20_14_roc_data_of_16_features.txt"
        input_file = "Figures/uSc1C2_z-score_20_14_roc_data_of_16_features.txt"
        plot_roc(input_file, title_flg=True, title='')
        # plot_roc_with_scikit_plot(input_file, title_flg=True, title='')
    else:
        input_file = "Figures/uSc1C2_z-score_3d_data.txt"
        plot_3d_feature_selection(input_file)
        print('not implement.')
        pass
