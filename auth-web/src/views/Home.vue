<template>
  <v-container>
    <div class="view-container">
      <article>
        <h1>File BC Co-operative <span>Annual Reports</span></h1>
        <p class="intro-text">Sign in to start filing your BC Co-operative Annual Report. You will need to provide your <em>Incorporation Number</em> and your <em>Passcode</em> in the letter you received in the mail.</p>
        <v-card class="sign-in-card">
          <v-container>
            <h2 class="mb-7">Sign In</h2>
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

<style lang="scss" scoped>
  // Layout
  article {
    flex: 1 1 auto;
  }

  aside {
    flex: 0 0 auto;
    margin-top: 2rem;
  }

  @media (min-width: 960px) {
    article {
      padding-top: 0.5rem;
      padding-bottom: 0.5rem;
    }

    aside {
      margin-top: 0;
      margin-left: 2rem;
      width: 20rem;
    }

    .view-container {
      flex-flow: row nowrap;
    }
  }

  .intro-text {
    margin-bottom: 3rem;
  }

  // Sign In
  .sign-in-card .container {
    padding: 1.5rem;
  }

  @media (min-width: 960px) {
    .sign-in-card .container {
      padding: 2rem;
    }
  }
</style>
