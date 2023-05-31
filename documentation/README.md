# TXM Knowledge Base

*Italic text = fun facts*

## What is HLA?

HLA is a set of proteins on the surface of every person’s cells. HLA stands for
Human Leukocyte Antigen. Leukocyte means
white blood cell and antigen is something the immune system reacts to.

Antigens on cell surfaces can act as flags that the immune system looks at to
determine if something is an invader.

HLA is composed of many genes of different classes. We differentiate between
Class I (A, B, C), Class II (DR, DQ, DP),
and Class III.

*Groups everyone is tested for are A, B and DR. They are the oldest known, so
all labs are able to detect them. Each
person has 2 antigens within each of these groups. One is inherited from the
mother, the other one from the father. It is important
to know that HLA is inherited as a "set" of the three HLA groups, A, B and DR.
This set is known as a "haplotype".*

## Gene groups

We are currently considering 6 groups of HLA antigens: A, B, C, DR, DP, and DQ.
All of the other groups are not relevant to
the immune system. The most important groups are A, B, and DR.

For every antigen from groups A, B, and C, the patient has exactly 2 HLA codes (
one from the mother and one from the father),
and if only one is present, it is duplicated. This is the same for serological
notation as for high resolution.

Antigens from groups DP, DQ, and DR are a little more complex, because they are
composed of more genes.

### DQ

These genes are composed of two chains: A and B. That means, that for their high
resolution, we need 4 sequences specified
(two for A and two for B). The square brackets can be used for this, e.g.:
DQ[01:03,06:02], where the first part
describes A, and the second describes B.

For conversion of DQ genes to serological notation, it is needed to use the
table from https://en.wikipedia.org/wiki/HLA-DQ,
where a certain combination of DQA and DQB gives a specific DQ HLA code.

### DP

In the case of DP genes, during conversion, we only take "DP" and the first
number of the DPB gene, but this conversion
isn't a standardized one, and we should consider primarily DP genes in high
resolution.

### DR

This is the most complex group of antigens.

It is composed of 5 types of genes:

**DRB1** - this type contains most of the variants, DR1-DR18.

**DRB3, DRB4, DRB5** - each of these genes is either present or not, but at most
2 out of these 3 can be present (meaning
also 0 or 1 can be present). In the serological notation, they are listed as
DR52, DR53, and DR51 if present.

**DRA1** - this gene is not changing, and it is not considered at all.

In conclusion, from this group, we can have 2 HLA codes from DR1-DR18 (or one
code duplicated) and 0-2 codes from
DR51-DR53.

## Broad, split, high resolution (Nomenclature)

There are several “levels” on which the HLA antigen can be specified. For
example:

HLA-A9 consists of 3 closely related specificities, A23, A24, A2403.

First is the broad specificity, which is kind of a supertype. In this example,
it is A9.

Next is split specificity. Splits or “subtypes” are the finer specificities that
comprise the supertype. In this
example, it's for instance A23.

*Here is the table of Broad-Splits associations used in this
app: http://hla.alleles.org/antigens/broads_splits.html*

Last resolution type is high resolution. It defines specific HLA protein,
etc. E.g.: A\*24:19

| Nomenclature          | Indicates                                                                                                                                                                                             |
|-----------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| HLA                   | the HLA region and prefix for an HLA gene                                                                                                                                                             |
| HLA-DRB1              | a particular HLA locus i.e. DRB1                                                                                                                                                                      |
| HLA-DRB1\*13          | a group of alleles that encode the DR13 antigen or sequence homology to other DRB1\*13 alleles                                                                                                        |
| HLA-DRB1\*13:01       | a specific HLA allele                                                                                                                                                                                 |
| HLA-DRB1\*13:01:02    | an allele that differs by a synonymous mutation from DRB1\*13:01:01                                                                                                                                   |
| HLA-DRB1\*13:01:01:02 | an allele which contains a mutation outside the coding region from DRB1\*13:01:01:01                                                                                                                  |
| HLA-A\*24:09N         | a 'Null' allele - an allele that is not expressed                                                                                                                                                     |
| HLA-A\*30:14L         | an allele encoding a protein with significantly reduced or 'Low' cell surface expression                                                                                                              |
| HLA-A\*24:02:01:02L   | an allele encoding a protein with significantly reduced or 'Low' cell surface expression, where the mutation is found outside the coding region                                                       |
| HLA-B\*44:02:01:02S   | an allele encoding a protein which is expressed as a 'Secreted' molecule only                                                                                                                         |
| HLA-A\*32:11Q         | an allele that has a mutation that has previously been shown to have a significant effect on cell surface expression, but where this has not been confirmed and its expression remains 'Questionable' |

