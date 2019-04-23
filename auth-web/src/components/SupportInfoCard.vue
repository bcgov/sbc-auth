<template>
  <v-card>
    <header>Need Assistance?</header>
    <div class="container">
      {{ $t('helpText') }}
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'SupportInfoCard'
}
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  header
    padding 1rem 1.25rem
    color #fff
    background $BCgovBlue5
    font-weight 700

  .v-card
    font-size: 0.875rem

</style>
