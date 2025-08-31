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
      vue: vue,
      prettier: prettier
    },
    rules: {
      'prettier/prettier': 'error',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      'vue/multi-word-component-names': 'off',

      // ==========================================
      // Modular boundary enforcement
      // ==========================================
      'no-restricted-imports': [
        'error',
        {
          patterns: [
            {
              group: ['@features/*/components/*', '@features/*/services/*', '@features/*/stores/*'],
              message:
                "Deep imports into features are not allowed. Use the feature's public barrel export or shared API client."
            },
            {
              group: ['../features/*', '../../features/*', '../../../features/*'],
              message:
                'Relative imports between features are not allowed. Use path aliases and public exports.'
            },
            {
              group: [
                '@features/documents/*',
                '@features/pm-templates/*',
                '@features/risk-inspections/*'
              ],
              message:
                'Direct imports between feature modules are not allowed. Features must be independent.'
            }
          ],
          paths: [
            {
              name: '@features/documents',
              importNames: ['*'],
              message: 'Import specific exports from @features/documents/index.ts only'
            },
            {
              name: '@features/pm-templates',
              importNames: ['*'],
              message: 'Import specific exports from @features/pm-templates/index.ts only'
            },
            {
              name: '@features/risk-inspections',
              importNames: ['*'],
              message: 'Import specific exports from @features/risk-inspections/index.ts only'
            }
          ]
        }
      ],

      // Enforce using path aliases instead of relative imports
      'no-restricted-syntax': [
        'error',
        {
          selector: 'ImportDeclaration[source.value=/^\\.\\.\\//]',
          message:
            'Use path aliases (@features, @shared, @app) instead of relative imports going up directories'
        }
      ]
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
