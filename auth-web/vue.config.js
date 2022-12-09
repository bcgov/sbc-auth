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
        'vue': path.resolve('./node_modules/vue'),
        '$assets': path.resolve('./src/assets/')
      }
    }
  },
  chainWebpack(config) {
    // disable type check for build (composition api library fails)
    if (process.env.NODE_ENV === 'production') config.plugins.delete('fork-ts-checker')
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuetify', 'vuex-persist', 'fas-ui', 'clickout-event', 'vue-plugin-helper-decorator'],
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  }
}
