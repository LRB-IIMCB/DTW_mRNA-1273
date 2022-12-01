# sDTW_mRNA-1273
Subsequence Dynamic Time Warping functions used for the identification of mRNA-1273 reads in the nanopore DRS raw sequencing data (accompanying article: SARS-CoV-2 mRNA vaccine is re-adenylated in vivo, enhancing antigen production and immune response). 

Reference signal was obtained from one of the reads from the DRS run of crude mRNA-1273 material (read id: [df408ab3-7418-4ee4-9a67-92743257b20a](df408ab3-7418-4ee4-9a67-92743257b20a.tsv)), which was giving good coverage of 3’end of mRNA-1273 reference. The reference contains 5000 sampling points from the raw current DRS readout, 1000 coming from poly(A) tail, to have a good anchoring to the 3'UTR of mRNA-1273, and the rest covering the 3'UTR.

Picture below shows the principles of subsequence Dynamic Time Warping. On the left the reference signal is shown (with poly(A) tail marked in green), on the top - the query signal, with the subsequence matching they query marked in red. 

![Subsequence Dynamic Time Warping](sDTW.png)
