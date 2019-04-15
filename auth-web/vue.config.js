module.exports = {
  configureWebpack: {
    devtool: 'source-map'
  },
  devServer: {
    proxy: 'https://auth-api-dev.pathfinder.gov.bc.ca/',
  }
}
