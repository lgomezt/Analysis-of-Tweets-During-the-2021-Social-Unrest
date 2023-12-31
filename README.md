# Analysis of Tweets During the 2021 Social Outburst

In this project, we analyze the evolution of various segregation metrics during the "Social Outburst of Colombia" in 2021.

To accomplish this, we collected over X million tweets for three distinct periods:
1. Regional elections prior to the Social Outburst (October 2019).
2. Three months preceding the Social Outburst (January 2021).
3. The Social Outburst in Colombia (April 28th to June 29th, 2021).

---

## Repository Structure

The repository is organized into three main folders:

1. **Code**: Houses the Jupyter notebooks needed for data analysis and other computational tasks.
2. **Results**: Contains the outputs from the analyses, such as graphs, CSV files, etc.
3. **Tutorials**: Provides step-by-step instructions for setting up your environment and installing dependencies.

---

### 1. Tutorials

The `Tutorials` folder includes markdown files that guide you through the initial setup:

- **[0. VM Setup.md](https://github.com/lgomezt/Analysis-of-Tweets-During-the-2021-Social-Unrest/blob/main/Tutorials/0.%20VM%20Setup.md)**: Instructions for setting up a Virtual Machine to run the project.
- **[1. Create venv.md](https://github.com/lgomezt/Analysis-of-Tweets-During-the-2021-Social-Unrest/blob/main/Tutorials/1.%20Create%20venv.md)**: A guide for creating a Python virtual environment to isolate the project's dependencies.
- **[2. Install graph-tool.md](https://github.com/lgomezt/Analysis-of-Tweets-During-the-2021-Social-Unrest/blob/main/Tutorials/2.%20Install%20graph-tool.md)**: Instructions for installing the `graph-tool` library, which is essential for this project.

### 2. Code

The `Code` folder contains all the Jupyter notebooks necessary for the analysis. For a more detailed explanation of the project's pipeline, refer to `Dictionary.xlsx`.

### 3. Results

The `Results` folder includes all the output generated from the Jupyter notebooks in the `Code` folder. This can include, but is not limited to:

- CSV files
- Graphs and plots
- Model checkpoints

---

## Getting Started

1. **Clone the repository**: 
    ```bash
    git clone https://github.com/lgomezt/Analysis-of-Tweets-During-the-2021-Social-Unrest.git
    ```
2. **Navigate to the Tutorials folder**: 
    ```bash
    cd Analysis-of-Tweets-During-the-2021-Social-Unrest/Tutorials
    ```
    Follow the setup guides to prepare your environment.

3. **Install Requirements**:
    ```bash
    cd Analysis-of-Tweets-During-the-2021-Social-Unrest
    pip install -r requirements.txt
    ```
    Install the necessary Python packages specified in requirements.txt.

3. **Navigate to the Code folder**: 
    ```bash
    cd ../Code
    ```
    Run the Jupyter notebooks in the following order.
   1. Save_tweets.ipynb
   2. Political Labelling.ipynb
   3. Retweet Adjacency Matrices.ipynb

5. **Check Results**: After successfully running the code, you can examine the `Results` folder for the output.
