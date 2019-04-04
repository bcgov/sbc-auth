<template>
  <footer class="app-footer" dark app>
    <div class="container">
      <nav>
        <ul>
          <li><a href="#">Nav Item</a></li>
          <li><a href="#">Nav Item</a></li>
          <li><a href="#">Nav Item</a></li>
          <li><a href="#">Nav Item</a></li>
        </ul>
      </nav>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
};
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  .app-footer
    background-color $BCgovBlue5
    font-size 0.9375rem

  nav
    ul
      margin 0
      padding 0
      list-style-type none

    li
      display block

    a
      color #fff
      text-decoration none

      &:hover
        text-decoration underline

  @media (min-width: 960px)
    nav
      li
        display inline-block

        + li
          margin-left 1rem
          padding-left 1rem
          border-left 1px solid $BCgovBlue3

</style>