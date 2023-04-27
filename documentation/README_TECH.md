## Square bracket antibody parsing algorithm

When we receive antibodies in the notation DP*[01:01;02:02], we use a special algorithm 
to determine whether there are antibodies against both alpha and beta alleles or just one of them.

### Algorithm description

Let us first explain the terminology we used to describe the algorithm:

* "double antibody" refers to an antibody enclosed in square brackets.
* "alpha chain" refers to the first code of a double antibody.
* "beta chain" refers to the second code of a double antibody.
* "positive MFI" is the MFI value that is equal to or above the cutoff.
* "negative MFI" is the MFI value below the cutoff.

At the beginning of the algorithm execution, we have three lists:
1. `antibodies` - a list of all antibodies to parse.
2. `parsed` - a list of parsed antibodies.
3. `parsing_issues` - a list of parsing issues that occur during the algorithm execution.

We parse each antibody in the list of `antibodies` one by one using a for-loop. If both chains of the antibody are 
already in the `parsed` list, we move on to the next antibody. 

If at least one of the chains is not in the `parsed` list yet, we examine the antibody with the following logic:
</br>
First, we check if the antibody has a positive MFI.

#### Double antibody has a positive MFI:
If **both antibody chains have only positive MFI representation** among all the antibodies 
in the list for parsing, we add each chain **separately** to the `parsed` list with the arithmetic mean of the MFI from all antibodies with this chain in the list.</br></br>
If **one of the chains has at least one negative MFI representation** and the **other chain has only positive MFI representation** 
among other antibodies in the list, we add the **chain with only positive MFI representation** to the `parsed` 
list with the arithmetic mean of the MFI from all antibodies with this chain. For the **chain with mixed MFI representation**, 
if this is the only positive occurrence of this chain, we add it to the `parsed` list with the arithmetic mean 
of the MFI from all antibodies with negative MFI for this chain in the list. 
However, if there is another positive occurrence for this chain, we skip it.</br></br>
If **both chains have at least one negative MFI among other antibodies**, 
we add them to the `parsed` list as one double antibody with the provided MFI. 
Moreover, we add each chain **separately** to the `parsed` list, and we denote their type as "theoretical", 
with the arithmetic mean of the positive MFI from all antibodies with this chain in the list.
Finally, we add a parsing issue about this to the `parsing_issue` list.

#### Double antibody has a negative MFI:
We check each chain of the antibody separately, and if that chain has **only negative MFI representation** 
among other antibodies in the list, we add this chain to the `parsed` list with the arithmetic mean of 
the MFI from all antibodies in the list. Otherwise, we skip this chain.

### The algorithm scheme
The algorithm scheme is represented in this PDF 
[file](double_antibodies_parsing/double_antibodies_parsing_algorithm.pdf).

**P.S.** The last time this algorithm was in the `_add_double_hla_antibodies` function.