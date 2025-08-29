import js from '@eslint/js'
import typescript from '@typescript-eslint/eslint-plugin'
import typescriptParser from '@typescript-eslint/parser'
import vue from 'eslint-plugin-vue'
import prettier from 'eslint-plugin-prettier'
import prettierConfig from 'eslint-config-prettier'

export default [
  js.configs.recommended,
  prettierConfig,
  {
    files: ['**/*.{js,jsx,ts,tsx,vue}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module'
      }
    },
    plugins: {
      '@typescript-eslint': typescript,
      'vue': vue,
      'prettier': prettier
    },
    rules: {
      'prettier/prettier': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'vue/multi-word-component-names': 'off'
    }
  },
  {
    files: ['**/*.vue'],
    languageOptions: {
      parser: vue.parser,
      parserOptions: {
        parser: typescriptParser
      }
    }
  }
]