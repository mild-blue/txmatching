# Parsing antibody data

The parsing is done in two modes, type A and type B. Both of them are described
below. (The name is purely our, it has no connection with any term used in
immunology). The decision which parsing mode is selected is simple, if
requirements for type A are fulfilled, type A processing runs, otherwise we fall
back to type B.

Type A requires that all antibodies are in high resolution and having all tested
antibodies of a patient. We assume that if the criteria below are fulfilled this
holds.

- All antibodies we receive are in high resolution.
- There are at least 20 antibodies provided.
- There is at least 1 antibody below the cutoff.

## Processing logic of type A

In this case, we assume we have received all tested antibodies in high
resolution with MFI values and the required cutoff (The cutoff is configurable.
In some cases the user can decide to change it for some patients, for more
details see section Configuring Cutoff).

This case can handle also an antibody in the form of DP*[01:01;02:02]. It uses
an algorithm that parses the specific antibodies against alpha and beta chains.
After parsing, most double antibodies are decomposed into separate chains and
analyzed as normal single antibodies. The remaining double antibodies for a positive
crossmatch must have a positive crossmatch for each of their chains.
In case there is some unclear case it raises a warning and requires an
immunologist to check the correctness of the algorithm result.

There are three reasons why we ask for all tested antibodies of a patient and
not only the positive ones:

- It is required for the algorithm that is parsing antibodies of type
  DP*[01:01;02:02], see the detailed description of the algorithm below.
- In case the user wants to alter MFI, the antibodies that were negative can
  become positive.
- When estimating crossmatch, sometimes it is crucial to have the full
  picture. (See below HIGH_RES and HIGH_RES_WITH_SPLIT crossmatch types where
  type A is required.)

## Processing logic of type B

In this case, we do not get all the antibodies the test was done for, we get the
antibodies in split or mixed resolution. In this case, the results are limited:

- Processing of antibodies such as DP*[01:01;02:02] is not allowed.
- MFI modification can be done but lead to omitting some antibodies.
- Some crossmatches might not be found. (See below HIGH_RES and
  HIGH_RES_WITH_SPLIT crossmatch types where type A is required.). This is more
  important in the case the antibodies are in high resolution. Because in split
  it can be usually quite safely assumed that all split antibodies were tested.

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

#### 1. Antibody chain is negative

```text
Example:
DP*[01:01;02:02], MFI 100, cutoff 2000
DP*[01:01;03:03], MFI 200, cutoff 2000
DP*[03:03;02:02], MFI 3000, cutoff 2000
```

In this case, the chain `DPA1*01:01` is negative because there is no
representation
of this chain with MFI above the cutoff among all antibodies.
As a result, we parse this chain as:

```text
DPA1*01:01 MFI 150 (average MFI), cutoff 2000
```

Please note that the chain `DPB1*02:02` is not negative because it has a
positive
representation in the antibody `DP*[03:03;02:02] MFI 3000, cutoff 20000`.
Therefore, this chain is mixed.

Similarly, the chain `DPB1*03:03` is negative and parsed in the same way
as `DPA1*01:01`.

#### 2. Both chains are only positive

```text
Example:
DP*[03:03;02:02], MFI 3000, cutoff 2000
DP*[01:01;03:03], MFI 200, cutoff 2000
DP*[03:03;01:01], MFI 2100, cutoff 2000
DP*[04:01;03:03], MFI 3000, cutoff 2000
```

In this case, the antibody `DP*[03:03;02:02]` has both chains positive because
both `DPA1*03:03` and `DPB1*02:02` have only positive MFIs among all
antibodies.
As a result, we parse this antibody as two separate chains:

```text
DPA1*03:03 MFI 2550 (average MFI), cutoff 2000
DPB1*02:02 MFI 3000 (average MFI), cutoff 2000
```

The antibody `DP*[03:03;01:01]` is also only positive.
However, `DP*[04:01;03:03]`
is not positive because it has negative representation of the
chain `DPB1*03:03` in the antibody `DP*[01:01;03:03]`.

#### 3. One chain is only positive, another one is mixed:

```text
Example:
DP*[03:03;02:02], MFI 3000, cutoff 2000
DP*[01:13;02:02], MFI 3000, cutoff 2000
DP*[01:01;02:02], MFI 100, cutoff 2000
DP*[04:01;01:05], MFI 3000, cutoff 2000
DP*[03:01;01:05], MFI 2500, cutoff 2000
DP*[01:01;01:05], MFI 200, cutoff 2000
DP*[03:01;06:02], MFI 100, cutoff 2000
```

In this case, the antibody `DP*[03:03;02:02]` has an only positive chain,
`DPA1*03:03`, and a mixed chain, `DPB1*02:02`, because `DPB1*02:02` has a
negative
MFI representation in the antibody `DP*[01:01;02:02]` with an
MFI of 100 (below the cutoff of 2000), while `DPA1*03:03` does not.
As a result, we parse the positive chain `DPA1*03:03` with its average MFI among
all antibodies with this chain:

```text
DPA1*03:03, MFI 3000 (average MFI), cutoff 2000
```

This mixed chain `DPB1*02:02`, which has positive
representation in the antibodies `DP*[01:03;02:02]` and `DP*[01:13;02:02]`, is parsed as

```text
DPB1*02:02, MFI 100 (average negative MFI), cutoff 2000
```
We suppose that the positive MFI is caused by the second chain,
so we do not consider this positive value for the mixed `DPB1*02:02` chain.

Pay attention that a similar mixed chain, `DPB1*01:05`,
but for the antibody `DP*[04:01;01:05]`, is not parsed through this antibody but
through the `DP*[03:01;01:05]` antibody, as explained in the next section.
In summary, if we encounter this positive and mixed chain case where the mixed
chain has several positive representations among all the antibodies,
we expect to parse the mixed chain through other antibodies.

#### 4. Both chains are mixed

```text
Example:
DP*[03:03;02:02], MFI 3000, cutoff 2000
DP*[01:01;02:02], MFI 100, cutoff 2000
DP*[03:03;04:01], MFI 200, cutoff 2000
DP*[03:03;05:02], MFI 2200, cutoff 2000
```

In this case, the antibody `DP*[03:03;02:02]` has both chains as mixed because
its chains,
`DPA1*03:03` and `DPB1*02:02`, have negative representation in the antibodies
`DP*[03:03;04:01]` and `DP*[01:01;02:02]` respectively.
As a result, we parse this double antibody in its entirety as follows:

```text
DP*[03:03;02:02], MFI 3000, cutoff 2000
```

We also parse its two theoretical chains separately as follows:

```text
DPA1*03:03 MFI, 2600 (average positive MFI), cutoff 2000
DPB1*02:02 MFI, 3000 (average positive MFI), cutoff 2000
```

We always notify the user if theoretical antibodies are presented.

### The algorithm scheme

The algorithm scheme is represented in this PDF
[file](double_antibodies_parsing/double_antibodies_parsing_algorithm.drawio.pdf).
