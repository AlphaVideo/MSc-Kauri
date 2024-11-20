# Rotating Kauri


Kauri is a BFT communication abstraction that leverages dissemination/aggregation trees for load balancing and scalability while avoiding the main limitations of previous tree-based solutions, namely, poor throughput due to additional round latency and the collaps eof the tree to a star even in runs with few faults
while at the same time avoiding the bottleneck of star based solutions.

This version enables the original Kauri (https://github.com/Raycoms/Kauri-Public) to instead take on a rotating leader approach with an optimised reconfiguration process.


## Features

Kauri extends the publicly available implementation of HotStuff (https://github.com/hot-stuff/libhotstuff) with the following additions:

- Tree Based Dissemination and Aggregation equally balancing the message propagation and processing load among the internal nodes in the tree.

- BLS Signatures: Through BLS signatures the bandwidth load of the system is reduced significantly and signatures may be aggregated at each internal node.

- Extra Pipelining: Additional pipelining allows to offset the inherent latency cost of trees, allowing the system to perform significantly better even in high latency settings.

Additionally, this rotating leader version of Kauri has the following properties:

- The schedule of trees to be used in the rotating leader policy can be fed by a file or can be set to be the baseline default schedule, where every node is the leader of a different tree.

- The reconfiguration process overlaps part of the pipeline work during the transition between trees. All messages are now identified in regards to their relevant tree.

- The system revamps some hardcoded aspects of the original prototype, such as the DummyPacemaker which naively removed the old leader from the execution upon failure and didn't preserve internal state.

## Run Kauri

Disclaimer: As was with the original Kauri, this project is not production ready and is still a work in progress considering certain system conditions.

#### Preliminary Setup

Make sure that Docker Version "20.10.5" or above is installed. Older Docker Versions won't work as they does not support adjusting network privileges.

The project can be ran in two different ways: by locally compiling the project and then afterwards transferring the necessary files to the docker swarm containers (faster for development but requires more prep-work) or by pulling the entire repository and compiling everything from scratch remotely in each container (easier to deploy but a lot slower).

### Local Compilation

First, make sure you have all the required packages installed and updated.

```
sudo apt-get update
sudo apt-get upgrade
sudo DEBIAN_FRONTEND=noninteractive apt-get -y install git gcc g++ make cmake libuv1-dev libssl-dev libsodium-dev autoconf libnet1-dev libtool pastebinit python3 bash gdb dnsutils nano inetutils-ping net-tools sudo iproute2 w3m htop pip
```

Then, install GMP:

```
git clone https://github.com/aixoss/gmp 
cd gmp
sudo ./configure
sudo make install
```

Finally, do the first compilation with:

```
cd ..
git clone git@github.com:AlphaVideo/MSc-Kauri.git
cd MSc-Kauri
git submodule update --init --recursive
git submodule update --recursive --remote
cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED=ON -DHOTSTUFF_PROTO_LOG=ON -DHOTSTUFF_NORMAL_LOG=ON
make
```

Afterwards, build the Docker Images with the Dockerfile on the project root folder:

```
docker build -t kauri .
```

On each of the physical machines.

Next, setup docker swarm with:

```
docker swarm init
```

On one of the servers.

Next, let the other machines join with:

```
docker swarm join --token <token> <ip>
```

Based on the token and IP the server where the init command was executed printed on start.

Next, promote all servers to manager through:

```
docker node promote <ip>
```

On the machine where "docker swarm init" was executed on.

On the same machine, setup a docker network with:

```
docker network create --driver=overlay --subnet=10.1.0.0/16 kauri_network
```

### Remote Container Compilation

Simply clone the repository and build the Docker images using the Dockerfile in the ```runkauri``` folder.
Please edit and ensure that ```runkauri/Dockerfile``` and ```runkauri/server.sh``` are pointing towards a public version of this project repo and also to an existing branch in said repository.

The remainder of the setup logic follows the **Local Compile** section starting in the docker build command.

#### Run Experiments

To run and configure experiments we first take a look at the "experiments" file inside the ```runkauri``` directory.

```
# type, fanout pipeline-depth pipeline-lat latency bandwidth
['bls','10','6','10','100','25']
```
Each of the lines represents an experiment, given a specific fanout, pipelining depth, latency and bandwidth. Change these in accordance to your needs.

By default, the system will rotate alongside the baseline schedule every 100 blocks. To alter the rotating leader schedule, edit the file ```treegen.conf``` in the root folder with the desired trees. Each line is a different tree, in order, for the schedule. Make sure that the amount of nodes is the same as replicas being deployed!

Afterwards, in ```examples/hotstuff_app```, change the value from
```
auto opt_tree_generation = Config::OptValStr::create("default");
```
to
```
auto opt_tree_generation = Config::OptValStr::create("file");
```

The block duration the schedule trees can also be changed in the "opt_tree_switch_period" parameter above this one. Don't forget to compile and rebuild the docker image (local compilation). In the case of a remote compilation, push the changes into the repository before rebuilding the docker images.

Edit or create an experiments file in accordance to your preferences. Then, in the script ```test.sh```, change the experiments file path to your liking and simply run the script:

```
./test.sh
```

 It will create an output folder called logs with every replica's execution log (once the system is done running).

#### Run Experiments (w/ Kollaps)

The logic to run the project with Kollaps is similar to without, except that instead of an experiments file, system properties are defined in a topology .xml file. It is then the user that manually deploys the system and initiates it with Kollaps' dashboard.

Make sure you install Kollaps following the guide on their website (https://kollaps.dev/installation.html) and then simply create a topology to your liking. Several examples can be found in the directory ```runkauri/kollaps```.

With the desired topology, run the command:

```
./KollapsDeploymentGenerator <topology_name>.xml -s kauri-kollaps.yaml
```

And then afterwards deploy the topology with:

```
docker stack deploy -c kauri-kollaps.yaml kauriservice
```

When everything is done deploying, start the experiment with Kollaps' dashboard (e.g w3m 127.0.0.1:8080) and at any time fetch the execution logs by running the script ```runkauri/get_test_outputs.sh```.

### Visualizing Results

We provide a script to graph and compare the throughput of different executions (```scripts/thr_comp.py```).

Install the required python packages and execute in the style of:

```
python thr_comp.py --window-size 2 --moving-average-window 10 --output <output_path> --files <all execution txt files in order> --labels <labels for the execution txt files in order> --warmups <warmup period for the execution txt files in order> --cutoffs <cooldown cutoff for the execution txt files in order>
```

Window size dictates how the grapher batches the throughput (number of points in the x-axis) and the moving average window dictates the intensity of filter pass for graph readibility.

An example of the grapher being used would be:

```
python thr_comp.py --window-size 2 --moving-average-window 10 --output case1.png --files case1.1.txt case1.2.txt case1.3.txt --labels "h=3" "h=5" "h=2 (HotStuff)" --warmups 110 110 110 --cutoffs 145 145 145
```
