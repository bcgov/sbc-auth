<template>
  <v-card>
    <header>Aside Header</header>
    <div class="container">
      Aside Content
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'Aside'
};
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  header
    padding 1.25rem
    color #fff
    background $BCgovBlue5
</style>