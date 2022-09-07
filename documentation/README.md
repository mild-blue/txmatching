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

## Crossmatch

The ultimate test to determine if a donor is compatible with a patient is called a crossmatch. The crossmatch determines
if a patient has antibodies to a particular donor.

You can either test for a crossmatch in the lab, or virtually.

When you test it in the lab, the crossmatch is performed by mixing the patient’s serum (the part of the blood where
antibodies are) with the donor's cells. If the patient has antibodies, the crossmatch is positive.

When you perform the test virtually, you do it like we do in TXM and check whether the recipient has antibodies against
any HLAs the donor has been typed for programmatically.

## Types of crossmatches in TXM

IMPORTANT: When we get antibodies in high res, we assume that we are getting all antibodies the patient was tested for. Meaning, both with MFI below and above cutoff. 

In the case of split or broad resolution we do not assume that. We assume that the patient has been tested for all relevant antibodies but only the positive MFI values are required. Although, negative can be send too.

**HIGH_RES** - both donor antigens and recipient antibodies are in high resolution OR donor has typization in split or
broad and recipient has antibodies all in high res and all antibodies are positive against donor typization. E.g.: donor
has antigen DRB1\*08:18, and recipient has antibody DRB1\*08:18 OR donor has antigen DR8, and recipient has antibodies
DRB1\*08:01 and DRB1\*08:18 and both are positive (over cutoff).

**SPLIT** - both donor antigens and recipient antibodies are in split resolution. E.g.: donor has antigen DQ8 and
recipient has antibody DQ8 (both are missing high res).

**HIGH_RES_WITH_SPLIT** - donor antigens are in split, recipient antibodies are in high res, but not all antibodies are
over cutoff. E.g.: donor has antigen DR8, and recipient has antibodies DRB1\*08:01 and DRB1\*08:18 and only one is over
the cutoff.

**BROAD** - both donor antigens and recipient antibodies are in broad resolution. E.g.: donor has antigen DQ3 and
recipient has antibody DQ3 (both are missing high res and split).

**HIGH_RES_WITH_BROAD** - donor antigens are in broad, recipient antibodies are in high res, but not all antibodies are
over cutoff. E.g.:  donor has antigen A9, and recipient has antibodies A\*23:01, A\*24:02 and A\*23:04 and at least one
is over the cutoff, and at least one is below the cutoff.

**UNDECIDABLE** - recipient has antibodies (of any specificity) against antigens that donor has not been typed for.
E.g.: donor has antigens in groups DPB and DQA: DPB1\*512:01, DQA1\*02:05, and recipient has antibodies in groups DQB and DPB: DQB1\*03:10,
DPB1\*414:01. Thus, DQB1\*03:10 is UNDECIDABLE.

**NONE** - antibody is over cutoff, but there is no crossmatch. E.g.: donor has antigen DQA1\*03:10 and recipient has antibody DQA1\*04:07.

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
