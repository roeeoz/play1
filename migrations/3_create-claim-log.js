/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.up = (pgm) => {
  pgm.sql(`
    CREATE TABLE claim_log (
      claim_id     TEXT        PRIMARY KEY,
      policy_id    TEXT        NOT NULL REFERENCES policies(policy_id),
      year         SMALLINT    NOT NULL,
      processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
  `);
};

/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.down = (pgm) => {
  pgm.sql('DROP TABLE claim_log');
};
