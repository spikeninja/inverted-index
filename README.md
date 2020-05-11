## Setting up the project
In order to run the program you need python 3.8.2 or higher to be installed on your system. 
There is no extra packages required for the project so requirements.txt does not exist.
Actions:
- Fill in data/ directory by your own files in such pattern: data/folder_name/(some files). Parallelization comes down to having multiple folders in the data/ directory.
- Change **paths** variable into main function by your own folders you have created.
- run this command 
-- python main.py 5
where number **5** is a max amount of processes program will use.


## Test It using existing data
You can also quickly check the program by executing such commands in python shell:
> from main import *
> ii = InvertedIndex(Preprocessor(), Serializer())
> ii.create_index('data/test/')
> ii.search('so')