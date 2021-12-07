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
