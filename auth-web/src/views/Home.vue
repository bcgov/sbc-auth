<template>
  <div class="view-container">
    <article>
      <h1>Page Title</h1>
      <p class="mb-0">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?</p>
    </article>
    <aside>
      <v-card flat>
        <header>Aside Header</header>
        <div class="container">
          Aside Content
        </div>
      </v-card>
    </aside>
  </div>
</template>

<script>
import Vue from 'vue';
import Aside from '@/components/Aside.vue';

export default ({
  name: 'Home'
});
</script>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  .view-container
    display flex
    flex-flow column nowrap

  article
    flex 1 1 auto

  aside
    flex 0 0 auto
    margin-top 2rem

  .v-card header
    padding 1rem 1.25rem
    color #fff
    background-color $BCgovBlue5

  @media (min-width: 960px)
    .view-container
        flex-flow row nowrap

    aside
      margin-top 0
      margin-left 2rem
      width 20rem

</style>