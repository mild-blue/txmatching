# TXM Knowledge Base

*Italic text = fun facts*

## What is HLA?

HLA is a set of proteins on the surface of every person’s cells. HLA stands for Human Leukocyte Antigen. Leukocyte means
white cell, and antigen is something the immune system reacts to.

Antigens on cell surfaces can act as flags that the immune system looks at to determine if something is an invader.

HLA is composed of many genes of different classes. We differentiate between Class I (A, B, C), Class II (DR, DQ, DP),
and Class III.

*The groups everyone is tested for are A, B, DR. They are the oldest known, so all labs are able to detect them. Each
person has 2 antigens within each of these groups. One inherited from mother, the other one from father. It is important
to know that HLA is inherited as a "set" of the three HLA groups, A, B, DR. This set is known as a "haplotype".*

## Broad, split, high resolution (Nomenclature)

There are several “levels” on which the HLA antigen can be specified. For example:

HLA-A9 consists of 3 closely related specificities, A23, A24, A2403.

*Here is the table of more Broad-Splits associations: http://hla.alleles.org/antigens/broads_splits.html*

First is the broad specificity, which is kind of a supertype. In this example, it is A9.

Next is split specificity. Splits or “subtypes” are the finer specificities that comprise the supertype. In this
example, it's for instance A23.

Finally, we also specify high resolution, which is the most specific, specifying also things like specific HLA protein,
etc. E.g.: A\*24:19

|Nomenclature | Indicates|
|--- | ---|
|HLA    | the HLA region and prefix for an HLA gene|
|HLA-DRB1 | a particular HLA locus i.e. DRB1|
|HLA-DRB1\*13 | a group of alleles that encode the DR13 antigen or sequence homology to other DRB1\*13 alleles|
|HLA-DRB1\*13:01 | a specific HLA allele|
|HLA-DRB1\*13:01:02 | an allele that differs by a synonymous mutation from DRB1\*13:01:01|
|HLA-DRB1\*13:01:01:02 | an allele which contains a mutation outside the coding region from DRB1\*13:01:01:01|
|HLA-A\*24:09N | a 'Null' allele - an allele that is not expressed|
|HLA-A\*30:14L | an allele encoding a protein with significantly reduced or 'Low' cell surface expression|
|HLA-A\*24:02:01:02L | an allele encoding a protein with significantly reduced or 'Low' cell surface expression, where the mutation is found outside the coding region|
|HLA-B\*44:02:01:02S | an allele encoding a protein which is expressed as a 'Secreted' molecule only|
|HLA-A\*32:11Q | an allele which has a mutation that has previously been shown to have a significant effect on cell surface expression, but where this has not been confirmed and its expression remains 'Questionable'|

## HLA Typing Process

When a patient goes through the pre-transplant workup, one of the tests performed is HLA typing to determine the
patient’s HLA antigens.

When a patient is put on the transplant list, the HLA antigens are listed into a special computer system (for instance
TXM), along with several other pieces of information.

A lot of factors play a role in determining which patient receives the donor’s organ. Special consideration may be given
to people on the waiting list whose HLA type closely matches the donor’s HLA type, or their age differences, and so on.

## Antibodies

There are two arms of the immune system, cell-based and antibody-based. Till now, we’ve only talked about cell-based.
Let’s talk about antibodies.

*An antibody is a Y-shaped molecule made by B-cells. B-cells are part of the immune system and develop from stem cells
in the bone marrow.*

Basically, antibodies bind to antigens. Normally, antibodies are very important in protecting us.

*Antibodies are among the defenses that the body uses to repel foreign invaders.*

*Vaccines cause the immune system to make antibodies which protect us from infectious diseases, and antibodies prevent
us from getting most diseases a second time.*

*Allergies are caused by antibodies that are attacking a fairly harmless thing like plant pollen.*

However, sometimes antibodies can be bad, for instance in situations like organ transplantation, because they can attack
an organ after it is transplanted, and cause the immune system to destroy it. Most of the time these antibodies are
directed against HLA.

Antibodies of a patient are found by a special lab test. This test does not find the antibodies directly but tests which antigens (from a limited set) the patient has the antibodies against. The lab test can differ from lab to lab, each can use a bit different set of antibodies in the test.

For each antigen the test reports MFI value and the higher the MFI value is the stronger was the immunological response. The lab then uses some cutoff value to distinguish which antibodies the patient has and which not. This cutoff can differ between labs and in some special cases in can be set differently for patients from the same lab (in the case the patient really needs a kidney and it is worth for the patient to have the transplant even when there is a small immunological response)

The parsing is done in two modes. In case we receive about the patient all antibodies, positive and negative in high resolution we use processing logic of type A. This is the better, more precise case. In other situations we use type B

### Processing logic of type A
In this case we assume we have received ALL antibodies in high resolution the antibody test was done for, with MFI values and required cutoff (the cutoff is sometimes then changed later in case it is found useful).

This case can handle also antibody in the form of DP*[01:01;02:02]. It uses an algorithm that parses the specific antibodies against alpha and beta chains. In case there is some unclear case it raises a warning and requires an immunologist to check the correctness of the algorithm result.

There are three reasons why we ask for ALL antibodies the test was done for and not only the positive ones:
- for the algorithm that is parsing of antibodies of type DP*[01:01;02:02] it is needed (see detailed description of the algorithm below)
- In case the user wants to alter MFI, the antibodies that were negative can become positive
- When estimating crossmatch, sometimes it is crucial to have the full picture. (See below HIGH_RES and HIGH_RES_WITH_SPLIT crossmatch types where type A is required.)

