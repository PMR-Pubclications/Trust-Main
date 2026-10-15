<?php
/**
 * TRUST-MAIN CRYPTOGRAPHIC AUDIT LEDGER
 * Provides tamper-evident, SHA-256 chained logging for all institutional 
 * outreach, system updates, and evidence transmittals.
 */
class AuditLedger {
    private $logFile;

    public function __construct($logPath = __DIR__ . '/../logs/trust_chain.ledger') {
        $this->logFile = $logPath;
        if (!is_dir(dirname($this->logFile))) {
            mkdir(dirname($this->logFile), 0755, true);
        }
        if (!file_exists($this->logFile)) {
            touch($this->logFile);
        }
    }

    /**
     * Commits a new event to the ledger with cryptographic chaining.
     */
    public function logEvent(string $eventType, array $eventData): string {
        $timestamp = gmdate('Y-m-d\TH:i:s\Z');
        $previousHash = $this->getLastHash();

        $record = [
            'prev_hash'  => $previousHash,
            'timestamp'  => $timestamp,
            'event_type' => $eventType,
            'data'       => $eventData
        ];

        // Generate SHA-256 hash of the exact record structure
        $recordJson = json_encode($record, JSON_UNESCAPED_SLASHES);
        $currentHash = hash('sha256', $recordJson);

        $finalEntry = [
            'hash'   => $currentHash,
            'record' => $record
        ];

        // Append immutably to ledger file
        file_put_contents($this->logFile, json_encode($finalEntry, JSON_UNESCAPED_SLASHES) . PHP_EOL, FILE_APPEND | LOCK_EX);

        return $currentHash;
    }

    /**
     * Retrieves the hash of the most recent ledger entry for chaining.
     */
    private function getLastHash(): string {
        if (!filesize($this->logFile)) {
            return '0000000000000000000000000000000000000000000000000000000000000000'; // Genesis hash
        }
        $lines = file($this->logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if (empty($lines)) {
            return '0000000000000000000000000000000000000000000000000000000000000000';
        }
        $lastLine = end($lines);
        $decoded = json_decode($lastLine, true);
        return $decoded['hash'] ?? '0000000000000000000000000000000000000000000000000000000000000000';
    }

    /**
     * Verifies the mathematical integrity of the entire ledger.
     */
    public function verifyLedger(): bool {
        if (!filesize($this->logFile)) return true;
        
        $lines = file($this->logFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $expectedPrevHash = '0000000000000000000000000000000000000000000000000000000000000000';

        foreach ($lines as $line) {
            $entry = json_decode($line, true);
            if (!$entry || !isset($entry['hash']) || !isset($entry['record'])) {
                return false; // Corrupted structure
            }

            $record = $entry['record'];
            if ($record['prev_hash'] !== $expectedPrevHash) {
                return false; // Chain broken
            }

            // Re-calculate hash
            $recalculatedHash = hash('sha256', json_encode($record, JSON_UNESCAPED_SLASHES));
            if ($recalculatedHash !== $entry['hash']) {
                return false; // Data tampered
            }

            $expectedPrevHash = $entry['hash'];
        }
        return true;
    }
}
