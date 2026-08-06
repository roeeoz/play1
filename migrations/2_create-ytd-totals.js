/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.up = (pgm) => {
  pgm.sql(`
    CREATE TABLE ytd_totals (
      policy_id               TEXT          NOT NULL REFERENCES policies(policy_id),
      year                    SMALLINT      NOT NULL,
      ytd_deductible_consumed NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (ytd_deductible_consumed >= 0),
      ytd_ceiling_consumed    NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (ytd_ceiling_consumed >= 0),
      PRIMARY KEY (policy_id, year)
    )
  `);
};

/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.down = (pgm) => {
  pgm.sql('DROP TABLE ytd_totals');
};