## HLA Typing Process

When a patient goes through the pre-transplant workup, one of the tests
performed is HLA typing to determine the
patient’s HLA antigens.

When a patient is put on the transplant list, the HLA antigens are listed into a
special computer system (for instance
TXM), along with several other pieces of information.

A lot of factors play a role in determining which patient receives the donor’s
organ. Special consideration may be given
to people on the waiting list whose HLA type closely matches the donor’s HLA
type, or their age differences, and so on.

## Antibodies

There are two arms of the immune system, cell-based and antibody-based. Till
now, we’ve only talked about cell-based.
Let’s talk about antibodies.

*An antibody is a Y-shaped molecule made by B-cells. B-cells are part of the
immune system and develop from stem cells
in the bone marrow.*

Basically, antibodies bind to antigens. Normally, antibodies are very important
in protecting us.

*Antibodies are among the defenses that the body uses to repel foreign
invaders.*

*Vaccines cause the immune system to make antibodies that protect us from
infectious diseases, and antibodies prevent
us from getting most diseases a second time.*

*Allergies are caused by antibodies that are attacking a fairly harmless thing
like plant pollen.*

However, sometimes antibodies can be bad, for instance in situations like organ
transplantation, because they can attack
an organ after it is transplanted, and cause the immune system to destroy it.
Most of the time these antibodies are
directed against HLA.

The patient's antibodies are found by a special lab test. This test does not
find the antibodies directly but tests which antigens (from a limited set) the
patient has the antibodies against. The lab test can differ from lab to lab,
each can use a bit different set of antigens in the test. This set of found antibodies is called the luminex.

For each antigen, the test reports an MFI value, higher MFI values indicate the
stronger immunological response. The lab then uses some cutoff value to
distinguish which antibodies of the patient are strong enough and which are not.
This cutoff can differ between labs and in some special cases it can be set
differently for patients from the same lab (in the case the patient really needs
a kidney and the transplant is worth it even with a small immunological
response).

Further we will be using terms:

- Positive antibody of a patient: antibody of the patient was in a lab test
  higher or equal to cutoff (we use also "over cutoff").
- Negative antibody of a patient: antibody of the patient was in a lab test
  strictly lower than the cutoff (we use also "below").
- All tested antibodies of a patient: all antibodies the patient was tested for.

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

### Processing logic of type A

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

### Processing logic of type B

In this case, we do not get all the antibodies the test was done for, we get the
antibodies in split or mixed resolution. In this case, the results are limited:

- Processing of antibodies such as DP*[01:01;02:02] is not allowed.
- MFI modification can be done but lead to omitting some antibodies.
- Some crossmatches might not be found. (See below HIGH_RES and
  HIGH_RES_WITH_SPLIT crossmatch types where type A is required.). This is more
  important in the case the antibodies are in high resolution. Because in split
  it can be usually quite safely assumed that all split antibodies were tested.

## What is MFI and cutoff?

MFI stands for Mean Fluorescence Intensity. The MFI is supposed to measure the
shift in fluorescence intensity of a
population of cells. Basically it is saying how strong an antibody is, and
whether to perceive it as a threat. That’s
why we define “cutoffs”. They are thresholds that indicate which antibodies are
dangerous for the transplantation.

## Crossmatch

The ultimate test to determine if a donor is compatible with a patient is called
a crossmatch. The crossmatch determines
if a patient has antibodies to a particular donor.

You can either test for a crossmatch in the lab, or virtually.

When you test it in the lab, the crossmatch is performed by mixing the patient’s
serum (the part of the blood where
antibodies are) with the donor's cells. If the patient has antibodies, the
crossmatch is positive.

When you perform the test virtually, you do it like we do in TXM and check
whether the recipient has antibodies against
any HLAs the donor has been typed for programmatically.

### Virtual crossmatch in TXM

In the case of a lab crossmatch there either is a crossmatch or there is not.
But in the case of virtual crossmatch, it is always only an approximation of
reality and estimation of a likelihood of a crossmatch. Therefore, in
cooperation with immunologists, we have concluded that it makes sense to have
several levels of virtual crossmatch.

Some crossmatch levels or ways to find a crossmatch are meaningful only in the
case of processing logic of type A, because with type B we have less
information.

Below we describe all the different crossmatch levels. For each level, we
describe a crossmatch for one specific antigen of the donor.

#### HIGH RES