#### Type B
In this case we do not get all the antibodies the test was done for we get the antibodies in split or mixed resolution. In this case the results are limited:
- processing of antibodies such as DP*[01:01;02:02] is not allowed,
- MFI modification can be done but lead to omitting some antibodies
- Some crossmatches might not be found. (See below HIGH_RES and HIGH_RES_WITH_SPLIT crossmatch types where type A is required.). This is more important in the case the antibodies are in high resolution. Because in split it can be usually quite safely assumed that all split antibodies were tested.

## Crossmatch

The ultimate test to determine if a donor is compatible with a patient is called a crossmatch. The crossmatch determines
if a patient has antibodies to a particular donor.

You can either test for a crossmatch in the lab, or virtually.

When you test it in the lab, the crossmatch is performed by mixing the patient’s serum (the part of the blood where
antibodies are) with the donor's cells. If the patient has antibodies, the crossmatch is positive.

When you perform the test virtually, you do it like we do in TXM and check whether the recipient has antibodies against
any HLAs the donor has been typed for programmatically.

### Virtual crossmatch in TXM

In the case of a lab crossmatch there either is a crossmatch or there is not. But in the case of virtual crossmatch it is always only an approximation of reality and estimation of a likelihood of a crossmatch. Therefore, in cooperation with immunologists we have concluded that it makes sense to have several levels of virtual crossmatch.

In the case of split or broad resolution we do not assume that. We assume that the patient has been tested for all relevant antibodies but only the positive MFI values are required. Although, negative can be send too.

Below we describe all the different crossmatch level. For each level we describe a crossmatch for one specific antigen of donor. We use terms
- all antibodies - all antibodies the recipient was tested for, both with MFI below and above cutoff
- positive antibodies - antibodies that the recipient really has (with MFI above cutoff)
- negative antibodies - antibodies that the recipient was tested for, but were not present. (makes sense only for type A parsing)

#### HIGH RES
1. donor antigen is in high resolution and recipient has an antibody against the exact antigen.
2. donor antigen is in high resolution and recipient is type A parsed and was not tested for donors antigen. But all antibodies that match donors antigen in split resolution are positive (and there is at least one such antibody)
3. donor antigen is in low resolution and recipient is type A parsed and all antibodies that match donors antigen in low resolution are positive (and there is at least one such antibody).


Example for case 1: donor has antigen DRB1\*08:18, and recipient has antibody DRB1\*08:18.

Example for case 3: donor has antigen DR8, and recipient has antibodies DRB1\*08:01, DRB1\*08:02, ... DRB1\*08:18 and all are positive.

#### SPLIT
1. Donor antigen is in split resolution and recipient has matching antibody in split or high resolution (after conversion)
2. Donor antigen is in high resolution and recipient has matching antibody in split resolution

Example: donor has antigen DQ8 and recipient has antibody DRB1\*08:01 or donor has antigen DQ8 and recipient has antibody DQ8


#### HIGH_RES_WITH_SPLIT
1. Donor antigen is in split resolution and recipient is type A parsed. Some antibodies that match donors antigen in split resolution are positive and some negative.
2. Donor antigen is in high resolution and recipient is type A parsed and was not tested for donors antigen. Some antibodies that match donors antigen in split resolution are positive and some negative.

Example for case 1: donor has antigen DR8, and recipient has antibodies DRB1\*08:01 and DRB1\*08:18 and only one is over
the cutoff.

#### BROAD
1. Donor antigen is in broad resolution and recipient has matching antibody in split/broad/high resolution
2. Donor antigen is in high/split/broad resolution and recipient has matching antibody in broad resolution

Example for both cases: donor has antigen DQ3 and recipient has antibody DQ3.

#### HIGH_RES_WITH_BROAD
Donor antigen is in broad resolution and recipient is type A parsed. Some antibodies that match donors antigen in broad resolution are positive and some negative.

Example: Donor has antigen A9 and recipient has antibodies A\*23:01, A\*24:02 and A\*23:04 and at least one
is over the cutoff, and at least one is below the cutoff.

#### UNDECIDABLE
Recipient has antibodies (of any specificity) against antigens that donor has not been typed for.

Example: donor has not been typized for DP and DQ antigens, but recipient has an antibody DQB1*03:10.

## What is MFI and cutoff?

MFI stands for Mean Fluorescence Intensity. The MFI is supposed to measure the shift in fluorescence intensity of a
population of cells. Basically it is saying how strong an antibody is, and whether to perceive it as a threat. That’s
why we define “cutoffs”. They are thresholds that indicate which antibodies are dangerous for the transplantation.

## What is PRA?

A panel-reactive antibody (PRA) is a group of antibodies in a test serum that are reactive against any of several known
specific antigens.

It is an immunologic test routinely performed by clinical laboratories on the blood of people awaiting organ
transplantation. In this test recipient cells are exposed to random cells of donor population and estimation risk of
acute rejection.

The PRA score is expressed as a percentage between 0% and 100%. It represents the proportion of the population to which
the person being tested will react via pre-existing antibodies against human cell surface antigens.

## Square bracket antibody parsing algorithm

When we receive antibodies in format DP*[01:01;02:02] we are using special algorithm to deduce whether there are
antibodies against both alpha and beta allels or just from one of them.

TODO Add algorithm description
