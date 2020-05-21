<template>
  <v-container id="incorporate-info-container">
    <v-row>
      <!-- Info Column -->
      <v-col cols="12" md="6">
        <h2>Incorporate or Register</h2>
        <v-list-item class="list-item" v-for="(item, index) in bulletPoints" :key="index">
          <v-icon size="6" class="list-item-bullet">mdi-square</v-icon>
          <v-list-item-content>
            <v-list-item-subtitle class="list-item-text">
              {{item.text}}
            </v-list-item-subtitle>
          </v-list-item-content>
        </v-list-item>
        <!-- Panel Btns -->
        <div class="incorporate-info-btns">
          <v-btn large color="#fcba19" @click="login()" class="my-5">
            Log in with BC Services Card
          </v-btn>
          <v-btn large outlined color="#003366" class="btn-learn-more"
            href="https://smallbusinessbc.ca/article/how-to-choose-the-right-business-structure-for-your-small-business/%7D"
            target="_blank" rel="noopener noreferrer">
            Learn More
          </v-btn>
        </div>
      </v-col>
      <!-- Image Column -->
      <v-col cols="12" md="6">
        <v-img src="../../assets/img/Step3-Incorporate-x1.png" aspect-ratio="1.2" contain></v-img>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { Pages } from '@/util/constants'

@Component({})
export default class IncorpOrRegisterInfo extends Vue {
  private bulletPoints: Array<any> = [
    { text: 'If you have an approved Name Request (NR number), or you want a numbered Benefit Company, you can start your Incorporation Application.' },
    { text: 'For Name Companies, add your existing Name Request number to your account and open it.' },
    { text: 'Establish your company\'s articles and prepare an incorporation agreement. Either create your own, or use template provided in the incorporation application.' },
    { text: 'Complete the Incorporation application by providing information about your company: addresses, directors and share structure.' },
    { text: 'Retain a copy of all Incorporation documents for your business\'s records.' }
  ]

  private login (): void {
    this.$router.push(`/signin/bcsc/${Pages.CREATE_ACCOUNT}`)
  }
}
</script>

<style lang="scss" scoped>
  @import '$assets/scss/theme.scss';

  #incorporate-info-container {
    padding-top: 0!important;
    flex-wrap: wrap;

    .list-item {
      margin: .5rem 0;
      padding-left: 0;
    }

    .list-item-bullet {
      color: #CCCCCC;
      margin-right: 1rem;
    }

    .list-item-text {
      white-space: initial;
      color: $gray7;
      font-size: 16px;
      letter-spacing: 0;
      line-height: 24px;
    }

    .incorporate-info-btns {
      display: flex;
      flex-direction: column;

      .v-btn {
        max-width: 250px;
        font-weight: bold;
      }

      .btn-learn-more {
        font-weight: bold;
        width: 160px;
      }
    }
  }
</style>