1. donor antigen is in high resolution and the recipient has an antibody against
   the exact antigen.
2. donor antigen is in high resolution and the recipient is type A parsed and
   was not tested for donor's antigen. But all tested antibodies that match the
   donor's antigen in split resolution are positive (and there is at least one
   such antibody).
3. donor antigen is in split/broad resolution and the recipient is type A parsed
   and all tested antibodies that match donor's antigen in split/broad
   resolution are positive (and there is at least one such antibody).

Example for case 1: donor has antigen DRB1\*08:18, and the recipient has
antibody DRB1\*08:18.

Example for case 3: donor has antigen DR8, and the recipient has antibodies
DRB1\*08:01, DRB1\*08:02, ... DRB1\*08:18 and all are positive.

#### SPLIT

1. Donor antigen is in split resolution and the recipient has a matching
   antibody in split or high resolution (after conversion)
2. Donor antigen is in high resolution and the recipient is type B and the
   recipient has a matching antibody in split resolution

Example for case 1: donor has antigen DQ8 and the recipient has antibody
DRB1\*08:01 or donor has antigen DQ8 and the recipient has antibody DQ8

#### HIGH_RES_WITH_SPLIT

1. Donor antigen is in split resolution and the recipient is type A parsed. Some
   antibodies that match donors' antigens in split resolution are positive and
   some are negative.
2. This criterion is more complex. Here we list the requirements in a list:
    1. Donor antigen is in high resolution.
    2. The recipient is type A parsed.
    3. Donor's antigen is not in the set of all tested antibodies.
    4. Some antibodies that match donor's antigens in split resolution are
       positive and some are negative.

Example for case 1: donor has antigen DR8, and the recipient has antibodies
DRB1\*08:01 and DRB1\*08:18 and only one is over
the cutoff.
Example for case 3:

- Donor has antigen DRB1\*08:01
- Cutoff is 2000
- and we received the following antibodies for the recipient:
    - DRB1\*08:02 with MFI 2500
    - DRB1\*08:03 with MFI 1800

#### BROAD

1. Donor antigen is in broad resolution and the recipient has a matching
   antibody in split/broad/high resolution
2. Donor antigen is in high/split/broad resolution and the recipient is type B
   and the recipient has a matching antibody in broad resolution

Example for both cases: donor has antigen DQ3 and the recipient has antibody
DQ3.

#### HIGH_RES_WITH_BROAD

Donor antigen is in broad resolution and the recipient is type A parsed. Some
antibodies that match donors' antigen in broad resolution are positive and some
are negative.

Example: Donor has antigen A9 and the recipient has antibodies A\*23:01, A\*24:
02 and A\*23:04 and at least one
is over the cutoff, and at least one is below the cutoff.

#### UNDECIDABLE

The recipient has antibodies (of any specificity) against antigens that the
donor has not been typed for.

Example: the donor has not been typed for DP and DQ antigens, but the recipient
has an antibody DQB1*03:10.

#### Evaluating crossmatch

When determining a crossmatch, we need the antigens of the donor and the antibodies of the recipient.
However, each HLA has a specific level of detail. For instance, an HLA may look like this: `A*01:02:03:05`,
but some transplant centers might shorten it to `A*01:02`. Moreover, each allele occurs with varying frequencies.
For instance, `A*01:02:03:05` is a very rare allele, whereas `A*01:02:01:01` is quite common, but both are shortened
to the same form: `A*01:02`.


Therefore, we accept "potential hla typing" for the donor as a list of lists. Each inner list is a collection of HLA
codes, all of which share the same code on the split level. Furthermore, each code is accompanied by information about
whether it occurs frequently or not, denoted as 1 (the code occurs frequently) or 0 (the code does not occur frequently).

To evaluate the potential hla typing and to determine which codes the donor likely has, we use the following logic:

**If all codes in such a list have 1** (they are all frequent), we consider them all.
**If all codes in such a list have 0** (none of them are frequent), we take only the split code they all share.
**If some codes are 0 and some are 1**, we consider all the codes, and we calculate the crossmatch as usual. The only
difference arises when we create the final summary of the crossmatch. For HLA codes that have a 1, if we have
at least one positive match, we report the crossmatch as usual, but we consider only the highest crossmatch for this
one HLA code. If there is a positive crossmatch with an HLA code labeled with 0, we issue an empty summary with a
warning that further detailed investigation may be required.

Detailed example:

