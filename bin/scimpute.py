import pandas as pd
import numpy as np
import time
import os
import matplotlib
matplotlib.use('Agg')  # for plotting without GUI
import matplotlib.pyplot as plt
from scipy.stats.stats import pearsonr
import math
import tensorflow as tf


# Data I/O #
def read_csv(fname):
    '''read_csv into pd.df, assuming index_col=0, and header=True'''
    print('reading ', fname)
    tic = time.time()
    df = pd.read_csv(fname, index_col=0)
    # print("read matrix: [genes, cells]")
    print(df.shape)
    # print(df.axes)
    if df.shape[0] > 2 and df.shape[1] > 2:
        print(df.ix[0:3, 0:2])
    toc = time.time()
    print("reading took {:.1f} seconds".format(toc - tic))
    return (df)


def save_csv(arr, fname):
    '''if fname=x.csv.gz, will be compressed
    if fname=x.csv, will not be compressed'''
    tic = time.time()
    np.savetxt(fname, arr, delimiter=',', newline='\n')
    toc = time.time()
    print("saving" + fname + " took {:.1f} seconds".format(toc - tic))


def save_hd5(df, out_name):
    tic = time.time()
    df.to_hdf(out_name, key='null', mode='w', complevel=9, complib='blosc')
    toc = time.time()
    print("saving" + out_name + " took {:.1f} seconds".format(toc - tic))


def read_hd5(in_name):
    '''
    :param in_name: 
    :return df: 
    '''
    print('reading: ', in_name)
    df = pd.read_hdf(in_name)
    print(df.shape)
    # print(df.axes)
    if df.shape[0] > 2 and df.shape[1] > 2:
        print(df.ix[0:3, 0:2])
    return (df)


# Pre-processing of data frames #
def df_filter(df):
    df_filtered = df.loc[(df.sum(axis=1) != 0), (df.sum(axis=0) != 0)]
    print("filtered out any rows and columns with sum of zero")
    return df_filtered


def df_normalization(df):
    '''
    :param df: assume df.shape = [gene, cell]
    :return: Reads Per Million (RPM)
    '''
    read_counts = df.sum(axis=0)  # colsum
    # df_normalized = df.div(read_counts, axis=1).mul(np.median(read_counts)).mul(1)
    df_normalized = df.div(read_counts, axis=1).mul(1e6)
    return df_normalized


def df_log_transformation(df, pseudocount=1):
    df_log = np.log10(np.add(df, pseudocount))
    return df_log


def multinormial_downsampling(in_df, libsize_out):
    out_df = in_df.copy()
    for i in range(len(in_df)):
        slice_arr = in_df.values[i, :]
        libsize = slice_arr.sum()
        p_lst = slice_arr / libsize
        slice_resample = np.random.multinomial(libsize_out, p_lst)
        out_df.ix[i, :] = slice_resample
    return out_df


def mask_df(df, nz_goal):
    df_msked = df.copy()
    nz_now = nnzero_rate_df(df)
    nz_goal = nz_goal/nz_now
    zero_goal = 1-nz_goal
    df_msked = df_msked.where(np.random.uniform(size=df.shape) > zero_goal, 0)
    return df_msked


# Plots #
def density_plot(x, y,
                 title='density plot',
                 dir='plots',
                 xlab='x',
                 ylab='y'):
    '''x and y must be arr [m, 1]'''
    from scipy.stats import gaussian_kde
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = "./{}/{}".format(dir, title)
    # Calculate the point density
    xy = np.vstack([x, y])
    z = gaussian_kde(xy)(xy)
    # sort: dense on top (plotted last)
    idx = z.argsort()
    x, y, z = x[idx], y[idx], z[idx]
    # plt
    fig = plt.figure(figsize=(5, 5))
    fig, ax = plt.subplots()
    cax = ax.scatter(x, y, c=z, s=50, edgecolor='')
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.colorbar(cax)
    plt.savefig(fname + ".png", bbox_inches='tight')
    plt.close(fig)


def scatterplot(x, y,
                title='scatterplot',
                dir='plots',
                xlab='xlab',
                ylab='ylab',
                alpha=1):
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = "./{}/{}".format(dir, title)
    fig = plt.figure(figsize=(5, 5))
    plt.plot(x, y, 'o', alpha=alpha)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)
    print('heatmap vis ', title, ' done')


