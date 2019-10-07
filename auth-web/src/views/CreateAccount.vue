<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>Create Account</h1>
          <p>Before you can create an account with BC Registries & Online Services,
            you'll need to sign-in to our application with an existing
            <span><a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card"
            target="_blank">BC Services Card</a></span>
          </p>

          <v-btn color='primary' to="/signin/bcsc" class=".signin-button">
            <span>Sign in with my BC Services Card</span>
          </v-btn>
          <p>
            <span><a href="https://www2.gov.bc.ca/gov/content/governments/government-id/bc-services-card/get-a-card"
            target="_blank">I don't have BC Services Card</a></span>
          </p>
          <h2>Why do I need to sign in with my BC Services Card?</h2>
          <p>
            <span>A BC Services Card provides secure access to provincial government services and access to online services and features with BC Registries. </span>
          </p>
      </article>
      <aside>
        <SupportInfoCard/>
      </aside>
    </div>
  </v-container>
</template>

<script lang="ts">
import SupportInfoCard from '@/components/SupportInfoCard.vue'
import { Vue, Component } from 'vue-property-decorator'
import { getModule } from 'vuex-module-decorators'

import UserModule from '../store/modules/user'

@Component({
  components: {
    SupportInfoCard
  }
})
export default class CreateAccount extends Vue {

}
</script>
