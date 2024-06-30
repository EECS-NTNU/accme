# AccMe Examples:

AccMe is a simple performance model which leverages the AIO abstraction for comparing diverse accelerators. 

To learn more about the details of AIO and AccMe please refer to the original paper:
AIO: An Abstraction for Performance Analysis Across Diverse Accelerator Architectures

This page provides jupyter notebook examples to demonstrate different ways that AIO+AccMe can be used for early-stage analysis of architectures.

`example1-uncertainty.ipynb`: This example focuses on comparing device performances while working with high uncertainties for AIO latency. This example allows users to adjust the AIO uncertainty, as well as the clock frequency of each considered accelerator. 

`example2-spa-stacks.ipynb`: This example demonstrates the use of AccMe SPA stacks to expore performance saturation. This example allows the user to change the AIO, as well as the input size. It also allows for changing the memory bandwidth of the device.

`example3-energy-analysis.ipynb`: This example couples AIO+AccMe to a simple energy model, where both the compute and memory systems of the accelerator have both static and dynamic power components. The user may adjust each of these power components to see how the energy efficiency scaling of the device changes depending on the AIO being executed.


Installation Notes:
These examples use a variety of python libraries to function correctly.


Example repo setup using Anaconda:

`clone https://github.com/EECS-NTNU/accme.git`<br />
`cd accme`<br />
`conda create --name accme_examples python=3.12`<br />
`conda activate accme_examples`<br />
`conda install numpy`<br />
`conda install pandas`<br />
`conda install jupyterlab`<br />
`conda install ipywidgets`<br />
`conda install matplotlib`<br />
`conda install plotly`<br />
