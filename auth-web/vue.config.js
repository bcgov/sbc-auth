const RemoveServiceWorkerPlugin = require('webpack-remove-serviceworker-plugin')
var path = require('path')
module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    plugins: [
      // this is needed to remove existing service workers on users' systems
      // ref: https://www.npmjs.com/package/webpack-remove-serviceworker-plugin
      // ref: https://github.com/NekR/self-destroying-sw/tree/master/packages/webpack-remove-serviceworker-plugin
      new RemoveServiceWorkerPlugin({ filename: 'service-worker.js' })
    ],
    resolve: {
      alias: {
        // Important to have this line otherwise wrong vue instance can happen while including fas-ui.
        '@vue/composition-api': path.resolve('./node_modules/@vue/composition-api'),
        'vue': path.resolve('./node_modules/vue'),
        '$assets': path.resolve('./src/assets/')
      }
    }
  },
  chainWebpack (config) {
    // disable type check for build (composition api library fails)
    if (process.env.NODE_ENV === 'production') config.plugins.delete('fork-ts-checker')
    config.module
      .rule('i18n')
      .resourceQuery(/blockType=i18n/)
      .type('javascript/auto')
      .use('i18n')
      .loader('@intlify/vue-i18n-loader')
      .end()
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuetify', 'vuex-persist', 'fas-ui', 'clickout-event', 'vue-plugin-helper-decorator'],
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  },
  
}
