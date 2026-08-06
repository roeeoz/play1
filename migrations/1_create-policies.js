/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.up = (pgm) => {
  pgm.sql(`
    CREATE TABLE policies (
      policy_id           TEXT          PRIMARY KEY,
      coverage_pct        NUMERIC(5,4)  NOT NULL CHECK (coverage_pct >= 0 AND coverage_pct <= 1),
      deductible          NUMERIC(12,2) NOT NULL CHECK (deductible >= 0),
      annual_ceiling      NUMERIC(12,2) NOT NULL CHECK (annual_ceiling >= 0),
      coverage_start      DATE          NOT NULL,
      waiting_period_days INT           NOT NULL CHECK (waiting_period_days >= 0)
    )
  `);
};

/** @param { import("node-pg-migrate").MigrationBuilder } pgm */
exports.down = (pgm) => {
  pgm.sql('DROP TABLE policies');
};
