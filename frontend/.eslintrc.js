// .eslintrc.js
module.exports = {
    root: true,
    env: {
      node: true,
      browser: true,
      es2020: true,
    },
    extends: [
      'plugin:vue/vue3-essential',
      'eslint:recommended',
    ],
    parserOptions: {
      ecmaVersion: 2020,
      sourceType: 'module',
      parser: '@babel/eslint-parser',
      requireConfigFile: false,
    },
    rules: {
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    },
  };
  