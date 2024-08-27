# Basic terms

## HLA

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

## MFI and cutoff

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
any HLAs the donor has been typed for programmatically this is called virtual crossmatch.

## PRA

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
