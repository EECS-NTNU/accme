
import numpy as np
import pandas as pd
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib
import plotly.graph_objects as go

def accme_compute(aio_latency, num_aios, cores, parallelism):
    compute_cycles = (num_aios*aio_latency)/(min(cores,parallelism))
    return compute_cycles

def accme_memory(mem_latency, ext_data_movement, mem_overlap, bus_width, compute_cycles):
    
    bandlimit = False
   
    memory_cycles = mem_latency + (ext_data_movement*mem_overlap)/bus_width
    min_memory_cycles = mem_latency + (ext_data_movement)/bus_width # Operating at max bandwidth.

    # Special case for seeing the total memory cycles
    if mem_overlap == 1:
        return min_memory_cycles

    # Set memory cycles to those from the max bandwidth if necessary
    if min_memory_cycles > compute_cycles + memory_cycles:
        bandlimit = True
        memory_cycles = min_memory_cycles - compute_cycles
    
    return memory_cycles

def accme_invocation(mem_latency, working_set_size, cores, bus_width):
    invocation_cycles = mem_latency + (working_set_size * (cores/2))/bus_width
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
    memory_cycles = accme_memory(mem_latency, ext_data_movement, mem_overlap, bus_width, compute_cycles)
    invokation_cycles = accme_invocation(mem_latency, working_set_size, cores, bus_width)




    return [compute_cycles, memory_cycles, invokation_cycles]
    #return compute_cycles + memory_cycles + invokation_cycles # Sum of all cycles

def generate_accme_cycles_column(input_df):
    accme_cycles = []
    for i in range(len(input_df)):
        accme_cycles.append(get_accme_cycles(input_df,i))
    
    input_df['AccMe Cycles'] = accme_cycles
    return input_df


####################################
# Uncertainty Specific function
####################################
def calculate_cycle_uncertainty_from_aio(df, aio_uncertainty, frequency):
    
    #df['Time (s)'] = sum(df['AccMe Cycles']) / frequency
    time_list = []
    for i in range(len(df)):
        time_list.append(sum(df['AccMe Cycles'][i]) / frequency)
    df['Time (s)'] = time_list
    df['AIOs/Sec'] = df['Matrix Size'] / df['Time (s)']
    df['AIOs/Sec Upper'] = df['AIOs/Sec'] * aio_uncertainty
    df['AIOs/Sec Lower'] = df['AIOs/Sec'] / aio_uncertainty

    return df

def graph_cholesky_comparison(input_dfs, frequencies, aio_uncertainty):
    
    # Some Appearence Settings
    names = ['DSA','SCM','AMBIT','UPMEM']
    line_colors = ['blue','green','red','orange']
    fill_colors = ['rgba(0, 0, 255, 0.2)','rgba(0, 0, 255, 0.2)','rgba(255, 0, 0, 0.2)','rgba(250, 200, 0, 0.2)']
    color_opacity = 0.8
    line_thickness = 2
    axis_title_size = 24
    tick_label_size = 16
    legend_text_size = 18

    # Graph Performance Data
    fig = go.Figure()
    for i in range(len(input_dfs)):
        calculate_cycle_uncertainty_from_aio(input_dfs[i], aio_uncertainty, frequencies[i])
        fig.add_trace(go.Scatter(x=input_dfs[i]['Matrix Size'], y=input_dfs[i]['AIOs/Sec Upper'], fill='none', mode='lines', line = dict(color=line_colors[i], width=line_thickness, dash='dash'), opacity=color_opacity, name='DSA', showlegend=False))
        fig.add_trace(go.Scatter(x=input_dfs[i]['Matrix Size'], y=input_dfs[i]['AIOs/Sec Lower'], fill='tonexty', mode='lines', fillcolor=fill_colors[i], line = dict(color=line_colors[i], width=line_thickness, dash='dash'), opacity=color_opacity, name=(names[i]+'\u00B1'+str(aio_uncertainty)+'X AIO Latency')))
        fig.add_trace(go.Scatter(x=input_dfs[i]['Matrix Size'], y=input_dfs[i]['AIOs/Sec'], fill='none', mode='lines', line = dict(color=line_colors[i], width=line_thickness), opacity=color_opacity, name='DSA', showlegend=False))


    # Format Appearence
    fig.add_annotation(xref="paper", yref="paper", x=0.5, y=-0.35, text="Matrix Size", showarrow=False,
        font=dict(
            size=axis_title_size
        ),
    )
    fig.add_annotation(xref="paper", yref="paper", x=-0.17, y=0.5, text="AIOs / Sec", showarrow=False, textangle=-90,
        font=dict(
            size=axis_title_size
        ),
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            entrywidth=200,
            y=1.02,
            xanchor="left",
            x=-0.05,
            itemwidth=30,
            font=dict(size=legend_text_size),
            traceorder='normal'
            ),
        autosize=False,
        width=600,
        height=380,
    )
    fig.update_xaxes(type="log",tickvals=[2**i for i in range(12)])
    fig.update_yaxes(type="log", dtick=1)

    fig.update_layout(
        xaxis=dict(
            tickfont=dict(
                size=tick_label_size  # Set the tick font size for the x-axis
            )
        ),
        yaxis=dict(
            tickfont=dict(
                size=tick_label_size  # Set the tick font size for the y-axis
            )
        )
    )
    fig.show()


