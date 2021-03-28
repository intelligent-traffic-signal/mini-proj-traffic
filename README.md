# mini-proj-traffic

## Use Makefile to create trips and routes

1. Convert osm to net.xml

    ```shell
    make osm
    ```

2. Create trips

    ```shell
    make trips
    ```

3. Run simulation in sumo-gui

    ```shell
    make sim
    ```

4. Clean

    ```shell
    make clean
    ```

## Create env for tensorforce

1. Create conda env from requirements

    ```shell
    conda create --name <env> --file conda_requirements.txt
    ```

2. Activate the environment

    ```shell
    source activate <env>
    ```

3. Install pip inside the conda environment

    ```shell
    conda install pip
    ```

4. Install pip requirements inside the env

    ```shell
    pip install -r pip_requirements.txt
    ```
