module.exports = {
  configureWebpack: {
    devtool: 'source-map'
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuex-persist','vuetify'],
  devServer: {
    // not used
    proxy: {
      '/auth/api/*': {
        target: 'https://auth-api-dev.pathfinder.gov.bc.ca/api/v1', // if your local server is running , use that here
        pathRewrite: {
          '/auth/api/': ''
        }
      },
      '/pay/api/*': { // TODO I havent tested this..but hopefully it will work..
        target: 'https://pay-api-dev.pathfinder.gov.bc.ca/api/v1',
        pathRewrite: {
          '/pay/api/': ''
        }
      }
    }
  }
}
