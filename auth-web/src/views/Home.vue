<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>File BC Co-operative <span>Annual Reports</span></h1>
        <p class="intro-text">Sign in to start filing your BC Co-operative Annual Report. You will need to provide your <em>Incorporation Number</em> and your <em>Passcode</em> in the letter you received in the mail.</p>
        <v-card class="sign-in-card">
          <v-container>
            <h2>Sign In</h2>
            <PasscodeForm/>
          </v-container>
        </v-card>
      </article>
      <aside>
        <SupportInfoCard/>
      </aside>
    </div>
  </v-container>
</template>

<script>
import Vue from 'vue'
import PasscodeForm from '@/components/auth/PasscodeForm.vue'
import SupportInfoCard from '@/components/SupportInfoCard.vue'

export default ({
  name: 'Home',
  components: {
    PasscodeForm,
    SupportInfoCard
  }
})
</script>

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
