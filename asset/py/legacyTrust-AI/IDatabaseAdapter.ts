import { Account, JournalEntry, Posting, TrialBalanceRow } from './types';

export interface IDatabaseClient {
  query<T = unknown>(sql: string, params?: unknown[]): Promise<T[]>;
}

export interface IDatabaseAdapter {
  /** Run logic inside an isolated, atomic database transaction */
  transaction<T>(work: (client: IDatabaseClient) => Promise<T>): Promise<T>;
  getAccountsByIds(ids: string[], client?: IDatabaseClient): Promise<Account[]>;
  saveJournalWithPostings(entry: JournalEntry, client: IDatabaseClient): Promise<JournalEntry>;
  markJournalReversed(journalId: string, client: IDatabaseClient): Promise<void>;
  getJournalById(journalId: string, client?: IDatabaseClient): Promise<JournalEntry | null>;
  calculateAccountBalance(accountId: string, client?: IDatabaseClient): Promise<bigint>;
  generateTrialBalance(client?: IDatabaseClient): Promise<TrialBalanceRow[]>;
}
