## Automated Streamlining for Constraint Satisfaction Problem

This repo contains the code and data for the paper:

Patrick Spracklen, Nguyen Dang, Ozgur Akgun, Ian Miguel. "Automated Streamliner Portfolio for Constraint Satisfaction Problem". Submitted to the Artificial Intelligence Journal (AIJ) ([pdf](https://drive.google.com/file/d/11rppwDqPMbmCOZRrYcp4tMDVW6RPX09k/view?usp=sharing) preprint version)

Given a constraint satisfaction problem described as a constraint model in [Essence](https://conjure.readthedocs.io/en/latest/essence.html) (a high-level constraint modelling language), our system automatically build a streamliner porfolio with complementary strengths, and an automatd selector for choosing the best streamlined model for any given problem instance. The main objective is to speed up the solving of the given problem by leveraging the ability of streamliners to prune the search space effectively while ensuring the existence of at least one solution for each instance. For more details, please see our paper.

Folder structure:
- `EssenceStreamliningCode`: the source code for running the system.
- `data`: input and immediate data for reproducing our experimental results in the paper.
