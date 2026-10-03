import { Account, PostingInput, PostJournalEntryDTO } from './types';

export class LedgerValidationError extends Error {
  constructor(message: string, public readonly details?: unknown) {
    super(message);
    this.name = 'LedgerValidationError';
  }
}

export class LedgerValidator {
  /**
   * Validates a candidate journal entry against fundamental accounting invariants.
   */
  public static validate(dto: PostJournalEntryDTO, accountsMap: Map<string, Account>): void {
    if (!dto.postings || dto.postings.length < 2) {
      throw new LedgerValidationError('A journal entry must contain at least two postings.');
    }

    if (!dto.description || dto.description.trim().length === 0) {
      throw new LedgerValidationError('Journal entry requires a non-empty description.');
    }

    let zeroSumCheck = 0n;
    let hasDebit = false;
    let hasCredit = false;

    for (const posting of dto.postings) {
      // 1. Account existence and status check
      const account = accountsMap.get(posting.accountId);
      if (!account) {
        throw new LedgerValidationError(`Account ID '${posting.accountId}' does not exist.`);
      }
      if (!account.isActive) {
        throw new LedgerValidationError(`Account '${account.code} - ${account.name}' is inactive.`);
      }

      // 2. Amount validity check
      if (posting.amount === 0n) {
        throw new LedgerValidationError(`Posting amount for account '${account.code}' cannot be zero.`);
      }

      // Track debit/credit presence
      if (posting.amount > 0n) hasDebit = true;
      if (posting.amount < 0n) hasCredit = true;

      // 3. Zero-Sum Accumulation
      zeroSumCheck += posting.amount;
    }

    // 4. Double-Entry Atomic Invariant: Sum of debits (+) and credits (-) must equal 0
    if (zeroSumCheck !== 0n) {
      throw new LedgerValidationError(
        `Unbalanced Journal Entry: Sum of postings must equal zero. Imbalance = ${zeroSumCheck.toString()} micro-units.`
      );
    }

    if (!hasDebit || !hasCredit) {
      throw new LedgerValidationError('Journal entry must contain at least one Debit and one Credit.');
    }
  }
}
