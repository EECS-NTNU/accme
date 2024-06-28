def accme_compute(aio_latency, num_aios, cores, parallelism):
    compute_cycles = (num_aios*aio_latency)/(min(cores,parallelism))
    return compute_cycles

def accme_memory(mem_latency, ext_data_movement, mem_overlap, bus_width):
    memory_cycles = mem_latency + (ext_data_movement*mem_overlap)/bus_width
    return memory_cycles

def accme_invocation(mem_latency, working_set_size, cores, mem_bandwidth):
    invocation_cycles = mem_latency + (working_set_size * (cores/2))/mem_bandwidth
    return invocation_cycles

def get_accme_cycles(parameters_df, index):

    aio_latency = parameters_df['AIO Latency'][index]
    num_aios = parameters_df['Num AIOs'][index]
    cores = parameters_df['Cores'][index]
    parallelism = parameters_df['Parallelism'][index]
    mem_latency = parameters_df['Mem Latency'][index]
    ext_data_movement = parameters_df['Ext Data Movement'][index]
    mem_overlap = parameters_df['Mem Overlap'][index]
    bus_width = parameters_df['Bus Width'][index]
    working_set_size = parameters_df['Working Set Size'][index]
    mem_bandwidth = parameters_df['Mem Bandwidth'][index]

    # Do not overcalculate for invocation.
    if cores > parallelism:
        cores = parallelism
    
    #print('cores',cores)
    compute_cycles = accme_compute(aio_latency, num_aios, cores, parallelism)
    memory_cycles = accme_memory(mem_latency, ext_data_movement, mem_overlap, bus_width)
    invokation_cycles = accme_invocation(mem_latency, working_set_size, cores, mem_bandwidth)

    return compute_cycles, memory_cycles, invokation_cycles
    #return compute_cycles + memory_cycles + invokation_cycles # Sum of all cycles

def generate_accme_cycles_column(input_df):
    accme_cycles = []
    for i in range(len(input_df)):
        accme_cycles.append(get_accme_cycles(input_df,i))
    
    input_df['AccMe Cycles'] = accme_cycles
    return input_df

def calculate_cycle_uncertainty_from_aio(df, aio_uncertainty, frequency):
    
    df['Time (s)'] = df['AccMe Cycles'] / frequency
    df['AIOs/Sec'] = df['Matrix Size'] / df['Time (s)']
    df['AIOs/Sec Upper'] = df['AIOs/Sec'] * aio_uncertainty
    df['AIOs/Sec Lower'] = df['AIOs/Sec'] / aio_uncertainty

    return df