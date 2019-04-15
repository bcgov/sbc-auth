<template>
  <v-card flat>
    <header>Need Assistance?</header>
    <div class="container">
      For questions or assistance with about filing online, contact the our help desk at 1-800-663-6102 from 8:00 a.m. to 7:00 p.m. Monday to Friday except statutory holidays.
    </div>
  </v-card>
</template>

<script>
export default {
  name: 'SupportInfoCard'
};
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