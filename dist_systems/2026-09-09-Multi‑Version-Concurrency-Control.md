# qubit-note: Distributed Systems | Databases & Storage | Multi‑Version Concurrency Control

## Overview

Multi-Version Concurrency Control (MVCC) is a database concurrency technique that maintains multiple versions of each data record to allow simultaneous reads and writes without conflicts, giving each transaction a consistent snapshot of the data. In simple terms, reads do not block writes, and writes do not block reads under MVCC, because each user or transaction works on its own snapshot of data.

This approach is widely used in modern databases to improve performance and avoid locking conflicts, enabling fast, concurrent transactions even under heavy multi-user workloads.



When many users access a database at the same time, some form of concurrency control is needed to keep data consistent.

Without it, a reader could see half-written (inconsistent) data if another user is in the middle of an update.

For example, imagine a bank transfer: if one transaction debits an account and another credits a different account, a concurrent reader might catch the system between those steps and see money “disappear” or partial results.

The database isolation property (the “I” in ACID) is meant to prevent such anomalies by controlling concurrent access.

A traditional solution is to use locks, for instance, making readers wait until a writer finishes (a read-write lock).

While locking does ensure consistency, it introduces contention: long-running reads block writes, and writes block reads, leading to waiting transactions and reduced throughput.

In a high-traffic application, this can become a bottleneck, causing slow performance and even deadlocks (two transactions waiting on each other indefinitely).

MVCC was created to solve this concurrency bottleneck.

Instead of forcing every transaction to line up and take turns, the database keeps multiple copies (versions) of data. This way, each user sees a snapshot of the database at a particular point in time, and writers don’t overwrite existing data until they finish their changes.

Any updates occur on a new version, so other transactions can continue reading the old version without waiting.

Once a writer commits (completes) the changes, the new version becomes the one that future readers will see, while older versions may eventually be cleaned up.

By doing this, MVCC provides isolation and keeps data consistent without relying on coarse locking.

MVCC works on the principle of versioned data and snapshot isolation.

Instead of a single “current value” for each database item, there can be several versions of that item, each tagged with a timestamp or transaction ID indicating when it was created.

Here’s a simplified look at how MVCC enables concurrent reads/writes:

Versioned Records: Each data record in the database carries a version identifier (e.g. a version number or timestamp). New transactions see the latest committed version of a record as of their start time.

Readers Use Snapshots: A read operation always accesses the record version that was the latest and committed when the transaction began. This means the reader sees a consistent snapshot of the database as of its start—no matter what writes occur afterward.

Writers Create New Versions: When a transaction wants to write (update some data), it doesn’t modify the record in place. Instead, it works on a copy of the record (an independent new version). The original version is left untouched so that active readers can still access it.

Non-Blocking Updates: While the writer is updating the copy, other users can continue reading the older version concurrently. There’s no interference: the writer is isolated with its new version, and readers are unaffected by the in-progress change.

Commit and Version Switch: When the write transaction successfully commits, the record’s version is incremented/updated to mark the new data as the latest version. Future transactions or reads will now see this new version (with the updated data).

Continuous Version Cycle: If another update comes along later, the database will again create a new version of the record, leaving the now-previous version as a historical one. In this way, the cycle continues with each update creating a new version while old versions persist for any transactions that still need them.

Under this mechanism, readers and writers don’t block each other.

A reader simply picks the appropriate version (the one valid for its start time) for each data item, and a writer creates a new version for its changes.

In effect, reads never have to wait for writes, and writes don’t have to wait for reads.

Multiple transactions can query or update the same data simultaneously with minimal contention because each one is working with its own versioned view.

The only time transactions need to synchronize is if two writers try to update the exact same item. In that case, the system will allow one to commit and typically abort or retry the other to prevent conflicting changes (this happens at commit time in MVCC).

However, reads never conflict with writes under MVCC’s design, which is the key to its high concurrency.

MVCC is popular because it greatly improves the concurrency and user experience in database systems.

Key benefits include:

No Read Locks Needed (Non-blocking Reads): Under MVCC, reading transactions do not need to lock data, so reads never wait on writes. This leads to faster read performance under heavy load, since queries aren’t stuck behind updates. It also means long-running analytical queries can run without freezing out other updates.

High Concurrency & Throughput: Because reads and writes can happen in parallel, overall throughput increases. Many users can use the system at once with minimal interference, which is ideal for read-heavy or mixed read-write workloads (e.g. web applications, real-time dashboards). The database can handle more transactions per second as it avoids many locking delays.

Reduced Contention and Deadlocks: MVCC diminishes the need for strict locks, thereby cutting down on contention issues where transactions fight over the same data. Fewer locks also mean fewer deadlocks. Scenarios where two transactions each hold a lock the other needs (since reads don’t lock at all in MVCC, the lock wait graph is much simpler). This makes the system more robust under concurrent access.

Consistent Snapshots (Isolation): Every transaction sees a point-in-time consistent snapshot of the data, which avoids problems like dirty reads (seeing uncommitted data) or half-done updates. MVCC provides strong isolation guarantees (often snapshot isolation level), meaning a transaction’s view doesn’t change mid-stream. This improves data integrity without sacrificing concurrency.

Better Read Performance Under Load: For workloads that involve heavy reading (reporting, analytics) alongside writes, MVCC shines. Readers are not blocked by writers, so read performance remains predictable and stable even as updates occur in the background. This is a big advantage for systems that must serve many simultaneous queries.

Overall, MVCC’s optimistic concurrency approach (let transactions proceed without waiting unless there’s a true conflict) provides a smoother experience in multi-user environments than traditional locking.

It lets databases scale to more users and operations with less performance degradation.

While MVCC offers significant advantages, it also comes with a few trade-offs and overheads to be aware of:

Storage Overhead (Multiple Versions): Maintaining several versions of data means the database will use more storage. Every update creates a new copy of a row (or equivalent in an undo log), so a database can grow in size (bloat) due to old versions hanging around. In write-heavy systems or with long transactions, these old versions can accumulate and consume disk space.

Cleanup/Garbage Collection: The system must eventually remove obsolete versions that are no longer needed. MVCC databases require background processes to clean up old records. For example, PostgreSQL uses a VACUUM routine to purge outdated row versions. Managing this cleanup adds complexity and can consume resources. If cleanup doesn’t keep up, performance can suffer from all the extra versions.

Implementation Complexity: MVCC is more complex to implement inside the database engine compared to simple locking. The database must track transaction timestamps, manage version visibility logic, and handle the above-mentioned garbage collection. All of this is hidden from the end user (the DBMS does it behind the scenes), but it’s a complexity cost for the database system. However, this complexity is usually justified by the performance gain.

Write Conflict Handling: Although reads don’t block writes, simultaneous writes to the same data still need to be managed. MVCC typically uses an optimistic approach where conflicts are detected at commit time. This can result in a transaction failing to commit if another committed first on the same record (requiring a retry). Thus, MVCC doesn’t eliminate write-write conflicts; it just handles them differently (often by aborting one transaction), which developers need to be aware of in high-contention scenarios.

Despite these issues, most databases mitigate them with tuning and design (e.g., frequent vacuuming, using indexes to reduce scans of old versions, etc.).

In practice, the benefits outweigh the drawbacks for the majority of applications that need high concurrency.