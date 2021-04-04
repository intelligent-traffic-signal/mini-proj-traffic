# mini-proj-traffic

## Env for training and testing

Make sure sumo and sumo-gui are installed

1. Enter conda env

    ```shell
    conda activate base
    ```

2. Install pip in conda env

    ```shell
    conda install pip
    ```

3. Install TraCI and Pydot

    ```shell
    pip install traci
    pip install pydot
    ```

4. Make sure Graphviz is installed

    <https://graphviz.gitlab.io/download/>

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

4. Run python Round Robin script

   ```shell
   make rr
   ```

5. Clean

    ```shell
    make clean
    ```
