module.exports = {
  publicPath: 'auth-app',
  configureWebpack: {
    devtool: 'source-map'
  },
  devServer: {
    proxy: 'https://auth-api-dev.pathfinder.gov.bc.ca/'
  }
}
