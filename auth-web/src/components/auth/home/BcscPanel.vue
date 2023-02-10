<template>
  <v-container id="bcsc-container">
    <h2>Create an Account to Incorporate</h2>
    <p class="my-5">
      Log in securely using your mobile BC Services Card, government's trusted way to access online services
    </p>
    <v-row class="mt-5">
      <!-- Image Column -->
      <v-col cols="12" md="6" class="bcsc-info-col">
        <h2>It's Secure</h2>
        <v-list-item class="list-item" v-for="(item, index) in secureBulletPoints" :key="`List-1-${index}`" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-col>
      <!-- Info Column -->
      <v-col cols="12" md="6" class="bcsc-info-col">
        <h2>It's Quick and Easy</h2>
        <v-list-item class="list-item">
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">It normally takes about 5 minutes to
              <a :href="cardSetUpUrl" class="link" target="_blank">set up a mobile card</a>
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <v-list-item class="list-item" v-for="(item, index) in easeBulletPoints" :key="`List-2-${index}`" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
      </v-col>
    </v-row>
    <!-- Panel Btns -->
    <div class="mt-10">
      <template v-if="!user">
        <v-btn large color="bcgovblue" class="cta-btn font-weight-bold white--text mr-2 px-7"
          to="/choose-authentication-method">
          Create a BC Registries Account
        </v-btn>
      </template>
      <learn-more-button :redirect-url="learnMoreUrl" />
    </div>
  </v-container>
</template>

<script lang="ts">
import { PropType, defineComponent } from '@vue/composition-api'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'
import { User } from '@/models/user'
import Vue from 'vue'

export default defineComponent({
  name: 'BcscPanel',
  components: {
    LearnMoreButton
  },
  props: {
    userProfile: Object as PropType<User>
  },
  emits: ['login', 'account-dialog'],
  setup (props, { emit }) {
    const user = props.userProfile
    const cardSetUpUrl = 'https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup'
    const learnMoreUrl = 'https://www2.gov.bc.ca/gov/content/governments/government-id/bcservicescardapp/setup'
    const secureBulletPoints = [
      { text: 'A mobile card is a representation of your BC Services Card on your mobile device. It\'s used to prove who you are when you log in to access government services online.' },
      { text: 'Only your name and a unique identifier is stored on the mobile device.' }
    ] as { text: String }[]

    const easeBulletPoints = [
      { text: 'You can verify your identity by video right from your mobile device. You don\'t need to go in person unless you can\'t verify by video.' }
    ] as { text: String }[]

    const emitLogin = () => {
      emit('login')
    }

    const emitAccountDialog = () => {
      emit('account-dialog')
    }

    return {
      user,
      cardSetUpUrl,
      learnMoreUrl,
      secureBulletPoints,
      easeBulletPoints,
      emitLogin,
      emitAccountDialog
    }
  }
})
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #bcsc-container {
    background: $BCgovBG;
    display: flex;
    flex-direction: column;
    text-align: center;

    h2 {
      font-size: 2rem;
    }

    .bcsc-info-col {
     justify-content: flex-start;
      text-align: left;
    }

    .list-item {
      align-items: flex-start;
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-bullet {
      color: $BCgovBullet;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 1rem;
      letter-spacing: 0;
      line-height: 1.5rem;
    }

    .v-btn {
      max-width: 300px;
      font-weight: bold;
      color: $BCgovBlue5;
    }

    .v-btn:hover {
      opacity: .8;
      color: white !important;
    }

    .link {
      font-size: 1rem;
      color: $BCgoveBueText1;
    }

    .link:hover {
      color: $BCgoveBueText2;
    }
  }
</style>
