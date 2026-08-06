import { defineConfig } from "vitest/config";
import { resolve } from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@claim-engine/types": resolve(__dirname, "packages/types/src/index.ts"),
      "@claim-engine/input": resolve(__dirname, "packages/input/src/index.ts"),
      "@claim-engine/engine": resolve(
        __dirname,
        "packages/engine/src/index.ts",
      ),
      "@claim-engine/runner": resolve(
        __dirname,
        "packages/runner/src/index.ts",
      ),
    },
  },
  test: {
    passWithNoTests: true,
    coverage: {
      enabled: true,
    },
  },
});
