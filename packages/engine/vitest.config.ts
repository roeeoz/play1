import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    include: ['src/**/__tests__/**/*.test.ts'],
  },
  resolve: {
    alias: {
      '@claim-engine/types': resolve(__dirname, '../../packages/types/src/index.ts'),
    },
  },
});
