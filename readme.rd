# Droneways - Building new paths in the sky

This repository have all the scripts and files from the PhD thesis entitled _Droneways - Building new paths in the skies_.

Down below you will find the instructions to navigate through the files and to execute the scripts to generate the droneways.

## Repository structure

In the root of the repository are all the python scripts created for this work. The scripts were developed using oriented object programing and runs on from a terminal.

Also, in the root you can find the thesis in PDF format.

In the folder _graphs_ you will find the three graphs used in the research. The graphs are in graph-tool format (gt extension). You can use any other graph, since it is in this format.

In the folders manhattan, paris, and uruapan, you can find the resulting files for each location, specifically calculated for the work results: 
- the plots comparing the two heuristics (Fishbone and Spiderweb);
- the serialized dictionaries containing the efficiency calculated for each droneways;
- CSV files containing all the calculated properties for each droneways;
- in the pictures folder, the images of the resulting droneways maps can be found, in eps format;
- in the graphs folder, the graphs of the resulting droneways can be found, in gt format.

## Executing the scripts

If you want to execute the scripts, the easiest way is using docker, as compiling the graph-tool takes a very long time. 

Clone this repository in your source folder then follow the steps below. It is highly recommended to use Linux operating system.

### Preparing the environment using Docker

After cloning the repository, open a terminal and navigate to the folder of the cloned project. 

Build the image in your computer, using the command below.

`docker build -t [docker_image_name] .`

Change [docker_image_name] to the name you want for the container. This will create the container using the configurations inside  the Dockerfile.

After the container is created, you can connect to the docker using bash, with the command below as root:

`docker run -it -u root -v /source/folder/host/machine:/destination/folder/in/docker/ -w /home/user [docker_image_name] bash`

Remember to replace source and destination folders accordingly. The source folder is where you must put this repository scripts. The destination folder is where you want to map the scripts inside the docker container.

### Preparing the environment directly in the operational system

It is recommended to use Arch Linux. The scripts were not tested in other O.S.

Clone this repository in the destination folder. If you are on Arch Linux, execute the following command:

`sh install.sh`

This will install the necessary libraries to execute the scripts. The graph-tool library is most written on C language, so it takes a long time compiling it (it took 5 hours using a Ryzen 5 processor with 16Gb of RAM).

### Executing the scripts

Navigate to the folder where the python scripts are located. If you are using docker, you must see a folder named `src`. The scripts shoud be inside it, if mapped correctly.
 
Run the command below:

`python Main.py [path_of_the_map.gt] [destination/folder]`

Change `[path_of_the_map.gt]`to the graph in gt (graph-tool) format full path. In the repository you can find a folder called maps, which contains the three maps used in the thesis result, from Manhattan, Paris and Uruapan cities. 
Change `[destination/folder]`to the folder you want the resulting droneways to be stored. It is not recommended to use the same folder for two different maps.

You must see an options menu like below:

```
Select option: 
1. Execute fishbone heuristics 
2. Execute spiderweb heuristics
3. Calculate properties
4. Compare strategies and generate plot
Choose any other number to exit
```

The first two options execute each heuristics and creates the droneways graphs in eps and gt format. Choosing any of them will ask 3 values:

`Start` is the initial number of paths that the fist droneway is going to have.
`Iterations`is the number of droneways that will be created. If you choose 1, only one will be created.
`Step` is the number of new paths that will be added to `Start` on each `Iteration`.

For example, if you type `10`, `10`, `10`, the first droneway will have 10 paths, the second one, 20 pahts, then 30 pahts, until the 100 paths droneway. 

The graphs will be saved into the `[destination/folder]`.

The options `3` and `4` must be selected only after the Fishbone and Spiderweb droneways for the selected map were found by the two first options. 

The option `3. Calculate properties` will calculate the graph properties and store them into pickle file types, to be used by Python, and into `csv` files, to be visualized on a compatible spreadsheet software.

Finally, the option `4. Compare heuristics and generate plot` compare the strategies and generate the plots found in the Results and Discussion chapter of the thesis.