def genescatterplot(gene1, gene2, scdata):
    gene1 = str(gene1);
    gene2 = str(gene2)
    fig, ax = scdata.scatter_gene_expression([gene1, gene2])
    fig.savefig(gene1 + "_" + gene2 + '.biaxial.png')
    # after magic
    fig, ax = scdata.magic.scatter_gene_expression([gene1, gene2])
    fig.savefig(gene1 + "_" + gene2 + '.magic.biaxial.png')
    plt.close(fig)


def genescatterplot3d(gene1, gene2, gene3, scdata):
    gene1 = str(gene1);
    gene2 = str(gene2);
    gene3 = str(gene3);
    fig, ax = scdata.scatter_gene_expression([gene1, gene2, gene3])
    fig.savefig(gene1 + "_" + gene2 + "_" + gene3 + '.biaxial.png')
    # after magic
    fig, ax = scdata.magic.scatter_gene_expression([gene1, gene2, gene3])
    fig.savefig(gene1 + "_" + gene2 + "_" + gene3 + '.magic.biaxial.png')
    plt.close(fig)


def hist_list(list, xlab='xlab', title='histogram', bins=100, dir='plots'):
    '''output histogram of a list into png'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = str(title) + '.png'
    fname = "./{}/{}".format(dir, fname)
    fig, ax = plt.subplots()
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel('Frequency')
    hist = plt.hist(list, bins=bins)
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)
    print('hist of {} is done'.format(title))
    return hist

def bone_marrow_biaxial_plots(scdata):
    # Gene-Gene scatter plot (before & after magic)
    # Fig3
    print("gene-gene plot for bone marrow dataset")
    genescatterplot('Cd34', 'Gypa', scdata)  # CD325a
    genescatterplot('Cd14', 'Itgam', scdata)  # cd11b
    genescatterplot('Cd34', 'Fcgr2b', scdata)  # cd32, similar plot
    genescatterplot3d('Cd34', 'Gata1', 'Gata2', scdata)
    genescatterplot3d('Cd44', 'Gypa', 'Cpox', scdata)
    genescatterplot3d('Cd34', 'Itgam', 'Cd14', scdata)
    # Fig12
    genescatterplot('Cd34', 'Itgam', scdata)
    genescatterplot('Cd34', 'Apoe', scdata)
    genescatterplot('Cd34', 'Gata1', scdata)
    genescatterplot('Cd34', 'Gata2', scdata)
    genescatterplot('Cd34', 'Ephb6', scdata)
    genescatterplot('Cd34', 'Lepre1', scdata)
    genescatterplot('Cd34', 'Mrpl44', scdata)
    genescatterplot('Cd34', 'Cnbp', scdata)
    # Fig14
    genescatterplot('Gata1', 'Gata2', scdata)
    genescatterplot('Klf1', 'Sfpi1', scdata)
    genescatterplot('Meis1', 'Cebpa', scdata)
    genescatterplot('Elane', 'Cebpe', scdata)


def heatmap_vis(arr, title='visualization of matrix in a square manner', cmap="rainbow",
                vmin=None, vmax=None, xlab='', ylab='', dir='plots'):
    '''heatmap visualization of 2D matrix, with plt.imshow(), in a square manner
    cmap options PiYG for [neg, 0, posi]
    Greys Reds for [0, max]
    rainbow for [0,middle,max]'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = './' + dir + '/' + title + '.vis.png'

    if (vmin is None):
        vmin = np.min(arr)
    if (vmax is None):
        vmax = np.max(arr)

    fig = plt.figure(figsize=(9, 9))
    plt.imshow(arr, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.colorbar()
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)
    print('heatmap vis ', title, ' done')


def heatmap_vis2(arr, title='visualization of matrix', cmap="rainbow",
                 vmin=None, vmax=None, xlab='', ylab='', dir='plots'):
    '''heatmap visualization of 2D matrix, with plt.pcolor()
    cmap options PiYG for [neg, 0, posi]
    Greys Reds for [0, max]
    rainbow for [0,middle,max]'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = './' + dir + '/' + title + '.vis.png'

    if (vmin is None):
        vmin = np.min(arr)
    if (vmax is None):
        vmax = np.max(arr)

    fig = plt.figure(figsize=(9, 9))
    plt.pcolor(arr, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.colorbar()
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)
    print('heatmap vis ', title, ' done')


def hist_arr_flat(arr, title='hist', xlab='x', ylab='Frequency', bins=100, dir='plots'):
    '''create histogram for flattened arr'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = "./{}/{}".format(dir, title) + '.png'

    fig = plt.figure(figsize=(9, 9))
    n, bins, patches = plt.hist(arr.flatten(), bins, normed=1, facecolor='green', alpha=0.75)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)
    print("histogram ", title, ' done')


