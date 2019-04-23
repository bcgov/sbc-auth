<template>
  <v-card flat>
    <header>Need Assistance?</header>
    <div class="container">

      {{ $t('helpText') }}
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'Aside'
}
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  header
    padding 1.25rem
    color #fff
    background $BCgovBlue5
</style>
