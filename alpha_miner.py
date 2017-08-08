import csv
import snakes.plugins
snakes.plugins.load('gv', 'snakes.nets', 'my_nets')
from my_nets import *

""" 
    AlphaMiner Algorithm Implementation
    based on ProM AlphaMiner
    https://svn.win.tue.nl/repos/prom/Packages/AlphaMiner/Trunk/src/
"""

event_log_path = 'event_log.csv'  # Path to event log
model = PetriNet("Process Model")


def get_traces():
    with open(event_log_path) as file:
        trace_list = list(csv.reader(file))
    return trace_list


def create_tl_set(log):
    # Create set of transitions Tl
    tl = set()
    [tl.add(state) for trace in log for state in trace]
    return tl


def create_ti_set(log):
    # Create set of initial transitions Ti
    ti = set()
    [ti.add(trace[0]) for trace in log]
    return ti


def create_to_set(log):
    # Create set of end transitions To
    to = set()
    [to.add(trace[-1]) for trace in log]
    return to


def create_task_sequence_set(log):
    # Create set of event/task sequences
    ts_set = set()
    for task in log:
        for i in range(0, len(task) - 1):
            ts_set.add((task[i], task[i + 1]))
    return ts_set


def create_causal_set(sequences):
    # Generate set of causal relations
    c_set = set()
    for sequence in sequences:
        if (sequence[0], sequence[1]) in sequences and (sequence[1], sequence[0]) not in sequences:
            c_set.add(sequence)
    return c_set


def create_parallel_set(sequences):
    # Generate set of parallel activities
    p_set = set()
    for sequence in sequences:
        if (sequence[0], sequence[1]) in sequences and (sequence[1], sequence[0]) in sequences:
            if (sequence[0], sequence[1]) not in p_set and (sequence[1], sequence[0]) not in p_set:
                p_set.add(sequence)
    return p_set


def create_non_direct_causal_set(trace_log, sequences):
    # Generate set of non direct causal relations
    ndc_set = set()
    for trace in trace_log:
        for activity in trace:
            for second_activity in trace:
                if (activity, second_activity) not in ndc_set and (second_activity, activity) not in ndc_set:
                    if (activity, second_activity) not in sequences and (second_activity, activity) not in sequences:
                        ndc_set.add((activity, second_activity))
    return ndc_set


def create_xl_set(causals_set, parallels_set):
    xl = causal_set.copy()
    for parallels in parallels_set:
        for causals in causals_set:
            if (causals[0], parallels[0]) in causals_set and (causals[0], parallels[1]) in causals_set:
                xl.add((causals[0], parallels))
            if (parallels[0], causals[1]) in causals_set and (parallels[1], causals[1]) in causals_set:
                xl.add((parallels, causals[1]))
    return xl


def create_yl_set(xl):
    yl = xl.copy()
    for x in xl:
        a = set(x[0])
        b = set(x[1])
        for y in xl:
            if a.issubset(y[0]) and b.issubset(y[1]):
                if x != y:
                    yl.discard(x)
                    break
    return yl


def clear_to_set(to_set, xl):
    to = to_set.copy()
    for t in to:
        for x in xl:
            if t == x[0]:
                to_set.discard(t)
    return to_set


def set_start_place():
    # Add initial place to model il
    model.add_place(Place('Start', [1]))
    for activity in init_activities:
        model.add_input('Start', activity, Variable('C'))


def set_end_place():
    # Add end place to model ol
    model.add_place(Place('End', [0]))
    for activity in end_activities:
        model.add_output('End', activity, Variable(activity))


def gen_transitions():
    # Create transitions in model
    for t in trace_set:
        model.add_transition(Transition(t))


def gen_places():
    # Generate places in Petri net
    i = 1
    for (a, b) in yl_set:
        model.add_place(Place(str(i), []))
        for activity in a:
            model.add_output(str(i), activity, Variable('C'))
        for activity in b:
            model.add_input(str(i), activity, Variable('C'))
        i += 1


traces = get_traces()  # Get list of traces from event log
trace_set = create_tl_set(traces)  # Set of Activities Tl
init_activities = create_ti_set(traces)  # Init Activity/es Ti
end_activities = create_to_set(traces)  # End Activity/es To
task_sequence_set = create_task_sequence_set(traces)  # Task sequences set
causal_set = create_causal_set(task_sequence_set)  # Causal relations between activities
parallel_set = create_parallel_set(task_sequence_set)  # Parallel activities
non_direct_causal_set = create_non_direct_causal_set(traces, task_sequence_set)  # Non direct causal relations
xl_set = create_xl_set(causal_set, parallel_set)  # Xl set
yl_set = create_yl_set(xl_set)  # Yl set
end_activities = clear_to_set(end_activities, xl_set)  # Check for deviations in To set

"""Petri net"""
gen_transitions()
set_start_place()
set_end_place()
gen_places()


net_file = "test.png"
model.draw(net_file)
