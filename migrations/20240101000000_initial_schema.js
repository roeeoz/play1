/** @type {(pgm: import('node-pg-migrate').MigrationBuilder) => void} */
exports.up = (pgm) => {
  pgm.createTable('policies', {
    policy_id: { type: 'varchar(255)', primaryKey: true },
    coverage_pct: { type: 'numeric(10,6)', notNull: true },
    deductible: { type: 'numeric(14,2)', notNull: true },
    annual_ceiling: { type: 'numeric(14,2)', notNull: true },
    coverage_start: { type: 'date', notNull: true },
    waiting_period_days: { type: 'integer', notNull: true },
  });

  pgm.createTable('ytd_totals', {
    policy_id: {
      type: 'varchar(255)',
      notNull: true,
      references: '"policies"',
      onDelete: 'CASCADE',
    },
    year: { type: 'integer', notNull: true },
    ytd_deductible_consumed: { type: 'numeric(14,2)', notNull: true, default: 0 },
    ytd_ceiling_consumed: { type: 'numeric(14,2)', notNull: true, default: 0 },
  });
  pgm.addConstraint('ytd_totals', 'ytd_totals_pkey', 'PRIMARY KEY (policy_id, year)');

  pgm.createTable('claims', {
    claim_id: { type: 'varchar(255)', primaryKey: true },
    policy_id: { type: 'varchar(255)', notNull: true },
    reimbursement: { type: 'numeric(14,2)', notNull: true },
    reason: { type: 'varchar(50)', notNull: true },
    deductible_applied: { type: 'numeric(14,2)', notNull: true },
    processed_at: {
      type: 'timestamptz',
      notNull: true,
      default: pgm.func('NOW()'),
    },
  });
};

/** @type {(pgm: import('node-pg-migrate').MigrationBuilder) => void} */
exports.down = (pgm) => {
  pgm.dropTable('claims');
  pgm.dropTable('ytd_totals');
  pgm.dropTable('policies');
};
