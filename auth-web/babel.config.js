module.exports = {
  'presets': [
    [
      '@vue/app',
      {
        'useBuiltIns': 'entry'
      }
    ]
  ],
  'env': {
    'test': {
      'plugins': ['transform-require-context']
    }
  },
  'compact': true
}
