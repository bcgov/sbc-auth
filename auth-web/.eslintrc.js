module.exports = {
  root: true,
  env: {
    es2021: true
  },
  'extends': [
    'plugin:vue/essential',
    '@vue/standard',
    '@vue/typescript'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'sort-imports': 'error',
    'space-before-function-paren': 1,
    'no-use-before-define': 'off',
    '@typescript-eslint/no-use-before-define': ['error', { 'functions': false, 'classes': true, 'variables': true }],
    'no-unused-expressions': 'off',
    '@typescript-eslint/no-unused-expressions': ['error', { 'allowShortCircuit': true, 'allowTernary': true }],
    'vue/multi-word-component-names': ['error', { 'ignores': ['Transactions'] }],
    // Not ideal but shallowOnly option isn't working for this, so leaving it off for now.
    // https://eslint.vuejs.org/rules/no-mutating-props.html
    'vue/no-mutating-props': 'off'
  },
  parserOptions: {
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint']
  }
}
