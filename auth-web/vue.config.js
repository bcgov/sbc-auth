var path = require('path')
module.exports = {
  configureWebpack: {
    devtool: 'source-map',
    resolve: {
      alias: {
        'vue': path.resolve('./node_modules/vue'),
        '$assets': path.resolve('./src/assets/')
      }
    }
  },
  publicPath: process.env.VUE_APP_PATH,
  transpileDependencies: ['vuetify', 'vuex-persist', 'fas-ui', 'clickout-event', 'vue-plugin-helper-decorator'],
  devServer: {
    overlay: {
      warnings: true,
      errors: true
    }
  },
  pwa: {
    name: 'Business Registry',
    themeColor: '#003366',
    msTileColor: '#fcba19',
    appleMobileWebAppCapable: 'yes',
    appleMobileWebAppStatusBarStyle: 'black',
    manifestOptions: {
      name: 'Business Registry',
      short_name: 'Business Registry',
      start_url: '/business/auth/',
      display: 'standalone',
      theme_color: '#003366',
      background_color: '#fcba19',
      scope: '.'
    },
    iconPaths: {
      favicon32: 'img/icons/favicon-32x32.png',
      favicon16: 'img/icons/favicon-16x16.png',
      appleTouchIcon: 'img/icons/apple-touch-icon-152x152.png',
      maskIcon: 'img/icons/safari-pinned-tab.svg',
      msTileImage: 'img/icons/msapplication-icon-144x144.png'
    },
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      // swSrc is required in InjectManifest mode.
      swSrc: 'src/service-worker.js',
      // skip precaching json files such as configs
      exclude: [/\.json$/, /\.map$/, /^manifest.*\.js(?:on)?$/]
    }
  }
}
