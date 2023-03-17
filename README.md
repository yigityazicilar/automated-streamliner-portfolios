## Automated Streamlining for Constraint Satisfaction Problem

This repo contains the code and data for the paper:

Patrick Spracklen, Nguyen Dang, Ozgur Akgun, Ian Miguel. "Automated Streamliner Portfolio for Constraint Satisfaction Problem". Submitted to the Artificial Intelligence Journal (AIJ) ([pdf](https://drive.google.com/file/d/11rppwDqPMbmCOZRrYcp4tMDVW6RPX09k/view?usp=sharing) preprint version)

Given a constraint satisfaction problem described as a constraint model in [Essence](https://conjure.readthedocs.io/en/latest/essence.html) (a high-level constraint modelling language), our system automatically build a streamliner porfolio with complementary strengths, and an automated selector for choosing the best streamlined model for any given problem instance. The main objective is to speed up the solving of the given problem by leveraging the ability of streamliners to prune the search space effectively while ensuring the existence of at least one solution for each instance. For more details, please see our paper.

Folder structure:
- `EssenceStreamliningCode`: the source code for running the system.
- `data`: input and immediate data for reproducing our experimental results in the paper.

# Examples
## Docker
A [Dockerfile](EssenceStreamlining/Dockerfile) is provided to give a runnable example of the automated streamlining pipeline in action.

First you need to build:
```
docker build . -t journal_streamlining
```
The image is then directly runnable:
```
> docker run journal_streamlining
DEBUG:root:Generating candidate streamliners
INFO:root:Adding node 
DEBUG:root:------SELECTION-----
DEBUG:root:Not all children have been created. Returning set()
INFO:root:Adding node 121
INFO:root:New combo 121
DEBUG:root:Building streamlined models for 121: ['conjure', 'modelling', '/examples/VesselLoading//model.essence', '--generate-streamliners', '121', '--portfolio=1', '-o', '/examples/VesselLoading//conjure-output']
...
```

## Python
If you don't want to use docker you can run the Python code directly:
```
> pip3.9 install pipenv && pipenv install
> pipenv run python ./src/Main.py /examples/VesselLoading/ examples/VesselLoading/params
```
Note however that you will need to have all of the various tools in the pipeline (conjure/savilerow/minion) on the runtime path for this to work.

## Required Files
If you want to adapt this to other problems it requires the following files:
- [Essence Specification](EssenceStreamlining/examples/VesselLoading/model.essence): Essence specification of the problem
- [Essence problem params](EssenceStreamlining/examples/VesselLoading/params): Training params used to construct the streamliner portfolio
- [Yaml Configuration File](EssenceStreamlining/examples/VesselLoading/conf.yaml): Configuration of : solver,# cores, # mcts iterations, etc.
- [Base Model Results](EssenceStreamlining/examples/VesselLoading/BaseModelResults.csv): A csv file detailing runtime information of the training params under a non-streamlined context


## Configuration
The execution of the pipeline is configured via a yaml configuration file ([Conf File](EssenceStreamlining/examples/VesselLoading/conf.yaml)) which currently supports tweaking:
- conjure
    - portfolio_size: The number of models to build for each streamlined model. [Towards Portfolios of Streamlined Constraint Models: A Case Study with the Balanced Academic Curriculum Problem](https://arxiv.org/abs/2009.10152) has shown there is potential for exploring different modelling choices to opimize the effectiveness of the streamliner portfolio
- solver : The current solver to use. Currently supported are "chuffed" and "lingeling"
- executor
    - num_cores: The number of cores on the machine to use for evaluating and searching the streamliner lattice 
- mcts
    - num_iterations: The number of iterations of MCTS to do in a single round
- hydra
    - num_rounds: The number of rounds of [Hydra](https://www.cs.ubc.ca/labs/algorithms/Projects/Hydra/) to perform
