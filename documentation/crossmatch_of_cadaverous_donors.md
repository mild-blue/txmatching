## Evaluating crossmatch with cadaverous donors

When determining a crossmatch, it is essential to consider the antigens of the cadaverous donor and the antibodies of
the recipient. The program offers an API to facilitate this process. For detailed documentation on the data expected by
the API, please refer to the [Swagger documentation](https://txmatching.ikem.cz/doc/), specifically the section on
crossmatch.

The provided list of donors antibodies is first parsed. This is fairly complex process described in
[Antibody parsing](./antibody_parsing.md).
There you can also find the logic how the antibodies are parsed.

Unlike virtual crossmatch in the case of KPD, information about the donor's HLA may be limited in cadaverous virtual crossmatch,
so we work with the so-called "potential HLA typing". This potential HLA typing for the donor is structured as a list of
lists,
where each inner list contains a collection of HLA codes that typically all share the same code at the split level.
Furthermore, each code is accompanied by information about whether it occurs frequently in population or not.
The necessity for having multiple potential HLA codes stems from the occasional
uncertainty about the exact code the donor has, thus we have to consider several variants of one HLA code.

### The determination of donor's most likely HLA typing

To evaluate the potential HLA typing and to determine the assumed HLA typing based on it
with codes the donor likely has, we aim to retain only codes that are present
among antibodies the recipient was tested for. If it isn't possible, we convert these codes to their split version.
However, if there is only one code in the list, we leave it unchanged.

For example, donor has such potential hla typing

```text
A*01:01, frequent
A*01:02, frequent
-
A*02:01, frequent
-
B*01:01, infrequent
B*01:03, frequent
...
```

and recipient has some antibodies

```text
A*01:01
A*02:03
```

In this case the first `A1` potential HLA type is evaluated just as

```text
A*01:01, frequent
```

because crossmatch occurs just with `A1*01:01` antibody.

Further note that in the case of `B1` potential HLA type, the crossmatch did not occur with any of the antibodies,
so this potential HLA type transforms to the assumed HLA type with only one SPLIT:

```text
B1, frequent
```

In the last case, with only one HLA code, `A*02:01`, in the potential HLA type, it will remain unchanged.

### Special crossmatch with theoretical antibodies

One more distinguishing feature of this API compared to the virtual crossmatch in KPD
is the fact that if we have a double antibody that has both chains among the donor's antigens
and splits into two separate theoretical antibodies,
these theoretical antibodies have a negative crossmatch.

For example, donor has such potential hla typing:

```text
DQA1*01:01, frequent
DQB1*02:02, frequent
...
```

And recipient has some antibodies:

```text
DQ[01:01,02:02], MFI 100, cutoff 2000
DQ[01:01,03:03], MFI 3000, cutoff 2000
DQ[01:02,03:03], MFI 100, cutoff 2000
DQ[01:01,04:04], MFI 100, cutoff 2000
```

Note that both chains of the first antibody `DQ[01:01,02:02]` in the list correspond to two
potential HLA typing codes `DQA1*01:01`, respectively `DQB1*02:02`.
Moreover, these antibody chains will be parsed by our algorithm
(which you can also read about in [this document](./antibody_parsing.md)) as two separate theoretical antibodies.
In a normal situation with living patients, a virtual crossmatch on TXM will find a
positive crossmatch with these antigens, but in the case of cadaverous donors,
we evaluate this crossmatch as **negative**.

### Crossmatch description in summary

For each assumed hla type, we return a boolean `is_positive_crossmatch` simply saying if there are any antibodies
positively
crossmatched with it.
The crossmatch situation is described in more detail in `summary` which contains `hla_code` (see
[How to choose summary HLA code?](#how-to-choose-summary-hla-code)), `mfi` (see
[How to calculate summary MFI?](#how-to-calculate-summary-mfi)) and `details_and_issues` (see below).

To describe the crossmatch type, instead of showing the user the crossmatch level as in txm
(see [Virtual crossmatch in TXM](./crossmatch_for_living_donors.md)), we send a message
describing the crossmatch type together with some possible issues in the `details_and_issues` property of the summary.

We do this mainly to distinguish two types of `HIGH_RES` match that can occur:
If the `HIGH_RES` match occurs due to a single HIGH RES antibody matching to single HIGH RES antigen, we send a message:
`There is a single positively crossmatched HIGH RES HLA type - HIGH RES antibody pair.`,
if there are multiple antibody - antigen pairs, we send a different message informing about this: `SPLIT HLA code
displayed in summary, but there are multiple positive crossmatches of HIGH RES HLA type - HIGH RES antibody pairs.`

`HIGH_RES` match can also occur if all positive HIGH RES antibodies correspond to an antigen on SPLIT level (satisfying
some more conditions, described as case 2. and 3. in
the [HIGH_RES match description](./crossmatch_for_living_donors.md#high_res)
In this case we send a message saying: `Recipient was not tested for donor's HIGH RES HLA type (or donor's HLA type
is in SPLIT resolution), but all HIGH RES antibodies corresponding to the summary HLA code on SPLIT level are positively
crossmatched.`

The rest of match types are described with corresponding messages in a straightforward manner.

We illustrate this on some examples:

1.

```text
Assumed HLA types:
    B*07:04, frequent
    B*07:05, frequent

Recipient's antibodies:
    B*07:04, MFI 2500, cutoff 2000
    B*07:06, MFI 2500, cutoff 2000
```

There is a single match between HIGH RES hla type and HIGH RES antibody, we return message:
`There is a single positively crossmatched HIGH RES HLA type - HIGH RES antibody pair.`

2.

```text
Assumed HLA types:
    B*07:04, frequent
    B*07:05, frequent

Recipient's antibodies:
    B*07:04, MFI 2500, cutoff 2000
    B*07:05, MFI 2500, cutoff 2000
```

As there are multiple matches between HIGH RES hla type and HIGH RES antibody, we return message:
`SPLIT HLA code displayed in summary, but there are multiple positive crossmatches of HIGH RES HLA type - HIGH RES
antibody pairs.`

3.

```text
Assumed HLA types:
    B*07:03, infrequent
    B*07:04, infrequent
    B*07:05, infrequent

Recipient's antibodies:
    B*07:06, MFI 2500, cutoff 2000
    B*07:07, MFI 2500, cutoff 2000
```

In summary, we send a message: `Recipient was not tested for donor's HIGH RES HLA type (or donor's HLA type
is in SPLIT resolution), but all HIGH RES antibodies corresponding to the summary HLA code on SPLIT level are positively
crossmatched.`

### Allele frequencies in a population

There is one more aspect that we want to take into account:
each allele occurs with varying frequencies. For instance, `A*01:02:03:05` is a very rare allele,
whereas `A*01:02:01:01` is quite common, but both are shortened to the same form: `A*01:02`.

Furthermore, for a brief summarization of this match, we select HLA code and MFI
that best represents the presence or absence of a crossmatch.

For summary HLA code, we consider only the the matches with frequent HLA codes (up to some edge cases described later
in this text). From those matches, we filter out those with highest severity (based on match type).
Rest of the codes are less important and not considered for the summary.

#### How to calculate the most important match type?

In the summary, we only consider the most important crossmatch level that has occurred with the assumed HLA types.
Priority is arranged in the following way:

```text
1. HIGH_RES
2. HIGH_RES_WITH_SPLIT
3. HIGH_RES_WITH_BROAD
4. SPLIT
5. BROAD
6. THEORETICAL
7. UNDECIDABLE
8. NONE
```

For example, if some antibodies crossmatched at the `HIGH_RES` level, others at the `SPLIT` level,
then for the summary we would only consider the `HIGH_RES` matches as the most important of these.

#### How to choose summary HLA code?

For summary, we would like to take into account just frequent codes among all assumed HLA types.
When this code is the only one, then everything is quite simple, we consider this code as a summary,
but there are situations when there are several frequent codes in the list. In this case, we will take a split of these
codes if it is common, if there are several such splits, then we will take the one that corresponds to the antibody
with the highest MFI.
For example:

```text
Assumed HLA types:
    A*01:01, frequent
    A*02:01, frequent
    A*01:03, infrequent

Recipient's antibodies:
    A*01:01, MFI 3000, cutoff 2000
    A*02:01, MFI 4000, cutoff 2000
    A*01:03, MFI 5000, cutoff 2000
```

So the summarization code will be `A2`, because `A*02:01` has the highest MFI among frequent codes `A*01:01` and
`A*02:01`.

#### How to calculate summary MFI?

Again we take into account only frequent codes among the assumed HLA types.
We will consider the summary MFI as the arithmetic mean MFI values above cutoff of the corresponding antibodies.
In case there are no MFI values above cutoff for the frequent HLA code, we use the highest MFI value among infrequent
antibodies which are unlikely to crossmatch as the summary MFI. Also, we send describing issue:
`There is most likely no crossmatch, but there is a small chance that a crossmatch could occur. Therefore,
this case requires further investigation.`
(Do not forget that in the absolute majority of cases, the assumed HLA types list always has at least one frequent code
due to the fact that we convert the list of extremely rare codes to the SPLIT level. Therefore, the absence of frequent
codes in the assumed HLA types can be only in cases when SPLIT code does not exist or is unknown to our database).
For example,

```text
Assumed HLA types:
    A*01:01, frequent
    A*02:01, frequent
    A*01:03, infrequent

Recipient's antibodies:
    A*01:01, MFI 3000, cutoff 2000
    A*02:01, MFI 4000, cutoff 2000
    A*01:03, MFI 5000, cutoff 2000
```

The summary MFI in this case will be `4000`, because we just calculated the arithmetic mean MFI values for frequent
codes that have the summary HLA code at low res level `A*02:01`: `(4000) / 1 = 4000`. Also, we will send crossmatch
issue
`Ambiguity in HLA typization, for more see detailed section`.

#### Summary in case of no positive crossmatch

The description above assumes that there are some antibodies crossmatched with the frequent assumed HLA types.
It can, however, happen that there are no such antibodies (all the antibodies that supported the determination of
assumed hla typing have mfi values below cutoff).
In such case, we simply look for the antibody with highest mfi value among the antibodies that match with some of the
frequent assumed hla types and display this antibody in the summary.

A rare case can occur, where there is no antibody with HLA code matching to any of the assumed HLA types.
This can for example happen if there is an HLA type of special form ending with letter (e.g. `A*01:01N`).
In this case, we display the assumed HLA type as the HLA code in the summary with mfi set to `None`.

#### More examples for crossmatch summarization. Crossmatch issues during the summary count.

1. The recipient has no positively crossmatched antibodies against donor's assumed hla types:

```text
Assumed HLA types:
    B*07:04, frequent
    B*07:05, frequent

Recipient's antibodies:
    B*07:04, MFI 1500, cutoff 2000
    B*07:05, MFI 1000, cutoff 2000
```

This example corresponds to the last described case (with no positive crossmatch).
The summary HLA code will be `B*07:04` with summary MFI `1500`.
A crossmatch issue:
`There are no frequent antibodies crossmatched against this HLA type, the HLA code in summary
corresponds to an antibody with mfi below cutoff and is therefore not displayed in the list of matched antibodies.`
is sent to describe this.

2. The recipient doesn't have any **frequent** **positive** crossmatched antibodies against donor's assumed HLA types:

```text
Assumed HLA types:
    B*07:02, frequent
    B*07:04, infrequent

Recipient's antibodies:
    B*07:02, MFI 1000, cutoff 2000
    B*07:04, MFI 3000, cutoff 2000
```

In this case, there is only a positive crossmatch for `B*07:04`, but such a match is very unlikely because
this HLA is rare in the population, so we send crossmatch issue
`There is most likely no crossmatch, but there is a small chance that a crossmatch could occur.
Therefore, this case requires further investigation`. Also, we send `B7` as summary code and `None` as MFI value.

3. The donor has the only one SPLIT HLA code in the assumed HLA types list:

```text
Assumed HLA types:
    A1, frequent

Recipient's antibodies:
    A*01:01, MFI 3000, cutoff 2000
    A*01:02, MFI 100, cutoff 2000
    A*01:03, MFI 5000, cutoff 2000
```

So summary HLA code will be `A1` with summary MFI `= (3000 + 5000) / 2 = 4000`
(antibody `A*01:02` wasn't included, because it has MFI below cutoff)

!! Tady by to melo byt tak, ze bude zas dsa hlaska

4. The donor has several SPLIT HLA codes in the assumed HLA types list:

```text
Assumed HLA types:
    A1, frequent
    A2, frequent

Recipient's antibodies:
    A*01:01, MFI 3000, cutoff 2000
    A*02:01, MFI 2100, cutoff 2000
    A*02:02, MFI 100, cutoff 2000
```

In this case the summary HLA code is `A1`, because it has the highest MFI among antibodies (see `A*01:01, mfi 3000`).
The MFI value `= (3000) / 1 = 3000` (antibody `A*02:01` wasn't included, because it has different SPLIT code than
summary HLA code. `A*02:02` also has MFI below cutoff, so it wasn't included too).

5. The donor has several frequent HIGH RES codes that have **the same SPLIT** level in the assumed HLA types list:

```text
Assumed HLA types:
    B*07:02, frequent
    B*07:04, frequent
    B*07:05, frequent

Recipient's antibodies:
    B*07:02, MFI 3000, cutoff 2000
    B*07:04, MFI 4000, cutoff 2000
    B*07:05, MFI 100, cutoff 2000
```

So we just take their SPLIT `B7` as summary HLA code. The summary MFI is calculated via `= (3000 + 4000) / 2 = 3500`
(antibody `B*07:05` wasn't included, because it has MFI below cutoff). Also, we send a describing crossmatch issue
`Antibodies against this HLA Type might not be DSA, for more see detailed section` about this situation.

6. The donor has several frequent HIGH RES codes that have **different SPLIT** levels in the assumed HLA types list:

```text
Assumed HLA types:
    B*07:02, frequent
    B*08:01, frequent
    B*08:02, frequent

Recipient's antibodies:
    B*07:02, MFI 3000, cutoff 2000
    B*08:01, MFI 1990, cutoff 2000
    B*08:02, MFI 2500, cutoff 2000
```

So the summary HLA code is `B7`, because it has the highest MFI among antibodies (see `B*07:02, mfi 3000`).
The MFI value `= (3000) / 1 = 3000` (antibody `B*08:02` wasn't included, because it has different SPLIT code than
summary HLA code. `B*08:01` also has MFI below cutoff, so it wasn't included too).
In this case not all corresponding antibodies have MFI above cutoff (see `B*08:01`), so we show
crossmatch issue `Antibodies against this HLA Type might not be DSA, for more see detailed section`.

In case if all antibodies have MFI above cutoff:

```text
Assumed HLA types:
    B*07:02, frequent
    B*08:01, frequent
    B*08:02, frequent

Recipient's antibodies:
    B*07:02, MFI 3000, cutoff 2000
    B*08:01, MFI 2100, cutoff 2000
    B*08:02, MFI 2500, cutoff 2000
```

The summary HLA code is still `B7` with the MFI value `= (3000) / 1 = 3000`, but we send crossmatch issue
`Ambiguity in HLA typization, for more see detailed section`.

!! tohle by klidne mohlo byt taky to s tim DSA, neni to moc odlisny case od toho drhyho

7. The donor has the only one frequent HIGH RES HLA codes in the assumed HLA types list,
   and at the same time it has MFI **ABOVE** cutoff (otherwise see 0.):

```text
Assumed HLA types:
    B*07:02, frequent

Recipient's antibodies:
    B*07:02, MFI 3000, cutoff 2000
```

In this simple case the summary HLA code will be `B*07:02` with summary MFI value `3000`.

8. The recipient has no antibodies that match with the donor's assumed HLA types:

```text
Assumed HLA types:
    A*01:01N, infrequent

Recipient's antibodies:
    A*01:01, MFI 3000, cutoff 2000
```

In this case, HLA code `A*01:01N` cannot be matched with the antibody (not even in low resultion, as this special code
has the low resolution undefined).
Consequently, the corresponding list of matched antibodies to choose the summary antibody from is empty.
The summary HLA code is therefore set to `A*01:01N` with summary MFI `None` and a warning is sent:
`No matching antibody was found against this HLA type, HLA code displayed in summary taken from the HLA type` .
!! Zkontrolovat ze by tohle fungovalo i kdyby tam misto ty nulty allely A*01:01N A*02:02
!! Rozdelit na nutly allely a neexprimovany
