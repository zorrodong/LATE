import os
import sys
import time
home = os.environ['HOME']

# DATA
# BMB.MAGIC
fname_input = 'input.sub.hd5'
name_input = 'mouse_brain_sample'
ori_input = 'cell_row'
transformation_input = 'as_is'  # as_is/log/rpm_log/exp_rpm_log

fname_ground_truth = fname_input
name_ground_truth = name_input
ori_ground_truth = ori_input  # cell_row/gene_row
transformation_ground_truth = transformation_input  # as_is/log/rpm_log/exp_rpm_log

# # Mouse Brain Small
# fname_input = home + '/imputation/data/10x_mouse_brain_1.3M/20k/' \
#               'mouse_brain.10kg.h5'
# genome_input = 'mm10'  # only for 10x_genomics sparse matrix h5 data
# name_input = 'test_mouse_brain_sub20k'
# ori_input = 'gene_row'  # cell_row/gene_row
# transformation_input = 'log'  # as_is/log/rpm_log/exp_rpm_log
#
# fname_ground_truth = fname_input
# name_ground_truth = name_input
# ori_ground_truth = ori_input  # cell_row/gene_row
# transformation_ground_truth = transformation_input  # as_is/log/rpm_log/exp_rpm_log

# DATA SPLIT PROPORTION
[a, b, c] = [0.7, 0.15, 0.15]  # train/valid/test

# MODE
mse_mode = 'mse_nz'  # mse, mse_nz
mode = 'late'  # pre-training, translate, late, impute

# Automated Process
if mode == 'pre-training':
    # step1/rand_init for pre-training on reference
    stage = 'step1'
    run_flag = 'rand_init'
elif mode == 'translate':
    # step2/load_saved from step1, for transfer learning
    stage = 'step2'  # step1/step2 (not others)
    run_flag = 'load_saved'  # rand_init/load_saved
elif mode == 'late':
    # step2/rand_init for one step training
    stage = 'step2'
    run_flag = 'rand_init'
elif mode == 'impute':
    # step2/load_saved/learning_rate=0, just impute and output
    stage = 'impute'
    run_flag = 'impute'
else:
    raise Exception('mode err')

# HYPER PARAMETERS
L = 5  # 3/5/7
l = L//2
n_hidden_1 = 800  # 3L
n_hidden_2 = 400  # 5L
# n_hidden_3 = 200 # 7L

pIn = 0.8  # 0.8
pHidden = 0.5  # 0.5
reg_coef = 0.0  # reg3=1e-2, can set to 0.0

sd = 1e-3  # for rand_init of weights. 3-7L:1e-3, 9L:1e-4
if run_flag == 'rand_init':
    learning_rate = 3e-4  # step1: 3e-4 for 3-7L, 3e-5 for 9L
elif run_flag == 'load_saved':
    learning_rate = 3e-5  # step2: 3e-5 for 3-7L, 3e-6 for 9L
elif run_flag == 'impute':
    learning_rate = 0.0

batch_size = int(256)  # mini-batch size for training
sample_size = int(1000)  # sample_size for learning curve, slow output
large_size = int(1e5)  # if num-cells larger than this, use slow but robust method
#  for imputation and output

max_training_epochs = int(10)  # num_mini_batch / (training_size/batch_size)
display_step = int(5)  # interval on learning curve, 20 displays recommended
snapshot_step = int(50)  # interval of saving session, saving imputation
patience = int(3)  # early stop patience epochs, just print warning, no real stop

# For development usage #
seed_tf = 3
test_flag = False  # [True, False]
if test_flag:
    max_training_epochs = 10 # 3L:100, 5L:1000, 7L:1000, 9L:3000
    display_step = 1  # interval on learning curve
    snapshot_step = 5  # interval of saving session, imputation
    m = 1000
    n = 300
    sample_size = int(240)
    print('in test mode\n',
          'num-genes set to {}, num-cells set to {}\n'.format(n, m),
          'sample size set to {}'.format(sample_size))

# PRINT PARAMETERS
print('\nData:')
print('fname_input:', fname_input)
print('name_input:', name_input)
print('ori_input:', ori_input)
print('transformation_input:', transformation_input)
print('data split: [{}/{}/{}]'.format(a, b, c))

print('\nParameters:')
print('mode:', mode)
print('mse_mode:', mse_mode)
print('stage:', stage)
print('init:', run_flag)
print('test_mode:', test_flag)
print('{}L'.format(L))
for l_tmp in range(1, l+1):
  print("n_hidden{}: {}".format(l_tmp, eval('n_hidden_'+str(l_tmp))))

print('learning_rate:', learning_rate)
print('reg_coef:', reg_coef)
print('batch_size:', batch_size)
print('sample_zie: ', sample_size)
print('pIn:', pIn)
print('pHidden:', pHidden)
print('max_training_epochs:', max_training_epochs)
print('display_step', display_step)
print('snapshot_step', snapshot_step)
print()


# FOR RESULT ANALYSIS
if 'result_analysis.py' in sys.argv[0]:
    fname_imputation = 'imputation.sub.hd5'
    name_imputation = '{}_({})'.format(name_input, mode)
    ori_imputation = 'cell_row'  # gene_row/cell_row
    transformation_imputation = 'as_is'
    tag = 'Late'  # folder name for analysis results

    pair_list = [
        # E18 Mouse Brain (renyi input)
        ['ENSMUSG00000008683', 'ENSMUSG00000040010'],
        ['ENSMUSG00000064351', 'ENSMUSG00000068523'],
        ['ENSMUSG00000079523', 'ENSMUSG00000068523'],
        ['ENSMUSG00000028416', 'ENSMUSG00000040010'],
        ['ENSMUSG00000036478', 'ENSMUSG00000001300'],
        ['ENSMUSG00000020831', 'ENSMUSG00000074457'],
        ['ENSMUSG00000018042', 'ENSMUSG00000055024'],
        ['ENSMUSG00000049775', 'ENSMUSG00000020142'],
        ['ENSMUSG00000052305', 'ENSMUSG00000029536'],
        ['ENSMUSG00000059070', 'ENSMUSG00000022983'],
        ['ENSMUSG00000061477', 'ENSMUSG00000022983'],
        ['ENSMUSG00000079523', 'ENSMUSG00000054808'],

        # (dCov input)
        ['ENSMUSG00000072235', 'ENSMUSG00000026385'],
        ['ENSMUSG00000019874', 'ENSMUSG00000002985'],
        ['ENSMUSG00000019874', 'ENSMUSG00000028364'],
        ['ENSMUSG00000019874', 'ENSMUSG00000068523'],
        ['ENSMUSG00000063632', 'ENSMUSG00000031760'],
        ['ENSMUSG00000072235', 'ENSMUSG00000069919'],
        ['ENSMUSG00000092341', 'ENSMUSG00000073940'],
        # (renyi imputation)


    ]

    gene_list = [gene for pair in pair_list for gene in pair]

    print('''
    In result_analysis mode:
    fname_imputation: {}
    name_imputation: {}
    ori_imputation: {}
    trannsformation_imputation: {}
    pair_list: {}
    '''.format(fname_imputation, name_imputation,
               ori_imputation, transformation_imputation,
               pair_list))
    time.sleep(1)
