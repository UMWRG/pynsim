hydraTools
==========

pynsim2hydra
--------------

Conversion tool for pynsim components to Hydra templates. 

### Usage:

- Print help message:

  ```
  python pynsim2hydra.py [-h]
  ```

- Generate template file from model folder:

  ```
  python pynsim2hydra.py FOLDERNAME
  ```

  This will generate a file called `FOLDERNAME.xml`.

- Specify filename:

  ```
  python pynsim2hydra.py FOLDERNAME -o output.xml
  ```

  creates `output.xml`.

### Authors:

Adrien Gaudard, Eawag

Philipp Meier, Eawag

### (c) Copyright:
Copyright (c) 2015 Eawag, Swiss Federal Institute of Aquatic Science and Technology

Seestrasse 79, CH-6047 Kastanienbaum, Switzerland

hydra2pynsim
--------------

### Usage:

- Print help message:

  ```
  python pynsim2hydra.py [-h]
  ```

- Generate a set of agent classes from a template file:

  ```
  python hydra2pynsim.py TEMPLATE.xml -o components_folder
  ```

  For each agent type (nodes, links, networks, and institutions) a separate
  file is created inside `components_folder`.


### Authors:

Adrien Gaudard, Eawag

Philipp Meier, Eawag

### (c) Copyright:
Copyright (c) 2015 Eawag, Swiss Federal Institute of Aquatic Science and Technology

Seestrasse 79, CH-6047 Kastanienbaum, Switzerland