def split_arr(arr, a=0.8, b=0.1, c=0.1, seed_var=1):
    """input array, output rand split arrays
    a: train, b: valid, c: test
    e.g.: [arr_train, arr_valid, arr_test] = split(df.values)"""
    print(">splitting data")
    np.random.seed(seed_var)  # for splitting consistency
    train_indices = np.random.choice(arr.shape[0], int(round(arr.shape[0] * a // (a + b + c))), replace=False)
    remain_indices = np.array(list(set(range(arr.shape[0])) - set(train_indices)))
    valid_indices = np.random.choice(remain_indices, int(round(len(remain_indices) * b // (b + c))), replace=False)
    test_indices = np.array(list(set(remain_indices) - set(valid_indices)))
    np.random.seed()  # cancel seed effect
    print("total samples being split: ", len(train_indices) + len(valid_indices) + len(test_indices))
    print('train:', len(train_indices), ' valid:', len(valid_indices), 'test:', len(test_indices))

    arr_train = arr[train_indices]
    arr_valid = arr[valid_indices]
    arr_test = arr[test_indices]

    return (arr_train, arr_valid, arr_test)


def split_df(df, a=0.8, b=0.1, c=0.1, seed_var=1):
    """input df, output rand split dfs
    a: train, b: valid, c: test
    e.g.: [df_train, df2, df_test] = split(df, a=0.7, b=0.15, c=0.15)"""
    np.random.seed(seed_var)  # for splitting consistency
    train_indices = np.random.choice(df.shape[0], int(df.shape[0] * a // (a + b + c)), replace=False)
    remain_indices = np.array(list(set(range(df.shape[0])) - set(train_indices)))
    valid_indices = np.random.choice(remain_indices, int(len(remain_indices) * b // (b + c)), replace=False)
    test_indices = np.array(list(set(remain_indices) - set(valid_indices)))
    np.random.seed()  # cancel seed effect
    print("total samples being split: ", len(train_indices) + len(valid_indices) + len(test_indices))
    print('train:', len(train_indices), ' valid:', len(valid_indices), 'test:', len(test_indices))

    df_train = df.ix[train_indices, :]
    df_valid = df.ix[valid_indices, :]
    df_test = df.ix[test_indices, :]

    return df_train, df_valid, df_test


def random_subset_arr(arr, m_max, n_max):
    [m, n] = arr.shape
    m_reduce = min(m, m_max)
    n_reduce = min(n, n_max)
    np.random.seed(1201)
    row_rand_idx = np.random.choice(m, m_reduce, replace=False)
    col_rand_idx = np.random.choice(n, n_reduce, replace=False)
    np.random.seed()
    arr_sub = arr[row_rand_idx][:, col_rand_idx]
    print('matrix from [{},{}] to a random subset of [{},{}]'.
          format(m, n, arr_sub.shape[0], arr_sub.shape[1]))
    return arr_sub


def median_corr(arr1, arr2, num=100, accuracy=3, seed_var=100):
    """arr1 & arr2 must have same shape
    will calculate correlation between corresponding rows"""
    # from scipy.stats.stats import pearsonr
    pearsonrlog = []
    m, n = arr1.shape
    num = min(num, m)  # same 100 cells being evaluated for learning curves
    # print(num, 'samples being used to calculate pearsonr')
    np.random.seed(seed_var)
    idx = np.random.choice(range(m), num, replace=False)
    for i in idx:
        pearsonrlog.append(pearsonr(arr1[i], arr2[i]))
    pearsonrlog.sort()
    result = round(pearsonrlog[int(num // 2)][0], accuracy)
    np.random.seed()
    return result


def curveplot(x, y, title, xlabel, ylabel, dir='plots'):
    # scimpute.curveplot(epoch_log, corr_log_valid,
    #                      title='learning_curve_pearsonr.step2.gene'+str(j)+", valid",
    #                      xlabel='epoch',
    #                      ylabel='Pearson corr (predction vs ground truth, valid, including cells with zero gene-j)')
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fprefix = "./{}/{}".format(dir, title)
    # plot
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()


def curveplot2(x, y, z, title, xlabel, ylabel, dir='plots'):
    '''curveplot2(epoch_log, train_log, valid_log, title="t", xlabel="x", ylabel="y")'''
    # scimpute.curveplot2(epoch_log, corr_log_train, corr_log_valid,
    #                      title='learning_curve_pearsonr.step2.gene'+str(j)+", train_valid",
    #                      xlabel='epoch',
    #                      ylabel='Pearson corr (predction vs ground truth, valid, including cells with zero gene-j)')
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fprefix = "./{}/{}".format(dir, title)
    # plot
    plt.plot(x, y, label='train')
    plt.plot(x, z, label='valid')
    plt.legend()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()


def scatterplot2(x, y, title=None, xlabel=None, ylabel=None, range='same', dir='plots'):
    '''x is slice, y is a slice
    have to be slice to help pearsonr(x,y)[0] work
    range=[min, max]'''
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fprefix = "./{}/{}".format(dir, title)
    # plot
    corr, _ = pearsonr(x, y)
    corr = str(round(corr, 4))
    plt.plot(x, y, 'o')
    plt.title(str(title + "\ncorr: " + corr))
    plt.xlabel(xlabel + "\nmean: " + str(round(np.mean(x), 2)))
    plt.ylabel(ylabel + "\nmean: " + str(round(np.mean(y), 2)))
    if range is 'same':
        max, min = max_min_element_in_arrs([x, y])
        plt.xlim(min, max)
        plt.ylim(min, max)
    elif range is 'flexible':
        next
    else:
        plt.xlim(range[0], range[1])
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()


def gene_corr_hist(arr1, arr2, title='hist_gene_corr', dir='plots'):
    '''calculate correlation between genes [columns]
    arr [cells, genes]'''
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fprefix = "./{}/{}".format(dir, title)

    # if arr1.shape is arr2.shape:
    range_size = arr2.shape[1]
    hist = []
    for i in range(range_size):
        corr = pearsonr(arr1[:, i], arr2[:, i])[0]
        if not math.isnan(corr):
            hist.append(corr)
    hist.sort()
    median = round(np.median(hist), 3)
    mean = round(np.mean(hist), 3)
    print('median gene_corr: {}'.format(median))

    # histogram of correlation
    fig = plt.figure(figsize=(5, 5))
    plt.hist(hist, bins=100)
    plt.xlabel('Gene-corr (Pearson)' + '\nmedian=' + str(median) + ', mean=' + str(mean))
    plt.ylabel('Freq')
    plt.xlim(-1, 1)
    plt.title(title)
    plt.savefig(fprefix + ".png", bbox_inches='tight') #todo remove \n from out-name
    plt.close(fig)
    return hist


def cell_corr_hist(arr1, arr2, title='hist_cell_corr', dir='plots'):
    '''calculate correlation between genes [columns]
    arr [cells, genes]'''
    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)
    fprefix = "./{}/{}".format(dir, title)

    # if arr1.shape is arr2.shape:
    range_size = arr2.shape[0]
    hist = []
    for i in range(range_size):
        corr = pearsonr(arr1[i, :], arr2[i, :])[0]
        if not math.isnan(corr):
            hist.append(corr)
    hist.sort()
    median = round(np.median(hist), 3)
    mean = round(np.mean(hist), 3)
    print('median cell_corr: {}'.format(median))

    # histogram of correlation
    fig = plt.figure(figsize=(5, 5))
    plt.hist(hist, bins=100)
    plt.xlabel('Cell-corr (Pearson)' + '\nmedian=' + str(median) + ', mean=' + str(mean))
    plt.ylabel('Freq')
    plt.xlim(-1, 1)
    plt.title(title)
    plt.savefig(fprefix + ".png", bbox_inches='tight')
    plt.close(fig)
    return hist


def refresh_logfolder(log_dir):
    '''delete and recreate log_dir'''
    if tf.gfile.Exists(log_dir):
        tf.gfile.DeleteRecursively(log_dir)
        print(log_dir, "deleted")
    tf.gfile.MakeDirs(log_dir)
    print(log_dir, 'created\n')


def max_min_element_in_arrs(arr_list):
    '''input a list of np.arrays
    e.g: max_element_in_arrs([df_valid.values, h_valid])'''
    max_list = []
    for x in arr_list:
        max_tmp = np.nanmax(x)
        max_list.append(max_tmp)
    max_all = np.nanmax(max_list)

    min_list = []
    for x in arr_list:
        min_tmp = np.nanmin(x)
        min_list.append(min_tmp)
    min_all = np.nanmin(min_list)

    return max_all, min_all


def visualize_weights_biases(weight, bias, title, cmap='rainbow', dir='plots'):
    '''heatmap visualization of weight and bias
    weights: [1000, 500]
    bias: [1, 500]
    '''
    # https://stackoverflow.com/questions/43076488/single-row-or-column-heat-map-in-python
    if not os.path.exists(dir):
        os.makedirs(dir)
    fname = "./{}/{}".format(dir, title) + '.vis.png'

    vmax_w, vmin_w = max_min_element_in_arrs([weight])
    vmax_b, vmin_b = max_min_element_in_arrs([bias])

    norm_w = matplotlib.colors.Normalize(vmin=vmin_w, vmax=vmax_w)
    norm_b = matplotlib.colors.Normalize(vmin=vmin_b, vmax=vmax_b)

    grid = dict(height_ratios=[weight.shape[0], weight.shape[0] / 40, weight.shape[0] / 40],
                width_ratios=[weight.shape[1], weight.shape[1] / 40])
    fig, axes = plt.subplots(ncols=2, nrows=3, gridspec_kw=grid)

    axes[0, 0].imshow(weight, aspect="auto", cmap=cmap, norm=norm_w)
    axes[1, 0].imshow(bias, aspect="auto", cmap=cmap, norm=norm_b)

    for ax in [axes[1, 0]]:
        ax.set_xticks([])

    for ax in [axes[1, 0]]:
        ax.set_yticks([])

    for ax in [axes[1, 1], axes[2, 1]]:
        ax.axis("off")

    # axes[1, 0].set_xlabel('node out')
    # axes[1, 0].set_ylabel('node in')

    sm_w = matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm_w)
    sm_w.set_array([])
    sm_b = matplotlib.cm.ScalarMappable(cmap=cmap, norm=norm_b)
    sm_b.set_array([])

    fig.colorbar(sm_w, cax=axes[0, 1])
    fig.colorbar(sm_b, cax=axes[2, 0], orientation="horizontal")
    # todo: add title in plot
    plt.savefig(fname, bbox_inches='tight')
    plt.close(fig)


def corr_one_gene(col1, col2, accuracy=3):
    """will calculate pearsonr for gene(i)"""
    # from scipy.stats.stats import pearsonr
    result = pearsonr(col1, col2)[0][0]
    result = round(result, accuracy)
    return (result)


def hist_df(df, title="hist of df", xlab='xlab', bins=100, dir='plots'):
    if not os.path.exists(dir):
        os.makedirs(dir)
    df_flat = df.values.reshape(df.size, 1)
    # fig = plt.figure(figsize=(9, 9))
    hist = plt.hist(df_flat, bins=bins)
    plt.title(title)
    plt.xlabel(xlab)
    plt.ylabel('Frequency')
    plt.savefig('./{}/{}.png'.format(dir, title), bbox_inches='tight')
    plt.close()
    print('hist of ', title, 'is done')
    return hist


def nnzero_rate_df(df):
    idx = df != 0
    nnzero_rate = round(sum(sum(idx.values)) / df.size, 3)
    return (nnzero_rate)


def mean_df(df):
    Sum = sum(sum(df.values))
    Mean = Sum / df.size
    return (Mean)


def subset_df(df_big, df_subset):
    return (df_big.ix[df_subset.index, df_subset.columns])


def read_data(data_name):
    if data_name is 'splatter':  # only this mode creates gene-gene plot
        file = "../data/v1-1-5-3/v1-1-5-3.E3.hd5"  # data need imputation
        file_benchmark = "../data/v1-1-5-3/v1-1-5-3.E3.hd5"
        name1 = '(E3)'
        name2 = '(E3)'  # careful
        df = pd.read_hdf(file).transpose()  # [cells,genes]
        df2 = pd.read_hdf(file_benchmark).transpose()  # [cells,genes]
    elif data_name is 'EMT2730':  # 2.7k cells used in magic paper
        file = "../../../../data/mouse_bone_marrow/python_2730/bone_marrow_2730.norm.log.hd5"  # data need imputation
        file_benchmark = "../../../../data/mouse_bone_marrow/python_2730/bone_marrow_2730.norm.log.hd5"
        name1 = '(EMT2730)'
        name2 = '(EMT2730)'
        df = pd.read_hdf(file).transpose()  # [cells,genes]
        df2 = pd.read_hdf(file_benchmark).transpose()  # [cells,genes]
    elif data_name is 'EMT9k':  # magic imputation using 8.7k cells > 300 reads/cell
        file = "../../../../magic/results/mouse_bone_marrow/EMT_MAGIC_9k/EMT.MAGIC.9k.A.hd5"  # data need imputation
        file_benchmark = "../../../../magic/results/mouse_bone_marrow/EMT_MAGIC_9k/EMT.MAGIC.9k.A.hd5"
        name1 = '(EMT9k)'
        name2 = '(EMT9k)'
        df = pd.read_hdf(file).transpose()  # [cells,genes]
        df2 = pd.read_hdf(file_benchmark).transpose()  # [cells,genes]
    elif data_name is 'EMT9k_log':  # magic imputation using 8.7k cells > 300 reads/cell
        file = "../../../../magic/results/mouse_bone_marrow/EMT_MAGIC_9k/EMT.MAGIC.9k.A.log.hd5"  # data need imputation
        file_benchmark = "../../../../magic/results/mouse_bone_marrow/EMT_MAGIC_9k/EMT.MAGIC.9k.A.log.hd5"
        name1 = '(EMT9kLog)'
        name2 = '(EMT9kLog)'
        df = pd.read_hdf(file).transpose()  # .ix[:, 1:1000]  # [cells,genes]
        df2 = pd.read_hdf(file_benchmark).transpose()  # .ix[:, 1:1000]  # [cells,genes]
    else:
        raise Warning("data name not recognized!")

    # df = df.ix[1:1000] # todo: for development
    # df2 = df.ix[1:1000]

    m, n = df.shape  # m: n_cells; n: n_genes
    print("\ninput df: ", name1, " ", file, "\n", df.values[0:4, 0:4], "\n")
    print("ground-truth df: ", name2, " ", file_benchmark, "\n", df2.values[0:4, 0:4], "\n")

    return (df, df2, name1, name2, m, n)


def variable_summaries(name, var):
    """Attach a lot of summaries to a Tensor (for TensorBoard visualization)."""
    with tf.name_scope(name):
        # mean = tf.reduce_mean(var)
        # tf.summary.scalar('mean', mean)
        # with tf.name_scope('stddev'):
        #     stddev = tf.sqrt(tf.reduce_mean(tf.square(var - mean)))
        # tf.summary.scalar('stddev', stddev)
        # tf.summary.scalar('max', tf.reduce_max(var))
        # tf.summary.scalar('min', tf.reduce_min(var))
        tf.summary.histogram('histogram', var)


def weight_variable(name_scope, dim_in, dim_out, sd):
    """
    define weights
    
    :param name_scope: 
    :param dim_in: 
    :param dim_out: 
    :param sd: 
    :return: 
    """
    with tf.name_scope(name_scope):
        W = tf.Variable(tf.random_normal([dim_in, dim_out], stddev=sd),
                        name=name_scope + '_W')

    variable_summaries(name_scope + '_W', W)

    return W


def bias_variable(name_scope, dim_out, sd):
    """
    define biases

    :param name_scope: 
    :param dim_out: 
    :param sd: 
    :return: 
    """
    with tf.name_scope(name_scope):
        b = tf.Variable(tf.random_normal([dim_out], mean=100 * sd, stddev=sd),
                        name=name_scope + '_b')

    variable_summaries(name_scope + '_b', b)

    return b


def weight_bias_variable(name_scope, dim_in, dim_out, sd):
    """
    define weights and biases

    :param name_scope: 
    :param dim_in: 
    :param dim_out: 
    :param sd: 
    :return: 
    """
    with tf.name_scope(name_scope):
        W = tf.Variable(tf.random_normal([dim_in, dim_out], stddev=sd, dtype=tf.float32),
                        name=name_scope + '_W')
        b = tf.Variable(tf.random_normal([dim_out], mean=100 * sd, stddev=sd, dtype=tf.float32),
                        name=name_scope + '_b')

    variable_summaries(name_scope + '_W', W)
    variable_summaries(name_scope + '_b', b)

    return W, b


def dense_layer(name, input, W, b, pRetain):
    """
    define a layer and return output
    
    :param name: 
    :param input: X_placeholder or a(l-1)
    :param W: weights
    :param b: biases 
    :param pRetain: 
    :return: 
    """
    x_drop = tf.nn.dropout(input, pRetain)
    z = tf.add(tf.matmul(x_drop, W), b)
    a = tf.nn.relu(z)

    variable_summaries(name + '_a', a)

    return a


def dense_layer_BN(name, input, W, b, pRetain, epsilon=1e-3):
    """
    define a layer and return output

    :param name: 
    :param input: X_placeholder or a(l-1)
    :param W: weights
    :param b: biases 
    :param pRetain: 
    :return: 
    """
    x_drop = tf.nn.dropout(input, pRetain)
    z = tf.add(tf.matmul(x_drop, W), b)
    # BN
    batch_mean, batch_var = tf.nn.moments(z, [0])
    z_bn = tf.nn.batch_normalization(z, batch_mean, batch_var, beta, scale, epsilon)
    # NL
    a = tf.nn.relu(z_bn)

    variable_summaries(name + '_a', a)

    return a


def learning_curve_mse(epoch, mse_batch, mse_valid,
                       title='learning curve (MSE)', xlabel='epochs', ylabel='MSE',
                       range=None,
                       dir='plots'):
    """
    depreciated
    """

    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)

    # list to np.array, to use index
    epoch = np.array(epoch)
    mse_batch = np.array(mse_batch)
    # mse_train = np.array(mse_train)
    mse_valid = np.array(mse_valid)

    # plot (full range)
    fprefix = "./{}/{}".format(dir, title)
    plt.plot(epoch, mse_batch, 'b--', label='mse_batch')
    # plt.plot(epoch, mse_train, 'g--', label='mse_train')
    plt.plot(epoch, mse_valid, 'r-', label='mse_valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid mse:' + str(mse_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([mse_batch, mse_valid])
        # max, min = max_min_element_in_arrs([mse_batch, mse_train, mse_valid])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()

    # plot (no epoch0)
    fprefix = "./{}/{}".format(dir, title) + '.cropped'
    zoom = np.arange(1, len(mse_batch))
    plt.plot(epoch[zoom], mse_batch[zoom], 'b--', label='mse_batch')
    # plt.plot(epoch[zoom], mse_train[zoom], 'g--', label='mse_train')
    plt.plot(epoch[zoom], mse_valid[zoom], 'r-', label='mse_valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid mse:' + str(mse_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([mse_batch[zoom], mse_valid[zoom]])
        # max, min = max_min_element_in_arrs([mse_batch, mse_train, mse_valid])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()


def learning_curve_corr(epoch, corr_batch, corr_valid,
                        title='learning curve (corr)',
                        xlabel='epochs',
                        ylabel='median cell-corr (100 cells)',
                        range=None,
                        dir='plots'):
    """
    depreciated
    """

    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)

    # list to np.array, to use index
    epoch = np.array(epoch)
    corr_batch = np.array(corr_batch)
    # corr_train = np.array(corr_train)
    corr_valid = np.array(corr_valid)

    # plot (full range)
    fprefix = "./{}/{}".format(dir, title)
    plt.plot(epoch, corr_batch, 'b--', label='corr_batch')
    # plt.plot(epoch, corr_train, 'g--', label='corr_train')
    plt.plot(epoch, corr_valid, 'r-', label='corr_valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid corr:' + str(corr_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([corr_batch, corr_valid])
        # max, min = max_min_element_in_arrs([corr_batch, corr_train, corr_valid])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()

    # plot (no epoch0)
    fprefix = "./{}/{}".format(dir, title) + '.cropped'
    zoom = np.arange(1, len(corr_batch))
    plt.plot(epoch[zoom], corr_batch[zoom], 'b--', label='corr_batch')
    # plt.plot(epoch[zoom], corr_train[zoom], 'g--', label='corr_train')
    plt.plot(epoch[zoom], corr_valid[zoom], 'r-', label='corr_valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid corr:' + str(corr_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([corr_batch[zoom], corr_valid[zoom]])
        # max, min = max_min_element_in_arrs([corr_batch, corr_train, corr_valid])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()

def learning_curve(epoch, metrics_batch, metrics_valid,
                   title='Learning curve (Metrics)',
                   xlabel='epochs',
                   ylabel='Metrics',
                   range=None,
                   skip=1,
                   dir='plots'):
    '''
    plot learning curve
    :param epoch: vector
    :param metrics_batch: vector
    :param metrics_valid: vector
    :param title: 
    :param xlabel: 
    :param ylabel: 
    :param range: 
    :param dir:
    :return: 
    '''

    # create plots directory
    if not os.path.exists(dir):
        os.makedirs(dir)

    # list to np.array, to use index
    epoch = np.array(epoch)
    metrics_batch = np.array(metrics_batch)
    metrics_valid = np.array(metrics_valid)

    # plot (full range)
    fprefix = "./{}/{}".format(dir, title)
    plt.plot(epoch, metrics_batch, 'b--', label='batch')
    plt.plot(epoch, metrics_valid, 'r-', label='valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid:' + str(metrics_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([metrics_batch, metrics_valid])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()

    # plot (no epoch0)
    fprefix = "./{}/{}".format(dir, title) + '.cropped'
    zoom = np.arange(skip, len(metrics_batch))
    plt.plot(epoch[zoom], metrics_batch[zoom], 'b--', label='batch')
    plt.plot(epoch[zoom], metrics_valid[zoom], 'r-', label='valid')
    plt.title(title)
    plt.xlabel(xlabel + '\nfinal valid:' + str(metrics_valid[-1]))
    plt.ylabel(ylabel)
    plt.legend()
    if range is None:
        max, min = max_min_element_in_arrs([metrics_batch[zoom], metrics_valid[zoom]])
        plt.ylim(min, max)
    else:
        plt.ylim(range[0], range[1])

    plt.savefig(fprefix + '.png', bbox_inches='tight')
    plt.close()

# RESULT ANALYSIS (Factors Affecting Gene Prediction)
# example usage:
# gene_corr = scimpute.gene_corr_list(M.values, H.values)
def gene_corr_list(arr1, arr2):
    '''calculate correlation between genes [columns]
    arr [cells, genes], note, some genes don't have corr'''
    # if arr1.shape is arr2.shape:
    n = arr2.shape[1]
    list = []
    for j in range(n):
        corr = pearsonr(arr1[:, j], arr2[:, j])[0]
        if math.isnan(corr):
            list.append(-1.1)  # NA becomes -1.1
        else:
            list.append(corr)
    list = np.array(list)
    return list


def gene_mse_list(arr1, arr2):
    '''mse for each gene(column)
    arr [cells, genes]
    arr1: X
    arr2: H'''
    n = arr2.shape[1]
    list = []
    for j in range(n):
        mse = ((arr1[:, j] - arr2[:, j]) ** 2).mean()
        list.append(mse)
    list = np.array(list)
    return list


def gene_nz_rate_list(arr1):
    '''nz_rate for each gene(column)
    arr [cells, genes]
    arr1: X'''
    n = arr1.shape[1]
    list = []
    for j in range(n):
        nz_rate = np.count_nonzero(arr1[:, j]) / n
        list.append(nz_rate)
    list = np.array(list)
    return list


def gene_var_list(arr1):
    '''variation for each gene(column)
    arr [cells, genes]
    arr: X'''
    n = arr1.shape[1]
    list = []
    for j in range(n):
        var = np.var(arr1[:, j])
        list.append(var)
    list = np.array(list)
    return list


def gene_nzvar_list(arr1):
    '''variation for non-zero values in each gene(column)
    arr [cells, genes]
    arr: X'''
    n = arr1.shape[1]
    list = []
    for j in range(n):
        data = arr1[:, j]
        nz_data = data[data.nonzero()]
        var = np.var(nz_data)
        list.append(var)
    list = np.array(list)
    return list

