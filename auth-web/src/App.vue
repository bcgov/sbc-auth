<template>
  <v-app class="app-container" id="app">
    <Header/>
    <div class="app-body">
      <div class="app-body__inner">
        <div class="container">
          <main>
            <router-view/>
          </main>
        </div>
      </div>
    </div>
    <Footer/>
  </v-app>
</template>

<script>
import Vue from 'vue';
import Header from './components/Header.vue';
import Footer from './components/Footer.vue';

export default Vue.extend({
  name: 'app',
  components: {
    Header,
    Footer
  }
});
</script>

<style lang="stylus">
  @import "./assets/styl/base.styl";
  @import "./assets/styl/layout.styl";
  @import "./assets/styl/overrides.styl";
</style>