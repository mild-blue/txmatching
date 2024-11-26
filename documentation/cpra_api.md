## Calculated Panel Reactive Antibody (cPRA)

We offer a public API for cPRA calculation using the [ETRL VPRA Calculator](https://www.etrl.org/vPRA.aspx)
(based on consultation with IKEM, cPRA and vPRA are the same terms for us).
The procedure is straightforward: you need to input antibodies along with their MFI values in the same format as in TXM.
Subsequently, we will parse the antibodies using the algorithm
described [below](./antibody_parsing.md) and provide parsed antibodies along with parsing issues,
just as you're accustomed to.

The most important aspect is that we will send to the [ETRL server](https://www.etrl.org/calculator4.0/calculator4.0.asmx)
parsed antibodies with MFI above the cutoff as
["unacceptable antibodies"](https://journals.lww.com/co-transplantation/Fulltext/2008/08000/Defining_unacceptable_HLA_antigens.14.aspx)
once we convert them into the [required format](https://etrl.eurotransplant.org/resources/hla-tables/) they use.
Afterward, we will show the received CPRA in the output.

**It should be noted that by prior agreement with IKEM, we won't consider**:
- Theoretical antibodies
- Double antibodies (antibodies with two HLA codes)
