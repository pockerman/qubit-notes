# qubit-note: Distributed Systems | Databases & Storage | Checksums & Etags


## Overview

Checksums are short digital fingerprints of data used to verify integrity, and ETags (entity tags) are unique identifiers often derived from checksums or hashes that web and storage systems use to track data versions and detect changes.

What Is a Checksum? (Data Integrity Basics)
A checksum is a small code calculated from a block of digital data to detect errors or alterations. By recomputing the checksum later and comparing it to the original value, you can verify whether the data has changed.

If the checksums match, the data is almost certainly unaltered.

Checksums are widely used for data integrity in storage and transmission, for example, to ensure a file wasn’t corrupted during download or to detect disk errors. They don’t by themselves prove authenticity (i.e. who created the data), but they excel at catching accidental corruption.

Common checksum algorithms range from simple ones (like parity bits or summing bytes) to more complex hash functions.

Good checksum algorithms change significantly even if the input data changes only a little. This property means even a one-bit error in the data will result in a very different checksum value, alerting us to corruption.