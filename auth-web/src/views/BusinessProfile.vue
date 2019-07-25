<template>
  <div class="view-container">
    <article>
      <h1>Update Business Profile</h1>
      <p class="intro-text">It looks like we are missing some contact information for your {{businessType}}. You will need to supply us with a few additional details before you can get started...</p>
      <v-card class="profile-card">
        <v-container>
          <h2>Business Contact</h2>
          <BusinessContactForm/>
        </v-container>
      </v-card>
    </article>
    <aside>
      <SupportInfoCard/>
    </aside>
  </div>
</template>

<script>
import Vue from 'vue'
import BusinessContactForm from '@/components/auth/BusinessContactForm'
import SupportInfoCard from '@/components/SupportInfoCard'

export default {
  name: 'BusinessProfile',
  components: {
    BusinessContactForm,
    SupportInfoCard
  }
}
</script>

<style lang="stylus" scoped>
  @import '../assets/styl/theme.styl';

  h1, h2
    margin-bottom: 1.5rem;

  article
    flex: 1 1 auto;

  aside
    flex 0 0 auto
    margin-top 2rem

  .intro-text
    margin-bottom 2rem
    letter-spacing -0.01rem
    font-size 1rem
    font-weight 300

    em
      font-style: normal
      font-weight: 400

  .view-container
    display flex
    flex-flow column nowrap

  .profile-card .container
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

  .view-container
      flex-flow row nowrap
</style>