Donor has either (`A*01:02:03:05`, 0) or (`A*01:02:01:01`, 1). But we only get `A*01:02` with MFI 3000 and `A*01:02`
with MFI 1000. But recipient has also an antibody `A*01:02`.
Thus we say that there is a crossmatch for `A*01:02` with MFI 3000. But this is a problem, since `A*01:02:03:05` has a
very small frequency and there is a much bigger chance that the donor has a HLA `A*01:02:01:01`. This gets evaluated
as "there is most probably not a crossmatch but this case needs further investigation".

Suppose the donor could have either `A*01:02:03:05` (marked as 0) or `A*01:02:01:01` (marked as 1). However,
we only receive `A*01:02` with MFI 3000 and `A*01:02` with MFI 1000, and the recipient also has an antibody `A*01:02`.
Consequently, we conclude that there is a crossmatch for `A*01:02` with MFI 3000. However, this could be problematic as
`A*01:02:03:05` has a very low frequency, and there is a much higher chance that the donor has the HLA `A*01:02:01:01`.
As a result, this case is evaluated as "there is most likely no crossmatch, but this case requires further investigation."

## What is PRA?

A panel-reactive antibody (PRA) is a group of antibodies in a test serum that
are reactive against any of several known
specific antigens.

It is an immunologic test routinely performed by clinical laboratories on the
blood of people awaiting organ
transplantation. In this test recipient cells are exposed to random cells of
donor population and estimation risk of
acute rejection.

The PRA score is expressed as a percentage between 0% and 100%. It represents
the proportion of the population to which
the person being tested will react via pre-existing antibodies against human
cell surface antigens.

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
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[01:01;03:03] MFI 200, cutoff 2000
DP*[03:03;02:02] MFI 3000, cutoff 2000
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
DP*[03:03;02:02] MFI 3000, cutoff 2000
DP*[01:01;03:03] MFI 200, cutoff 2000
DP*[03:03;01:01] MFI 2100, cutoff 2000
DP*[04:01;03:03] MFI 3000, cutoff 2000
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
DP*[03:03;02:02] MFI 3000, cutoff 2000
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[04:01;01:05] MFI 3000, cutoff 2000
DP*[03:01;01:05] MFI 2500, cutoff 2000
DP*[01:01;01:05] MFI 200, cutoff 2000
DP*[03:01;06:02] MFI 100, cutoff 2000
```

In this case, the antibody `DP*[03:03;02:02]` has an only positive chain,
`DPA1*03:03`, and a mixed chain, `DPB1*02:02`, because `DPB1*02:02` has a
negative
MFI representation in the antibody `DP*[01:01;02:02]` with an
MFI of 100 (below the cutoff of 2000), while `DPA1*03:03` does not.
As a result, we parse the positive chain `DPA1*03:03` with its average MFI among
all antibodies with this chain:

```text
DPA1*03:03 MFI 3000 (average MFI), cutoff 2000
```

This mixed chain `DPB1*02:02`, which has positive
representation just in this antibody `DP*[01:03;02:02]` (there aren't any other
antibodies where this chain has positive MFI), is parsed as

```text
DPB1*02:02 MFI 100 (average negative MFI), cutoff 2000
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
DP*[03:03;02:02] MFI 3000, cutoff 2000
DP*[01:01;02:02] MFI 100, cutoff 2000
DP*[03:03;04:01] MFI 200, cutoff 2000
DP*[03:03;05:02] MFI 2200, cutoff 2000
```

In this case, the antibody `DP*[03:03;02:02]` has both chains as mixed because
its chains,
`DPA1*03:03` and `DPB1*02:02`, have negative representation in the antibodies
`DP*[03:03;04:01]` and `DP*[01:01;02:02]` respectively.
As a result, we parse this double antibody in its entirety as follows:

```text
DP*[03:03;02:02] MFI 3000, cutoff 2000
```

We also parse its two theoretical chains separately as follows:

```text
DPA1*03:03 MFI 2600 (average positive MFI), cutoff 2000
DPB1*02:02 MFI 3000 (average positive MFI), cutoff 2000
```

We always notify the user if theoretical antibodies are presented.

### The algorithm scheme

The algorithm scheme is represented in this PDF
[file](double_antibodies_parsing/double_antibodies_parsing_algorithm.pdf).

## Configuring cutoff

The original cutoff can be sometimes configured. The usual reason is that there
is a patient that really needs a kidney and is highly immunized. In this case,
it might be worth it for the patient to get a kidney from a donor against whom
the patient has antibodies. However, only antibodies with MFI only slightly over
the original cutoff. This is possible in the app via an increase in the cutoff
of the patient. Whether to increase the cutoff and how much is always up to the
user to decide.
