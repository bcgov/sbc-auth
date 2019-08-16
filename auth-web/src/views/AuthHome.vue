<template>
  <div class="view-container">
    <article>
      <p class="intro-text"><span><h1>Quick and easy access to BC Government and partner services for legal, business, government and professionals.</h1></span></p>

        <v-btn class="sign-in-btn" @click="login" color="primary" large to="/createaccount">
          <span>Create an Account</span>
        </v-btn>
        <v-btn class="sign-in-btn" @click="login" color="primary" large>
          <span>Learn More</span>
        </v-btn>
    </article>

  </div>
</template>

<style lang="stylus" scoped>
  @import "../assets/styl/theme.styl"

  h1, h2
    margin-bottom 1.5rem

  article
    flex 1 1 auto

  aside
    flex 0 0 auto
    margin-top 2rem

  .intro-text
    margin-bottom 2rem
    letter-spacing -0.01rem
    font-size 1rem
    font-weight 300

    em
      font-style normal
      font-weight 400

  .view-container
    display flex
    flex-flow column nowrap

  .sign-in-card .container
    padding 1.5rem

  @media (max-width 480px)
    h1 span
      display block

  @media (min-width 768px)
    h1
      margin-bottom 2rem

    .intro-text
      margin-bottom 3rem
      font-size 1.125rem

  @media (min-width: 960px)
    article
      padding-top 0.8rem
      padding-bottom 0.8rem

    aside
      margin-top 0
      margin-left 2rem
      width 20rem

    .sign-in-card .container
      padding 2rem

    .view-container
      flex-flow row nowrap

</style>
