import js from '@eslint/js';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import prettier from 'eslint-plugin-prettier';

export default [
  js.configs.recommended,
  {
    files: ["**/*.{js,jsx,ts,tsx}"] ,
    languageOptions: {
      parser: typescriptParser,
      ecmaVersion: "latest",
      sourceType: "module",
      globals: {
        React: "readonly"
      }
    },
    plugins: {
      react,
      'react-hooks': reactHooks,
      '@typescript-eslint': typescript,
      'jsx-a11y': jsxA11y,
      prettier
    },
    rules: {
      'prettier/prettier': "error",
      'react/react-in-jsx-scope': "off",
      'react/prop-types': "off"
    },
    settings: {
      react: {
        version: "detect"
      }
    }
  }
];
