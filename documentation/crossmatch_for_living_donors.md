# Virtual crossmatch for living donors

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

## HIGH_RES

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

## SPLIT

1. Donor antigen is in split resolution and the recipient has a matching
   antibody in split or high resolution (after conversion)
2. Donor antigen is in high resolution and the recipient is type B and the
   recipient has a matching antibody in split resolution

Example for case 1: donor has antigen DQ8 and the recipient has antibody
DRB1\*08:01 or donor has antigen DQ8 and the recipient has antibody DQ8

## HIGH_RES_WITH_SPLIT

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

## BROAD

1. Donor antigen is in broad resolution and the recipient has a matching
   antibody in split/broad/high resolution
2. Donor antigen is in high/split/broad resolution and the recipient is type B
   and the recipient has a matching antibody in broad resolution

Example for both cases: donor has antigen DQ3 and the recipient has antibody
DQ3.

## HIGH_RES_WITH_BROAD

Donor antigen is in broad resolution and the recipient is type A parsed. Some
antibodies that match donors' antigen in broad resolution are positive and some
are negative.

Example: Donor has antigen A9 and the recipient has antibodies A\*23:01, A\*24:
02 and A\*23:04 and at least one
is over the cutoff, and at least one is below the cutoff.

## UNDECIDABLE

The recipient has antibodies (of any specificity) against antigens that the
donor has not been typed for.

Example: the donor has not been typed for DP and DQ antigens, but the recipient
has an antibody DQB1*03:10.


# Notes

## Configuring cutoff

The original cutoff can be configured. The usual reason is that there
is a patient that really needs a kidney and is highly immunized. In this case,
it might be worth it for the patient to get a kidney from a donor against whom
the patient has antibodies. However, only antibodies with MFI only slightly over
the original cutoff. This is possible in the app via an increase in the cutoff
of the patient. Whether to increase the cutoff and how much is always up to the
user to decide.
