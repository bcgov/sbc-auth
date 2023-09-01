module.exports = {
  root: true,
  env: {
    es2021: true
  },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:vue/base',
    'plugin:vue/essential',
    'plugin:vue/recommended',
    'plugin:vue/strongly-recommended',
    // Disabling these until the time is right.
    // 'plugin:vue/vue3-essential',
    // 'plugin:vue/vue3-recommended',
    // 'plugin:vue/vue3-strongly-recommended',
    'plugin:vuetify/base',
    'plugin:vuetify/recommended',
    '@vue/standard',
    '@vue/typescript'
  ],
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
    'no-case-declarations': 'warn',
    'sort-imports': 'error',
    'space-before-function-paren': 1,
    'no-use-before-define': 'off',
    'max-len': ['warn', { code: 150, ignoreRegExpLiterals: true }],
    'vue/attribute-hyphenation': 'off',
    'vue/no-deprecated-filter': 'warn',
    'vue/no-deprecated-slot-scope-attribute': 'warn',
    'vue/no-deprecated-v-bind-sync': 'off', // FUTURE: Fix deprecated v-bind sync
    'vue/no-deprecated-v-on-native-modifier': 'off', // Enable for Vue3
    'vue/no-v-for-template-key-on-child': 'off', // Enable for Vue 3
    'vue/no-v-html': 'off',
    'vue/v-on-event-hyphenation': 'off',
    // Off for now, might want to turn on for Vue3.
    'vue/no-v-model-argument': 'off',
    // Some of these can be infered by their default.
    'vue/require-prop-types': 'off',
    '@typescript-eslint/ban-types': 'warn',
    '@typescript-eslint/no-duplicate-enum-values': 'warn',
    '@typescript-eslint/no-empty-function': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
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
