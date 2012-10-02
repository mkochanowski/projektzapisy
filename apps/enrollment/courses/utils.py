# -*- coding: utf-8 -*-


def divide_queues_by_group(groups, queues):

    divide = {}

    for group in groups:
        divide[group.id] = {'group': group, 'students': []}

    for queue in queues:
        divide[queue.group_id].students.append(queue)

    return divide