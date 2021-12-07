from parse import read_input_file, write_output_file
from operator import itemgetter
from Task import T
import os
import sys
import heapq

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

        for task_id in lines:
            task = task_dict[task_id]
            time += task.get_duration()
            profit += task.get_late_benefit(time - task.get_deadline(), time)
        f.close()

    return profit


def switch(tasks, score):
    i = 0
    time = tasks[0].get_duration()
    index = None
    time_index = None

    while (i < len(tasks)):
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

            # task_benefit = task.get_late_benefit(time - task.get_deadline())
            # prev_task_benefit = prev_task.get_late_benefit(time - task.get_duration() - prev_task.get_deadline())
            # new_task_benefit = task.get_late_benefit(time - prev_task.get_duration() - task.get_deadline())
            # new_prev_task_benefit = prev_task.get_late_benefit(time - prev_task.get_deadline())

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

            if new_score - score > 0.00000000001 or (all_late and theoretical_gain > 0.00000000001):
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


def mesh(currentTime, already_seen, output1, output2):
    output1_tup = tuple(output1)
    output2_tup = tuple(output2)
    already_seen_tup = tuple(already_seen)

    if (currentTime, already_seen_tup, output1_tup, output2_tup) in cache:
        return cache[(currentTime, already_seen_tup, output1_tup, output2_tup)]

    if output1 == []:
        score = 0
        time = currentTime
        final_list = []
        for x in output2:
            if x.get_task_id() not in already_seen:
                time += x.get_duration()
                score += x.get_late_benefit(time - x.get_deadline(), time)
                final_list.append(x)

        return score, final_list

    if output2 == []:
        score = 0
        time = currentTime
        final_list = []
        for x in output1:
            if x.get_task_id() not in already_seen:
                time += x.get_duration()
                score += x.get_late_benefit(time - x.get_deadline(), time)
                final_list.append(x)

        return score, final_list

    if currentTime > T:
        return 0, []


    score1, score2 = 0, 0
    output1_list, output2_list = [], []

    # with output 1
    if output1[0].get_task_id() not in already_seen:
        time = currentTime + output1[0].get_duration()
        already_seen.add(output1[0].get_task_id())

        remaining = mesh(time, already_seen, output1[1:], output2)
        score1 = output1[0].get_late_benefit(time - output1[0].get_deadline()) + remaining[0]
        output1_list = [output1[0]] + remaining[1]

        already_seen.remove(output1[0].get_task_id())

    # with output2
    if output2[0].get_task_id() not in already_seen:
        time = currentTime + output2[0].get_duration()
        already_seen.add(output2[0].get_task_id())

        remaining = mesh(time, already_seen, output1, output2[1:])
        score2 = output2[0].get_late_benefit(time - output2[0].get_deadline()) + remaining[0]
        output2_list = [output2[0]] + remaining[1]

        already_seen.remove(output2[0].get_task_id())

    if score1 > score2:
        cache[(currentTime, already_seen_tup, output1_tup, output2_tup)] = score1, output1_list
    else:
        cache[(currentTime, already_seen_tup, output1_tup, output2_tup)] = score2, output2_list

    return cache[(currentTime, already_seen_tup, output1_tup, output2_tup)]


if __name__ == '__main__':
            count = 0
    # for size in os.listdir('inputs/'):
    #     if size not in ['small']:
    #         continue
    #     for input_file in os.listdir('inputs/{}/'.format(size)):
    #         if size not in input_file:
    #             continue
    #
    #         input_path = 'inputs/{}/{}'.format(size, input_file)
    #         output_path = 'outputs/{}/{}.out'.format(size, input_file[:-3])
            input_path = 'inputs/small/small-65.in'
            output_path = 'test_file.out'
            print(input_path, output_path)

            tasks = read_input_file(input_path)

            tasks.sort(key=lambda x: x.get_deadline())
            deadline_score, deadline_output, deadline_not_taken = solver(tasks)
            cache = {}

            current_time = sum([x.get_duration() for x in deadline_output])
            deadline_not_taken.sort(key=lambda x: x.get_duration())
            for x in deadline_not_taken:
                current_time += x.get_duration()
                deadline_score += x.get_late_benefit(current_time - x.get_deadline(), current_time)

            tasks.sort(key=lambda x: x.get_duration()/x.get_max_benefit())
            duration_score, duration_output, duration_not_taken = solver(tasks)
            cache = {}

            current_time = sum([x.get_duration() for x in duration_output])
            duration_not_taken.sort(key=lambda x: x.get_deadline(), reverse=True)
            for x in duration_not_taken:
                current_time += x.get_duration()
                duration_score += x.get_late_benefit(current_time - x.get_deadline(), current_time)

            deadline_output += deadline_not_taken
            duration_output += duration_not_taken

            switch(deadline_output, deadline_score)
            switch(duration_output, duration_score)

            configs = []

            current_time = 0
            deadline_final = []
            final_deadline_score = 0
            for x in deadline_output:
                if current_time + x.get_duration() <= T:
                    deadline_final.append(x.get_task_id())
                    current_time += x.get_duration()
                    final_deadline_score += x.get_late_benefit(current_time - x.get_deadline())
                else:
                    break

            configs.append((final_deadline_score, deadline_final))

            current_time = 0
            duration_final = []
            final_duration_score = 0
            for x in duration_output:
                if current_time + x.get_duration() <= T:
                    duration_final.append(x.get_task_id())
                    current_time += x.get_duration()
                    final_duration_score += x.get_late_benefit(current_time - x.get_deadline())
                else:
                    break

            configs.append((final_duration_score, duration_final))

            current_time = 0
            mesh_output = mesh(0, set(), deadline_output, duration_output)[1]
            cache = {}
            mesh_final = []
            final_mesh_score = 0
            for x in mesh_output:
                if current_time + x.get_duration() <= T:
                    mesh_final.append(x.get_task_id())
                    current_time += x.get_duration()
                    final_mesh_score += x.get_late_benefit(current_time - x.get_deadline())
                else:
                    break

            configs.append((final_mesh_score, mesh_final))

            print(configs[0][0], configs[1][0], configs[2][0])
            final_list = (max(configs, key=itemgetter(0)))

            if final_list[0] == final_mesh_score:
                count += 1

            final_list = final_list[1]

            write_output_file(output_path, final_list)
            # print(bad_bitch(input_path, output_path))
            print(count)
