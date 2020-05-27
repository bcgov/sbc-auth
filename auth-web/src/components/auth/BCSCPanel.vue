<template>
  <v-container id="bcsc-container" class="my-10">
    <h2 class="mt-5">Create an Account to Incorporate</h2>
    <p class="my-5">Log in securely using your mobile BC Services Card, government's trust way to access online services</p>
    <v-row>
      <!-- Image Column -->
      <v-col cols="12" md="5">
        <v-img src="../../assets/img/BCSC-Helper.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
      <v-spacer></v-spacer>
      <!-- Info Column -->
      <v-col cols="12" md="6" class="bcsc-info-col">
        <h2>It's Secure</h2>
        <v-list-item class="list-item" v-for="(item, index) in secureBulletPoints" :key="index" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <h2>It's Quick and Easy</h2>
        <v-list-item class="list-item" v-for="(item, index) in easeBulletPoints" :key="index" >
          <v-icon size="8" class="list-item-bullet mt-5">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <template v-if="!userProfile">
          <v-btn large color="#fcba19" @click="emitLogin()" class="mt-5">
            Log in with BC Services Card
          </v-btn>
          <p class="my-5">New to BC Registries? <a @click="emitAccountDialog()" class="create-account-link">
            <u>Create a BC Registries Account</u></a>
          </p>
        </template>
        <LearnMoreButton />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator'
import LearnMoreButton from '@/components/auth/common/LearnMoreButton.vue'

@Component({
  components: {
    LearnMoreButton
  }
})
export default class BCSCPanel extends Vue {
  private secureBulletPoints: Array<any> = [
    { text: 'A mobile card is a representation of your BC Services Card on your mobile device. It\'s used to prove who you are when you log in to access government services online.' },
    { text: 'Only your name and a unique identifier is stored on the mobile device.' }
  ]

  private easeBulletPoints: Array<any> = [
    { text: 'It normally takes about 5 minutes to set up a mobile card.' },
    { text: 'you can verify your identity by video right from your mobile device. You don\'t need to go in person unless you can\'t verify by video.' }
  ]

  @Prop() userProfile

  @Emit('login')
  private emitLogin () {}

  @Emit('account-dialog')
  private emitAccountDialog () {}
}
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

    a:hover {
      color: $BCgoveBueText2;
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
    }
  }
</style>
