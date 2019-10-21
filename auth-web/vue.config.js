module.exports = {
  configureWebpack: {
    devtool: 'source-map'
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