####################################
# SPA Stack Functions
####################################
def plot_spa_stacks(df, bus_width, config_choice):
  plt.rcParams.update({'font.size': 16})
  plt.rcParams['hatch.linewidth'] = 3.0
  fig, ax = plt.subplots(figsize=(5,3.5))
  x_pos = np.linspace(1,4,4)
  core_counts = [4,16,64,256]
  device_text_size = 14

  bar_width = 0.8
  core_labels = ['4c','16c','64c','256c']
  benchmark_label = 'CONV'

  memory_color = 'tab:orange'
  invoke_color = 'tab:red'
  compute_color = 'tab:blue'

  total = []
  compute = []
  unmasked = []
  invoke = []
  masked = []

  df['Bus Width'] = bus_width

  for i in range(len(core_counts)):
    df['Cores'] = core_counts[i]
    df['Mem Overlap'] = 0
    df = generate_accme_cycles_column(df)
    print(df['AccMe Cycles'][config_choice])
    total.append(sum(df['AccMe Cycles'][config_choice]))
    compute.append(df['AccMe Cycles'][config_choice][0])
    unmasked.append(df['AccMe Cycles'][config_choice][1])
    invoke.append(df['AccMe Cycles'][config_choice][2])
    df['Mem Overlap'] = 1
    df = generate_accme_cycles_column(df)
    masked.append(df['AccMe Cycles'][config_choice][1]-unmasked[-1])

  total = np.asarray(total)
  compute = np.asarray(compute)/total[0]
  unmasked = np.asarray(unmasked)/total[0]
  invoke = np.asarray(invoke)/total[0]
  masked = np.asarray(masked)/total[0]

  y1 = compute
  y2 = invoke
  y3 = unmasked
  y4 = masked

  plt.bar(x_pos[0:4], y2, bottom=y1+y3, color=invoke_color, width=bar_width, zorder=3)
  plt.bar(x_pos[0:4], y3, bottom=y4, color=memory_color, width=bar_width, zorder=3)
  plt.bar(x_pos[0:4], y1, color=compute_color, width=bar_width, zorder=3)
  plt.bar(x_pos[0:4], y4, hatch='///', bottom=(y1-y4), edgecolor=compute_color, color=memory_color, width=bar_width, zorder=3)
  plt.bar(x_pos[0:4], y1+y2+y3, edgecolor='black', color='none', lw=1.5, width=bar_width, zorder=3)

  # labels
  ax.tick_params(axis=u'both', which=u'both',length=0)
  plt.xticks(x_pos[0:4]+0.4, core_labels[0:4])
  plt.setp( ax.xaxis.get_majorticklabels(), rotation=30, ha="right" )


  plt.text(2.5, -0.22, benchmark_label, color='black', rotation=0, ha="center", va="top", fontweight='bold', fontsize=device_text_size)

  plt.ylabel('Normalized SPA Stacks')
  plt.ylim(0,1.1)
  plt.xlim(0,5)

  plt.legend(
                  [
                  'Invocation',
                  'Memory',
                  'Compute',
                  'Masked Memory',
                ],
      ncol=2,
      loc='upper center',
      bbox_to_anchor=(0.485, 1.40),
      )
  plt.grid()
  plt.show()

####################################
# Energy analysis function
####################################
def accme_ee_cycles(df, cores, config_choice):

    df['Mem Overlap'] = 1 # Set mem overlap so that AccMe returns full mem cycles (Assume non are hidden) 
    df['Cores'] = cores
    df = generate_accme_cycles_column(df)
    compute_cycles = df['AccMe Cycles'][config_choice][0]
    memory_cycles = df['AccMe Cycles'][config_choice][1] # Independent of whether or not they are hidden.

    return compute_cycles, memory_cycles


def get_accme_ee_range(df, cores_array, frequency, core_dpower, core_spower, mem_dpower, mem_spower, config_choice):
    
    aios_per_joule_array = []
    
    for i in range(len(cores_array)):
        cores = cores_array[i]
        compute_cycles, memory_cycles = accme_ee_cycles(df, cores_array[i], config_choice)
        time = max(compute_cycles,memory_cycles) / frequency        

        # Caculate compute static energy
        compute_static_energy = time * core_spower * cores_array[i]
        
        # See if cores are bottlenecked by memory
        core_scaler = compute_cycles / memory_cycles
        effective_cores = cores_array[i] * core_scaler
        if effective_cores < cores_array[i]:
            cores = effective_cores
        
        # Calculate compute dynamic energy
        compute_dynamic_energy = time * core_dpower * cores
        # Memory static energy
        memory_static_energy = time * mem_spower

        # Memory dynamic energy
        memory_dynamic_energy = df['Ext Data Movement'][config_choice] * mem_dpower
        
        # AIO efficiency
        total_energy = compute_static_energy + compute_dynamic_energy + memory_static_energy + memory_dynamic_energy
        aios_per_joule = df['Image Pixels'][config_choice] / total_energy
        aios_per_joule = df['Num AIOs'][config_choice] / total_energy
        aios_per_joule_array.append(aios_per_joule)
    
    return aios_per_joule_array