def solve(currentTime, not_taken_late, not_taken_early, tasks):
    # not_taken_late stores youngest->oldest (i.e. most recently expired job on top)
    # not_taken_early stores oldest->youngest (i.e. most likely to expire job on top)

    tasks_tup = tuple(tasks)
    nt_late_tup = tuple(not_taken_late)
    nt_early_tup = tuple(not_taken_early)

    if (currentTime, nt_late_tup, nt_early_tup, tasks_tup) in cache:
        return cache[(currentTime, nt_late_tup, nt_early_tup, tasks_tup)]

    if (len(tasks) == 0 && len(not_taken_late) == 0 && len(not_taken_early) == 0)
        return 0, []

    all_configs = []
    past_duration = currentTime + tasks[0].get_duration()

    for job in not_taken_early:
        if past_duration > job.get_deadline():
            not_taken_late = job + not_taken_late
            not_taken_early = not_taken_early[1:]

    # take job
    if past_duration <= T:
        remaining_profit, remaining_list, remaining_not_taken = solve(past_duration, not_taken_late, not_taken_early, tasks[1:])
        take_job_profit = remaining_profit + tasks[0].get_late_benefit(past_duration - tasks[0].get_deadline())
        take_job_list = [tasks[0]] + remaining_list
        take_job_not_taken = remaining_not_taken

        all_configs.append(take_job_profit, take_job_list, take_job_not_taken)

    # don't take job
    if len(tasks) > 0:
        if past_duration > tasks[0].get_deadline():
            no_job_profit, no_job_list, no_job_not_taken = solve(past_duration, not_taken_late + tasks[0], not_taken_early, tasks[1:])
        else:
            no_job_profit, no_job_list, no_job_not_taken = solve(past_duration, not_taken_late, tasks[0] + not_taken_early, tasks[1:])

        all_configs.append(no_job_profit, no_job_list, no_job_not_taken + [tasks[0]])

    # take an expired job
    if len(not_taken_late) > 0:
        new_time = currentTime + not_taken_late[0].get_duration()
        remaining_profit, remaining_list, remaining_not_taken = solve(new_time, not_taken_late[1:], not_taken_early, tasks[1:])


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
