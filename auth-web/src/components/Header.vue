<template>
  <header class="app-header" dark fixed app>
    <div class="container">
      <router-link to="/" class="navbar-brand">
        <img class="brand-img" src="@/assets/img/gov3_bc_logo.png"
          alt="Province of British Columbia Logo"
          title="Province of British Columbia"/>
      </router-link>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Header'
};
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  .app-header
    position fixed
    display flex
    align-items: center;
    width 100%
    color #fff
    border-bottom 3px solid $BCgovGold5
    background-color $BCgovBlue5

    .container
      padding-top 0
      padding-bottom 0

  .brand-img
    margin-top 0.2rem

</style>
