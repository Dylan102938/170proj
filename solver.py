from parse import read_input_file, write_output_file
from operator import itemgetter
from Task import T
import os
import sys
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import time

cache = {}


def solve(tasks, currTime):
    tasks_tuple = tuple(tasks)

    if (tasks_tuple, currTime) in cache:
        return cache[(tasks_tuple, currTime)]

    if len(tasks) == 0 or currTime >= T:
        return 0, [], []

    # take job
    all_configs = []
    past_duration = currTime + tasks[0].get_duration()
    if past_duration <= T:
        remaining_profit, remaining_list, remaining_not_taken = solve(tasks[1:], past_duration)
        take_job_profit = remaining_profit + tasks[0].get_late_benefit(past_duration - tasks[0].get_deadline())
        take_job_list = [tasks[0]] + remaining_list
        take_job_not_taken = remaining_not_taken
    else:
        take_job_profit, take_job_list, take_job_not_taken = 0, [], []

    all_configs.append((take_job_profit, take_job_list, take_job_not_taken))

    # don't take job
    no_job_profit, no_job_list, no_job_not_taken = solve(tasks[1:], currTime)
    all_configs.append((no_job_profit, no_job_list, no_job_not_taken + [tasks[0]]))

    cache[(tuple(tasks), currTime)] = max(all_configs, key=itemgetter(0))
    return cache[(tuple(tasks), currTime)]


def solver(tasks):
    return solve(tasks, 0)


# prints out score of output_file
def bad_bitch(input_file, output_file):
    tasks = read_input_file(input_file)
    task_dict = {}
    for task in tasks:
        task_dict[task.get_task_id()] = task

    profit = 0
    time = 0
    with open(output_file) as f:
        lines = f.readlines()
        lines = [int(x) for x in lines]

        with open(output_file + 'd', 'w') as f2:
            for task_id in lines:
                task = task_dict[task_id]
                time += task.get_duration()
                f2.write(str(task) + ' currTime ' + str(time) + '\n')
                profit += task.get_late_benefit(time - task.get_deadline(), time)
            f2.close()
        f.close()

    return profit


def switch(tasks, score):
    i = 0
    time = tasks[0].get_duration()
    index = None
    time_index = None

    while i < len(tasks):
        if i == 0:
            if index != None:
                i = index
                time = time_index
                index = None
                time_index = None
            else:
                i += 1
                time += tasks[1].get_duration()
            continue

        else:
            task = tasks[i]
            prev_task = tasks[i-1]

            task_benefit = task.get_late_benefit(time - task.get_deadline(), time)
            prev_task_benefit = prev_task.get_late_benefit(time - task.get_duration() - prev_task.get_deadline(), time - task.get_duration())
            new_task_benefit = task.get_late_benefit(time - prev_task.get_duration() - task.get_deadline(), time - prev_task.get_duration())
            new_prev_task_benefit = prev_task.get_late_benefit(time - prev_task.get_deadline(), time)

            new_score = score - task_benefit - prev_task_benefit + new_task_benefit + new_prev_task_benefit
            all_late = not (task_benefit or prev_task_benefit or new_task_benefit or new_prev_task_benefit)

            theoretical_gain = 0
            if all_late:
                th_task_benefit = task.get_late_benefit(time - task.get_deadline())
                th_prev_task_benefit = prev_task.get_late_benefit(time - task.get_duration() - prev_task.get_deadline())
                th_new_task_benefit = task.get_late_benefit(time - prev_task.get_duration() - task.get_deadline())
                th_new_prev_task_benefit = prev_task.get_late_benefit(time - prev_task.get_deadline())
                theoretical_gain += th_new_task_benefit + th_new_prev_task_benefit - th_task_benefit - th_prev_task_benefit

            if new_score - score > 0.0000000001 or (all_late and theoretical_gain > 0.0000000001):
                if index == None:
                    index = i
                    time_index = time

                temp = task
                tasks[i] = tasks[i-1]
                tasks[i-1] = task
                time -= tasks[i].get_duration()
                score = new_score

                i -= 1
                continue

            if index != None:
                i = index
                time = time_index
                index = None
                time_index = None
            else:
                i += 1
                if i < len(tasks):
                    time += tasks[i].get_duration()
                else:
                    time += tasks[i-1].get_duration()


def solve_by(tasks, function):
    global cache

    tasks.sort(key=function)
    score, output, not_taken = solver(tasks)
    cache = {}

    not_taken.sort(key=lambda x: x.get_duration())
    for x in not_taken:
        potential_score = score
        potential_output = output
        for i in range(1, len(output)+1):
            new_output = output[:i] + [x] + output[i:]
            new_score = compute_score(new_output)
            if new_score > potential_score:
                potential_score = new_score
                potential_output = new_output

        score = potential_score
        output = potential_output

    return score, output


def compute_score(output):
    score = 0
    currTime = 0
    for x in output:
        currTime += x.get_duration()
        score += x.get_late_benefit(currTime-x.get_deadline(), currTime)

    return score


def post_process_output(output):
    currTime = 0
    final = []
    score = 0
    for x in output:
        if currTime + x.get_duration() <= T:
            final.append(x.get_task_id())
            currTime += x.get_duration()
            score += x.get_late_benefit(currTime - x.get_deadline())
        else:
            break

    return score, final


if __name__ == '__main__':
    # sizes = ['small', 'medium', 'large']
    # actual_size = [sizes[int(sys.argv[1])]]
    #
    # for size in os.listdir('inputs/'):
    #     if size not in actual_size:
    #         continue
    #     for input_file in os.listdir('inputs/{}/'.format(size)):
    #         if size not in input_file:
    #             continue
    #
    #         input_path = 'inputs/{}/{}'.format(size, input_file)
    #         output_path = 'outputs/{}/{}.out'.format(size, input_file[:-3])
    #         print(input_path, output_path)

            input_paths = ['inputs/large/large-79.in', 'inputs/small/small-245.in', 'inputs/small/small-254.in', 'inputs/small/small-267.in']
            output_paths = ['test_file.out', 'test_file2.out', 'test_file3.out', 'test_file3.out']

            for i in range(len(input_paths)):

                input_path = input_paths[i]
                output_path = output_paths[i]
                print(input_path, output_path)

                tasks = read_input_file(input_path)

                deadline_score, deadline_output = solve_by(tasks, lambda x: x.get_deadline())
                duration_score, duration_output = solve_by(tasks, lambda x: x.get_duration())
                duration_profit_score, duration_profit_output = solve_by(tasks, lambda x: x.get_duration()/x.get_max_benefit())
                deadline_profit_score, deadline_profit_output = solve_by(tasks, lambda x: x.get_deadline()/x.get_max_benefit())

                switch(deadline_output, deadline_score)
                switch(duration_output, duration_score)
                switch(duration_profit_output, duration_profit_score)
                switch(deadline_profit_output, deadline_profit_score)

                configs = list()
                configs.append(post_process_output(deadline_output))
                configs.append(post_process_output(duration_output))
                configs.append(post_process_output(duration_profit_output))
                configs.append(post_process_output(deadline_profit_output))

                print(configs[0][0], configs[1][0], configs[2][0], configs[3][0], configs[4][0])
                final_list = max(configs, key=itemgetter(0))

                final_list = final_list[1]

                write_output_file(output_path, final_list)
                print(bad_bitch(input_path, output_path))
