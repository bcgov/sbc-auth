var path = require('path')
module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    resolve: {
      alias: {
        'vue': path.resolve('./node_modules/vue')
      }
    }
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuetify'],
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  }
}
