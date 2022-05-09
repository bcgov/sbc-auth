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
    'no-console': 'error',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'sort-imports': 'error',
    'space-before-function-paren': 1,
    'no-use-before-define': 'off',
    '@typescript-eslint/no-use-before-define': 'error'
  },
  parserOptions: {
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint']
  }
}
