# Response to Reviewer 2

## Comment 1

> The reference set seems too small to be reliable, and it might bias the filter.

We thank the reviewer for this question. We would like to clarify that the reference set has 64 verified samples,
and Table 6 shows that accuracy changes by less than 0.3 points between 32 and 128 samples. We acknowledge that a
larger set would make the estimate tighter. Admittedly, we did not test sets above 128 samples. Larger reference
sets are beyond the scope of this paper, and Section 7 now says so.

## Comment 2

> Why is the threshold fixed?

We apologize for the confusion. Due to space limitations the sensitivity study was in Appendix C, and it is now
in Section 5.3. In some cases the filter may potentially discard clean samples.
