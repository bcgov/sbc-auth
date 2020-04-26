module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/essential',
    '@vue/standard',
    '@vue/typescript'
  ],
  rules: {
    'sort-imports': 'error',
    'space-before-function-paren': 1
  },
  parserOptions: {
    parser: '@typescript-eslint/parser'
  }
}
