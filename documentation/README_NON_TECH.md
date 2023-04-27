## Square bracket antibody parsing algorithm

When we receive antibodies in the notation DP*[01:01;02:02], we use a special 
algorithm to determine whether there are antibodies against both alpha and 
beta alleles or just one of them.

### Algorithm description

Let us first explain the terminology we used to describe the algorithm:

* "double antibody" refers to an antibody enclosed in square brackets.
* "alpha chain" refers to the first code of a double antibody.
* "beta chain" refers to the second code of a double antibody.
* "positive MFI" is the MFI value that is equal to or above the cutoff.
* "negative MFI" is the MFI value below the cutoff.

We parse each antibody one by one and detect several situations:

## 1. Antibody chain is negative
```text
Example:
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[01:01;03:03] MFI 200, cutoff 2000
DP*[03:03, 02:02] MFI 3000, cutoff 2000
```
In this case, the chain `DPA1*01:01` is negative because there is no representation 
of this chain with MFI above the cutoff among all antibodies. 
As a result, we parse this chain as:
```text
DPA1*01:01 MFI 150 (average MFI), cutoff 2000
```

Please note that the chain `DPB1*02:02` is not negative because it has a positive 
representation in the antibody `DP*[03:03, 02:02] MFI 3000, cutoff 20000`. 
Therefore, this chain is mixed.

Similarly, the chain `DPB1*03:03` is negative and parsed in the same way as `DPA1*01:01`.

## 2. Both chains are only positive
```text
Example:
DP*[03:03, 02:02] MFI 3000, cutoff 2000
DP*[01:01;03:03] MFI 200, cutoff 2000
DP*[03:03, 01:01] MFI 2100, cutoff 2000
DP*[04:01, 03:03] MFI 3000, cutoff 2000
```
In this case, the antibody `DP*[03:03, 02:02]` has both chains positive because 
either `DPA1*03:03` or `DPB1*02:02` have only positive MFIs among all antibodies. 
As a result, we parse this antibody as two separate chains:
```text
DPA1*03:03 MFI 2550 (average MFI), cutoff 2000
DPB1*02:02 MFI 3000 (average MFI), cutoff 2000
```

The antibody `DP*[03:03, 01:01]` is also only positive. However, `DP*[04:01, 03:03]`
is not positive because it has negative representation of the 
chain `DPB1*03:03` in the antibody `DP*[01:01, 03:03]`.
# TODO!!!! DOWN
## 3. One chain is only positive, another one is mixed:
```text
Example:
DP*[03:03, 02:02] MFI 3000, cutoff 2000
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[04:01, 01:05] MFI 3000, cutoff 2000
DP*[03:01, 01:05] MFI 2500, cutoff 2000
DP*[01:01, 01:05] MFI 200, cutoff 2000
DP*[03:01, 06:02] MFI 100, cutoff 2000
```
In this case, the antibody `DP*[01:03;02:02]` has only a positive chain, 
`DPA1*03:03`, and a mixed chain, `DPB1*02:02`, because `DPB1*02:02` has a negative 
MFI representation in the antibody `DP*[01:01;02:02]` with an 
MFI of 100 (below the cutoff of 2000), while `DPA1*03:03` does not.
As a result, we only consider the positive chain `DPA1*03:03`, 
and calculate its average MFI among all antibodies with this chain, 
which results in:
```text
DPA1*03:03 MFI 3000 (average MFI), cutoff 2000
```

This mixed chain `DPB1*02:02`, which has positive
representation just in this antibody `DP*[01:03;02:02]` (there aren't any other
antibodies where this chain has positive MFI), is parsed as 
```text
DPB1*02:02 MFI 100 (average negative MFI), cutoff 2000
```

Pay attention that a similar mixed chain, `DPB1*01:05`, 
but for the antibody `DP*[04:01, 01:05]`, is not parsed through this antibody but 
through the `DP*[03:01, 01:05]` antibody, as explained in the next section. 
In summary, if there are several positive representations in this positive + mixed case, 
we expect to parse this chain through other antibodies.

## 4. Both chains are mixed
```text
Example:
DP*[03:03, 02:02] MFI 3000, cutoff 2000
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[03:03, 04:01] MFI 200, cutoff 2000
DP*[03:03, 05:02] MFI 2200, cutoff 2000
```
In this case, the antibody `DP*[03:03, 02:02]` has both chains as mixed because its chains, 
`DPA1*03:03` and `DPB1*02:02`, have negative representation in the antibodies 
`DP*[03:03, 04:01]` and `DP*[01:01;02:02]`, respectively. 
As a result, we parse this double antibody in its entirety as follows:
```text
DP*[03:03, 02:02] MFI 3000, cutoff 2000
```

We also parse the two theoretical chains separately as follows:
```text
DPA1*03:03 MFI 2600 (average positive MFI), cutoff 2000
DPB1*02:02 MFI 3000 (average positive MFI), cutoff 2000
```
We always notify the user if theoretical antibodies are presented.
