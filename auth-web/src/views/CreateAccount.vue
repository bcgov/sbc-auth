<template>
  <div class="view-container">
    <article>
      <h1>Create Account</h1>
        <p>Before you can create an account with BC Registries & Online Services, 
          you'll need to sign-in to our application with an existing 
          <span><a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card" 
          target="_blank">BC Services Card</a></span>
        </p>
  
        <IdpLogin v-bind:label="'Sign in with my BC Services Card'" v-bind:hint="'bcsc'"/>
        
    </article>
    <aside>
      <SupportInfoCard/>
    </aside>
  </div>
</template>

<script lang="ts">
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import IdpLogin from '@/components/auth/IdpLogin.vue'
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'

import UserModule from '../store/modules/user'

@Component({
  components: {
    SupportInfoCard,
    IdpLogin
  }
})
export default class CreateAccount extends Vue {
  private userStore = getModule(UserModule, this.$store)

  mounted () {
    this.userStore.initKeycloak().then((kcInit) => {
      kcInit.success((authenticated)=>{
        console.log('User is logged in '+authenticated);
        if (authenticated === true){
          this.userStore.initializeSession().then(()=>{
            this.userStore.getUserProfile(this.userStore.currentUser.keycloakGuid).then(()=>{
              //If profile exists redirect to dashboard, else to user profile page
              this.$router.push(this.userStore.userProfile ? '/dashboard' : '/userprofile' )
            })
          })
        }
      })
      
    })
  }


}
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
