const tseslint = require("typescript-eslint");
const prettierConfig = require("eslint-config-prettier");

module.exports = [
  ...tseslint.configs.recommended,
  prettierConfig,
  {
    ignores: ["**/dist/**", "**/node_modules/**", "vitest.config.ts"],
  },
];
