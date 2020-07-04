# creates environment from the file
conda-create:
	conda env create -f conda.yml

# exports all changes made localy - then one must copy the changes to conda.yml
conda-export:
	conda env export --from-history

# updates environment when some changes were applied to the file
conda-update:
	conda env update --file conda.yml  --prune