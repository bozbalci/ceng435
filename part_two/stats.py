import json

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats


def mean_confidence_interval(data, confidence=0.95):
    """
    Copied from https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
    """
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
    return m, m - h, m + h


if __name__ == '__main__':
    exp1_5ms = 'experiment_results/exp1_5ms.json'
    exp1_15ms = 'experiment_results/exp1_15ms.json'
    exp1_38ms = 'experiment_results/exp1_38ms.json'

    with open(exp1_5ms, 'r') as infile:
        exp1_5ms_data = json.load(infile)
    with open(exp1_15ms, 'r') as infile:
        exp1_15ms_data = json.load(infile)
    with open(exp1_38ms, 'r') as infile:
        exp1_38ms_data = json.load(infile)

    mean_1, ci_start_1, ci_end_1 = mean_confidence_interval(exp1_5ms_data)
    mean_2, ci_start_2, ci_end_2 = mean_confidence_interval(exp1_15ms_data)
    mean_3, ci_start_3, ci_end_3 = mean_confidence_interval(exp1_38ms_data)

    lines = []
    lines.append('EXP-1 5ms')
    lines.append('=========')
    lines.append(f'Mean: {mean_1}')
    lines.append(f'Confidence Interval: ({ci_start_1}, {ci_end_1})')
    lines.append('')
    lines.append('EXP-1 15ms')
    lines.append('===========')
    lines.append(f'Mean: {mean_2}')
    lines.append(f'Confidence Interval: ({ci_start_2}, {ci_end_2})')
    lines.append('')
    lines.append('EXP-1 38ms')
    lines.append('===========')
    lines.append(f'Mean: {mean_3}')
    lines.append(f'Confidence Interval: ({ci_start_3}, {ci_end_3})')
    lines.append('')

    with open('stats.txt', 'w') as outfile:
        outfile.write('\n'.join(lines))

    x_axis = ('5', '15', '38')
    y_pos = np.arange(len(x_axis))
    y_axis = [mean_1, mean_2, mean_3]
    plt.bar(y_pos, y_axis, align='center', alpha=0.75)
    plt.xticks(y_pos, x_axis)
    plt.xlabel('Network emulation loss (%)')
    plt.ylabel('File transfer time (s)')
    plt.savefig('chart.png', bbox_inches='tight')
