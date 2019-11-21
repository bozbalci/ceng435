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
    experiment_1 = './experiment_1/network-d/end_to_end_costs.json'
    experiment_2 = './experiment_2/network-d/end_to_end_costs.json'
    experiment_3 = './experiment_3/network-d/end_to_end_costs.json'

    with open(experiment_1, 'r') as infile_1:
        data_1 = json.load(infile_1)
    with open(experiment_2, 'r') as infile_2:
        data_2 = json.load(infile_2)
    with open(experiment_3, 'r') as infile_3:
        data_3 = json.load(infile_3)

    mean_1, ci_start_1, ci_end_1 = mean_confidence_interval(data_1)
    mean_2, ci_start_2, ci_end_2 = mean_confidence_interval(data_2)
    mean_3, ci_start_3, ci_end_3 = mean_confidence_interval(data_3)

    lines = []
    lines.append('Experiment 1')
    lines.append('============')
    lines.append(f'Mean: {mean_1}')
    lines.append(f'Confidence Interval: ({ci_start_1}, {ci_end_1})')
    lines.append('')
    lines.append('Experiment 2')
    lines.append('============')
    lines.append(f'Mean: {mean_2}')
    lines.append(f'Confidence Interval: ({ci_start_2}, {ci_end_2})')
    lines.append('')
    lines.append('Experiment 3')
    lines.append('============')
    lines.append(f'Mean: {mean_3}')
    lines.append(f'Confidence Interval: ({ci_start_3}, {ci_end_3})')
    lines.append('')

    with open('stats.txt', 'w') as outfile:
        outfile.write('\n'.join(lines))

    x_axis = ('20', '40', '50')
    y_pos = np.arange(len(x_axis))
    y_axis = [mean_1*1000, mean_2*1000, mean_3*1000]
    plt.bar(y_pos, y_axis, align='center', alpha=0.75)
    plt.xticks(y_pos, x_axis)
    plt.xlabel('Network emulation delay (ms)')
    plt.ylabel('End-to-end delay (ms)')
    plt.savefig('chart.png', bbox_inches='tight')
