export enum AccountType {
  ASSET = 'ASSET',
  LIABILITY = 'LIABILITY',
  EQUITY = 'EQUITY',
  REVENUE = 'REVENUE',
  EXPENSE = 'EXPENSE',
}

export enum NormalBalance {
  DEBIT = 'DEBIT',
  CREDIT = 'CREDIT',
}

export interface Account {
  id: string;
  code: string;
  name: string;
  type: AccountType;
  normalBalance: NormalBalance;
  currency: string;
  isActive: boolean;
  createdAt: Date;
}

export interface PostingInput {
  accountId: string;
  /** Amount in micro-units (e.g., $10.50 USD = 10_500_000n). Positive for Debit, Negative for Credit. */
  amount: bigint;
  description?: string;
}

export interface Posting extends PostingInput {
  id: string;
  journalEntryId: string;
  createdAt: Date;
}

export enum JournalStatus {
  POSTED = 'POSTED',
  REVERSED = 'REVERSED',
}

export interface PostJournalEntryDTO {
  description: string;
  referenceId?: string;
  postings: PostingInput[];
  metadata?: Record<string, unknown>;
}

export interface JournalEntry {
  id: string;
  description: string;
  referenceId?: string;
  reversesJournalId?: string;
  status: JournalStatus;
  metadata?: Record<string, unknown>;
  postedAt: Date;
  postings: Posting[];
}

export interface TrialBalanceRow {
  accountId: string;
  accountCode: string;
  accountName: string;
  totalDebits: bigint;
  totalCredits: bigint;
  netBalance: bigint;
}
