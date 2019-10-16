module.exports = {
  configureWebpack: {
    devtool: 'source-map'
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuex-persist', 'vuetify'],
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  }
}
